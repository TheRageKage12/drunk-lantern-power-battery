// test_green_lantern.cpp - host-side simulation of firmware/green_lantern/green_lantern.ino
//
// The mocks (Arduino.h, Adafruit_NeoPixel.h, EEPROM.h in this directory) are included first,
// then the sketch itself is pulled in as part of this translation unit, so the scenarios can
// call setup()/loop(), drive the pins through the fake clock and inspect the sketch's globals.
//
// Build + run:   make -C firmware/test test      (or ./run.sh)
// Baseline:      make -C firmware/test baseline  (compiles with -DGL_BASELINE against a sketch
//                that does not have the pumpOnSince/pumpCal globals, i.e. the pre-review version)

#include "Arduino.h"
#include "Adafruit_NeoPixel.h"
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
struct BootOpts { uint64_t startUs = 0; bool keepFlash = false; bool switchHeld = false; bool ringPresent = false; };
static void reboot(BootOpts o = BootOpts{}) {
  sim::resetPins();
  sim::nowUs = o.startUs;
  Serial.reset();
  EEPROM.powerCycle();
  if (!o.keepFlash) EEPROM.eraseFlash();
  setSwitch(o.switchHeld);
  setRing(o.ringPresent);

  settings = Settings{SETTINGS_MAGIC, DEFAULT_POUR_MS, DEFAULT_MAX_BRIGHT};
  state = State::IDLE;
  stateSince = hallChanged = swChanged = 0;
  hallRaw = swRaw = hallStable = swStable = switchJammed = pouredThisInsertion = false;
  pumpOn = false; pumpStarted = pumpRunFor = 0;
#ifndef GL_BASELINE
  pumpOnSince = 0; pumpCal = false;
#endif
  lineBuf = "";
  ring.reset(); strip.reset();

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
    unsigned showsBefore = ring.shows;
    runMs(60000);
    CHECK(state == State::ARMED, "state %s", stateName(state));
    CHECK(pumpRuns() == 0, "pump energised %zu times", pumpRuns());
    CHECK(ring.shows > showsBefore + 1000 && ring.maxComponentShown() > 0, "ARMED animation not running");
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

  scenario("f", "ring removed during POURING: pump off within one loop pass, state IDLE", [] {
    reboot();
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runMs(3000);
    CHECK(state == State::POURING && pumpPinOn(), "precondition");
    const double tRemove = nowMs();
    setRing(false);
    // step one loop at a time: the pass that sees the debounced absence must end with the pump off
    bool offSameLoop = false; double tStable = -1; int passes = 0;
    while (passes++ < 100) {
      loop();
      if (!hallStable) { tStable = nowMs(); offSameLoop = !pumpPinOn(); break; }
    }
    CHECK(tStable >= 0, "ring absence never debounced");
    CHECK(offSameLoop, "pump still on in the loop pass that saw the ring gone");
    CHECK(state == State::IDLE, "state %s", stateName(state));
    CHECK(pumpRuns() == 1, "runs %zu", pumpRuns());
    const double offLatencyRaw = pumpRunEndMs(0) - tRemove;
    CHECK(offLatencyRaw <= RING_GONE_MS + LOOP_MS, "pump off %.1f ms after raw removal (budget %u + loop)", offLatencyRaw, (unsigned)RING_GONE_MS);
    CHECK(pumpPinQuiet(), "pump pad not released");
    NOTE("pump off %.1f ms after the raw removal (RING_GONE_MS=%u debounce), same loop pass as the debounced absence", offLatencyRaw, (unsigned)RING_GONE_MS);
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
    CHECK(ring.maxComponentShown() > 0, "LEDs dark after the wrap");
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

  scenario("n", "Hall dropout shorter than RING_GONE_MS mid-pour does not abort (documented behaviour)", [] {
    reboot();
    setRing(true); runUntil([] { return state == State::ARMED; }, 1000);
    setSwitch(true); runUntil([] { return state == State::POURING; }, 1000); setSwitch(false);
    runMs(3000); setRing(false); runMs(100); setRing(true);
    CHECK(pumpPinOn() && state == State::POURING, "100 ms dropout aborted the pour");
    runUntil([] { return !pumpPinOn(); }, 20000);
    CHECK(pumpRuns() == 1 && pumpRunMs(0) >= settings.pourMs - 1 && pumpRunMs(0) <= settings.pourMs + LOOP_MS && state == State::LOCKED, "pour %.1f ms state %s", pumpRunMs(0), stateName(state));
  });

  scenario("o", "LED math: no channel ever exceeds maxBright in any state (maxBright 160 / 255 / 1 / 0)", [] {
    for (int mb : {(int)DEFAULT_MAX_BRIGHT, 255, 1, 0}) {
      reboot();
      settings.maxBright = (uint8_t)mb;
      auto worst = [&](const char* phase) {
        uint32_t w = std::max(ring.maxComponentShown(), strip.maxComponentShown());
        CHECK(w <= (uint32_t)mb, "maxBright %d, %s: channel value %u", mb, phase, w);
      };
      auto runChecked = [&](double ms, const char* phase) { double end = nowMs() + ms; while (nowMs() < end) { loop(); worst(phase); } };
      runChecked(5000, "IDLE");
      setRing(true); runChecked(25000, "ARMED");            // ceiling clamps at 20 s
      setSwitch(true); runChecked(300, "FLASH/POURING");
      setSwitch(false); runChecked(11000, "POURING/LOCKED");
      runChecked(6000, "LOCKED");
      setRing(false); runChecked(1000, "IDLE again");
      CHECK(pumpRuns() == 1, "maxBright %d: runs %zu", mb, pumpRuns());
    }
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
