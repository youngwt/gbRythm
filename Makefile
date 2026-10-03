# Builds the Game Boy ROM and runs the headless check.
# Tools live in tools/ and are found by explicit path; see docs/setup.md.

GBDK_HOME ?= tools/gbdk
LCC       := $(GBDK_HOME)/bin/lcc
PYTHON    := tools/venv/bin/python

BUILD_DIR := build
ROM       := $(BUILD_DIR)/gbrythm.gb
SOURCES   := $(wildcard src/*.c)
HEADERS   := $(wildcard src/*.h)
OBJECTS   := $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES))

# Remove a half-written target when its recipe fails, so a failed build
# never leaves a ROM that looks up to date.
.DELETE_ON_ERROR:

.PHONY: all check clean require-gbdk require-python

all: $(ROM)

$(ROM): $(OBJECTS) | require-gbdk
	$(LCC) -o $@ $(OBJECTS)

# Every object depends on every header: coarse, but a changed header can
# never leave a stale object behind.
$(BUILD_DIR)/%.o: src/%.c $(HEADERS) | $(BUILD_DIR) require-gbdk
	$(LCC) -c -o $@ $<

$(BUILD_DIR):
	mkdir -p $@

check: $(ROM) | require-python
	$(PYTHON) scripts/check_rom.py $(ROM) $(BUILD_DIR)/screenshot.png

clean:
	rm -rf $(BUILD_DIR)

require-gbdk:
	@test -x $(LCC) || { echo "GBDK not found at $(LCC). Follow docs/setup.md."; exit 1; }

require-python:
	@test -x $(PYTHON) || { echo "PyBoy environment not found at $(PYTHON). Follow docs/setup.md."; exit 1; }
