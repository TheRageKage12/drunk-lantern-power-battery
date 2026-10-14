/*
 * Green Lantern power battery - twist-to-pour firmware
 * Board: Seeed Studio XIAO RP2040 (Arduino core: earlephilhower "Raspberry Pi Pico/RP2040",
 *        board "Seeed XIAO RP2040"). No extra libraries.
 *
 * Interaction (hold-to-pour)
 *   insert ring (magnet -> Hall sensor)   -> ARMED: the light fades up to ARMED_LEVEL (~15 %)
 *   twist ~45 deg and HOLD (cam presses the microswitch)
 *                                         -> POURING: the pump runs and the light climbs from ARMED_LEVEL to
 *                                            POUR_PEAK (~90 %) over the pour time (pourMs, ~11 s)
 *   pour time reached while still held    -> HOLDING: pump off, light stays at POUR_PEAK
 *   let the ring turn back (switch opens) -> FINALE: light swells to 100 %, then fades out -> LOCKED (dark)
 *   let go early, mid-pour                -> pump stops where it is; light swells by EARLY_BUMP (~10 %) then
 *                                            fades out -> LOCKED
 *   remove ring                           -> IDLE (dark); only a removed ring re-arms the prop
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
 *   - the pump only runs while the ring is in AND the switch is held (dead-man): letting go stops it
 *   - the pump only starts if the Hall sensor sees the ring at that instant
 *   - the only ways to run the pump without the ring are the serial "cal" bench command and the
 *     PRIME button, which works only in IDLE with no ring, only while held, never changes state,
 *     and after a cap stop needs a release before it runs again
 *   - during POURING the pump stops once the Hall input has been absent for POUR_ABORT_MS (60 ms)
 *     and the prop goes LOCKED; the slower RING_GONE_MS only governs the LOCKED -> IDLE reset
 *
 * Wiring (see docs/BUILD_GUIDE.md and docs/images/wiring.svg):
 *   D1  <- A3144 open-collector OUT directly; external 4.7 k to 3V3. Hall VCC is regulated 5 V,
 *          with local 0.1 uF to GND. Internal pull-up can remain enabled.
 *   Lock cable (JST PH 4-pin): regulated 5V, HALL OUT, SW/NO, GND. LED: JST SM 2-pin (+, -).
 *   D2  <- NTE585 anode; cathode to switch NO. COM to GND; 3.3 k from NO to regulated 5 V.
 *          External 4.7 k from D2 to 3V3; active LOW. Do not connect the 5 V switch node directly to D2.
 *   D3  -> U1 74AHCT125 IN pin 2; OUT pin 3 -> Q1 gate (pump).
 *   D4  -> U1 74AHCT125 IN pin 5; OUT pin 6 -> Q2 gate (LED).
 *          Each input has 10 k to GND. U1 pin 14 = regulated 5 V, pin 7 = GND;
 *          existing 0.1 uF locally across supply. OE pins 1/4/10/13 and unused IN 9/12 = GND;
 *          unused OUT pins 8/11 unconnected.
 *          NTE586 3 A/40 V flyback across pump, cathode to switched battery positive.
 *   D6  <- optional PRIME button to GND.
 *   D0  <- battery sense: 100 k from switched battery rail, 22 k and 0.1 uF to GND.
 *          12.6 V full -> 2.27 V at the pin. Reads 0 V if absent: compensation/warning off.
 *   5V  <- buck through NTE585 (stripe to XIAO), then removable JP1. Remove JP1 before USB.
 *          Follow build-guide sequencing; remove U1 for USB-only flashing to disconnect GPIOs
 *          from the unpowered buffer. Normal operation is battery-only.
 *   3V3 -> the external Hall and twist GPIO pull-ups only.
 *
 * Serial (115200) commands for bench calibration, type then Enter:
 *   status            print state and settings
 *   cal 10000         run the pump for 10000 ms (water calibration; works without the ring)
 *   pour 11000        pour time in ms (500..20000) = length of the light build-up
 *   speed 70          pump speed in percent (30..100): sets the VOLUME for the fixed pour time
 *   leds 200          maximum LED brightness 0..255
 *   idle 0            idle glow, raw PWM 0..255; raise it (e.g. 30) for a pilot glow
 *   vcal 12.31        battery voltage measured with a meter right now: calibrates the battery reading
 *   save              store pour time, speed, brightness, idle glow and the vcal correction in flash
 *   stop              stop the pump now
 */

