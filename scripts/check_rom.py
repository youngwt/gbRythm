"""Run a Game Boy ROM with no window and check what it shows.

Usage: check_rom.py ROM OUTPUT_DIR [IMAGE ...]

Saves screenshot-before.png and screenshot-after.png to OUTPUT_DIR: the
screen before and after pressing A. Exits non-zero when the ROM is missing,
the screen is one flat colour, an IMAGE does not appear on the screen, or
pressing A does not change the screen.

Each IMAGE is a PNG the ROM is meant to display. The check looks for it
anywhere on the screen, so it needs no copy of the image's position and no
stored reference picture: edit the PNG and the check follows.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pyboy import PyBoy

# Frames to run before each screenshot. The Game Boy draws about 60 a second;
# two seconds is ample for the ROM to start, and one for it to react.
BOOT_FRAMES = 120
REACT_FRAMES = 60


def shades(image: Image.Image) -> np.ndarray:
    """Reduce a picture to the Game Boy's four shades, 0 (white) to 3 (black).

    The PNG and the emulator use slightly different greys for the same shade,
    so both are sorted into four brightness bands before they are compared.
    """
    brightness = np.asarray(image.convert("L"), dtype=np.int16)
    return 3 - np.clip(brightness // 64, 0, 3)


def appears_on(screen: np.ndarray, image: np.ndarray) -> bool:
    """True when the image is found, pixel for pixel, somewhere on the screen."""
    height, width = image.shape
    for top in range(screen.shape[0] - height + 1):
        for left in range(screen.shape[1] - width + 1):
            if np.array_equal(screen[top:top + height, left:left + width], image):
                return True
    return False


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    rom = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    before_path = output_dir / "screenshot-before.png"
    after_path = output_dir / "screenshot-after.png"
    image_paths = [Path(arg) for arg in sys.argv[3:]]

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

    screen = shades(before)
    for image_path in image_paths:
        if not image_path.is_file():
            print(f"FAIL: image file not found: {image_path}")
            return 1
        image = shades(Image.open(image_path))
        # A picture of one flat shade would match any empty patch of screen.
        if image.min() == image.max():
            print(f"FAIL: {image_path} is one flat shade, so the check cannot look for it")
            return 1
        if not appears_on(screen, image):
            print(f"FAIL: {image_path} was not found on screen; see {before_path}")
            return 1

    if before.tobytes() == after.tobytes():
        print(f"FAIL: pressing A did not change the screen; see {after_path}")
        return 1

    shown = f"{len(image_paths)} image(s) shown and " if image_paths else ""
    print(f"PASS: {shown}screen changed after pressing A; see {before_path} and {after_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
