# Host-side simulation of firmware/green_lantern/green_lantern.ino (no board needed).
#   make test       build and run the scenarios
#   make baseline   run the same scenarios against a pre-review copy of the sketch (expects failures)
CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O1 -g -Wall -Wextra -Wno-unused-parameter -Wno-unused-function
SKETCH    = ../green_lantern/green_lantern.ino
MOCKS     = Arduino.h Adafruit_NeoPixel.h EEPROM.h

all: build/test_green_lantern

build/test_green_lantern: test_green_lantern.cpp $(MOCKS) $(SKETCH)
	@mkdir -p build
	$(CXX) $(CXXFLAGS) -I. -x c++ test_green_lantern.cpp -o $@

test: build/test_green_lantern
	./build/test_green_lantern

# BASELINE_SKETCH: path to an older .ino without the pumpOnSince/pumpCal globals
BASELINE_SKETCH ?= build/baseline.ino
baseline: $(MOCKS) test_green_lantern.cpp
	@mkdir -p build
	@test -f $(BASELINE_SKETCH) || git show HEAD:firmware/green_lantern/green_lantern.ino > $(BASELINE_SKETCH)
	$(CXX) $(CXXFLAGS) -I. -x c++ -DGL_BASELINE -DSKETCH_PATH='"$(BASELINE_SKETCH)"' test_green_lantern.cpp -o build/test_baseline
	-./build/test_baseline

clean:
	rm -rf build

.PHONY: all test baseline clean
