#!/bin/sh
# Build and run the host-side simulation of green_lantern.ino.
set -e
cd "$(dirname "$0")"
make -s test
