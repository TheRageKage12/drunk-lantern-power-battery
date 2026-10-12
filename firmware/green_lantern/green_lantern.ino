/*
 * Green Lantern power battery - twist-to-pour firmware
 * Board: Seeed Studio XIAO RP2040 (Arduino core: earlephilhower "Raspberry Pi Pico/RP2040",
 *        board "Seeed XIAO RP2040"). No extra libraries.
 *
 * Interaction
 *   insert ring (magnet -> Hall sensor)      -> ARMED: the green strip brightens steadily over RAMP_MS
 *   recite oath, twist ring ~45 deg          -> cam presses microswitch
 *   Hall present AND switch pressed AND not poured yet -> FLASH (full brightness), then POURING (pump on)
 *   pour finishes                            -> LOCKED: holds bright, then fades to the idle glow
 *   remove ring                              -> IDLE
 *   PRIME button (D6, optional) held while IDLE, no ring -> pump runs to prime the tube, stops on release
 *
 * Safety interlocks (do not remove)
 *   - pump output is driven LOW before anything else at boot
 *   - switch alone never pumps; Hall alone never pumps
 *   - exactly one pour per ring insertion
 *   - ring removal at any time stops the pump immediately
 *   - absolute pump run-time cap MAX_PUMP_MS on CONTINUOUS run time, independent of the state
 *     machine (a cal run followed by a pour cannot stack past it)
 *   - a switch that is already pressed at boot, or when the ring arrives (jammed cam), is ignored
 *     until it has been released
 *   - the pump only starts from FLASH if the Hall sensor sees the ring at that instant
 *   - the only ways to run the pump without the ring are the serial "cal" bench command and the
 *     PRIME button, which works only in IDLE with no ring, only while held, never changes state,
 *     and after a cap stop needs a release before it runs again
 *   - during POURING the pump stops once the Hall input has been absent for POUR_ABORT_MS (60 ms)
 *     and the prop goes LOCKED; the slower RING_GONE_MS only governs the LOCKED -> IDLE reset
 *
 * Wiring (see docs/BUILD_GUIDE.md and docs/images/wiring.svg):
 *   D1  <- Hall sensor OUT, active LOW when the magnet is present. Adafruit DRV5032 breakout on 3V3/GND
 *          (D1 uses the XIAO's internal pull-up). Alternative: 5 V A3144 with a 1N5819 (anode on D1,
 *          cathode on the sensor OUT) so D1 never sees 5 V.
 *   D2  <- microswitch NO   (COM -> GND, internal pull-up, active LOW)
 *   D3  -> 74AHCT125 ch.1 (pin 2 in, pin 3 out) -> gate of Q1 (pump MOSFET, low side); 10 k from D3 to GND
 *          keeps it off while the XIAO boots. 1N5819 flyback across the pump (stripe to +12 V).
 *   D4  -> 74AHCT125 ch.2 (pin 5 in, pin 6 out) -> gate of Q2 (LED strip MOSFET, low side); 10 k D4 to GND.
 *   D6  <- PRIME button, momentary to GND (optional; leave unconnected if you skip it)
 *   5V  <- 5 V from the LM2596 buck through a 1N5819 (USB and the buck never back-feed each other)
 *   3V3 -> DRV5032 VCC
 *
 * Serial (115200) commands for bench calibration, type then Enter:
 *   status            print state and settings
 *   cal 10000         run the pump for 10000 ms (water calibration; works without the ring)
 *   pour 9000         set the pour time in ms (500..20000)
 *   speed 80          pump speed in percent (30..100); slower pump = longer pour for the same volume
 *   leds 200          maximum LED brightness 0..255
 *   idle 20           idle glow, raw PWM 0..255 (a small load keeps some power banks from switching off)
 *   save              store pour time, speed, brightness and idle glow in flash
 *   stop              stop the pump now
 */

#include <EEPROM.h>

// ------------------------------------------------------------------ pins
constexpr uint8_t HALL_PIN      = D1;
constexpr uint8_t SWITCH_PIN    = D2;
constexpr uint8_t PUMP_PIN      = D3;
constexpr uint8_t LED_PIN       = D4;  // PWM to the LED strip MOSFET (through the 74AHCT125)
constexpr uint8_t PRIME_PIN     = D6;  // momentary to GND: primes the tube while held (IDLE, no ring)

