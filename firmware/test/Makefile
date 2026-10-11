# Host-side simulation of firmware/green_lantern/green_lantern.ino (no board needed).
#   make test       build and run the scenarios
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

clean:
	rm -rf build

.PHONY: all test clean
