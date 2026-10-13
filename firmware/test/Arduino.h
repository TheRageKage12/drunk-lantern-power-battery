// Arduino.h - minimal host-side mock of the Arduino core for the green_lantern test harness.
//
// Everything lives in this header (C++17 inline variables) so the test runner is a single
// translation unit that #includes the mocks and then the .ino itself.
//
//   sim::nowUs            fake clock (micros). millis()/micros() read it, delay() advances it,
//                         NeoPixel show() advances it by the real wire time.
//   sim::setInput(pin,l)  level a digitalRead() of an input pin returns (default HIGH = pulled up)
//   sim::pin[p]           recorded pinMode / digitalWrite / analogWrite state, modelled after the
//                         earlephilhower core: analogWrite moves the pad to the PWM function,
//                         digitalWrite moves it back to SIO.
//   sim::runs[p]          every on/off run of an output pin with start/end timestamps, so a test
//                         can measure exactly how long the pump pin was energised.
#pragma once
#include <cstdint>
#include <cstddef>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <deque>
#include <algorithm>
#include <math.h>
#include <type_traits>

#define HIGH 1
#define LOW  0
#define INPUT          0
#define OUTPUT         1
#define INPUT_PULLUP   2
#define INPUT_PULLDOWN 3

// Seeed XIAO RP2040 pin map (rp2040 core, variants/seeed_xiao_rp2040/pins_arduino.h)
static const uint8_t D0 = 26, D1 = 27, D2 = 28, D3 = 29, D4 = 6, D5 = 7,
                     D6 = 0, D7 = 1, D8 = 2, D9 = 4, D10 = 3;
static const uint8_t A0 = 26, A1 = 27, A2 = 28, A3 = 29;

using std::min;
using std::max;
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))
#define F(x) (x)
#define PROGMEM

namespace sim {

constexpr int NPINS = 32;
enum Func { FUNC_SIO, FUNC_PWM };

struct Pin {
  int  mode  = -1;        // last pinMode(), -1 = never configured
  Func func  = FUNC_SIO;  // pad function, as the rp2040 core switches it
  int  out   = LOW;       // SIO output register (digitalWrite)
  int  pwm   = 0;         // PWM level 0..analogWriteRange (analogWrite)
  int  in    = HIGH;      // external level seen by digitalRead() (default: pulled up / idle)
  bool on    = false;     // effective output: PWM level > 0, or SIO HIGH
  int  writes = 0;        // number of digitalWrite+analogWrite calls
};

struct Run { uint64_t startUs; uint64_t endUs; bool open; };
struct Event { uint64_t tUs; uint8_t pin; const char* what; int val; };

inline uint64_t nowUs = 0;
inline Pin pin[NPINS];
inline std::vector<Run> runs[NPINS];
inline std::vector<Event> events;              // every pinMode/digitalWrite/analogWrite
inline uint64_t showUsPerPixel = 30;           // 24 bits x 1.25 us
inline uint64_t showLatchUs    = 300;          // WS2812 reset/latch time the library waits for

inline void resetPins() {
  for (int i = 0; i < NPINS; i++) { pin[i] = Pin(); runs[i].clear(); }
  events.clear();
}

inline bool effective(const Pin& p) { return p.func == FUNC_PWM ? p.pwm > 0 : p.out == HIGH; }

inline void updateRuns(uint8_t p) {
  bool now = effective(pin[p]);
  if (now == pin[p].on) return;
  pin[p].on = now;
  if (now) runs[p].push_back(Run{nowUs, 0, true});
  else if (!runs[p].empty() && runs[p].back().open) { runs[p].back().endUs = nowUs; runs[p].back().open = false; }
}

inline void advanceUs(uint64_t us) { nowUs += us; }

inline void setInput(uint8_t p, int level) { pin[p].in = level; }

// longest closed-or-open run on a pin, in microseconds, and the number of runs
inline uint64_t runLengthUs(const Run& r) { return (r.open ? nowUs : r.endUs) - r.startUs; }
inline uint64_t longestRunUs(uint8_t p) {
  uint64_t m = 0;
  for (auto& r : runs[p]) m = std::max(m, runLengthUs(r));
  return m;
}
inline uint64_t totalOnUs(uint8_t p) {
  uint64_t t = 0;
  for (auto& r : runs[p]) t += runLengthUs(r);
  return t;
}

} // namespace sim

// ------------------------------------------------------------------ time
inline unsigned long millis() { return (unsigned long)(uint32_t)(sim::nowUs / 1000); }
inline unsigned long micros() { return (unsigned long)(uint32_t)(sim::nowUs); }
inline void delay(unsigned long ms) { sim::advanceUs((uint64_t)ms * 1000); }
inline void delayMicroseconds(unsigned int us) { sim::advanceUs(us); }
inline void yield() {}
inline void noInterrupts() {}
inline void interrupts() {}