// ------------------------------------------------------------------ light
constexpr uint32_t RAMP_MS       = 15000;  // ARMED: brightness climbs over this long; set it to your oath
constexpr float    ARMED_START   = 0.15f;  // perceived brightness when the ring goes in (0..1)
constexpr float    ARMED_PEAK    = 0.75f;  // perceived brightness at the end of the ramp; the twist goes to 1.0
constexpr uint32_t LOCK_HOLD_MS  = 1500;   // after the pour: stay at full brightness this long
constexpr uint32_t FADE_MS       = 3000;   // full -> dark fade time (also used when the ring is pulled)
constexpr float    GAMMA         = 2.2f;   // eye response: makes the ramp look steady instead of front-loaded

// ------------------------------------------------------------------ timing
constexpr uint32_t HALL_DEBOUNCE_MS   = 100;   // ring must be seen this long before ARMED
constexpr uint32_t SWITCH_DEBOUNCE_MS = 40;
constexpr uint32_t PRIME_DEBOUNCE_MS  = 40;
constexpr uint32_t RING_GONE_MS       = 200;   // ring must be absent this long to reset (LOCKED -> IDLE)
constexpr uint32_t POUR_ABORT_MS      = 60;    // ring absent this long during POURING -> pump off, LOCKED
constexpr uint32_t FLASH_MS           = 220;   // bright flash before the pump starts
constexpr uint32_t PUMP_RAMP_MS       = 300;   // PWM soft start: tames the motor inrush on the 12 V rail
constexpr uint32_t DEFAULT_POUR_MS    = 9000;  // ~30 mL at the Kamoer's rated 200 mL/min; set by calibration (see guide)
constexpr uint32_t MAX_PUMP_MS        = 20000; // hard cap, independent of everything else
constexpr uint8_t  DEFAULT_MAX_BRIGHT = 255;   // 0..255 cap on the strip PWM
constexpr uint8_t  DEFAULT_IDLE_DUTY  = 20;    // raw PWM floor in every state: a faint glow and a small keep-alive load
constexpr uint8_t  DEFAULT_PUMP_SPEED = 100;   // percent; lower it to stretch the pour if the Kamoer is too fast

// (declared before the first function so the Arduino prototype generator sees it)
// ------------------------------------------------------------------ state
enum class State : uint8_t { IDLE, ARMED, FLASH, POURING, LOCKED };
State state = State::IDLE;

// ------------------------------------------------------------------ persistent settings
struct Settings {
  uint32_t magic;
  uint32_t pourMs;
  uint8_t  maxBright;
  uint8_t  idleDuty;
  uint8_t  pumpSpeed;
};
constexpr uint32_t SETTINGS_MAGIC = 0x474C3032; // "GL02"
Settings defaultSettings() {
  return Settings{SETTINGS_MAGIC, DEFAULT_POUR_MS, DEFAULT_MAX_BRIGHT, DEFAULT_IDLE_DUTY, DEFAULT_PUMP_SPEED};
}
Settings settings = defaultSettings();


uint32_t stateSince   = 0;     // millis() when the current state began
uint32_t hallChanged  = 0;     // last raw edge on the Hall input
uint32_t swChanged    = 0;     // last raw edge on the switch input
bool     hallRaw      = false;
bool     swRaw        = false;
bool     hallStable   = false; // debounced "ring present"
bool     swStable     = false; // debounced "switch pressed"
bool     switchJammed = false; // pressed at boot -> ignore until released
bool     pouredThisInsertion = false;
uint32_t primeChanged = 0;     // last raw edge on the PRIME button
bool     primeRaw     = false;
bool     primeStable  = false; // debounced "PRIME held"
bool     primeReady   = false; // PRIME seen released since the last prime run (no auto-restart after the cap)

