"""Run a Game Boy ROM with no window and check what it shows.

Usage: check_rom.py ROM OUTPUT_DIR [IMAGE ...]

Saves screenshot-before.png and screenshot-after.png to OUTPUT_DIR: the
screen before and after pressing A. Exits non-zero when the ROM is missing,
the screen is one flat colour, an IMAGE does not appear on the screen, the
ROM makes no sound, the sound never changes note, or pressing A does not
change the screen.

Each IMAGE is a PNG the ROM is meant to display. The check looks for it
anywhere on the screen, so it needs no copy of the image's position and no
stored reference picture: edit the PNG and the check follows.
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pyboy import PyBoy

# Frames to run before each screenshot. The Game Boy draws about 60 a second;
# two seconds is ample for the ROM to start, and one for it to react.
BOOT_FRAMES = 120
REACT_FRAMES = 60
# Sound in the first second is ignored. The ROM makes a short blip about
# half a second after starting even when it plays no music, so sound that
# early says nothing about the music.
SOUND_SETTLE_FRAMES = 60
# How long to listen in all: eighteen seconds, enough for the song to play
# through once.
LISTEN_FRAMES = 1080
# A note counts once it has lasted this many frames in a row; shorter runs
# are the clicks between notes. And music must use at least this many
# different notes: one held note is sound, but it is not a tune.
MIN_NOTE_FRAMES = 5
MIN_DIFFERENT_NOTES = 3

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_in(samples: np.ndarray, sample_rate: int) -> str | None:
    """Name the note sounding in one frame of sound, or None for silence.

    A plain Game Boy tone switches between off and on at a steady rate, and
    how fast it switches is the pitch. This finds each off-to-on step,
    measures the usual gap between them, and names the nearest musical note,
    such as "G4".
    """
    if not samples.any():
        return None
    on = samples > samples.mean()
    steps = np.flatnonzero(on[1:] & ~on[:-1])
    if len(steps) < 3:
        return None
    frequency = sample_rate / float(np.median(np.diff(steps)))
    # 69 is the number musicians give the A above middle C, at 440 Hz; each
    # step of one is a semitone, twelve to the octave.
    number = round(69 + 12 * math.log2(frequency / 440))
    return f"{NOTE_NAMES[number % 12]}{number // 12 - 1}"


def notes_heard(per_frame: list[str | None]) -> list[str]:
    """Reduce a note per frame to the notes played, in order."""
    played: list[str] = []
    after_silence = True
    run_note, run_length = None, 0
    for note in per_frame + [None]:
        if note == run_note:
            run_length += 1
            continue
        if run_length >= MIN_NOTE_FRAMES:
            if run_note is None:
                after_silence = True
            # The same note twice in a row is one note interrupted by a
            # click, unless there was a real silence between.
            elif after_silence or played[-1] != run_note:
                played.append(run_note)
                after_silence = False
        run_note, run_length = note, 1
    return played


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

    # window="null" runs the emulator with no display at all. Sound is still
    # worked out, though nothing is played: after each frame the emulator
    # holds that frame's sound as a list of numbers, all zero when silent.
    pyboy = PyBoy(str(rom), window="null", sound_emulated=True)
    per_frame: list[str | None] = []

    def run(frames: int) -> None:
        """Run the ROM, noting which note sounds in each frame."""
        for _ in range(frames):
            pyboy.tick()
            # Both speakers carry the same sound here; the left is enough.
            samples = np.asarray(pyboy.sound.ndarray)[:, 0].astype(int)
            per_frame.append(note_in(samples, pyboy.sound.sample_rate))

    try:
        run(BOOT_FRAMES)
        before = pyboy.screen.image.convert("RGB")
        before.save(before_path)

        # Press and release A, as a quick tap would.
        pyboy.button("a")
        run(REACT_FRAMES)
        after = pyboy.screen.image.convert("RGB")
        after.save(after_path)

        # Keep listening until the song has had time to play through.
        run(LISTEN_FRAMES - BOOT_FRAMES - REACT_FRAMES)
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

    notes = notes_heard(per_frame[SOUND_SETTLE_FRAMES:])
    if not notes:
        print(f"FAIL: no sound was produced between frames {SOUND_SETTLE_FRAMES} and {LISTEN_FRAMES}")
        return 1
    if len(set(notes)) < MIN_DIFFERENT_NOTES:
        print(
            f"FAIL: the sound did not change note enough to be music; heard only {' '.join(notes)}, "
            f"and a tune needs at least {MIN_DIFFERENT_NOTES} different notes"
        )
        return 1

    if before.tobytes() == after.tobytes():
        print(f"FAIL: pressing A did not change the screen; see {after_path}")
        return 1

    shown = f"{len(image_paths)} image(s) shown, " if image_paths else ""
    print(
        f"PASS: {shown}notes heard: {' '.join(notes)}, "
        f"and screen changed after pressing A; see {before_path} and {after_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
