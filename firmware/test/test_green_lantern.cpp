// test_green_lantern.cpp - host-side simulation of firmware/green_lantern/green_lantern.ino
//
// The mocks (Arduino.h, EEPROM.h in this directory) are included first,
// then the sketch itself is pulled in as part of this translation unit, so the scenarios can
// call setup()/loop(), drive the pins through the fake clock and inspect the sketch's globals.
//
// Build + run:   make -C firmware/test test      (or ./run.sh)

#include "Arduino.h"
#include "EEPROM.h"

#ifndef SKETCH_PATH
#define SKETCH_PATH "../green_lantern/green_lantern.ino"
#endif
#include SKETCH_PATH

#include <functional>
#include <cmath>

// ------------------------------------------------------------------ tiny test framework
struct Result { std::string id, name; std::vector<std::string> fails, notes; };
static std::vector<Result> results;
static Result* cur = nullptr;

#define CHECK(cond, ...) do { if (!(cond)) { char _b[512]; snprintf(_b, sizeof _b, __VA_ARGS__); \
  cur->fails.push_back("line " + std::to_string(__LINE__) + ": " + _b); } } while (0)
#define NOTE(...) do { char _b[512]; snprintf(_b, sizeof _b, __VA_ARGS__); cur->notes.push_back(_b); } while (0)

static void scenario(const char* id, const char* name, const std::function<void()>& body) {
  results.push_back(Result{id, name, {}, {}});
  cur = &results.back();
  body();
  cur = nullptr;
}

// ------------------------------------------------------------------ sim helpers
static bool   pumpPinOn()   { return sim::pin[PUMP_PIN].on; }
static size_t pumpRuns()    { return sim::runs[PUMP_PIN].size(); }
static double pumpRunMs(size_t i) { return sim::runLengthUs(sim::runs[PUMP_PIN][i]) / 1000.0; }
static double pumpRunStartMs(size_t i) { return sim::runs[PUMP_PIN][i].startUs / 1000.0; }
static double pumpRunEndMs(size_t i)   { return sim::runs[PUMP_PIN][i].endUs / 1000.0; }
static double nowMs() { return sim::nowUs / 1000.0; }
static bool pumpPinQuiet() {           // PWM really released: pad back on SIO and driven LOW
  return sim::pin[PUMP_PIN].func == sim::FUNC_SIO && sim::pin[PUMP_PIN].out == LOW;
}

static void setRing(bool present)  { sim::setInput(HALL_PIN,   present ? LOW : HIGH); }  // A3144: LOW = magnet
static void setSwitch(bool pressed){ sim::setInput(SWITCH_PIN, pressed ? LOW : HIGH); }  // NO to GND, pull-up
static void setPrime(bool held)    { sim::setInput(PRIME_PIN,  held    ? LOW : HIGH); }  // button to GND, pull-up
static void serialLine(const std::string& l) { Serial.inject(l + "\n"); }
static bool serialSaid(const std::string& s) { return Serial.tx.find(s) != std::string::npos; }

static double LOOP_MS = 0;   // measured loop() period in simulation (delay(8) + show() wire time)
// Run-length checks allow 1 ms below the request: pumpStarted = millis() truncates sub-ms time, so a run
// can end up to 1 ms early (same on hardware), and up to one loop pass late.

// run loop() until `ms` of simulated time have passed
static unsigned runMs(double ms) {
  const uint64_t end = sim::nowUs + (uint64_t)(ms * 1000);
  unsigned n = 0;
  while (sim::nowUs < end) {
    loop(); n++;
    if (n > 100000000u) { fprintf(stderr, "loop() does not advance the fake clock\n"); exit(2); }
  }
  return n;
}
// run loop() until pred() holds (checked after every iteration) or maxMs elapse; elapsed ms or -1
static double runUntil(const std::function<bool()>& pred, double maxMs) {
  const uint64_t start = sim::nowUs, end = start + (uint64_t)(maxMs * 1000);
  while (sim::nowUs < end) { loop(); if (pred()) return (sim::nowUs - start) / 1000.0; }
  return -1;
}

// Power cycle: pins, clock, serial and the EEPROM RAM copy are reset, the sketch's globals go back
// to their declared initial values and setup() runs. The flash sector survives unless erased.
struct BootOpts { uint64_t startUs = 0; bool keepFlash = false; bool switchHeld = false; bool ringPresent = false; bool primeHeld = false; };
static void reboot(BootOpts o = BootOpts{}) {
  sim::resetPins();
  sim::pwmRange = 255;
  sim::nowUs = o.startUs;
  Serial.reset();
  EEPROM.powerCycle();
  if (!o.keepFlash) EEPROM.eraseFlash();
  setSwitch(o.switchHeld);
  setRing(o.ringPresent);
  setPrime(o.primeHeld);

  settings = defaultSettings();
  state = State::IDLE;
  stateSince = hallChanged = swChanged = 0;
  hallRaw = swRaw = hallStable = swStable = switchJammed = pouredThisInsertion = false;
  primeChanged = 0; primeRaw = primeStable = primeReady = false;
  pumpOn = false; pumpStarted = pumpRunFor = 0;
  pumpOnSince = 0; pumpCal = false; pumpPrime = false;
  lineBuf = "";
  ledShown = 0.0f; ledLastMs = 0; ledDuty = 0; finaleFrom = finaleTo = 0.0f;
  battV = 0.0f; lowBattWarn = false;
  for (int i = 0; i < sim::NPINS; i++) sim::analogIn[i] = 0;   // no battery divider unless a scenario fits one

  setup();
}