// pump bookkeeping (the cap is enforced here, not in the state machine)
bool     pumpOn       = false;
uint32_t pumpStarted  = 0;     // millis() of the latest pumpStart() (requested-duration timer)
uint32_t pumpRunFor   = 0;     // requested duration for the current run
uint32_t pumpOnSince  = 0;     // millis() when the pump last went off -> on (continuous-run cap)
bool     pumpCal      = false; // current run is a serial "cal" run: allowed without the ring
bool     pumpPrime    = false; // current run is a PRIME-button run: allowed without the ring, ends on release

// light bookkeeping
float    ledShown     = 0.0f;  // perceived brightness currently shown, 0..1
uint32_t ledLastMs    = 0;     // millis() of the previous light update (for the fade rate)
uint8_t  ledDuty      = 0;     // last PWM value written to LED_PIN

static inline uint32_t since(uint32_t t) { return millis() - t; } // wrap-safe

// ------------------------------------------------------------------ pump
void pumpStop() {
  analogWrite(PUMP_PIN, 0);
  digitalWrite(PUMP_PIN, LOW);       // rp2040 core: takes the pad back from the PWM slice to SIO
  pumpOn    = false;
  pumpCal   = false;
  pumpPrime = false;
}

void pumpStart(uint32_t runMs) {
  if (runMs > MAX_PUMP_MS) runMs = MAX_PUMP_MS;
  if (!pumpOn) pumpOnSince = millis();  // restarting an already running pump does not extend the cap
  pumpStarted = millis();
  pumpRunFor  = runMs;
  pumpOn      = true;
  pumpCal     = false;               // the "cal" command / PRIME logic set their flag after calling us
  pumpPrime   = false;
  analogWrite(PUMP_PIN, 1);          // ramp handled in pumpService()
}

// Runs every loop: soft start, requested-duration stop, absolute cap. Returns true while running.
bool pumpService() {
  if (!pumpOn) return false;
  const uint32_t t = since(pumpStarted);
  if (t >= pumpRunFor || t >= MAX_PUMP_MS || since(pumpOnSince) >= MAX_PUMP_MS) { pumpStop(); return false; }
  const uint32_t full = (255UL * settings.pumpSpeed) / 100;   // speed setting, 30..100 %
  uint32_t duty = full;
  if (t < PUMP_RAMP_MS) duty = 40 + ((full > 40 ? full - 40 : 0) * t) / PUMP_RAMP_MS;
  analogWrite(PUMP_PIN, duty);
  return true;
}

// ------------------------------------------------------------------ light
// Target perceived brightness (0..1) for the current state.
float lightTarget() {
  const uint32_t t = since(stateSince);
  switch (state) {
    case State::IDLE:    return 0.0f;                     // the idle floor (idleDuty) still applies
    case State::ARMED: {                                  // steady climb over the oath
      const float k = t >= RAMP_MS ? 1.0f : (float)t / (float)RAMP_MS;
      return ARMED_START + (ARMED_PEAK - ARMED_START) * k;
    }
    case State::FLASH:
    case State::POURING: return 1.0f;
    case State::LOCKED:  return t < LOCK_HOLD_MS ? 1.0f : 0.0f;
  }
  return 0.0f;
}

// Rises instantly to the target (the ARMED ramp is already gradual), falls at most 1.0 per FADE_MS.
void lightService() {
  const uint32_t now = millis();
  const uint32_t dt = now - ledLastMs;
  ledLastMs = now;
  const float target = lightTarget();
  if (target >= ledShown) {
    ledShown = target;
  } else {
    const float step = (float)dt / (float)FADE_MS;
    ledShown = (ledShown - step > target) ? ledShown - step : target;
  }
  uint32_t duty = (uint32_t)(powf(ledShown, GAMMA) * settings.maxBright + 0.5f);
  if (duty < settings.idleDuty) duty = settings.idleDuty;          // floor: faint glow + keep-alive load
  if (duty > 255) duty = 255;
  ledDuty = (uint8_t)duty;
  analogWrite(LED_PIN, ledDuty);
}

// ------------------------------------------------------------------ settings
void loadSettings() {
  EEPROM.begin(256);
  Settings s;
  EEPROM.get(0, s);
  if (s.magic == SETTINGS_MAGIC && s.pourMs >= 500 && s.pourMs <= MAX_PUMP_MS &&
      s.pumpSpeed >= 30 && s.pumpSpeed <= 100) settings = s;
}