// ------------------------------------------------------------------ GPIO
inline void pinMode(uint8_t p, int mode) {
  if (p >= sim::NPINS) return;
  sim::pin[p].mode = mode;
  sim::pin[p].func = sim::FUNC_SIO;
  sim::events.push_back({sim::nowUs, p, "pinMode", mode});
  sim::updateRuns(p);
}
inline void digitalWrite(uint8_t p, int val) {
  if (p >= sim::NPINS) return;
  sim::pin[p].func = sim::FUNC_SIO;          // core: gpio_set_function(pin, GPIO_FUNC_SIO)
  sim::pin[p].out  = val ? HIGH : LOW;
  sim::pin[p].writes++;
  sim::events.push_back({sim::nowUs, p, "digitalWrite", val});
  sim::updateRuns(p);
}
namespace sim { inline int pwmRange = 255; }  // analogWriteRange() of the rp2040 core (default 255)
inline void analogWriteRange(uint32_t r) { sim::pwmRange = (int)r; }
inline void analogWriteFreq(uint32_t) {}
inline void analogWrite(uint8_t p, int val) {
  if (p >= sim::NPINS) return;
  if (val < 0) val = 0;
  if (val > sim::pwmRange) val = sim::pwmRange;
  sim::pin[p].func = sim::FUNC_PWM;          // core: gpio_set_function(pin, GPIO_FUNC_PWM)
  sim::pin[p].pwm  = val;
  sim::pin[p].writes++;
  sim::events.push_back({sim::nowUs, p, "analogWrite", val});
  sim::updateRuns(p);
}
namespace sim { inline int analogIn[NPINS] = {}; }   // raw ADC counts analogRead() returns (default 0)
inline void analogReadResolution(int) {}
inline int analogRead(uint8_t p) { return p < sim::NPINS ? sim::analogIn[p] : 0; }
inline int digitalRead(uint8_t p) {
  if (p >= sim::NPINS) return LOW;
  const sim::Pin& x = sim::pin[p];
  if (x.mode == OUTPUT) return sim::effective(x) ? HIGH : LOW;
  return x.in;
}

// ------------------------------------------------------------------ String
class String {
  std::string s;
public:
  String() {}
  String(const char* c) : s(c ? c : "") {}
  String(const std::string& x) : s(x) {}
  String(char c) : s(1, c) {}
  unsigned int length() const { return (unsigned int)s.length(); }
  const char* c_str() const { return s.c_str(); }
  const std::string& str() const { return s; }
  void trim() {
    auto ws = [](char c) { return c == ' ' || c == '\t' || c == '\r' || c == '\n' || c == '\v' || c == '\f'; };
    size_t b = 0, e = s.size();
    while (b < e && ws(s[b])) b++;
    while (e > b && ws(s[e - 1])) e--;
    s = s.substr(b, e - b);
  }
  void toLowerCase() { for (auto& c : s) c = (char)tolower((unsigned char)c); }
  void toUpperCase() { for (auto& c : s) c = (char)toupper((unsigned char)c); }
  bool startsWith(const String& p) const { return s.compare(0, p.s.size(), p.s) == 0; }
  bool endsWith(const String& p) const { return s.size() >= p.s.size() && s.compare(s.size() - p.s.size(), p.s.size(), p.s) == 0; }
  String substring(unsigned int from) const { return from >= s.size() ? String() : String(s.substr(from)); }
  String substring(unsigned int from, unsigned int to) const {
    if (from > to) std::swap(from, to);
    if (from >= s.size()) return String();
    return String(s.substr(from, std::min<size_t>(to, s.size()) - from));
  }
  long toInt() const { return atol(s.c_str()); }       // same semantics as the Arduino String
  float toFloat() const { return (float)atof(s.c_str()); }
  int indexOf(char c) const { auto p = s.find(c); return p == std::string::npos ? -1 : (int)p; }
  char charAt(unsigned int i) const { return i < s.size() ? s[i] : 0; }
  char operator[](unsigned int i) const { return charAt(i); }
  bool operator==(const String& o) const { return s == o.s; }
  bool operator==(const char* o) const { return s == (o ? o : ""); }
  bool operator!=(const String& o) const { return !(*this == o); }
  bool operator!=(const char* o) const { return !(*this == o); }
  String& operator+=(char c) { s += c; return *this; }
  String& operator+=(const char* c) { if (c) s += c; return *this; }
  String& operator+=(const String& o) { s += o.s; return *this; }
  String& operator=(const char* c) { s = c ? c : ""; return *this; }
  String operator+(const String& o) const { return String(s + o.s); }
};

// ------------------------------------------------------------------ Serial
class SerialStub {
public:
  std::deque<char> rx;   // what the sketch will read (sim side writes with inject())
  std::string tx;        // everything the sketch printed
  bool begun = false;

  void begin(unsigned long) { begun = true; }
  void end() { begun = false; }
  operator bool() const { return true; }
  int available() { return (int)rx.size(); }
  int peek() { return rx.empty() ? -1 : rx.front(); }
  int read() { if (rx.empty()) return -1; char c = rx.front(); rx.pop_front(); return (unsigned char)c; }
  void flush() {}

  size_t print(const char* s) { if (!s) return 0; tx += s; return strlen(s); }
  size_t print(const String& s) { tx += s.str(); return s.length(); }
  size_t print(char c) { tx += c; return 1; }
  template <class T, class = std::enable_if_t<std::is_arithmetic<T>::value && !std::is_same<T, char>::value>>
  size_t print(T v) {
    std::string t = std::is_floating_point<T>::value ? std::to_string((double)v)
                  : std::is_signed<T>::value ? std::to_string((long long)v) : std::to_string((unsigned long long)v);
    tx += t; return t.size();
  }
  size_t print(double v, int digits) { char b[48]; snprintf(b, sizeof b, "%.*f", digits, v); tx += b; return strlen(b); }
  size_t println() { tx += '\n'; return 1; }
  template <class T> size_t println(T v) { size_t n = print(v); return n + println(); }
  size_t write(uint8_t c) { tx += (char)c; return 1; }

  // simulation side
  void inject(const std::string& s) { for (char c : s) rx.push_back(c); }
  void reset() { rx.clear(); tx.clear(); begun = false; }
};
inline SerialStub Serial;
