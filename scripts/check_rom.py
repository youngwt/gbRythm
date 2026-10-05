"""Run the Game Boy ROM with no window and check the game plays in time.

Usage: check_rom.py ROM OUTPUT_DIR FALLING_IMAGE PITCH=MARKER_IMAGE...

FALLING_IMAGE is the PNG of a falling note. Each PITCH=MARKER_IMAGE names a
pitch, such as D, and the PNG of the marker its notes should land on. The
check finds the images on the screen, so it needs no copy of where they are
drawn, and it reads the music from the sound, so it needs no copy of the
tune. The pitches and markers are the one thing it is told: they are the
game's design, and the check exists to hold the ROM to it.

Saves screenshot-play.png to OUTPUT_DIR: the screen part-way through the
song. Exits non-zero when the ROM is missing, the screen is one flat colour,
a marker is not on screen, the ROM makes no sound, the sound never changes
note, the falling notes do not match the notes heard, a note lands more than
a moment away from its sound, a note lands on the wrong marker, or a note
does not fall steadily.
"""

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pyboy import PyBoy

# How long to run the ROM: 25 seconds of Game Boy time, enough for the song
# to play through once and start again. The Game Boy draws about 60 frames a
# second; the emulator runs them much faster than that.
RUN_FRAMES = 1500
# When to save the screenshot: five seconds in, with notes on their way down.
SCREENSHOT_FRAME = 300
# How long the markers are looked for at the start.
MARKER_SEARCH_FRAMES = 120
# Sound in the first second is ignored. The ROM makes a short blip about
# half a second after starting even when it plays no music, so sound that
# early says nothing about the music.
SOUND_SETTLE_FRAMES = 60
# A note counts once it has lasted this many frames in a row; shorter runs
# are the clicks between notes. And music must use at least this many
# different notes: one held note is sound, but it is not a tune.
MIN_NOTE_FRAMES = 5
MIN_DIFFERENT_NOTES = 3
# A falling note should land on the marker in the frame its sound starts.
# This many frames either way, a thirtieth of a second, still counts.
MAX_GAP_FRAMES = 2
# The same pitch played twice in a row still starts a new note. Each note
# starts loud and fades, so a jump in loudness of at least this much, out of
# 15, marks the second one.
LOUDNESS_JUMP = 4

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def shades(pixels: np.ndarray) -> np.ndarray:
    """Reduce a picture to the Game Boy's four shades, 0 (white) to 3 (black).

    The PNG and the emulator use slightly different greys for the same shade,
    so both are sorted into four brightness bands before they are compared.
    Takes a grid of brightness values, 0 to 255.
    """
    return (3 - (pixels >> 6)).astype(np.uint8)


def load_shades(path: Path) -> np.ndarray:
    # "L" is a picture as brightness alone.
    return shades(np.asarray(Image.open(path).convert("L")))


def find_on(screen: np.ndarray, image: np.ndarray) -> tuple[int, int] | None:
    """Where the image is, pixel for pixel, on the screen: (top, left)."""
    height, width = image.shape
    # Only places where the image's darkest pixel matches are worth a full
    # comparison; on a mostly white screen that rules out nearly all of them.
    dark_row, dark_column = np.unravel_index(image.argmax(), image.shape)
    rows, columns = screen.shape[0] - height + 1, screen.shape[1] - width + 1
    candidates = screen[dark_row:dark_row + rows, dark_column:dark_column + columns] == image.max()
    for top, left in np.argwhere(candidates):
        if np.array_equal(screen[top:top + height, left:left + width], image):
            return int(top), int(left)
    return None


def falling_notes_in(strip: np.ndarray, note: np.ndarray) -> list[int]:
    """How far down each falling note is, in the strip of screen under them.

    A falling note is a sprite, and the white parts of a sprite are
    see-through, so only its other pixels are compared. That finds it over
    any background, including when it sits on the marker.
    """
    solid = note > 0
    # Every note-sized window down the strip, compared in one go.
    windows = np.lib.stride_tricks.sliding_window_view(strip, note.shape)[:, 0]
    matches = (windows[:, solid] == note[solid]).all(axis=1)
    return [int(top) for top in np.flatnonzero(matches)]


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


def note_starts(per_frame: list[str | None], loudness: list[int]) -> list[int]:
    """The frames in which a new note begins.

    A note begins when the pitch changes, when sound follows silence, or
    when the same pitch suddenly gets louder again.
    """
    starts = []
    for frame in range(SOUND_SETTLE_FRAMES, len(per_frame)):
        note, before = per_frame[frame], per_frame[frame - 1]
        if note is None:
            continue
        louder = loudness[frame] - loudness[frame - 1] >= LOUDNESS_JUMP
        if note != before or louder:
            # A pitch that changes for a single frame is a click, not a note.
            if frame + 1 < len(per_frame) and per_frame[frame + 1] == note:
                starts.append(frame)
    return starts


