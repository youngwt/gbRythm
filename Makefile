# Builds the Game Boy ROM, checks it, and opens it in an emulator.
# Tools live in tools/ and are found by explicit path; see docs/setup.md.
#
#   make         build the ROM
#   make check   build, then run the ROM with no window and check it
#   make debug   build a second ROM with debug symbols, for the debugger
#   make run     build, then open the ROM in Emulicious
#   make clean   delete everything the build made

GBDK_HOME  ?= tools/gbdk
LCC        := $(GBDK_HOME)/bin/lcc
PNG2ASSET  := $(GBDK_HOME)/bin/png2asset
PYTHON     := tools/venv/bin/python
EMULICIOUS := tools/emulicious/Emulicious.jar
# The music driver: a header to compile against and a library to link in.
HUGE_HOME  := tools/hugedriver
HUGE_LIB   := $(HUGE_HOME)/gbdk/hUGEDriver.lib
# Java is started through a wrapper so that it opens its window on the host
# when make runs inside the VS Code Flatpak; see docs/setup.md.
JAVA       := scripts/java-host.sh

# Extra compiler flags; empty for the normal build, set by the debug target.
LCCFLAGS   ?=

BUILD_DIR  := build
ROM        := $(BUILD_DIR)/gbrythm.gb
SOURCES    := $(wildcard src/*.c)
HEADERS    := $(wildcard src/*.h)

# Each PNG in assets/ is converted to a .c and .h pair in build/.
ASSETS     := $(wildcard assets/*.png)
ASSET_SRCS := $(patsubst assets/%.png,$(BUILD_DIR)/%.c,$(ASSETS))

OBJECTS    := $(patsubst src/%.c,$(BUILD_DIR)/%.o,$(SOURCES)) \
              $(ASSET_SRCS:.c=.o)

# Remove a half-written target when its recipe fails, so a failed build
# never leaves a ROM that looks up to date.
.DELETE_ON_ERROR:

.PHONY: all check debug run clean require-gbdk require-python require-emulicious require-hugedriver

all: $(ROM)

# -Wl-l passes the music driver's library to the linker.
$(ROM): $(OBJECTS) | require-gbdk require-hugedriver
	$(LCC) $(LCCFLAGS) -Wl-l$(HUGE_LIB) -o $@ $(OBJECTS)

# Every object depends on every header and every converted image: coarse,
# but a changed header or PNG can never leave a stale object behind.
# -I$(BUILD_DIR) lets source files include the generated image headers.
# -I$(HUGE_HOME)/include finds the music driver's header.
$(BUILD_DIR)/%.o: src/%.c $(HEADERS) $(ASSET_SRCS) | $(BUILD_DIR) require-gbdk require-hugedriver
	$(LCC) $(LCCFLAGS) -I$(BUILD_DIR) -I$(HUGE_HOME)/include -c -o $@ $<

$(BUILD_DIR)/%.o: $(BUILD_DIR)/%.c | require-gbdk
	$(LCC) $(LCCFLAGS) -c -o $@ $<

# Convert the PNGs to C as background images. They are converted together,
# by one run of the script, because each image's tile numbers start where
# the previous image's end; "&:" tells make that the one recipe writes every
# file. Changing any PNG reconverts them all. See scripts/convert-images.sh.
ifneq ($(ASSETS),)
$(ASSET_SRCS) &: $(ASSETS) scripts/convert-images.sh | $(BUILD_DIR) require-gbdk
	scripts/convert-images.sh $(PNG2ASSET) $(BUILD_DIR) $(sort $(ASSETS))
endif

# Keep the generated C files; without this make deletes them as temporary
# files and reconverts every image on the next build.
.SECONDARY: $(ASSET_SRCS)

$(BUILD_DIR):
	mkdir -p $@

# The check is given the marker and falling-note images so it can find them
# on the screen.
check: $(ROM) | require-python
	$(PYTHON) scripts/check_rom.py $(ROM) $(BUILD_DIR) assets/target.png assets/falling.png

# Build a second ROM for the debugger in build/debug, leaving the normal ROM
# alone. -debug writes the .cdb file that maps machine code back to C lines.
# -Wf--max-allocs-per-node0 turns off an optimisation that reorders code, so
# stepping follows the C source line by line; it makes the code bigger and
# slower, which is why the ROM that "make check" tests is built without it.
debug:
	$(MAKE) BUILD_DIR=$(BUILD_DIR)/debug LCCFLAGS="-debug -Wf--max-allocs-per-node0"

# Open the ROM in Emulicious to play it.
run: $(ROM) | require-emulicious
	$(JAVA) -jar $(EMULICIOUS) $(ROM)

clean:
	rm -rf $(BUILD_DIR)

require-gbdk:
	@test -x $(LCC) || { echo "GBDK not found at $(LCC). Follow docs/setup.md."; exit 1; }

require-hugedriver:
	@test -f $(HUGE_LIB) || { echo "hUGEDriver not found at $(HUGE_LIB). Follow docs/setup.md."; exit 1; }

require-python:
	@test -x $(PYTHON) || { echo "PyBoy environment not found at $(PYTHON). Follow docs/setup.md."; exit 1; }

# The wrapper script reports a missing Java itself.
require-emulicious:
	@test -f $(EMULICIOUS) || { echo "Emulicious not found at $(EMULICIOUS). Follow docs/setup.md."; exit 1; }