#include <EEPROM.h>

// ------------------------------------------------------------------ pins
constexpr uint8_t HALL_PIN      = D1;
constexpr uint8_t SWITCH_PIN    = D2;
constexpr uint8_t PUMP_PIN      = D3;
constexpr uint8_t LED_PIN       = D4;  // PWM to the LED strip MOSFET (through U1 74AHCT125)
constexpr uint8_t PRIME_PIN     = D6;  // momentary to GND: primes the tube while held (IDLE, no ring)
constexpr uint8_t BATT_PIN      = A0;  // = D0: battery voltage through a 100 k / 22 k divider

// ------------------------------------------------------------------ light (perceived brightness, 0..1)
constexpr float    ARMED_LEVEL      = 0.15f;  // ring in: the glow fades up to this
constexpr uint32_t ARMED_FADE_IN_MS = 600;
constexpr float    POUR_PEAK        = 0.90f;  // the light climbs to this as the pour completes
constexpr float    EARLY_BUMP       = 0.10f;  // let go mid-pour: swell this much above the current level
constexpr uint32_t FINALE_UP_MS     = 400;    // swell time (to 100 %, or by EARLY_BUMP)
constexpr uint32_t FINALE_HOLD_MS   = 300;    // stay at the top of the swell
constexpr uint32_t FINALE_FADE_MS   = 1200;   // then fade to dark
constexpr uint32_t FADE_MS          = 1000;   // any other fall (ring pulled) goes 1.0 -> 0 in this long
constexpr float    GAMMA            = 2.2f;   // eye response: makes the ramp look steady instead of front-loaded
constexpr uint32_t PWM_RANGE        = 1023;   // 10-bit PWM so the dim end of the ramp is smooth

// ------------------------------------------------------------------ timing
constexpr uint32_t HALL_DEBOUNCE_MS   = 100;   // ring must be seen this long before ARMED
constexpr uint32_t SWITCH_DEBOUNCE_MS = 40;
constexpr uint32_t PRIME_DEBOUNCE_MS  = 40;
constexpr uint32_t RING_GONE_MS       = 200;   // ring must be absent this long to reset (LOCKED -> IDLE)
constexpr uint32_t POUR_ABORT_MS      = 60;    // ring absent this long during POURING -> pump off, LOCKED
constexpr uint32_t PUMP_RAMP_MS       = 300;   // PWM soft start: tames the motor inrush on the 12 V rail
constexpr uint32_t DEFAULT_POUR_MS    = 11000; // pour time = length of the light build-up; the volume is set with speed
constexpr uint32_t MAX_PUMP_MS        = 20000; // hard cap, independent of everything else
constexpr uint8_t  DEFAULT_MAX_BRIGHT = 255;   // 0..255 cap on the strip PWM
constexpr uint8_t  DEFAULT_IDLE_DUTY  = 0;     // raw PWM floor in every state (0 = dark); raise it for a pilot glow
constexpr uint8_t  DEFAULT_PUMP_SPEED = 70;    // percent: ~30-37 mL (1-1.25 oz) in 11 s on the Kamoer; set by calibration