void saveSettings() {
  EEPROM.put(0, settings);
  EEPROM.commit();
}

// ------------------------------------------------------------------ serial console
String lineBuf;

const char* stateName(State s) {
  switch (s) {
    case State::IDLE: return "IDLE";
    case State::ARMED: return "ARMED";
    case State::FLASH: return "FLASH";
    case State::POURING: return "POURING";
    case State::LOCKED: return "LOCKED";
  }
  return "?";
}

void printStatus() {
  Serial.print(F("state=")); Serial.print(stateName(state));
  Serial.print(F(" ring=")); Serial.print(hallStable ? "present" : "absent");
  Serial.print(F(" switch=")); Serial.print(swStable ? "pressed" : "released");
  Serial.print(F(" pump=")); Serial.print(pumpOn ? "ON" : "off");
  Serial.print(F(" pourMs=")); Serial.print(settings.pourMs);
  Serial.print(F(" speed=")); Serial.print(settings.pumpSpeed);
  Serial.print(F(" maxBright=")); Serial.print(settings.maxBright);
  Serial.print(F(" idle=")); Serial.println(settings.idleDuty);
}

void handleCommand(String cmd) {
  cmd.trim();
  cmd.toLowerCase();
  if (cmd == "status") { printStatus(); return; }
  if (cmd == "stop") { pumpStop(); Serial.println(F("pump stopped")); return; }
  if (cmd == "save") { saveSettings(); Serial.println(F("saved")); return; }
  if (cmd.startsWith("cal ")) {
    const long ms = cmd.substring(4).toInt();
    if (ms <= 0 || (uint32_t)ms > MAX_PUMP_MS) { Serial.println(F("cal: 1..MAX_PUMP_MS")); return; }
    if (state == State::POURING) { Serial.println(F("busy")); return; }
    pumpStart((uint32_t)ms);
    pumpCal = true;                   // bench run: exempt from the no-ring interlock, cap still applies
    Serial.print(F("calibration run ")); Serial.print(ms); Serial.println(F(" ms - measure the volume"));
    return;
  }
  if (cmd.startsWith("pour ")) {
    const long ms = cmd.substring(5).toInt();
    if (ms < 500 || (uint32_t)ms > MAX_PUMP_MS) { Serial.println(F("pour: 500..MAX_PUMP_MS")); return; }
    settings.pourMs = (uint32_t)ms;
    Serial.print(F("pourMs=")); Serial.println(settings.pourMs);
    return;
  }
  if (cmd.startsWith("leds ")) {
    const long b = cmd.substring(5).toInt();
    if (b < 0 || b > 255) { Serial.println(F("leds: 0..255")); return; }
    settings.maxBright = (uint8_t)b;
    Serial.print(F("maxBright=")); Serial.println(settings.maxBright);
    return;
  }
  if (cmd.startsWith("speed ")) {
    const long v = cmd.substring(6).toInt();
    if (v < 30 || v > 100) { Serial.println(F("speed: 30..100")); return; }
    settings.pumpSpeed = (uint8_t)v;
    Serial.print(F("speed=")); Serial.println(settings.pumpSpeed);
    return;
  }
  if (cmd.startsWith("idle ")) {
    const long v = cmd.substring(5).toInt();
    if (v < 0 || v > 255) { Serial.println(F("idle: 0..255")); return; }
    settings.idleDuty = (uint8_t)v;
    Serial.print(F("idle=")); Serial.println(settings.idleDuty);
    return;
  }
  Serial.println(F("commands: status | cal <ms> | pour <ms> | speed <30-100> | leds <0-255> | idle <0-255> | save | stop"));
}

void serviceSerial() {
  while (Serial.available()) {
    const char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineBuf.length()) handleCommand(lineBuf);
      lineBuf = "";
    } else if (lineBuf.length() < 40) {
      lineBuf += c;
    }
  }
}

