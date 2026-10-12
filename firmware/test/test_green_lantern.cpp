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
  ledShown = 0.0f; ledLastMs = 0; ledDuty = 0;

  setup();
}

// ------------------------------------------------------------------ the canonical pour (d / j)
struct PourMeasure {
  double armedAfter = -1, flashAfter = -1, pumpAfterFlash = -1, pourLen = -1, offToLocked = -1;
  std::string endState; bool pwmReleased = false; int dutyAt400 = -1;
  uint32_t millisAtStart = 0, millisAtEnd = 0;
};
static PourMeasure doPour(uint64_t startUs) {
  PourMeasure m;
  reboot(BootOpts{startUs});
  m.millisAtStart = millis();
  setRing(true);
  m.armedAfter = runUntil([] { return state == State::ARMED; }, 1000);
  runMs(2000);                                            // the oath
  setSwitch(true);                                        // twist
  m.flashAfter = runUntil([] { return state == State::FLASH; }, 1000);
  const uint32_t flashSince = stateSince;
  if (runUntil([] { return pumpPinOn(); }, 1000) >= 0 && pumpRuns() == 1)
    m.pumpAfterFlash = (double)(uint32_t)((uint32_t)(sim::runs[PUMP_PIN][0].startUs / 1000) - flashSince);
  const std::string st = stateName(state);
  runMs(400);                                             // rotor spring-returns while the pump ramps
  m.dutyAt400 = sim::pin[PUMP_PIN].func == sim::FUNC_PWM ? sim::pin[PUMP_PIN].pwm : -1;
  setSwitch(false);
  runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 2000);
  if (pumpRuns() >= 1) m.pourLen = pumpRunMs(0);
  m.endState = stateName(state);
  m.pwmReleased = pumpPinQuiet();
  m.offToLocked = (state == State::LOCKED) ? 0 : runUntil([] { return state == State::LOCKED; }, 1000);
  m.millisAtEnd = millis();
  if (st != "POURING") m.endState = "pump on in state " + st + " then " + m.endState;
  return m;
}
static void checkPour(const PourMeasure& m) {
  CHECK(m.armedAfter >= HALL_DEBOUNCE_MS && m.armedAfter <= HALL_DEBOUNCE_MS + 2 * LOOP_MS, "ARMED after %.1f ms (edge seen next pass, debounced, acted on the pass after)", m.armedAfter);
  CHECK(m.flashAfter >= SWITCH_DEBOUNCE_MS && m.flashAfter <= SWITCH_DEBOUNCE_MS + 2 * LOOP_MS, "FLASH after %.1f ms", m.flashAfter);
  CHECK(m.pumpAfterFlash >= FLASH_MS && m.pumpAfterFlash <= FLASH_MS + LOOP_MS, "pump on %.1f ms after FLASH (want %u..%u)", m.pumpAfterFlash, (unsigned)FLASH_MS, (unsigned)(FLASH_MS + LOOP_MS));
  CHECK(m.dutyAt400 == 255, "duty after the 300 ms ramp = %d (want 255)", m.dutyAt400);
  CHECK(m.pourLen >= settings.pourMs - 1 && m.pourLen <= settings.pourMs + LOOP_MS, "pump ran %.1f ms (pourMs=%u)", m.pourLen, (unsigned)settings.pourMs);
  CHECK(m.endState == "LOCKED" && m.offToLocked == 0, "state after the pour: %s (LOCKED in the same loop pass expected)", m.endState.c_str());
  CHECK(m.pwmReleased, "pump pad still on the PWM function / not LOW after pumpStop()");
  CHECK(pumpRuns() == 1, "pump energised %zu times", pumpRuns());
}