// battery (a 3S2P 12 V Li-ion pack, 3 cells in series: 12.6 V full, ~9.5 V empty)
constexpr float    BATT_DIVIDER    = (100.0f + 22.0f) / 22.0f;   // divider ratio
constexpr float    ADC_VREF        = 3.3f;
constexpr float    ADC_MAX         = 4095.0f;  // 12-bit
constexpr float    BATT_NOMINAL_V  = 12.0f;    // the pump speed and LED levels mean "at 12.0 V"
constexpr float    BATT_PRESENT_V  = 6.0f;     // below this nothing is connected to D0: no compensation
constexpr float    BATT_LOW_V      = 10.5f;    // ring inserted below this -> double blink: recharge soon
constexpr float    BATT_K_MIN      = 0.8f;     // compensation limits (duty x k)
constexpr float    BATT_K_MAX      = 1.4f;
constexpr float    BATT_EMA        = 0.05f;    // smoothing per ~10 ms pass
constexpr uint32_t LOWBATT_BLINK_MS = 150;     // two 150 ms flashes before the normal fade-in
constexpr float    LOWBATT_LEVEL   = 0.6f;

// (declared before the first function so the Arduino prototype generator sees it)
// ------------------------------------------------------------------ state
enum class State : uint8_t { IDLE, ARMED, POURING, HOLDING, FINALE, LOCKED };
State state = State::IDLE;

// ------------------------------------------------------------------ persistent settings
struct Settings {
  uint32_t magic;
  uint32_t pourMs;
  uint8_t  maxBright;
  uint8_t  idleDuty;
  uint8_t  pumpSpeed;
  float    battScale;   // "vcal" correction of the divider / ADC reference
};
constexpr uint32_t SETTINGS_MAGIC = 0x474C3033; // "GL03"
Settings defaultSettings() {
  return Settings{SETTINGS_MAGIC, DEFAULT_POUR_MS, DEFAULT_MAX_BRIGHT, DEFAULT_IDLE_DUTY, DEFAULT_PUMP_SPEED, 1.0f};
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
uint32_t ledDuty      = 0;     // last PWM value written to LED_PIN (0..PWM_RANGE)
float    finaleFrom   = 0.0f;  // light level when FINALE began
float    finaleTo     = 0.0f;  // top of the FINALE swell

// battery
float    battV        = 0.0f;  // smoothed battery voltage (0 = not sensed yet)
bool     lowBattWarn  = false; // this insertion started with a low battery: blink first

static inline uint32_t since(uint32_t t) { return millis() - t; } // wrap-safe

// ------------------------------------------------------------------ battery
float battRead() {
  return (float)analogRead(BATT_PIN) / ADC_MAX * ADC_VREF * BATT_DIVIDER * settings.battScale;
}

void battService() {
  const float v = battRead();
  if (v < BATT_PRESENT_V) { battV = 0.0f; return; }   // nothing on D0 (bench, USB-only): no battery logic
  battV = battV <= 0.0f ? v : battV + (v - battV) * BATT_EMA;
}

bool battSensed() { return battV >= BATT_PRESENT_V; }

// duty multiplier that keeps pours and brightness as they were set at BATT_NOMINAL_V
float battK() {
  if (!battSensed()) return 1.0f;
  float k = BATT_NOMINAL_V / battV;
  if (k < BATT_K_MIN) k = BATT_K_MIN;
  if (k > BATT_K_MAX) k = BATT_K_MAX;
  return k;
}

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
  uint32_t full = (uint32_t)((float)(PWM_RANGE * settings.pumpSpeed) / 100.0f * battK() + 0.5f);   // speed at 12 V
  if (battK() == 1.0f) full = (PWM_RANGE * settings.pumpSpeed) / 100;   // exact when no battery is sensed
  if (full > PWM_RANGE) full = PWM_RANGE;
  const uint32_t start = PWM_RANGE / 6;                           // soft start from ~16 %
  uint32_t duty = full;
  if (t < PUMP_RAMP_MS) duty = start + ((full > start ? full - start : 0) * t) / PUMP_RAMP_MS;
  analogWrite(PUMP_PIN, duty);
  return true;
}

// ------------------------------------------------------------------ light
void enter(State s) {
  state = s;
  stateSince = millis();
}

