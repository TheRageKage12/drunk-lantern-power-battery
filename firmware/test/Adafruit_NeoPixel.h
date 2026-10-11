// Adafruit_NeoPixel.h - host-side mock. Records fill/setPixelColor/show calls and charges the
// fake clock the real wire time for show() (24 bits x 1.25 us per pixel, plus the 300 us latch
// the library waits for before the next frame), so the loop period in simulation matches the
// board: ~8 ms delay + ~2.5 ms of show() for 84 pixels.
#pragma once
#include "Arduino.h"

typedef uint16_t neoPixelType;
#define NEO_RGB  ((0 << 6) | (0 << 4) | (1 << 2) | (2))
#define NEO_GRB  ((1 << 6) | (1 << 4) | (0 << 2) | (2))
#define NEO_KHZ800 0x0000
#define NEO_KHZ400 0x0100

class Adafruit_NeoPixel {
public:
  Adafruit_NeoPixel(uint16_t n, int16_t p = 6, neoPixelType t = NEO_GRB + NEO_KHZ800)
    : numLEDs(n), pin(p), type(t), px(n, 0) {}

  bool begin() { begun = true; pinMode((uint8_t)pin, OUTPUT); digitalWrite((uint8_t)pin, LOW); return true; }

  void show() {
    if (!begun) return;
    // canShow(): block until 300 us after the previous frame ended
    uint64_t sinceEnd = sim::nowUs - endTimeUs;
    if (shows > 0 && sinceEnd < sim::showLatchUs) sim::advanceUs(sim::showLatchUs - sinceEnd);
    sim::advanceUs((uint64_t)numLEDs * sim::showUsPerPixel);
    endTimeUs = sim::nowUs;
    shows++;
    lastShown = px;
  }

  void setPixelColor(uint16_t n, uint32_t c) { if (n < numLEDs) { px[n] = c; sets++; } }
  void setPixelColor(uint16_t n, uint8_t r, uint8_t g, uint8_t b) { setPixelColor(n, Color(r, g, b)); }
  void fill(uint32_t c = 0, uint16_t first = 0, uint16_t count = 0) {
    if (first >= numLEDs) return;
    uint16_t end = (count == 0 || first + count > numLEDs) ? numLEDs : first + count;
    for (uint16_t i = first; i < end; i++) px[i] = c;
    fills++;
  }
  void clear() { std::fill(px.begin(), px.end(), 0u); clears++; }
  void setBrightness(uint8_t b) { brightness = b; }
  uint8_t getBrightness() const { return brightness; }
  uint16_t numPixels() const { return numLEDs; }
  uint32_t getPixelColor(uint16_t n) const { return n < numLEDs ? px[n] : 0; }
  int16_t getPin() const { return pin; }
  bool canShow() const { return sim::nowUs - endTimeUs >= sim::showLatchUs; }

  static uint32_t Color(uint8_t r, uint8_t g, uint8_t b) { return ((uint32_t)r << 16) | ((uint32_t)g << 8) | b; }
  static uint32_t Color(uint8_t r, uint8_t g, uint8_t b, uint8_t w) { return ((uint32_t)w << 24) | ((uint32_t)r << 16) | ((uint32_t)g << 8) | b; }

  // simulation side
  void reset() { begun = false; std::fill(px.begin(), px.end(), 0u); lastShown.clear(); shows = fills = sets = clears = 0; endTimeUs = 0; }
  uint32_t maxComponentShown() const {
    uint32_t m = 0;
    for (uint32_t c : lastShown) m = std::max({m, (c >> 16) & 255, (c >> 8) & 255, c & 255});
    return m;
  }

  uint16_t numLEDs;
  int16_t pin;
  neoPixelType type;
  std::vector<uint32_t> px;          // frame buffer (what the sketch has drawn)
  std::vector<uint32_t> lastShown;   // frame buffer as of the last show()
  bool begun = false;
  uint8_t brightness = 0;
  uint64_t endTimeUs = 0;
  unsigned shows = 0, fills = 0, sets = 0, clears = 0;
};
