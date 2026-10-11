/*
 * Green Lantern power battery - twist-to-pour firmware
 * Board: Seeed Studio XIAO RP2040 (Arduino core: earlephilhower "Raspberry Pi Pico/RP2040",
 *        board "Seeed XIAO RP2040"). Library: Adafruit NeoPixel.
 *
 * Interaction
 *   insert ring (magnet -> Hall sensor)      -> ARMED, slow green pulse
 *   recite oath, twist ring ~45 deg          -> cam presses microswitch
 *   Hall present AND switch pressed AND not poured yet -> FLASH, then POURING (pump on, light show)
 *   pour finishes                            -> LOCKED (afterglow) until the ring is removed
 *   remove ring                              -> IDLE
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
 *   - the only way to run the pump without the ring is the serial "cal" bench command
 *
 * Wiring (see docs/BUILD_GUIDE.md):
 *   D1  <- Hall sensor OUT, active LOW when the magnet is present. Primary: Adafruit DRV5032 breakout
 *          (open-drain, VCC 3V3, GND; D1 uses the XIAO's internal pull-up, no divider needed).
 *          Alternative: 5 V A3144 module, OUT -> 4.7k series -> D1, 22k from D1 to GND (divider off the
 *          module's own pull-up so the 3.3 V pin never sees 5 V).
 *   D2  <- microswitch NO   (COM -> GND, internal pull-up, active LOW)
 *   D3  -> D4184 MOSFET module PWM/TRIG input (HIGH = pump on); module GND tied to XIAO GND
 *   D4  -> 74AHCT125 in  -> out -> 330 ohm -> NeoPixel RING DIN (24 px, in the charging socket)
 *   D5  -> 74AHCT125 in  -> out -> 330 ohm -> NeoPixel STRIP DIN (60 px, inside the sphere)
 *
 * Serial (115200) commands for bench calibration, type then Enter:
 *   status            print state and settings
 *   cal 10000         run the pump for 10000 ms (water calibration; works without the ring, USB only)
 *   pour 12500        set the pour time in ms for this session
 *   save              store the pour time in flash (EEPROM emulation) so it survives power cycles
 *   stop              stop the pump now
 *   leds 128          set the maximum LED brightness 0..255 (saved with "save")
 */

#include <Adafruit_NeoPixel.h>
#include <EEPROM.h>

// ------------------------------------------------------------------ pins
constexpr uint8_t HALL_PIN      = D1;
constexpr uint8_t SWITCH_PIN    = D2;
constexpr uint8_t PUMP_PIN      = D3;
constexpr uint8_t RING_LED_PIN  = D4;
constexpr uint8_t STRIP_LED_PIN = D5;

// ------------------------------------------------------------------ LEDs
constexpr uint16_t RING_COUNT  = 24;   // Adafruit 24-px NeoPixel ring in the socket
constexpr uint16_t STRIP_COUNT = 60;   // WS2812B strip inside the sphere (set to your real count)

// ------------------------------------------------------------------ timing
constexpr uint32_t HALL_DEBOUNCE_MS   = 100;   // ring must be seen this long before ARMED
constexpr uint32_t SWITCH_DEBOUNCE_MS = 40;
constexpr uint32_t RING_GONE_MS       = 200;   // ring must be absent this long to reset
constexpr uint32_t FLASH_MS           = 220;   // bright flash before the pump starts
constexpr uint32_t PUMP_RAMP_MS       = 300;   // PWM soft start to avoid a 5 V brown-out
constexpr uint32_t DEFAULT_POUR_MS    = 10000; // replace after water calibration (see guide)
constexpr uint32_t MAX_PUMP_MS        = 20000; // hard cap, independent of everything else
constexpr uint8_t  DEFAULT_MAX_BRIGHT = 160;   // 0..255 cap for every animation (current budget)

// ------------------------------------------------------------------ persistent settings
struct Settings {
  uint32_t magic;
  uint32_t pourMs;
  uint8_t  maxBright;
};
constexpr uint32_t SETTINGS_MAGIC = 0x474C3031; // "GL01"
Settings settings{SETTINGS_MAGIC, DEFAULT_POUR_MS, DEFAULT_MAX_BRIGHT};

// ------------------------------------------------------------------ state
enum class State : uint8_t { IDLE, ARMED, FLASH, POURING, LOCKED };
State state = State::IDLE;