// Target perceived brightness (0..1) for the current state.
float lightTarget() {
  const uint32_t t = since(stateSince);
  switch (state) {
    case State::IDLE:    return 0.0f;
    case State::ARMED: {
      uint32_t u = t;
      if (lowBattWarn) {                                 // low battery: two quick flashes, then the normal glow
        if (u < 4 * LOWBATT_BLINK_MS) return ((u / LOWBATT_BLINK_MS) % 2 == 0) ? LOWBATT_LEVEL : 0.0f;
        u -= 4 * LOWBATT_BLINK_MS;
      }
      return u >= ARMED_FADE_IN_MS ? ARMED_LEVEL : ARMED_LEVEL * (float)u / (float)ARMED_FADE_IN_MS;
    }
    case State::POURING: {                                // climbs with the pour, reaching POUR_PEAK as it completes
      const float k = t >= settings.pourMs ? 1.0f : (float)t / (float)settings.pourMs;
      return ARMED_LEVEL + (POUR_PEAK - ARMED_LEVEL) * k;
    }
    case State::HOLDING: return POUR_PEAK;
    case State::FINALE: {                                 // swell, hold, fade to dark
      if (t < FINALE_UP_MS) return finaleFrom + (finaleTo - finaleFrom) * (float)t / (float)FINALE_UP_MS;
      if (t < FINALE_UP_MS + FINALE_HOLD_MS) return finaleTo;
      const uint32_t f = t - FINALE_UP_MS - FINALE_HOLD_MS;
      return f >= FINALE_FADE_MS ? 0.0f : finaleTo * (1.0f - (float)f / (float)FINALE_FADE_MS);
    }
    case State::LOCKED:  return 0.0f;
  }
  return 0.0f;
}

void startFinale(float to) {
  finaleFrom = ledShown;
  finaleTo = to > 1.0f ? 1.0f : to;
  enter(State::FINALE);
}

// Follows the target: rises instantly (every ramp is already gradual), falls at most 1.0 per FADE_MS.
void lightService() {
  const uint32_t now = millis();
  const uint32_t dt = now - ledLastMs;
  ledLastMs = now;
  const float target = lightTarget();
  const bool blinking = state == State::ARMED && lowBattWarn && since(stateSince) < 4 * LOWBATT_BLINK_MS;
  if (target >= ledShown || state == State::FINALE || blinking) {   // FINALE and the warning draw their own steps
    ledShown = target;
  } else {
    const float step = (float)dt / (float)FADE_MS;
    ledShown = (ledShown - step > target) ? ledShown - step : target;
  }
  uint32_t duty = (uint32_t)(powf(ledShown, GAMMA) * (float)settings.maxBright * ((float)PWM_RANGE / 255.0f) * battK() + 0.5f);
  const uint32_t floorDuty = (uint32_t)settings.idleDuty * PWM_RANGE / 255;   // idle glow / keep-alive load
  if (duty < floorDuty) duty = floorDuty;
  if (duty > PWM_RANGE) duty = PWM_RANGE;
  ledDuty = duty;
  analogWrite(LED_PIN, (int)ledDuty);
}

