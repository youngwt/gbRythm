"""Run a Game Boy ROM with no window and check it reacts to the A button.

Usage: check_rom.py ROM OUTPUT_DIR

Saves screenshot-before.png and screenshot-after.png to OUTPUT_DIR: the
screen before and after pressing A. Exits non-zero when the ROM is missing,
the screen is one flat colour, or pressing A does not change the screen.
"""

import sys
from pathlib import Path

from pyboy import PyBoy

# Frames to run before each screenshot. The Game Boy draws about 60 a second;
# two seconds is ample for the ROM to start, and one for it to react.
BOOT_FRAMES = 120
REACT_FRAMES = 60


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2

    rom = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    before_path = output_dir / "screenshot-before.png"
    after_path = output_dir / "screenshot-after.png"

    if not rom.is_file():
        print(f"FAIL: ROM not found: {rom}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    # window="null" runs the emulator with no display at all.
    pyboy = PyBoy(str(rom), window="null", sound_emulated=False)
    try:
        pyboy.tick(BOOT_FRAMES)
        before = pyboy.screen.image.convert("RGB")
        before.save(before_path)

        # Press and release A, as a quick tap would.
        pyboy.button("a")
        pyboy.tick(REACT_FRAMES)
        after = pyboy.screen.image.convert("RGB")
        after.save(after_path)
    finally:
        pyboy.stop(save=False)

    colours = before.getcolors()
    if colours is not None and len(colours) == 1:
        print(f"FAIL: screen is one flat colour; see {before_path}")
        return 1

    if before.tobytes() == after.tobytes():
        print(f"FAIL: pressing A did not change the screen; see {after_path}")
        return 1

    print(f"PASS: screen changed after pressing A; see {before_path} and {after_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