Adafruit_NeoPixel ring(RING_COUNT, RING_LED_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip(STRIP_COUNT, STRIP_LED_PIN, NEO_GRB + NEO_KHZ800);

uint32_t stateSince   = 0;     // millis() when the current state began
uint32_t hallChanged  = 0;     // last raw edge on the Hall input
uint32_t swChanged    = 0;     // last raw edge on the switch input
bool     hallRaw      = false;
bool     swRaw        = false;
bool     hallStable   = false; // debounced "ring present"
bool     swStable     = false; // debounced "switch pressed"
bool     switchJammed = false; // pressed at boot -> ignore until released
bool     pouredThisInsertion = false;

// pump bookkeeping (the cap is enforced here, not in the state machine)
bool     pumpOn       = false;
uint32_t pumpStarted  = 0;     // millis() of the latest pumpStart() (requested-duration timer)
uint32_t pumpRunFor   = 0;     // requested duration for the current run
uint32_t pumpOnSince  = 0;     // millis() when the pump last went off -> on (continuous-run cap)
bool     pumpCal      = false; // current run is a serial "cal" run: allowed without the ring

static inline uint32_t since(uint32_t t) { return millis() - t; } // wrap-safe

// ------------------------------------------------------------------ pump
void pumpStop() {
  analogWrite(PUMP_PIN, 0);
  digitalWrite(PUMP_PIN, LOW);       // rp2040 core: takes the pad back from the PWM slice to SIO
  pumpOn  = false;
  pumpCal = false;
}

void pumpStart(uint32_t runMs) {
  if (runMs > MAX_PUMP_MS) runMs = MAX_PUMP_MS;
  if (!pumpOn) pumpOnSince = millis();  // restarting an already running pump does not extend the cap
  pumpStarted = millis();
  pumpRunFor  = runMs;
  pumpOn      = true;
  pumpCal     = false;               // the "cal" command sets this after calling us
  analogWrite(PUMP_PIN, 1);          // ramp handled in pumpService()
}

// Runs every loop: soft start, requested-duration stop, absolute cap. Returns true while running.
bool pumpService() {
  if (!pumpOn) return false;
  const uint32_t t = since(pumpStarted);
  if (t >= pumpRunFor || t >= MAX_PUMP_MS || since(pumpOnSince) >= MAX_PUMP_MS) { pumpStop(); return false; }
  uint32_t duty = 255;
  if (t < PUMP_RAMP_MS) duty = 40 + (215UL * t) / PUMP_RAMP_MS;
  analogWrite(PUMP_PIN, duty);
  return true;
}

// ------------------------------------------------------------------ LED helpers
uint8_t capB(uint16_t v) { return (uint8_t)((v * settings.maxBright) / 255); }

uint32_t green(uint8_t b)      { return Adafruit_NeoPixel::Color(0, capB(b), 0); }
uint32_t greenWhite(uint8_t b) { return Adafruit_NeoPixel::Color(capB(b) / 3, capB(b), capB(b) / 4); }

void fillAll(uint32_t ringColor, uint32_t stripColor) {
  ring.fill(ringColor);
  strip.fill(stripColor);
}

// triangle wave 0..255 with the given period
uint8_t tri(uint32_t periodMs, uint32_t phaseMs) {
  const uint32_t p = (millis() + phaseMs) % periodMs;
  const uint32_t half = periodMs / 2;
  return (p < half) ? (uint8_t)((255UL * p) / half) : (uint8_t)((255UL * (periodMs - p)) / half);
}

void animateIdle() {              // faint ember so the prop never looks dead
  const uint8_t b = 6 + tri(4000, 0) / 32;         // 6..13
  fillAll(green(b), green(b / 2));
}

void animateArmed() {             // slow charging pulse that builds over ~20 s
  const uint32_t t = since(stateSince);
  const uint8_t ceiling = (uint8_t)min<uint32_t>(90 + t / 250, 170); // 90 -> 170 over 20 s
  const uint8_t b = 25 + (uint16_t)tri(1600, 0) * (ceiling - 25) / 255;
  fillAll(green(b), green(b));
  // a single bright pixel orbiting the socket ring sells "energy flowing in"
  const uint16_t i = (millis() / 60) % RING_COUNT;
  ring.setPixelColor(i, greenWhite(255));
}

void animateFlash() { fillAll(greenWhite(255), greenWhite(255)); }

void animatePouring() {           // bright swirl on the strip, breathing ring, all near max
  const uint8_t base = 140 + tri(700, 0) / 3;      // 140..225
  ring.fill(green(base));
  for (uint16_t i = 0; i < STRIP_COUNT; i++) {
    const uint16_t wave = (uint16_t)((i * 255UL) / max<uint16_t>(STRIP_COUNT, 1) + (millis() / 4)) & 255;
    const uint8_t b = 120 + ((wave < 128 ? wave : 255 - wave) * 135) / 128; // 120..255
    strip.setPixelColor(i, green(b));
  }
  const uint16_t head = (millis() / 25) % RING_COUNT;
  for (uint8_t k = 0; k < 6; k++) ring.setPixelColor((head + RING_COUNT - k) % RING_COUNT, greenWhite(255 - k * 35));
}

void animateLocked() {            // satisfied afterglow that slowly fades to a steady glow
  const uint32_t t = since(stateSince);
  const uint8_t b = (t < 4000) ? (uint8_t)(200 - (140UL * t) / 4000) : 60;
  fillAll(green(b), green(b));
}

// ------------------------------------------------------------------ settings
void loadSettings() {
  EEPROM.begin(256);
  Settings s;
  EEPROM.get(0, s);
  if (s.magic == SETTINGS_MAGIC && s.pourMs >= 500 && s.pourMs <= MAX_PUMP_MS) settings = s;
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
  Serial.print(F(" maxBright=")); Serial.println(settings.maxBright);
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
  Serial.println(F("commands: status | cal <ms> | pour <ms> | leds <0-255> | save | stop"));
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
  const bool h = digitalRead(HALL_PIN) == LOW;    // A3144 pulls LOW when the magnet is present
  const bool s = digitalRead(SWITCH_PIN) == LOW;  // NO contact to GND
  const uint32_t now = millis();
  if (h != hallRaw) { hallRaw = h; hallChanged = now; }
  if (s != swRaw)   { swRaw = s;   swChanged = now; }
  if (since(hallChanged) >= (hallRaw ? HALL_DEBOUNCE_MS : RING_GONE_MS)) hallStable = hallRaw;
  if (since(swChanged) >= SWITCH_DEBOUNCE_MS) swStable = swRaw;
  if (switchJammed && !swStable) switchJammed = false;  // released at last
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

  Serial.begin(115200);
  loadSettings();

  ring.begin();  ring.setBrightness(255);  ring.clear();  ring.show();
  strip.begin(); strip.setBrightness(255); strip.clear(); strip.show();

  // settle the debouncers; if the switch is already pressed something is jammed
  for (int i = 0; i < 30; i++) { readInputs(); delay(10); }
  switchJammed = swStable;

  // short boot sweep so you know it is alive (and that both LED chains work)
  for (uint16_t i = 0; i < RING_COUNT; i++) { ring.setPixelColor(i, green(120)); ring.show(); delay(12); }
  for (uint16_t i = 0; i < STRIP_COUNT; i++) { strip.setPixelColor(i, green(90)); strip.show(); delay(6); }
  delay(150);
  ring.clear(); strip.clear(); ring.show(); strip.show();
  enter(State::IDLE);
}

void loop() {
  readInputs();
  serviceSerial();
  const bool pumping = pumpService();   // enforces duration and the hard cap every pass

  // Global interlock: no ring -> no pump, whatever the state (only a serial "cal" run is exempt).
  if (!hallStable && pumpOn && !pumpCal) pumpStop();

  switch (state) {
    case State::IDLE:
      animateIdle();
      if (hallStable) {
        pouredThisInsertion = false;
        if (swStable) switchJammed = true;  // pressed before the twist (stuck cam): ignore until released
        enter(State::ARMED);
      }
      break;

    case State::ARMED:
      animateArmed();
      if (!hallStable) { enter(State::IDLE); break; }
      if (swStable && !switchJammed && !pouredThisInsertion) {
        pouredThisInsertion = true;       // one pour per insertion, decided here
        enter(State::FLASH);
      }
      break;

    case State::FLASH:
      animateFlash();
      if (!hallStable) { enter(State::IDLE); break; }
      if (since(stateSince) >= FLASH_MS && hallRaw) {   // raw too: never start on a stale debounced reading
        pumpStart(settings.pourMs);
        enter(State::POURING);
      }
      break;

    case State::POURING:
      animatePouring();
      if (!hallStable) { pumpStop(); enter(State::IDLE); break; }   // ring pulled: abort
      if (!pumping)   { enter(State::LOCKED); }
      break;

    case State::LOCKED:
      animateLocked();
      if (!hallStable) enter(State::IDLE);   // only a removed ring re-arms the prop
      break;
  }

  ring.show();
  strip.show();
  delay(8);   // ~100 Hz; NeoPixel show() for 84 px takes ~2.5 ms
}
