# Builds the Game Boy ROM and runs the headless check.
# Tools live in tools/ and are found by explicit path; see docs/setup.md.

GBDK_HOME ?= tools/gbdk
LCC       := $(GBDK_HOME)/bin/lcc
PNG2ASSET := $(GBDK_HOME)/bin/png2asset
PYTHON    := tools/venv/bin/python

BUILD_DIR := build
ROM       := $(BUILD_DIR)/gbrythm.gb
SOURCES   := $(wildcard src/*.c)
HEADERS   := $(wildcard src/*.h)

# Each PNG in assets/ is converted to a .c and .h pair in build/.
ASSETS      := $(wildcard assets/*.png)
ASSET_SRCS  := $(patsubst assets/%.png,$(BUILD_DIR)/%.c,$(ASSETS))

OBJECTS   := $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES)) \
             $(ASSET_SRCS:.c=.o)

# Remove a half-written target when its recipe fails, so a failed build
# never leaves a ROM that looks up to date.
.DELETE_ON_ERROR:

.PHONY: all check clean require-gbdk require-python

all: $(ROM)

$(ROM): $(OBJECTS) | require-gbdk
	$(LCC) -o $@ $(OBJECTS)

# Every object depends on every header and every converted image: coarse,
# but a changed header or PNG can never leave a stale object behind.
# -I$(BUILD_DIR) lets source files include the generated image headers.
$(BUILD_DIR)/%.o: src/%.c $(HEADERS) $(ASSET_SRCS) | $(BUILD_DIR) require-gbdk
	$(LCC) -I$(BUILD_DIR) -c -o $@ $<

$(BUILD_DIR)/%.o: $(BUILD_DIR)/%.c | require-gbdk
	$(LCC) -c -o $@ $<

# Convert a PNG to C as a background image: a set of 8x8 tiles plus a map
# saying which tile goes where. This writes both the .c and its .h.
# -tile_origin 128 numbers the tiles from 128 so they do not overwrite the
# text font, which occupies the lower tile numbers.
# -noflip keeps mirrored tiles separate; the original Game Boy cannot flip
# background tiles.
# png2asset exits 0 even when it reports an error such as too many colours,
# so its output is kept in a log and the build fails if the log has an error.
$(BUILD_DIR)/%.c: assets/%.png | $(BUILD_DIR) require-gbdk
	$(PNG2ASSET) $< -map -tile_origin 128 -noflip -o $@ > $@.log 2>&1; \
	status=$$?; cat $@.log; \
	test $$status -eq 0 && ! grep -qi "error" $@.log

# Keep the generated C files; without this make deletes them as temporary
# files and reconverts every image on the next build.
.SECONDARY: $(ASSET_SRCS)

$(BUILD_DIR):
	mkdir -p $@

check: $(ROM) | require-python
	$(PYTHON) scripts/check_rom.py $(ROM) $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

require-gbdk:
	@test -x $(LCC) || { echo "GBDK not found at $(LCC). Follow docs/setup.md."; exit 1; }

require-python:
	@test -x $(PYTHON) || { echo "PyBoy environment not found at $(PYTHON). Follow docs/setup.md."; exit 1; }