// ------------------------------------------------------------------ settings
void loadSettings() {
  EEPROM.begin(256);
  Settings s;
  EEPROM.get(0, s);
  if (s.magic == SETTINGS_MAGIC && s.pourMs >= 500 && s.pourMs <= MAX_PUMP_MS &&
      s.pumpSpeed >= 30 && s.pumpSpeed <= 100 && s.battScale >= 0.5f && s.battScale <= 2.0f) settings = s;
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
    case State::POURING: return "POURING";
    case State::HOLDING: return "HOLDING";
    case State::FINALE: return "FINALE";
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
  Serial.print(F(" idle=")); Serial.print(settings.idleDuty);
  Serial.print(F(" battery="));
  if (battSensed()) { Serial.print(battV, 2); Serial.println(battV < BATT_LOW_V ? F("V LOW - recharge") : F("V")); }
  else Serial.println(F("not sensed"));
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
  if (cmd.startsWith("vcal ")) {
    const float meter = cmd.substring(5).toFloat();
    const float raw = battRead() / settings.battScale;
    if (meter < 6.0f || meter > 15.0f || raw < BATT_PRESENT_V * 0.5f) { Serial.println(F("vcal: battery volts 6..15, divider fitted")); return; }
    const float k = meter / raw;
    if (k < 0.5f || k > 2.0f) { Serial.println(F("vcal: reading too far off - check the divider")); return; }
    settings.battScale = k;
    battV = 0.0f; battService();
    Serial.print(F("battery=")); Serial.print(battV, 2); Serial.println(F("V (save to keep)"));
    return;
  }
  Serial.println(F("commands: status | cal <ms> | pour <ms> | speed <30-100> | leds <0-255> | idle <0-255> | vcal <volts> | save | stop"));
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


// ------------------------------------------------------------------ setup / loop
void setup() {
  pinMode(PUMP_PIN, OUTPUT);
  digitalWrite(PUMP_PIN, LOW);          // FIRST: pump off
  pinMode(HALL_PIN, INPUT_PULLUP);      // A3144 open collector directly to D1; external 4.7 k to 3V3 also fitted
  pinMode(SWITCH_PIN, INPUT_PULLUP);
  pinMode(PRIME_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  analogWriteRange(PWM_RANGE);
  analogReadResolution(12);

  Serial.begin(115200);
  loadSettings();

  // settle the debouncers; if the switch is already pressed something is jammed
  for (int i = 0; i < 30; i++) { readInputs(); delay(10); }
  switchJammed = swStable;

  // short boot blink so you know it is alive and the strip works
  analogWrite(LED_PIN, (int)(PWM_RANGE / 2)); delay(250);
  analogWrite(LED_PIN, 0);   delay(150);
  ledShown = 0.0f;
  ledLastMs = millis();
  enter(State::IDLE);
}

void loop() {
  readInputs();
  battService();
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
        lowBattWarn = battSensed() && battV < BATT_LOW_V;   // judged before the pump loads the pack
        if (swStable) switchJammed = true;  // pressed before the twist (stuck cam): ignore until released
        enter(State::ARMED);
      }
      break;

    case State::ARMED:
      if (!hallStable) { enter(State::IDLE); break; }
      if (swStable && !switchJammed && !pouredThisInsertion && hallRaw) {   // raw too: never start on a stale reading
        pouredThisInsertion = true;         // one pour per insertion, decided here
        pumpStart(settings.pourMs);
        enter(State::POURING);
      }
      break;

    case State::POURING:
      // ring pulled: abort as soon as the raw input has been absent POUR_ABORT_MS, lock until it is really gone
      if (!hallStable || (!hallRaw && since(hallChanged) >= POUR_ABORT_MS)) { pumpStop(); enter(State::LOCKED); break; }
      // let go early (switch released): stop where it is, small swell, fade out
      if (!swStable) { pumpStop(); startFinale(ledShown + EARLY_BUMP); break; }
      if (!pumping) enter(State::HOLDING);  // pour time reached (or the hard cap): wait for the release
      break;

    case State::HOLDING:
      if (!hallStable) { enter(State::LOCKED); break; }
      if (!swStable) startFinale(1.0f);     // the ring turns back: full swell, then dark
      break;

    case State::FINALE:
      if (!hallStable) { enter(State::LOCKED); break; }
      if (since(stateSince) >= FINALE_UP_MS + FINALE_HOLD_MS + FINALE_FADE_MS) enter(State::LOCKED);
      break;

    case State::LOCKED:
      if (!hallStable) enter(State::IDLE);  // only a removed ring re-arms the prop
      break;
  }

  lightService();
  delay(10);   // ~100 Hz
}