// battery divider: the raw ADC count a given pack voltage produces (inverse of the sketch's battRead)
static void setBattery(double volts) {
  sim::analogIn[BATT_PIN] = (int)lround(volts / (ADC_VREF * BATT_DIVIDER) * ADC_MAX);
}

// ------------------------------------------------------------------ helpers for the hold-to-pour flow
static uint32_t speedDuty() { return (PWM_RANGE * settings.pumpSpeed) / 100; }
static uint32_t lightDuty(float p) {      // the sketch's own formula, for exact comparisons
  uint32_t d = (uint32_t)(powf(p, GAMMA) * (float)settings.maxBright * ((float)PWM_RANGE / 255.0f) + 0.5f);
  const uint32_t f = (uint32_t)settings.idleDuty * PWM_RANGE / 255;
  if (d < f) d = f;
  if (d > PWM_RANGE) d = PWM_RANGE;
  return d;
}
static const double FINALE_MS = FINALE_UP_MS + FINALE_HOLD_MS + FINALE_FADE_MS;
static bool insertRing() { setRing(true); return runUntil([] { return state == State::ARMED; }, 1000) >= 0; }
static bool twistAndHold() { setSwitch(true); return runUntil([] { return pumpPinOn(); }, 1000) >= 0; }
static bool holdToEnd() { return runUntil([] { return state == State::HOLDING; }, (double)MAX_PUMP_MS + 2000) >= 0; }

// ------------------------------------------------------------------ the canonical pour (d / j)
struct PourMeasure {
  double armedAfter = -1, pumpAfterPress = -1, pourLen = -1, finaleAfterRelease = -1, lockedAfterFinale = -1;
  std::string stateAtPumpOff; bool pwmReleased = false; int dutyAt600 = -1; uint32_t lightAtPumpOff = 0;
  uint32_t millisAtStart = 0, millisAtEnd = 0;
};
static PourMeasure doPour(uint64_t startUs) {
  PourMeasure m;
  reboot(BootOpts{startUs});
  m.millisAtStart = millis();
  setRing(true);
  m.armedAfter = runUntil([] { return state == State::ARMED; }, 1000);
  runMs(2000);                                            // the first words of the oath
  setSwitch(true);                                        // twist and hold
  m.pumpAfterPress = runUntil([] { return pumpPinOn(); }, 1000);
  runMs(600);
  m.dutyAt600 = sim::pin[PUMP_PIN].func == sim::FUNC_PWM ? sim::pin[PUMP_PIN].pwm : -1;
  runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 2000);
  if (pumpRuns() >= 1) m.pourLen = pumpRunMs(0);
  m.stateAtPumpOff = stateName(state);
  m.lightAtPumpOff = ledDuty;
  m.pwmReleased = pumpPinQuiet();
  runMs(1500);                                            // still holding: lights stay at the peak
  setSwitch(false);                                       // the ring turns back
  m.finaleAfterRelease = runUntil([] { return state == State::FINALE; }, 1000);
  m.lockedAfterFinale = runUntil([] { return state == State::LOCKED; }, 5000);
  m.millisAtEnd = millis();
  return m;
}
static void checkPour(const PourMeasure& m) {
  CHECK(m.armedAfter >= HALL_DEBOUNCE_MS && m.armedAfter <= HALL_DEBOUNCE_MS + 2 * LOOP_MS, "ARMED after %.1f ms", m.armedAfter);
  CHECK(m.pumpAfterPress >= SWITCH_DEBOUNCE_MS && m.pumpAfterPress <= SWITCH_DEBOUNCE_MS + 2 * LOOP_MS, "pump on %.1f ms after the twist", m.pumpAfterPress);
  CHECK(m.dutyAt600 == (int)speedDuty(), "running duty %d (want %u = speed %u %%)", m.dutyAt600, speedDuty(), settings.pumpSpeed);
  CHECK(m.pourLen >= settings.pourMs - 1 && m.pourLen <= settings.pourMs + LOOP_MS, "pump ran %.1f ms (pourMs=%u)", m.pourLen, (unsigned)settings.pourMs);
  CHECK(m.stateAtPumpOff == "HOLDING", "state when the pour completed: %s (want HOLDING)", m.stateAtPumpOff.c_str());
  CHECK(m.lightAtPumpOff + 2 >= lightDuty(POUR_PEAK) && m.lightAtPumpOff <= lightDuty(POUR_PEAK), "light at the end of the pour %u (want ~%u = %.0f %%)", m.lightAtPumpOff, lightDuty(POUR_PEAK), POUR_PEAK * 100);
  CHECK(m.pwmReleased, "pump pad still on the PWM function / not LOW after pumpStop()");
  CHECK(m.finaleAfterRelease >= SWITCH_DEBOUNCE_MS && m.finaleAfterRelease <= SWITCH_DEBOUNCE_MS + 2 * LOOP_MS, "FINALE %.1f ms after the release", m.finaleAfterRelease);
  CHECK(m.lockedAfterFinale >= FINALE_MS - LOOP_MS && m.lockedAfterFinale <= FINALE_MS + 2 * LOOP_MS, "LOCKED %.1f ms after FINALE began (want ~%.0f)", m.lockedAfterFinale, FINALE_MS);
  CHECK(pumpRuns() == 1, "pump energised %zu times", pumpRuns());
}

