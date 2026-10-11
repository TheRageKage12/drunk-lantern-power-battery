// EEPROM.h - host-side mock of the rp2040 core's flash-backed EEPROM emulation.
// begin() copies a 4 KB "flash sector" into RAM, get/put work on the RAM copy, commit() writes
// the RAM copy back to the sector (only when dirty, like the real one). powerCycle() drops the
// RAM copy but keeps the sector, which is what a reboot does.
#pragma once
#include "Arduino.h"

class EEPROMClass {
public:
  EEPROMClass() : _sector(4096, 0xFF) {}

  void begin(size_t size) {
    if (size <= 0 || size > 4096) size = 4096;
    size = (size + 255) & ~(size_t)255;
    _data.assign(_sector.begin(), _sector.begin() + size);
    _size = size;
    _dirty = false;
    begins++;
  }
  bool end() { if (!_size) return false; bool r = commit(); _data.clear(); _size = 0; _dirty = false; return r; }

  uint8_t read(int address) { if (address < 0 || (size_t)address >= _size) return 0; return _data[address]; }
  void write(int address, uint8_t v) {
    if (address < 0 || (size_t)address >= _size) return;
    if (_data[address] != v) { _data[address] = v; _dirty = true; }
  }
  template <typename T> T& get(int address, T& t) {
    if (address < 0 || address + sizeof(T) > _size) return t;
    memcpy(&t, _data.data() + address, sizeof(T));
    return t;
  }
  template <typename T> const T& put(int address, const T& t) {
    if (address < 0 || address + sizeof(T) > _size) return t;
    if (memcmp(_data.data() + address, &t, sizeof(T)) != 0) {
      _dirty = true;
      memcpy(_data.data() + address, &t, sizeof(T));
    }
    return t;
  }
  bool commit() {
    if (!_size) return false;
    if (!_dirty) return true;
    std::copy(_data.begin(), _data.end(), _sector.begin());
    _dirty = false;
    commits++;
    return true;
  }
  size_t length() const { return _size; }

  // simulation side
  void powerCycle() { _data.clear(); _size = 0; _dirty = false; }          // reboot: RAM copy lost, flash kept
  void eraseFlash() { std::fill(_sector.begin(), _sector.end(), 0xFF); } // factory-fresh flash
  const std::vector<uint8_t>& sector() const { return _sector; }

  unsigned begins = 0, commits = 0;
private:
  std::vector<uint8_t> _sector;
  std::vector<uint8_t> _data;
  size_t _size = 0;
  bool _dirty = false;
};
inline EEPROMClass EEPROM;
