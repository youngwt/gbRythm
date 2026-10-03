"""Run a Game Boy ROM with no window and save a screenshot of the screen.

Usage: check_rom.py ROM SCREENSHOT

Exits non-zero when the ROM is missing or the screen is one flat colour.
"""

import sys
from pathlib import Path

from pyboy import PyBoy

# Frames to run before the screenshot. The Game Boy draws about 60 a second;
# two seconds is ample for the ROM to start and print its text.
FRAMES = 120


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    rom = Path(sys.argv[1])
    screenshot = Path(sys.argv[2])

    if not rom.is_file():
        print(f"FAIL: ROM not found: {rom}")
        return 1

    # window="null" runs the emulator with no display at all.
    pyboy = PyBoy(str(rom), window="null", sound_emulated=False)
    try:
        pyboy.tick(FRAMES)
        image = pyboy.screen.image.convert("RGB")
        screenshot.parent.mkdir(parents=True, exist_ok=True)
        image.save(screenshot)
    finally:
        pyboy.stop(save=False)

    colours = image.getcolors()
    if colours is not None and len(colours) == 1:
        print(f"FAIL: screen is one flat colour; see {screenshot}")
        return 1

    print(f"PASS: screenshot saved to {screenshot}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