// ------------------------------------------------------------------ scenarios
int main() {
  reboot();
  { const uint64_t t0 = sim::nowUs; for (int i = 0; i < 100; i++) loop(); LOOP_MS = (sim::nowUs - t0) / 1000.0 / 100; }
  printf("simulated loop() period: %.2f ms; one-iteration budget: 20 ms\n", LOOP_MS);
  if (LOOP_MS > 20) { printf("FAIL loop period exceeds 20 ms\n"); return 1; }

  scenario("a", "boot: pump LOW first, lights dark, jammed switch ignored until released + twisted again", [] {
    reboot(BootOpts{0, false, /*switchHeld*/ true});
    CHECK(!pumpPinOn() && pumpRuns() == 0 && pumpPinQuiet(), "pump pin active after setup()");
    CHECK(sim::events.size() >= 2 && sim::events[0].pin == PUMP_PIN && !strcmp(sim::events[0].what, "pinMode") && sim::events[0].val == OUTPUT
          && sim::events[1].pin == PUMP_PIN && !strcmp(sim::events[1].what, "digitalWrite") && sim::events[1].val == LOW,
          "pump pin is not the first thing setup() configures");
    CHECK(switchJammed, "switch held through boot not flagged as jammed");
    runMs(1000);
    CHECK(state == State::IDLE && ledDuty == 0, "IDLE: state %s light %u (want dark)", stateName(state), ledDuty);
    CHECK(insertRing(), "never ARMED");
    runMs(8000);
    CHECK(pumpRuns() == 0, "jammed switch + ring poured");
    setSwitch(false); runMs(300);
    CHECK(!switchJammed && pumpRuns() == 0, "jam flag %d runs %zu after release", switchJammed, pumpRuns());
    CHECK(twistAndHold(), "no pour after release + twist");
    CHECK(holdToEnd(), "never reached HOLDING");
    setSwitch(false);
    runUntil([] { return state == State::LOCKED; }, 5000);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "runs=%zu state=%s", pumpRuns(), stateName(state));
  });

  scenario("b", "switch only (no ring): never pumps, 60 s of toggling", [] {
    reboot();
    bool everLeftIdle = false;
    for (int i = 0; i < 60; i++) {
      setSwitch(true);  runMs(500); everLeftIdle |= (state != State::IDLE);
      setSwitch(false); runMs(500); everLeftIdle |= (state != State::IDLE);
    }
    CHECK(pumpRuns() == 0 && !everLeftIdle && pumpPinQuiet(), "runs %zu, left IDLE %d", pumpRuns(), everLeftIdle);
  });

  scenario("c", "ring only: ARMED at the ~15 % glow for 60 s, never pumps", [] {
    reboot();
    CHECK(insertRing(), "never ARMED");
    runMs(60000);
    CHECK(state == State::ARMED && pumpRuns() == 0, "state %s runs %zu", stateName(state), pumpRuns());
    CHECK(ledDuty == lightDuty(ARMED_LEVEL), "ARMED light %u (want %u)", ledDuty, lightDuty(ARMED_LEVEL));
  });

  static PourMeasure pourD;
  scenario("d", "twist and hold: pump runs pourMs at the set speed, lights climb to ~90 %, HOLDING; release -> FINALE -> LOCKED", [] {
    pourD = doPour(0);
    checkPour(pourD);
    NOTE("ARMED +%.1f ms, pump %.1f ms after the twist, ran %.1f ms, light at the end %u/%u, FINALE %.1f ms after release, LOCKED %.1f ms later",
         pourD.armedAfter, pourD.pumpAfterPress, pourD.pourLen, pourD.lightAtPumpOff, PWM_RANGE, pourD.finaleAfterRelease, pourD.lockedAfterFinale);
  });

  scenario("e", "LOCKED: twisted and held 5 s, re-twisted 20x with the ring in -> no second pour", [] {
    CHECK(state == State::LOCKED && pumpRuns() == 1, "precondition: state %s runs %zu", stateName(state), pumpRuns());
    setSwitch(true); runMs(5000);
    for (int i = 0; i < 20; i++) { setSwitch(false); runMs(150); setSwitch(true); runMs(150); }
    setSwitch(false); runMs(500);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "runs=%zu state=%s", pumpRuns(), stateName(state));
    CHECK(sim::totalOnUs(PUMP_PIN) / 1000.0 <= settings.pourMs + LOOP_MS, "extra pump time");
  });

  scenario("f", "ring pulled out mid-pour (still twisted): pump off within one pass of POUR_ABORT_MS, LOCKED, then IDLE", [] {
    reboot();
    insertRing(); twistAndHold(); runMs(3000);
    CHECK(state == State::POURING && pumpPinOn(), "precondition");
    const double tRemove = nowMs();
    setRing(false);
    bool offSamePass = false, conditionSeen = false; int passes = 0;
    while (passes++ < 100) {
      const bool cond = !hallRaw && since(hallChanged) >= POUR_ABORT_MS;
      loop();
      if (cond) { conditionSeen = true; offSamePass = !pumpPinOn(); break; }
    }
    CHECK(conditionSeen && offSamePass, "pump still on in the pass that saw %u ms of absence", (unsigned)POUR_ABORT_MS);
    const double offLatency = pumpRunEndMs(0) - tRemove;
    CHECK(offLatency >= POUR_ABORT_MS && offLatency <= POUR_ABORT_MS + 2 * LOOP_MS, "pump off %.1f ms after the removal", offLatency);
    CHECK(state == State::LOCKED && pumpPinQuiet(), "state after abort %s", stateName(state));
    setSwitch(false);
    CHECK(runUntil([] { return state == State::IDLE; }, 1000) >= 0 && nowMs() - tRemove <= RING_GONE_MS + 2 * LOOP_MS, "IDLE %.1f ms after removal", nowMs() - tRemove);
    runMs(2000);
    CHECK(state == State::IDLE && pumpRuns() == 1 && ledDuty == 0, "after abort: %s runs %zu light %u", stateName(state), pumpRuns(), ledDuty);
    NOTE("pump off %.1f ms after the ring left", offLatency);
  });

  scenario("g", "remove and re-insert the ring: exactly one new pour each time", [] {
    CHECK(state == State::IDLE && pumpRuns() == 1, "precondition");
    CHECK(insertRing(), "not re-armed");
    runMs(1000);
    CHECK(twistAndHold() && holdToEnd(), "second pour did not complete");
    setSwitch(false); runUntil([] { return state == State::LOCKED; }, 5000);
    CHECK(pumpRuns() == 2 && pumpRunMs(1) >= settings.pourMs - 1 && pumpRunMs(1) <= settings.pourMs + LOOP_MS, "second pour %.1f ms", pumpRunMs(1));
    for (int i = 0; i < 5; i++) { setSwitch(true); runMs(300); setSwitch(false); runMs(300); }
    CHECK(pumpRuns() == 2 && state == State::LOCKED, "re-twist poured: runs %zu state %s", pumpRuns(), stateName(state));
    setRing(false); runMs(1000); insertRing(); runMs(500);
    CHECK(twistAndHold() && pumpRuns() == 3, "third insertion did not pour");
    setSwitch(false);
  });

  scenario("h", "hard cap: 'pour' above MAX_PUMP_MS rejected; forced long runs stop at MAX_PUMP_MS", [] {
    reboot();
    serialLine("pour 25000"); serialLine("pour 20001"); serialLine("pour 499"); runMs(50);
    CHECK(settings.pourMs == DEFAULT_POUR_MS, "invalid pour accepted: %u", (unsigned)settings.pourMs);
    serialLine("pour 20000"); runMs(50);
    CHECK(settings.pourMs == MAX_PUMP_MS, "pour 20000 (= cap) rejected");
    serialLine("pour 11000"); runMs(50);
    insertRing();
    pumpStart(MAX_PUMP_MS + 5000);
    CHECK(pumpRunFor == MAX_PUMP_MS, "pumpStart did not clamp: %u", (unsigned)pumpRunFor);
    pumpRunFor = MAX_PUMP_MS + 5000;                     // bypass the clamp: pumpService() must still stop it
    pumpCal = true;                                      // (a bare pumpStart() in ARMED is not a pour; keep the interlock out of the way)
    CHECK(runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 10000) >= 0, "forced run never stopped");
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= MAX_PUMP_MS - 1 && pumpRunMs(0) <= MAX_PUMP_MS + LOOP_MS, "forced run %.1f ms", pumpRunMs(0));
    setRing(false); runMs(1000);
    // the cap is on continuous run time: a cal run followed by a held pour cannot exceed it
    reboot();
    serialLine("cal 20000"); runMs(15000);
    insertRing(); twistAndHold();
    runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 20000);
    const double longest = sim::longestRunUs(PUMP_PIN) / 1000.0;
    CHECK(longest <= MAX_PUMP_MS + LOOP_MS, "cal + pour ran %.1f ms continuously (cap %u)", longest, (unsigned)MAX_PUMP_MS);
    CHECK(state == State::HOLDING, "state %s after the capped pour (want HOLDING until the release)", stateName(state));
    setSwitch(false);
    NOTE("cal+pour longest continuous run %.1f ms", longest);
  });

  scenario("i", "serial: cal without the ring, stop, pour/speed/leds/idle + save + reboot persist", [] {
    reboot();
    serialLine("cal 3000"); runMs(LOOP_MS * 2);
    CHECK(pumpPinOn() && state == State::IDLE, "cal did not start (no ring) or changed state");
    runUntil([] { return !pumpPinOn(); }, 6000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= 2999 && pumpRunMs(0) <= 3000 + LOOP_MS, "cal ran %.1f ms", pumpRunMs(0));
    serialLine("cal 3000"); runMs(500); serialLine("stop");
    CHECK(runUntil([] { return !pumpPinOn(); }, LOOP_MS * 2) >= 0 && serialSaid("pump stopped"), "stop did not stop the pump");
    serialLine("cal 0"); serialLine("cal 25000"); serialLine("cal abc"); runMs(100);
    CHECK(pumpRuns() == 2, "invalid cal values started the pump");
    // stop during a held pour -> pump off, still HOLDING-like? it stays POURING->HOLDING on the next pass
    insertRing(); twistAndHold(); runMs(2000); serialLine("stop"); runMs(LOOP_MS * 3);
    CHECK(!pumpPinOn() && state == State::HOLDING, "stop during a pour: pump %d state %s", pumpPinOn(), stateName(state));
    setSwitch(false); runUntil([] { return state == State::LOCKED; }, 5000);
    setSwitch(true); runMs(500); setSwitch(false);
    CHECK(pumpRuns() == 3, "re-pour after stop (runs %zu)", pumpRuns());
    setRing(false); runMs(1000);
    serialLine("pour 12500"); serialLine("speed 60"); serialLine("leds 128"); serialLine("idle 30"); runMs(50);
    Serial.tx.clear(); serialLine("status"); runMs(50);
    CHECK(serialSaid("pourMs=12500") && serialSaid("speed=60") && serialSaid("maxBright=128") && serialSaid("idle=30") && serialSaid("state=IDLE"),
          "status output: %s", Serial.tx.c_str());
    CHECK(EEPROM.commits == 0, "flash written before 'save'");
    serialLine("save"); runMs(50);
    CHECK(EEPROM.commits == 1 && serialSaid("saved"), "save did not commit");
    reboot(BootOpts{0, /*keepFlash*/ true});
    CHECK(settings.pourMs == 12500 && settings.pumpSpeed == 60 && settings.maxBright == 128 && settings.idleDuty == 30, "settings after reboot");
    CHECK(runUntil([] { return ledDuty == 30u * PWM_RANGE / 255; }, 2000) >= 0, "idle glow %u after reboot", ledDuty);
    insertRing(); twistAndHold(); holdToEnd(); setSwitch(false);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= 12499 && pumpRunMs(0) <= 12500 + LOOP_MS, "pour used %.1f ms", pumpRunMs(0));
    reboot();
    CHECK(settings.pourMs == DEFAULT_POUR_MS && settings.pumpSpeed == DEFAULT_PUMP_SPEED, "erased flash did not give defaults");
  });

  scenario("j", "millis() wraparound: clock starts at 0xFFFFF000, scenario d behaves identically", [] {
    PourMeasure m = doPour(0xFFFFF000ULL * 1000ULL);
    checkPour(m);
    CHECK(m.millisAtEnd < m.millisAtStart, "millis() did not wrap during the scenario");
    CHECK(m.armedAfter == pourD.armedAfter && m.pumpAfterPress == pourD.pumpAfterPress && m.pourLen == pourD.pourLen
          && m.finaleAfterRelease == pourD.finaleAfterRelease && m.lockedAfterFinale == pourD.lockedAfterFinale,
          "differs from d");
  });

  scenario("k", "debounce: 30 ms Hall glitch does not arm; 20 ms twist glitch does not pour; 20 ms bounce mid-pour does not stop it", [] {
    reboot();
    setRing(true); runMs(30); setRing(false);
    CHECK(runUntil([] { return state != State::IDLE; }, 2000) < 0, "30 ms Hall glitch armed the prop");
    insertRing(); runMs(500);
    setSwitch(true); runMs(20); setSwitch(false);
    CHECK(runUntil([] { return state != State::ARMED; }, 2000) < 0 && pumpRuns() == 0, "20 ms twist glitch poured");
    CHECK(twistAndHold(), "real twist after the glitch did not pour");
    runMs(2000);
    setSwitch(false); runMs(20); setSwitch(true);
    runMs(500);
    CHECK(state == State::POURING && pumpPinOn() && pumpRuns() == 1, "20 ms switch bounce stopped the pour (state %s)", stateName(state));
    setSwitch(false); setRing(false);
  });

  scenario("l", "let go early: pump stops where it is, light swells ~10 % then goes dark, LOCKED (no resume)", [] {
    reboot();
    insertRing(); runMs(1000); twistAndHold();
    runMs(4000);
    const uint32_t before = ledDuty;
    const float shownBefore = ledShown;
    const double tRelease = nowMs();
    setSwitch(false);
    CHECK(runUntil([] { return !pumpPinOn(); }, 500) >= 0, "pump kept running after the release");
    const double offLatency = pumpRunEndMs(0) - tRelease;
    CHECK(offLatency >= SWITCH_DEBOUNCE_MS && offLatency <= SWITCH_DEBOUNCE_MS + 2 * LOOP_MS, "pump off %.1f ms after the release", offLatency);
    CHECK(state == State::FINALE, "state %s after an early release", stateName(state));
    CHECK(pumpRunMs(0) > 3900 && pumpRunMs(0) < 4200, "partial pour %.1f ms", pumpRunMs(0));
    uint32_t peak = 0;
    const double end = nowMs() + FINALE_MS + 200;
    while (nowMs() < end) { loop(); peak = std::max(peak, ledDuty); }
    const uint32_t want = lightDuty(std::min(1.0f, shownBefore + EARLY_BUMP));
    CHECK(peak + 2 >= want && peak <= want + 2 && peak > before, "early-release swell peaked at %u (was %u, want ~%u)", peak, before, want);
    CHECK(state == State::LOCKED && ledDuty == 0, "after the swell: state %s light %u (want LOCKED, dark)", stateName(state), ledDuty);
    setSwitch(true); runMs(2000); setSwitch(false); runMs(500);
    CHECK(pumpRuns() == 1, "re-twist after an early release resumed the pour");
    NOTE("pump off %.1f ms after letting go; light %u -> peak %u -> 0", offLatency, before, peak);
  });

  scenario("m", "switch stuck pressed before the ring goes in: no pour until released and twisted", [] {
    reboot();
    setSwitch(true); runMs(2000);
    CHECK(state == State::IDLE && pumpRuns() == 0, "switch alone");
    setRing(true); runMs(3000);
    CHECK(pumpRuns() == 0 && state == State::ARMED, "stuck switch + ring: runs %zu state %s", pumpRuns(), stateName(state));
    setSwitch(false); runMs(300);
    CHECK(twistAndHold() && pumpRuns() == 1, "release + twist did not pour");
    setSwitch(false);
  });

  scenario("n", "Hall dropout mid-pour: 30 ms does not abort; 70 ms aborts -> LOCKED, no second pour", [] {
    auto pourTo3s = [] { reboot(); insertRing(); twistAndHold(); runMs(3000); };
    pourTo3s();
    setRing(false); runMs(30); setRing(true);
    CHECK(pumpPinOn() && state == State::POURING, "30 ms dropout aborted (state %s)", stateName(state));
    holdToEnd();
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= settings.pourMs - 1 && pumpRunMs(0) <= settings.pourMs + LOOP_MS, "after a 30 ms dropout: pour %.1f ms", pumpRunMs(0));
    setSwitch(false);
    pourTo3s();
    const double tDrop = nowMs();
    setRing(false); runMs(70); setRing(true);
    CHECK(!pumpPinOn() && state == State::LOCKED, "70 ms dropout: pump %d state %s", pumpPinOn(), stateName(state));
    const double off = pumpRunEndMs(0) - tDrop;
    CHECK(off >= POUR_ABORT_MS && off <= POUR_ABORT_MS + 2 * LOOP_MS, "pump off %.1f ms after the dropout", off);
    runMs(1000);
    setSwitch(false); runMs(300); setSwitch(true); runMs(500); setSwitch(false);
    CHECK(state == State::LOCKED && pumpRuns() == 1, "re-twist after an aborted pour poured again");
    setRing(false);
    CHECK(runUntil([] { return state == State::IDLE; }, 1000) >= 0, "no IDLE after removal");
    insertRing();
    CHECK(twistAndHold() && pumpRuns() == 2, "fresh insertion after an abort did not pour");
    setSwitch(false);
  });

  scenario("o", "light: dark idle, ~15 % with the ring, steady climb to ~90 % over the pour, 100 % swell on release, then dark", [] {
    for (int mb : {255, 160}) for (int idle : {0, 30}) {
      reboot();
      settings.maxBright = (uint8_t)mb; settings.idleDuty = (uint8_t)idle;
      const uint32_t floorD = (uint32_t)idle * PWM_RANGE / 255;
      runMs(1000);
      CHECK(ledDuty == floorD, "mb %d idle %d: IDLE light %u (want %u)", mb, idle, ledDuty, floorD);
      insertRing(); runMs(ARMED_FADE_IN_MS + 200);
      CHECK(ledDuty == lightDuty(ARMED_LEVEL), "mb %d idle %d: ARMED light %u (want %u)", mb, idle, ledDuty, lightDuty(ARMED_LEVEL));
      setSwitch(true);
      runUntil([] { return state == State::POURING; }, 1000);
      uint32_t prev = ledDuty, maxStep = 0; bool mono = true; uint32_t mid = 0;
      const double t0 = nowMs();
      while (state == State::POURING) {
        loop();
        if (state != State::POURING) break;
        if (ledDuty < prev) mono = false;
        maxStep = std::max(maxStep, ledDuty - std::min(ledDuty, prev));
        prev = ledDuty;
        if (mid == 0 && nowMs() - t0 >= settings.pourMs / 2.0) mid = ledDuty;
      }
      CHECK(mono, "mb %d idle %d: light went down during the pour", mb, idle);
      CHECK(maxStep <= 4, "mb %d idle %d: light jumped %u in one pass (not gradual)", mb, idle, maxStep);
      const uint32_t wantMid = lightDuty(ARMED_LEVEL + (POUR_PEAK - ARMED_LEVEL) * 0.5f);
      CHECK(mid + 6 >= wantMid && mid <= wantMid + 6, "mb %d idle %d: light halfway through the pour %u (want ~%u)", mb, idle, mid, wantMid);
      CHECK(state == State::HOLDING, "mb %d idle %d: state %s after the pour", mb, idle, stateName(state));
      runMs(1000);
      CHECK(ledDuty == lightDuty(POUR_PEAK), "mb %d idle %d: HOLDING light %u (want %u)", mb, idle, ledDuty, lightDuty(POUR_PEAK));
      setSwitch(false);
      uint32_t peak = 0; bool sawFull = false;
      const double end = nowMs() + FINALE_MS + 300;
      while (nowMs() < end) { loop(); peak = std::max(peak, ledDuty); sawFull |= (ledDuty == lightDuty(1.0f)); }
      CHECK(sawFull && peak == lightDuty(1.0f), "mb %d idle %d: release swell peaked at %u (want full %u)", mb, idle, peak, lightDuty(1.0f));
      CHECK(state == State::LOCKED && ledDuty == floorD, "mb %d idle %d: after the finale state %s light %u", mb, idle, stateName(state), ledDuty);
      setRing(false); runMs(1000);
      CHECK(state == State::IDLE && ledDuty == floorD, "mb %d idle %d: back to IDLE light %u", mb, idle, ledDuty);
    }
  });

  scenario("q", "pump speed sets the running duty and leaves the pour time alone; out-of-range rejected; persists", [] {
    reboot();
    serialLine("speed 50"); serialLine("speed 20"); serialLine("speed 101"); runMs(50);
    CHECK(settings.pumpSpeed == 50, "speed %u (want 50)", settings.pumpSpeed);
    insertRing(); twistAndHold(); runMs(600);
    CHECK(sim::pin[PUMP_PIN].pwm == (int)((PWM_RANGE * 50) / 100), "running duty %d", sim::pin[PUMP_PIN].pwm);
    holdToEnd();
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= DEFAULT_POUR_MS - 1 && pumpRunMs(0) <= DEFAULT_POUR_MS + LOOP_MS, "pour %.1f ms", pumpRunMs(0));
    setSwitch(false);
    serialLine("save"); runMs(50);
    reboot(BootOpts{0, /*keepFlash*/ true});
    CHECK(settings.pumpSpeed == 50, "after reboot: speed %u", settings.pumpSpeed);
  });

  scenario("p", "PRIME button (D6): runs only while held in IDLE with no ring, stops on release, capped, never changes state", [] {
    reboot();
    setPrime(true);
    const double t = runUntil([] { return pumpPinOn(); }, 500);
    CHECK(t >= PRIME_DEBOUNCE_MS && t <= PRIME_DEBOUNCE_MS + 2 * LOOP_MS, "prime started after %.1f ms", t);
    CHECK(state == State::IDLE && pumpPrime, "state %s pumpPrime %d", stateName(state), pumpPrime);
    runMs(100);
    CHECK(sim::pin[PUMP_PIN].func == sim::FUNC_PWM && sim::pin[PUMP_PIN].pwm > (int)(PWM_RANGE / 6) && sim::pin[PUMP_PIN].pwm < (int)speedDuty(), "no soft start (duty %d at 100 ms)", sim::pin[PUMP_PIN].pwm);
    runMs(300);
    CHECK(sim::pin[PUMP_PIN].pwm == (int)speedDuty(), "duty %d after the ramp (want %u)", sim::pin[PUMP_PIN].pwm, speedDuty());
    setPrime(false);
    CHECK(runUntil([] { return !pumpPinOn(); }, 2 * LOOP_MS) >= 0, "pump still on after release");
    CHECK(pumpRuns() == 1 && state == State::IDLE && pumpPinQuiet(), "after release: runs %zu state %s", pumpRuns(), stateName(state));
    setPrime(true); runMs(20); setPrime(false); runMs(500);
    CHECK(pumpRuns() == 1, "20 ms PRIME glitch ran the pump");
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500); runMs(500);
    setPrime(false); runMs(10); setPrime(true);
    CHECK(runUntil([] { return !pumpPinOn(); }, 2 * LOOP_MS) >= 0, "raw glitch did not stop the prime");
    runMs(1000);
    CHECK(pumpRuns() == 2 && !pumpPinOn(), "prime restarted after a glitch without a real release");
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 3, "no restart after a real release + press");
    setPrime(false); runMs(100);
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500);
    CHECK(runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 2000) >= 0, "capped prime never stopped");
    CHECK(pumpRuns() == 4 && pumpRunMs(3) >= MAX_PUMP_MS - 1 && pumpRunMs(3) <= MAX_PUMP_MS + LOOP_MS, "capped prime ran %.1f ms", pumpRunMs(3));
    runMs(3000);
    CHECK(pumpRuns() == 4, "prime restarted while still held after the cap");
    setPrime(false); runMs(100);
    reboot(BootOpts{0, false, false, false, /*primeHeld*/ true});
    runMs(2000);
    CHECK(pumpRuns() == 0, "PRIME held at boot primed");
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 1, "no prime after release + press");
    setPrime(false); runMs(100);
    // never in another state; does not disturb a held pour
    reboot();
    insertRing();
    setPrime(true); runMs(2000); setPrime(false); runMs(100);
    CHECK(pumpRuns() == 0 && state == State::ARMED, "PRIME in ARMED: runs %zu state %s", pumpRuns(), stateName(state));
    twistAndHold(); runMs(2000); setPrime(true); runMs(500); setPrime(false);
    CHECK(pumpPinOn() && state == State::POURING, "PRIME press/release during a pour stopped it");
    holdToEnd(); setSwitch(false); runUntil([] { return state == State::LOCKED; }, 5000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= settings.pourMs - 1, "pour after PRIME use %.1f ms", pumpRunMs(0));
    setPrime(true); runMs(2000);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "PRIME in LOCKED ran the pump");
    setPrime(false); runMs(100);
    // priming when the ring arrives: pump off no later than the pass that arms
    setRing(false); runMs(1000);
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500);
    setRing(true);
    CHECK(runUntil([] { return state == State::ARMED; }, 1000) >= 0, "no ARMED");
    CHECK(!pumpPinOn(), "pump still on when ARMED");
    runMs(2000);
    CHECK(pumpRuns() == 2, "ARMED with PRIME held: runs %zu", pumpRuns());
    setPrime(false); runMs(100);
    // PRIME does not interfere with a serial cal run
    setRing(false); runMs(1000);
    serialLine("cal 3000"); runMs(500);
    setPrime(true); runMs(300); setPrime(false);
    CHECK(pumpPinOn(), "PRIME release stopped a cal run");
    runUntil([] { return !pumpPinOn(); }, 5000);
    CHECK(pumpRuns() == 3 && pumpRunMs(2) >= 2999 && pumpRunMs(2) <= 3000 + LOOP_MS, "cal with PRIME use ran %.1f ms", pumpRunMs(2));
  });

  scenario("r", "battery compensation: the pump duty scales with 12 V / battery so pours stay the same; none without a divider", [] {
    struct Case { double v; double k; };
    for (Case c : {Case{12.0, 1.0}, Case{12.6, 12.0 / 12.6}, Case{10.0, 1.2}, Case{9.0, 1.3333}, Case{7.0, 1.4}}) {
      reboot(); setBattery(c.v); runMs(1500);              // let the smoothing settle
      setRing(true); runUntil([] { return state == State::ARMED; }, 1000); runMs(3000);
      setSwitch(true); runUntil([] { return pumpPinOn(); }, 1000); runMs(600);
      const double want = std::min((double)PWM_RANGE, (PWM_RANGE * settings.pumpSpeed) / 100.0 * c.k);
      const int got = sim::pin[PUMP_PIN].pwm;
      CHECK(fabs(got - want) <= 2.0, "at %.1f V pump duty %d, want ~%.0f (k %.3f)", c.v, got, want, c.k);
      setSwitch(false); runUntil([] { return state == State::LOCKED; }, 5000);
    }
    reboot(); runMs(1500);                                  // no divider fitted: reads 0 V
    CHECK(!battSensed() && battK() == 1.0f, "battery sensed with nothing on D0 (%.2f V)", battV);
    serialLine("status"); runMs(50);
    CHECK(serialSaid("battery=not sensed"), "status does not say 'not sensed'");
    NOTE("10.0 V -> duty x1.2, 12.6 V -> x0.95, clamped at x1.4 below 8.6 V");
  });

  scenario("s", "low battery: inserting the ring below 10.5 V double-blinks, then the normal glow; the pour still works", [] {
    reboot(); setBattery(10.2); runMs(1500);
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    CHECK(lowBattWarn, "no low-battery warning at 10.2 V");
    int flashes = 0; bool lit = false; uint32_t peak = 0;
    for (int i = 0; i < 70; i++) { runMs(10); const bool on = ledDuty > lightDuty(0.3f); if (on && !lit) flashes++; lit = on; peak = std::max(peak, ledDuty); }
    CHECK(flashes == 2, "%d flashes in the first 700 ms (want 2)", flashes);
    runMs(1500);
    const uint32_t glow = ledDuty;
    CHECK(glow > 0 && glow < lightDuty(0.3f) * 1.4, "glow after the warning %u", glow);
    setSwitch(true); runUntil([] { return pumpPinOn(); }, 1000);
    CHECK(pumpPinOn(), "no pour with a low battery");
    setSwitch(false); runUntil([] { return state == State::LOCKED; }, 5000);
    setRing(false); runMs(500);
    setBattery(11.6); runMs(3000);
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    CHECK(!lowBattWarn, "warning at 11.6 V");
    NOTE("peak during the blink %u of %u", peak, PWM_RANGE);
  });

  scenario("t", "vcal: the meter reading recalibrates the battery voltage; saved and restored; nonsense rejected", [] {
    reboot(); setBattery(11.0); runMs(2000);
    const float before = battV;
    serialLine("vcal 11.55"); runMs(50);
    CHECK(fabs(battV - 11.55) < 0.05, "after vcal 11.55 the reading is %.3f (was %.3f)", battV, before);
    serialLine("vcal 30"); runMs(50);
    CHECK(fabs(battV - 11.55) < 0.05 && serialSaid("vcal: battery volts"), "vcal 30 accepted");
    serialLine("save"); runMs(50);
    reboot(BootOpts{0, true}); setBattery(11.0); runMs(2000);
    CHECK(fabs(battV - 11.55) < 0.05, "after a reboot the reading is %.3f", battV);
    reboot(BootOpts{0, true}); runMs(500);
    serialLine("vcal 12"); runMs(50);
    CHECK(serialSaid("divider fitted"), "vcal accepted without a divider");
  });

  // ------------------------------------------------------------------ report
  int failed = 0;
  printf("\n%-5s %s\n", "", "scenario");
  for (auto& r : results) {
    const bool ok = r.fails.empty();
    failed += !ok;
    printf("%s  %s. %s\n", ok ? "PASS" : "FAIL", r.id.c_str(), r.name.c_str());
    for (auto& n : r.notes) printf("        %s\n", n.c_str());
    for (auto& f : r.fails) printf("        !! %s\n", f.c_str());
  }
  printf("\n%zu scenarios, %d failed\n", results.size(), failed);
  return failed ? 1 : 0;
}