// ------------------------------------------------------------------ scenarios
int main() {
  // measure the loop period once (IDLE, nothing happening)
  reboot();
  { const uint64_t t0 = sim::nowUs; for (int i = 0; i < 100; i++) loop(); LOOP_MS = (sim::nowUs - t0) / 1000.0 / 100; }
  printf("simulated loop() period: %.2f ms (delay(8) + show() wire time); one-iteration budget: 20 ms\n", LOOP_MS);
  if (LOOP_MS > 20) { printf("FAIL loop period exceeds 20 ms\n"); return 1; }

  scenario("a", "boot: pump LOW after setup(), jammed switch ignored until released + pressed again", [] {
    reboot(BootOpts{0, false, /*switchHeld*/ true});
    CHECK(!pumpPinOn(), "pump pin on right after setup()");
    CHECK(pumpRuns() == 0, "pump pin was energised during setup() (%zu runs)", pumpRuns());
    CHECK(pumpPinQuiet(), "pump pin not SIO/LOW after setup()");
    // the first two pin operations of the whole boot must be pinMode(PUMP, OUTPUT) + digitalWrite(PUMP, LOW)
    CHECK(sim::events.size() >= 2 && sim::events[0].pin == PUMP_PIN && !strcmp(sim::events[0].what, "pinMode") && sim::events[0].val == OUTPUT
          && sim::events[1].pin == PUMP_PIN && !strcmp(sim::events[1].what, "digitalWrite") && sim::events[1].val == LOW,
          "pump pin is not the first thing setup() configures");
    CHECK(switchJammed, "switch held through boot not flagged as jammed");
    CHECK(state == State::IDLE, "state %s", stateName(state));
    setRing(true);
    runMs(3000);
    CHECK(state == State::ARMED, "ring in, state %s", stateName(state));
    CHECK(pumpRuns() == 0, "jammed switch + ring poured");
    runMs(5000);
    CHECK(pumpRuns() == 0, "jammed switch + ring poured (held 8 s)");
    setSwitch(false); runMs(300);
    CHECK(!switchJammed, "jam flag not cleared after release");
    CHECK(pumpRuns() == 0, "pour on release");
    setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0, "no pour after release + press");
    setSwitch(false);
    runUntil([] { return state == State::LOCKED; }, (double)MAX_PUMP_MS + 1000);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "runs=%zu state=%s", pumpRuns(), stateName(state));
  });

  scenario("b", "switch only (no ring): never pumps, 60 s of toggling", [] {
    reboot();
    bool everLeftIdle = false;
    for (int i = 0; i < 60; i++) {           // 500 ms pressed / 500 ms released
      setSwitch(true);  runMs(500); everLeftIdle |= (state != State::IDLE);
      setSwitch(false); runMs(500); everLeftIdle |= (state != State::IDLE);
    }
    CHECK(pumpRuns() == 0, "pump energised %zu times", pumpRuns());
    CHECK(!everLeftIdle, "left IDLE on the switch alone");
    CHECK(pumpPinQuiet(), "pump pin not quiet");
  });

  scenario("c", "ring only: ARMED, never pumps (60 s)", [] {
    reboot();
    setRing(true);
    CHECK(runUntil([] { return state == State::ARMED; }, 1000) >= 0, "never ARMED");
    runMs(1000);
    const uint8_t early = ledDuty;
    runMs(59000);
    CHECK(state == State::ARMED, "state %s", stateName(state));
    CHECK(pumpRuns() == 0, "pump energised %zu times", pumpRuns());
    CHECK(ledDuty > early, "ARMED light did not climb (%u -> %u)", early, ledDuty);
  });

  static PourMeasure pourD;
  scenario("d", "ring + switch: FLASH, pump on after ~220 ms, off after pourMs -> LOCKED", [] {
    pourD = doPour(0);
    checkPour(pourD);
    NOTE("ARMED +%.1f ms, FLASH +%.1f ms after press, pump %.1f ms after FLASH, ran %.1f ms, then %s",
         pourD.armedAfter, pourD.flashAfter, pourD.pumpAfterFlash, pourD.pourLen, pourD.endState.c_str());
  });

  scenario("e", "LOCKED: switch held 5 s and re-pressed 20x with the ring in -> no second pour", [] {
    // continues from d: LOCKED, ring present, switch released
    CHECK(state == State::LOCKED && pumpRuns() == 1, "precondition: state %s runs %zu", stateName(state), pumpRuns());
    setSwitch(true); runMs(5000);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "held: runs=%zu state=%s", pumpRuns(), stateName(state));
    for (int i = 0; i < 20; i++) { setSwitch(false); runMs(150); setSwitch(true); runMs(150); }
    setSwitch(false); runMs(500);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "re-pressed: runs=%zu state=%s", pumpRuns(), stateName(state));
    CHECK(sim::totalOnUs(PUMP_PIN) / 1000.0 <= settings.pourMs + LOOP_MS, "extra pump time");
  });

  scenario("f", "ring removed during POURING: pump off within one pass of POUR_ABORT_MS (60 ms), LOCKED, then IDLE", [] {
    reboot();
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runMs(3000);
    CHECK(state == State::POURING && pumpPinOn(), "precondition");
    const double tRemove = nowMs();
    setRing(false);
    // step one pass at a time: the first pass that starts with the raw input absent for POUR_ABORT_MS
    // (what readInputs() will see, time does not move until the end of the pass) must end pump-off
    bool offSamePass = false, conditionSeen = false; int passes = 0;
    while (passes++ < 100) {
      const bool cond = !hallRaw && since(hallChanged) >= POUR_ABORT_MS;
      loop();
      if (cond) { conditionSeen = true; offSamePass = !pumpPinOn(); break; }
    }
    CHECK(conditionSeen, "abort condition never reached");
    CHECK(offSamePass, "pump still on in the pass that saw %u ms of absence", (unsigned)POUR_ABORT_MS);
    CHECK(pumpRuns() == 1, "runs %zu", pumpRuns());
    const double offLatency = pumpRunEndMs(0) - tRemove;
    CHECK(offLatency >= POUR_ABORT_MS && offLatency <= POUR_ABORT_MS + 2 * LOOP_MS, "pump off %.1f ms after the raw removal (want %u..%u)", offLatency, (unsigned)POUR_ABORT_MS, (unsigned)(POUR_ABORT_MS + 2 * LOOP_MS));
    CHECK(offLatency < RING_GONE_MS, "abort waited for RING_GONE_MS");
    CHECK(state == State::LOCKED, "state after abort %s (want LOCKED until the ring is really gone)", stateName(state));
    CHECK(pumpPinQuiet(), "pump pad not released");
    const double tIdle = runUntil([] { return state == State::IDLE; }, 1000);
    CHECK(tIdle >= 0 && nowMs() - tRemove <= RING_GONE_MS + 2 * LOOP_MS, "IDLE %.1f ms after removal", nowMs() - tRemove);
    NOTE("pump off %.1f ms after the raw removal (POUR_ABORT_MS=%u), LOCKED, IDLE after %.1f ms (RING_GONE_MS=%u)", offLatency, (unsigned)POUR_ABORT_MS, nowMs() - tRemove, (unsigned)RING_GONE_MS);
    runMs(2000);
    CHECK(state == State::IDLE && pumpRuns() == 1, "after abort: %s runs %zu", stateName(state), pumpRuns());
  });

  scenario("g", "remove and re-insert the ring: exactly one new pour", [] {
    // continues from f: IDLE, ring out, switch released, one aborted run so far
    CHECK(state == State::IDLE && pumpRuns() == 1, "precondition");
    runMs(1000);
    setRing(true);
    CHECK(runUntil([] { return state == State::ARMED; }, 1000) >= 0, "not re-armed");
    runMs(1000);
    setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0, "no pour after re-insertion");
    runMs(300); setSwitch(false);
    runUntil([] { return state == State::LOCKED; }, (double)MAX_PUMP_MS + 1000);
    CHECK(pumpRuns() == 2, "runs %zu (want 2)", pumpRuns());
    CHECK(pumpRunMs(1) >= settings.pourMs - 1 && pumpRunMs(1) <= settings.pourMs + LOOP_MS, "second pour %.1f ms", pumpRunMs(1));
    for (int i = 0; i < 5; i++) { setSwitch(true); runMs(300); setSwitch(false); runMs(300); }
    CHECK(pumpRuns() == 2 && state == State::LOCKED, "more pours on re-twist: runs %zu state %s", pumpRuns(), stateName(state));
    // and the cycle repeats cleanly
    setRing(false); runMs(1000); setRing(true); runMs(1000); setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0 && pumpRuns() == 3, "third insertion did not pour");
    setSwitch(false);
  });

  scenario("h", "hard cap: 'pour' above MAX_PUMP_MS rejected; forced long run stops at MAX_PUMP_MS", [] {
    reboot();
    serialLine("pour 25000"); runMs(50);
    CHECK(settings.pourMs == DEFAULT_POUR_MS, "pour 25000 accepted: pourMs=%u", (unsigned)settings.pourMs);
    CHECK(serialSaid("pour: 500..MAX_PUMP_MS"), "no rejection message");
    serialLine("pour 20001"); runMs(50);
    CHECK(settings.pourMs == DEFAULT_POUR_MS, "pour 20001 accepted");
    serialLine("pour 499"); runMs(50);
    CHECK(settings.pourMs == DEFAULT_POUR_MS, "pour 499 accepted");
    serialLine("pour 20000"); runMs(50);
    CHECK(settings.pourMs == MAX_PUMP_MS, "pour 20000 (= cap) rejected");
    serialLine("pour 10000"); runMs(50);

    // 1) pumpStart() clamps the request
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    pumpStart(MAX_PUMP_MS + 5000);
    CHECK(pumpRunFor == MAX_PUMP_MS, "pumpStart did not clamp: pumpRunFor=%u", (unsigned)pumpRunFor);
    // 2) even with the clamp bypassed, pumpService() stops at the cap
    pumpRunFor = MAX_PUMP_MS + 5000;
    CHECK(runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 10000) >= 0, "forced run never stopped");
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= MAX_PUMP_MS - 1 && pumpRunMs(0) <= MAX_PUMP_MS + LOOP_MS, "forced run lasted %.1f ms (cap %u)", pumpRuns() ? pumpRunMs(0) : -1.0, (unsigned)MAX_PUMP_MS);
    CHECK(state == State::ARMED, "state %s", stateName(state));
    setRing(false); runMs(1000);

    // 3) the cap is on continuous run time: a cal run followed by a real pour cannot exceed it
    reboot();
    serialLine("cal 20000"); runMs(50);
    CHECK(pumpPinOn(), "cal 20000 did not start");
    runMs(15000);
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 20000);
    const double longest = sim::longestRunUs(PUMP_PIN) / 1000.0;
    CHECK(longest <= MAX_PUMP_MS + LOOP_MS, "cal + pour ran %.1f ms continuously (cap %u)", longest, (unsigned)MAX_PUMP_MS);
    CHECK(state == State::LOCKED, "state %s after the capped pour", stateName(state));
    NOTE("forced run %.1f ms; cal+pour longest continuous run %.1f ms", pumpRunMs(0) > 0 ? pumpRunMs(0) : -1.0, longest);
  });

  scenario("i", "serial: cal 3000 without ring, stop, pour 12500 + save + reboot persists (EEPROM)", [] {
    reboot();
    CHECK(settings.pourMs == DEFAULT_POUR_MS && settings.maxBright == DEFAULT_MAX_BRIGHT, "blank flash did not give defaults");
    serialLine("cal 3000"); runMs(LOOP_MS * 2);
    CHECK(pumpPinOn(), "cal 3000 did not start the pump (no ring)");
    CHECK(state == State::IDLE, "cal changed the state to %s", stateName(state));
    runUntil([] { return !pumpPinOn(); }, 6000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= 2999 && pumpRunMs(0) <= 3000 + LOOP_MS, "cal ran %.1f ms", pumpRuns() ? pumpRunMs(0) : -1.0);
    CHECK(state == State::IDLE && pumpPinQuiet(), "after cal: %s", stateName(state));

    serialLine("cal 3000"); runMs(500);
    CHECK(pumpPinOn(), "second cal did not start");
    serialLine("stop");
    CHECK(runUntil([] { return !pumpPinOn(); }, LOOP_MS * 2) >= 0, "stop did not stop the pump within a loop pass");
    CHECK(pumpRuns() == 2 && pumpRunMs(1) < 500 + 2 * LOOP_MS, "stopped run lasted %.1f ms", pumpRuns() > 1 ? pumpRunMs(1) : -1.0);
    CHECK(serialSaid("pump stopped"), "no 'pump stopped' reply");

    serialLine("cal 0"); serialLine("cal 25000"); serialLine("cal abc"); runMs(100);
    CHECK(pumpRuns() == 2, "invalid cal values started the pump");

    // cal with the ring in (ARMED) runs but does not touch the state machine
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    serialLine("cal 1000"); runMs(2000);
    CHECK(pumpRuns() == 3 && pumpRunMs(2) >= 999 && pumpRunMs(2) <= 1000 + LOOP_MS && state == State::ARMED, "cal while ARMED: runs %zu state %s", pumpRuns(), stateName(state));
    // stop during a real pour -> LOCKED, no re-pour
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runMs(2000); serialLine("stop"); runMs(LOOP_MS * 2);
    CHECK(!pumpPinOn() && state == State::LOCKED, "stop during pour: pump %d state %s", pumpPinOn(), stateName(state));
    setSwitch(true); runMs(500); setSwitch(false);
    CHECK(pumpRuns() == 4, "re-pour after stop (runs %zu)", pumpRuns());
    setRing(false); runMs(1000);

    serialLine("pour 12500"); runMs(50);
    CHECK(settings.pourMs == 12500, "pour 12500 not applied");
    serialLine("leds 128"); runMs(50);
    CHECK(settings.maxBright == 128, "leds 128 not applied");
    Serial.tx.clear(); serialLine("status"); runMs(50);
    CHECK(serialSaid("pourMs=12500") && serialSaid("maxBright=128") && serialSaid("state=IDLE"), "status output: %s", Serial.tx.c_str());
    CHECK(EEPROM.commits == 0, "flash written before 'save'");
    serialLine("save"); runMs(50);
    CHECK(EEPROM.commits == 1 && serialSaid("saved"), "save did not commit (%u commits)", EEPROM.commits);

    reboot(BootOpts{0, /*keepFlash*/ true});
    CHECK(settings.pourMs == 12500 && settings.maxBright == 128, "settings after reboot: pourMs=%u maxBright=%u", (unsigned)settings.pourMs, settings.maxBright);
    // and the persisted value is what a pour actually uses
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000); setSwitch(true);
    runUntil([] { return pumpPinOn(); }, 1000); setSwitch(false);
    runUntil([] { return !pumpPinOn(); }, 20000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= 12499 && pumpRunMs(0) <= 12500 + LOOP_MS, "pour used %.1f ms", pumpRuns() ? pumpRunMs(0) : -1.0);
    // corrupt flash (bad magic) -> defaults
    reboot();
    CHECK(settings.pourMs == DEFAULT_POUR_MS, "erased flash did not give defaults");
  });

  scenario("j", "millis() wraparound: clock starts at 0xFFFFF000, scenario d behaves identically", [] {
    PourMeasure m = doPour(0xFFFFF000ULL * 1000ULL);
    checkPour(m);
    CHECK(m.millisAtEnd < m.millisAtStart, "millis() did not wrap during the scenario (start %u end %u)", m.millisAtStart, m.millisAtEnd);
    CHECK(m.armedAfter == pourD.armedAfter && m.flashAfter == pourD.flashAfter && m.pumpAfterFlash == pourD.pumpAfterFlash
          && m.pourLen == pourD.pourLen && m.endState == pourD.endState,
          "differs from d: armed %.1f/%.1f flash %.1f/%.1f pump %.1f/%.1f pour %.1f/%.1f %s/%s",
          m.armedAfter, pourD.armedAfter, m.flashAfter, pourD.flashAfter, m.pumpAfterFlash, pourD.pumpAfterFlash,
          m.pourLen, pourD.pourLen, m.endState.c_str(), pourD.endState.c_str());
    // LOCKED afterglow + IDLE ember keep animating across the wrap
    runMs(6000);
    CHECK(ledDuty >= settings.idleDuty && sim::pin[LED_PIN].pwm == ledDuty, "LED output wrong after the wrap (%u)", ledDuty);
  });

  scenario("k", "debounce: 30 ms Hall glitch does not arm, 20 ms switch glitch does not fire", [] {
    reboot();
    setRing(true); runMs(30); setRing(false);
    CHECK(runUntil([] { return state != State::IDLE; }, 2000) < 0, "30 ms Hall glitch armed the prop");
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000); runMs(500);
    setSwitch(true); runMs(20); setSwitch(false);
    CHECK(runUntil([] { return state != State::ARMED; }, 2000) < 0, "20 ms switch glitch fired (state %s)", stateName(state));
    CHECK(pumpRuns() == 0, "pump ran");
    // a real press still works afterwards
    setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0, "real press after the glitch did not pour");
    setSwitch(false); setRing(false);
  });

  scenario("l", "ring removed during FLASH (at 0 / 100 / 200 / 210 ms): pump never starts", [] {
    for (double offset : {0.0, 100.0, 200.0, 210.0}) {
      reboot();
      setRing(true); runUntil([] { return state == State::ARMED; }, 1000); runMs(500);
      setSwitch(true);
      CHECK(runUntil([] { return state == State::FLASH; }, 1000) >= 0, "no FLASH");
      runMs(offset);
      setRing(false); setSwitch(false);
      const double t = runUntil([] { return state == State::IDLE; }, 2000);
      CHECK(t >= 0, "offset %.0f: never returned to IDLE (state %s)", offset, stateName(state));
      CHECK(pumpRuns() == 0, "offset %.0f ms into FLASH: pump started (%zu runs, %.1f ms)", offset, pumpRuns(), pumpRuns() ? pumpRunMs(0) : 0.0);
      runMs(1000);
      CHECK(pumpRuns() == 0 && state == State::IDLE, "offset %.0f: late pour", offset);
    }
  });

  scenario("m", "switch stuck pressed after boot: ring insertion alone must not pour", [] {
    reboot();
    setSwitch(true); runMs(2000);                 // cam jams while the prop sits idle
    CHECK(state == State::IDLE && pumpRuns() == 0, "switch alone");
    setRing(true); runMs(3000);
    CHECK(pumpRuns() == 0, "inserting the ring onto a stuck switch poured without a twist");
    CHECK(state == State::ARMED, "state %s", stateName(state));
    setSwitch(false); runMs(300); setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0 && pumpRuns() == 1, "release + twist did not pour");
    setSwitch(false);
  });

  scenario("n", "Hall dropout mid-pour: 30 ms does not abort, 70 ms aborts -> LOCKED, no second pour", [] {
    auto pourTo3s = [] {
      reboot();
      setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
      setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
      runMs(3000);
    };
    pourTo3s();
    setRing(false); runMs(30); setRing(true);
    CHECK(pumpPinOn() && state == State::POURING, "30 ms dropout aborted the pour (state %s)", stateName(state));
    runUntil([] { return !pumpPinOn(); }, 20000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= settings.pourMs - 1 && pumpRunMs(0) <= settings.pourMs + LOOP_MS && state == State::LOCKED, "after 30 ms dropout: pour %.1f ms state %s", pumpRunMs(0), stateName(state));

    pourTo3s();
    const double tDrop = nowMs();
    setRing(false); runMs(70); setRing(true);
    CHECK(!pumpPinOn() && state == State::LOCKED, "70 ms dropout: pump %d state %s", pumpPinOn(), stateName(state));
    CHECK(pumpRuns() == 1, "runs %zu", pumpRuns());
    const double off = pumpRunEndMs(0) - tDrop;
    CHECK(off >= POUR_ABORT_MS && off <= POUR_ABORT_MS + 2 * LOOP_MS, "pump off %.1f ms after the dropout", off);
    runMs(1000);
    CHECK(state == State::LOCKED, "ring back after the abort: state %s (want LOCKED, one pour per insertion)", stateName(state));
    for (int i = 0; i < 3; i++) { setSwitch(true); runMs(300); setSwitch(false); runMs(300); }
    CHECK(pumpRuns() == 1, "re-twist after an aborted pour poured again");
    const double tOut = nowMs();
    setRing(false);
    CHECK(runUntil([] { return state == State::IDLE; }, 1000) >= 0 && nowMs() - tOut <= RING_GONE_MS + 2 * LOOP_MS, "no IDLE after removal");
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000); setSwitch(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0 && pumpRuns() == 2, "fresh insertion after an abort did not pour");
    setSwitch(false);
    NOTE("70 ms dropout: pump off %.1f ms after the raw drop, LOCKED kept while the ring was back", off);
  });

  scenario("o", "light: idle floor always, ARMED climbs steadily over RAMP_MS, FLASH/POURING at maxBright, LOCKED holds then fades", [] {
    for (int mb : {255, 160, 0}) {
      reboot();
      settings.maxBright = (uint8_t)mb;
      const uint32_t floorD = settings.idleDuty, cap = std::max<uint32_t>(mb, floorD);
      auto expect = [&](float p) { return std::max<uint32_t>(floorD, (uint32_t)(powf(p, GAMMA) * mb + 0.5f)); };
      uint32_t prevArmed = 0, armedFirst = 0, armedLast = 0, maxPour = 0, maxJump = 0;
      unsigned armedFrames = 0; bool armedMono = true;
      auto step = [&] {
        const State before = state;
        loop();
        const uint32_t d = ledDuty;
        CHECK(sim::pin[LED_PIN].pwm == (int)d, "maxBright %d: pin %d != ledDuty %u", mb, sim::pin[LED_PIN].pwm, d);
        CHECK(d >= floorD && d <= cap, "maxBright %d %s: duty %u outside [%u, %u]", mb, stateName(before), d, floorD, cap);
        if (before == State::ARMED && state == State::ARMED) {
          if (armedFrames == 0) armedFirst = d;
          else { if (d < prevArmed) armedMono = false; maxJump = std::max(maxJump, d - std::min(d, prevArmed)); }
          prevArmed = armedLast = d; armedFrames++;
        }
        if (before == State::POURING) maxPour = std::max(maxPour, d);
      };
      auto runChecked = [&](double ms) { const double end = nowMs() + ms; while (nowMs() < end) step(); };
      runChecked(3000);
      CHECK(ledDuty == floorD, "maxBright %d: IDLE duty %u (want floor %u)", mb, ledDuty, floorD);
      setRing(true); runChecked(RAMP_MS + 3000);
      CHECK(armedMono, "maxBright %d: ARMED light went down", mb);
      CHECK(maxJump <= 3, "maxBright %d: ARMED jumped %u in one frame (not gradual)", mb, maxJump);
      CHECK(armedFirst <= expect(ARMED_START) + 1, "maxBright %d: ARMED starts at %u (want ~%u)", mb, armedFirst, expect(ARMED_START));
      CHECK(armedLast + 1 >= expect(ARMED_PEAK) && armedLast <= expect(ARMED_PEAK) + 1, "maxBright %d: ARMED peak %u (want %u)", mb, armedLast, expect(ARMED_PEAK));
      setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
      runChecked(settings.pourMs + 200);
      CHECK(state == State::LOCKED, "maxBright %d: state %s after the pour", mb, stateName(state));
      CHECK(maxPour == cap, "maxBright %d: pour brightness %u (want %u)", mb, maxPour, cap);
      runChecked(LOCK_HOLD_MS - 400);
      CHECK(ledDuty == cap, "maxBright %d: LOCKED hold duty %u (want %u)", mb, ledDuty, cap);
      uint32_t prev = ledDuty; bool fadeMono = true;
      const double fadeEnd = nowMs() + 400 + FADE_MS + 200;
      while (nowMs() < fadeEnd) { step(); if (ledDuty > prev) fadeMono = false; prev = ledDuty; }
      CHECK(fadeMono, "maxBright %d: LOCKED fade went up", mb);
      CHECK(ledDuty == floorD, "maxBright %d: after the fade duty %u (want floor %u)", mb, ledDuty, floorD);
      setRing(false); runChecked(1000);
      CHECK(state == State::IDLE && ledDuty == floorD, "maxBright %d: back in IDLE duty %u", mb, ledDuty);
      CHECK(pumpRuns() == 1, "maxBright %d: runs %zu", mb, pumpRuns());
    }
  });

  scenario("q", "pump speed: 'speed 70' sets the running duty to 70 %, keeps the pour time, persists; out of range rejected", [] {
    reboot();
    serialLine("speed 70"); serialLine("speed 20"); serialLine("speed 101"); runMs(50);
    CHECK(settings.pumpSpeed == 70, "speed %u (want 70)", settings.pumpSpeed);
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setSwitch(true); runUntil([] { return pumpPinOn(); }, 1000); setSwitch(false);
    runMs(500);
    CHECK(sim::pin[PUMP_PIN].pwm == (255 * 70) / 100, "running duty %d (want %d)", sim::pin[PUMP_PIN].pwm, (255 * 70) / 100);
    runUntil([] { return !pumpPinOn(); }, 20000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= DEFAULT_POUR_MS - 1 && pumpRunMs(0) <= DEFAULT_POUR_MS + LOOP_MS, "pour %.1f ms", pumpRunMs(0));
    serialLine("idle 35"); serialLine("save"); runMs(50);
    reboot(BootOpts{0, /*keepFlash*/ true});
    CHECK(settings.pumpSpeed == 70 && settings.idleDuty == 35, "after reboot: speed %u idle %u", settings.pumpSpeed, settings.idleDuty);
  });

  scenario("p", "PRIME button (D6): runs only while held in IDLE with no ring, stops on release, capped, never changes state", [] {
    reboot();
    // 1. hold in IDLE without the ring: soft start, state unchanged, stops on release within one pass
    setPrime(true);
    const double t = runUntil([] { return pumpPinOn(); }, 500);
    CHECK(t >= PRIME_DEBOUNCE_MS && t <= PRIME_DEBOUNCE_MS + 2 * LOOP_MS, "prime started after %.1f ms", t);
    CHECK(state == State::IDLE && pumpPrime, "state %s pumpPrime %d", stateName(state), pumpPrime);
    runMs(100);
    CHECK(sim::pin[PUMP_PIN].func == sim::FUNC_PWM && sim::pin[PUMP_PIN].pwm > 40 && sim::pin[PUMP_PIN].pwm < 255, "no soft start (duty %d at 100 ms)", sim::pin[PUMP_PIN].pwm);
    runMs(300);
    CHECK(sim::pin[PUMP_PIN].pwm == 255, "duty %d after the ramp", sim::pin[PUMP_PIN].pwm);
    CHECK(state == State::IDLE, "state %s while priming", stateName(state));
    setPrime(false);
    CHECK(runUntil([] { return !pumpPinOn(); }, 2 * LOOP_MS) >= 0, "pump still on after release");
    CHECK(pumpRuns() == 1 && state == State::IDLE && pumpPinQuiet(), "after release: runs %zu state %s", pumpRuns(), stateName(state));
    // 2. 20 ms glitch: nothing
    setPrime(true); runMs(20); setPrime(false); runMs(500);
    CHECK(pumpRuns() == 1, "20 ms PRIME glitch ran the pump");
    // 2b. a 10 ms contact glitch while priming stops the pump; it does not restart until a real release + press
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500); runMs(500);
    setPrime(false); runMs(10); setPrime(true);
    CHECK(runUntil([] { return !pumpPinOn(); }, 2 * LOOP_MS) >= 0, "raw glitch did not stop the prime");
    runMs(1000);
    CHECK(pumpRuns() == 2 && !pumpPinOn(), "prime restarted after a glitch without a real release (runs %zu)", pumpRuns());
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 3, "no restart after a real release + press");
    setPrime(false); runMs(100);
    // 3. held past the cap: stops at MAX_PUMP_MS and does not restart until released and pressed again
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500);
    CHECK(runUntil([] { return !pumpPinOn(); }, (double)MAX_PUMP_MS + 2000) >= 0, "capped prime never stopped");
    CHECK(pumpRuns() == 4 && pumpRunMs(3) >= MAX_PUMP_MS - 1 && pumpRunMs(3) <= MAX_PUMP_MS + LOOP_MS, "capped prime ran %.1f ms", pumpRuns() > 3 ? pumpRunMs(3) : -1.0);
    runMs(3000);
    CHECK(pumpRuns() == 4 && !pumpPinOn(), "prime restarted while still held after the cap (runs %zu)", pumpRuns());
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 5, "release + press after the cap did not prime");
    setPrime(false); runMs(100);
    CHECK(state == State::IDLE, "state %s", stateName(state));
    // 4. held through boot: ignored until released and pressed
    reboot(BootOpts{0, false, false, false, /*primeHeld*/ true});
    CHECK(pumpRuns() == 0 && !pumpPinOn(), "pump ran during boot with PRIME held");
    runMs(2000);
    CHECK(pumpRuns() == 0, "PRIME held at boot primed");
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 1, "no prime after release + press");
    setPrime(false); runMs(100);
    // 5. never in another state: ARMED, POURING (does not stop the pour), LOCKED
    reboot();
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setPrime(true); runMs(2000); setPrime(false); runMs(100);
    CHECK(pumpRuns() == 0 && state == State::ARMED, "PRIME in ARMED: runs %zu state %s", pumpRuns(), stateName(state));
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runMs(2000); setPrime(true); runMs(500); setPrime(false);
    CHECK(pumpPinOn() && state == State::POURING, "PRIME press/release during a pour stopped it");
    runUntil([] { return !pumpPinOn(); }, 20000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= settings.pourMs - 1 && state == State::LOCKED, "pour after PRIME use: %.1f ms state %s", pumpRunMs(0), stateName(state));
    setPrime(true); runMs(2000);
    CHECK(pumpRuns() == 1 && state == State::LOCKED, "PRIME in LOCKED ran the pump");
    setPrime(false); runMs(100);
    // 6. priming when the ring arrives: pump off no later than the pass that arms, then a normal twist pour
    setRing(false); runMs(1000);
    setPrime(true); runUntil([] { return pumpPinOn(); }, 500);
    CHECK(pumpRuns() == 2 && state == State::IDLE, "precondition");
    setRing(true);
    CHECK(runUntil([] { return state == State::ARMED; }, 1000) >= 0, "no ARMED");
    CHECK(!pumpPinOn() && (uint32_t)(sim::runs[PUMP_PIN][1].endUs / 1000) <= stateSince, "pump still on when ARMED (off at %.1f, armed at %u)", pumpRunEndMs(1), (unsigned)stateSince);
    runMs(2000);
    CHECK(pumpRuns() == 2 && state == State::ARMED, "ARMED with PRIME held: runs %zu", pumpRuns());
    setSwitch(true); CHECK(runUntil([] { return pumpPinOn(); }, 1000) >= 0 && pumpRuns() == 3, "twist with PRIME held did not pour normally");
    setSwitch(false); runUntil([] { return state == State::LOCKED; }, 20000);
    // 7. ring removed with PRIME still held since step 6: no restart until released and pressed
    setRing(false); runUntil([] { return state == State::IDLE; }, 1000); runMs(2000);
    CHECK(pumpRuns() == 3, "PRIME auto-restarted after the ring left (runs %zu)", pumpRuns());
    setPrime(false); runMs(100); setPrime(true);
    CHECK(runUntil([] { return pumpPinOn(); }, 500) >= 0 && pumpRuns() == 4, "release + press did not prime");
    setPrime(false); runMs(100);
    // 8. PRIME does not interfere with a serial cal run
    serialLine("cal 3000"); runMs(500);
    setPrime(true); runMs(300); setPrime(false);
    CHECK(pumpPinOn(), "PRIME release stopped a cal run");
    runUntil([] { return !pumpPinOn(); }, 5000);
    CHECK(pumpRuns() == 5 && pumpRunMs(4) >= 2999 && pumpRunMs(4) <= 3000 + LOOP_MS, "cal with PRIME use ran %.1f ms", pumpRuns() > 4 ? pumpRunMs(4) : -1.0);
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