def main() -> int:
    if len(sys.argv) < 5 or not all("=" in arg for arg in sys.argv[4:]):
        print(__doc__)
        return 2

    rom = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    falling_path = Path(sys.argv[3])
    # The marker image for each pitch, in the order given: left to right.
    marker_paths = {pitch: Path(path) for pitch, path in (arg.split("=", 1) for arg in sys.argv[4:])}
    screenshot_path = output_dir / "screenshot-play.png"

    for path, what in [(rom, "ROM"), (falling_path, "image file")] + [
        (path, "image file") for path in marker_paths.values()
    ]:
        if not path.is_file():
            print(f"FAIL: {what} not found: {path}")
            return 1

    falling = load_shades(falling_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # window="null" runs the emulator with no display at all. Sound is still
    # worked out, though nothing is played: after each frame the emulator
    # holds that frame's sound as a list of numbers, all zero when silent.
    pyboy = PyBoy(str(rom), window="null", sound_emulated=True)
    frames: list[np.ndarray] = []      # the screen in shades, one per frame
    per_frame: list[str | None] = []   # the note sounding, one per frame
    loudness: list[int] = []           # the loudest sample, one per frame
    try:
        for frame in range(RUN_FRAMES):
            pyboy.tick()
            # The screen is grey, so one colour channel is its brightness.
            frames.append(shades(np.asarray(pyboy.screen.ndarray)[:, :, 0]))
            # Both speakers carry the same sound here; the left is enough.
            samples = np.asarray(pyboy.sound.ndarray)[:, 0].astype(int)
            per_frame.append(note_in(samples, pyboy.sound.sample_rate))
            loudness.append(int(samples.max()))
            if frame == SCREENSHOT_FRAME:
                pyboy.screen.image.convert("RGB").save(screenshot_path)
    finally:
        pyboy.stop(save=False)

    shown = frames[SCREENSHOT_FRAME]
    if shown.min() == shown.max():
        print(f"FAIL: screen is one flat colour; see {screenshot_path}")
        return 1

    # The markers are looked for in the first two seconds, before any note
    # has reached them; the ROM takes a moment to draw its screen.
    places: dict[str, tuple[int, int]] = {}
    for pitch, path in marker_paths.items():
        marker = load_shades(path)
        for screen in frames[:MARKER_SEARCH_FRAMES:5]:
            place = find_on(screen, marker)
            if place is not None:
                places[pitch] = place
                break
        else:
            print(f"FAIL: {path} was not found on screen; see {screenshot_path}")
            return 1
    target_top = next(iter(places.values()))[0]
    if any(top != target_top for top, _ in places.values()):
        print(f"FAIL: the markers are not in one row; see {screenshot_path}")
        return 1

    notes = notes_heard(per_frame[SOUND_SETTLE_FRAMES:])
    if not notes:
        print(f"FAIL: no sound was produced between frames {SOUND_SETTLE_FRAMES} and {RUN_FRAMES}")
        return 1
    if len(set(notes)) < MIN_DIFFERENT_NOTES:
        print(
            f"FAIL: the sound did not change note enough to be music; heard only {' '.join(notes)}, "
            f"and a tune needs at least {MIN_DIFFERENT_NOTES} different notes"
        )
        return 1

    # Follow the falling notes: for each lane, in every frame, how far down
    # each note is in the column of screen above that lane's marker.
    width = falling.shape[1]
    lanes = {
        pitch: [falling_notes_in(screen[:, left:left + width], falling) for screen in frames]
        for pitch, (_, left) in places.items()
    }

    # Steady motion: a note seen in one frame is the same distance further
    # down in the next. If the game ever fell behind and skipped a frame,
    # a note would stand still and then jump.
    moving = sorted(
        (frame, top, pitch)
        for pitch, positions in lanes.items()
        for frame, tops in enumerate(positions)
        for top in tops
        if top < target_top
    )
    if not moving:
        print(f"FAIL: no falling notes were seen above the markers; see {screenshot_path}")
        return 1
    first_frame, first_top, first_pitch = moving[0]
    later = [top for top in lanes[first_pitch][first_frame + 1] if top > first_top]
    step = min(later) - first_top if later else 0
    for frame, top, pitch in moving:
        if frame + 1 < RUN_FRAMES and top + step <= target_top and top + step not in lanes[pitch][frame + 1]:
            print(
                f"FAIL: the frame rate did not hold: a note at {top} pixels down in frame {frame} "
                f"was not {step} pixels further down in the next frame"
            )
            return 1

    # Timing and lane: each note should be on a marker in the frame its
    # sound starts, and on the marker for its pitch. The last few frames are
    # left out so a note cut off by the end of the run is not counted on one
    # side only.
    last = RUN_FRAMES - 2 * MAX_GAP_FRAMES
    landings = sorted(
        (frame, pitch)
        for pitch, positions in lanes.items()
        for frame, tops in enumerate(positions)
        if target_top in tops and frame < last
    )
    starts = [f for f in note_starts(per_frame, loudness) if f < last]
    if len(landings) != len(starts):
        print(
            f"FAIL: {len(landings)} notes landed on a marker but {len(starts)} notes were heard; "
            f"every note of the tune should have one falling note"
        )
        return 1
    worst = 0
    for number, ((landing, lane), start) in enumerate(zip(landings, starts), 1):
        heard = per_frame[start]
        # "F#4" is the pitch F# in octave 4; the lane depends on the pitch.
        pitch = heard.rstrip("0123456789")
        gap = landing - start
        if abs(gap) > MAX_GAP_FRAMES:
            print(
                f"FAIL: note {number} ({heard}) landed {abs(gap)} frames {'after' if gap > 0 else 'before'} "
                f"its sound started (frame {landing} against {start}); the most allowed is {MAX_GAP_FRAMES}"
            )
            return 1
        if pitch not in marker_paths:
            print(f"FAIL: note {number} is {heard}, and no marker was given for the pitch {pitch}")
            return 1
        if lane != pitch:
            print(
                f"FAIL: note {number} ({heard}) landed on {marker_paths[lane]}, "
                f"but its pitch {pitch} belongs on {marker_paths[pitch]}"
            )
            return 1
        worst = max(worst, abs(gap))

    print(
        f"PASS: {len(landings)} notes fell and {len(starts)} were heard, each on the marker for its pitch "
        f"within {worst} frame(s) of its sound, moving {step} pixels a frame; "
        f"notes heard: {' '.join(notes)}; see {screenshot_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