// ------------------------------------------------------------------ inputs
void readInputs() {
  const bool h = digitalRead(HALL_PIN) == LOW;    // DRV5032 / A3144 pull LOW when the magnet is present
  const bool s = digitalRead(SWITCH_PIN) == LOW;  // NO contact to GND
  const bool p = digitalRead(PRIME_PIN) == LOW;   // button to GND
  const uint32_t now = millis();
  if (h != hallRaw)  { hallRaw = h;  hallChanged = now; }
  if (s != swRaw)    { swRaw = s;    swChanged = now; }
  if (p != primeRaw) { primeRaw = p; primeChanged = now; }
  if (since(hallChanged) >= (hallRaw ? HALL_DEBOUNCE_MS : RING_GONE_MS)) hallStable = hallRaw;
  if (since(swChanged) >= SWITCH_DEBOUNCE_MS) swStable = swRaw;
  if (since(primeChanged) >= PRIME_DEBOUNCE_MS) primeStable = primeRaw;
  if (switchJammed && !swStable) switchJammed = false;  // released at last
  if (!primeStable && !primeRaw) primeReady = true;     // a held-at-boot or capped PRIME needs a real release first
}

void enter(State s) {
  state = s;
  stateSince = millis();
}

// ------------------------------------------------------------------ setup / loop
void setup() {
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);          // FIRST: pump off
  pinMode(HALL_PIN, INPUT_PULLUP);      // DRV5032 is open-drain; the A3144 divider also sits below the pull-up
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(PRIME_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  Serial.begin(115200);
  loadSettings();

  // settle the debouncers; if the switch is already pressed something is jammed
  for (int i = 0; i < 30; i++) { readInputs(); delay(10); }
  switchJammed = swStable;

  // short boot blink so you know it is alive and the strip works
  analogWrite(LED_PIN, 120); delay(250);
  analogWrite(LED_PIN, 0);   delay(150);
  ledShown = 0.0f;
  ledLastMs = millis();
  enter(State::IDLE);
}

void loop() {
  readInputs();
  serviceSerial();
  const bool pumping = pumpService();   // enforces duration and the hard cap every pass

  // Global interlock: no ring -> no pump, whatever the state (only "cal" and PRIME runs are exempt).
  if (!hallStable && pumpOn && !pumpCal && !pumpPrime) pumpStop();

  // PRIME button: tube priming. Only in IDLE with no ring, only while held, never changes state.
  // Starts on a debounced press (after a release has been seen), stops on the RAW release, on any
  // state/ring change, or at the cap, and does not restart after the cap until released and pressed.
  const bool primeAllowed = (state == State::IDLE) && !hallStable && primeStable && primeRaw;
  if (primeAllowed && primeReady && !pumpOn) { pumpStart(MAX_PUMP_MS); pumpPrime = true; primeReady = false; }
  if (pumpPrime && !primeAllowed) pumpStop();

  switch (state) {
    case State::IDLE:
      if (hallStable) {
        pouredThisInsertion = false;
        if (swStable) switchJammed = true;  // pressed before the twist (stuck cam): ignore until released
        enter(State::ARMED);
      }
      break;

    case State::ARMED:
      if (!hallStable) { enter(State::IDLE); break; }
      if (swStable && !switchJammed && !pouredThisInsertion) {
        pouredThisInsertion = true;       // one pour per insertion, decided here
        enter(State::FLASH);
      }
      break;

    case State::FLASH:
      if (!hallStable) { enter(State::IDLE); break; }
      if (since(stateSince) >= FLASH_MS && hallRaw) {   // raw too: never start on a stale debounced reading
        pumpStart(settings.pourMs);
        enter(State::POURING);
      }
      break;

    case State::POURING:
      // ring pulled: abort as soon as the raw input has been absent POUR_ABORT_MS, lock until it is
      // really gone (RING_GONE_MS) so a dropout can never buy a second pour
      if (!hallStable || (!hallRaw && since(hallChanged) >= POUR_ABORT_MS)) { pumpStop(); enter(State::LOCKED); break; }
      if (!pumping)   { enter(State::LOCKED); }
      break;

    case State::LOCKED:
      if (!hallStable) enter(State::IDLE);   // only a removed ring re-arms the prop
      break;
  }

  lightService();
  delay(10);   // ~100 Hz
}
