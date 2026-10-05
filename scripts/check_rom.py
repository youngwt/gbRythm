"""Run the Game Boy ROM with no window and check the game plays as designed.

Usage: check_rom.py ROM OUTPUT_DIR --falling IMAGE --lane PITCH=BUTTON=IMAGE...
                    --perfect IMAGE --good IMAGE --miss IMAGE --digits IMAGE

The check finds the game's images on the screen, so it needs no copy of
where they are drawn, and it reads the music from the sound, so it needs no
copy of the tune. What it is told is the game's design, which it exists to
hold the ROM to: which pitch belongs to which button and marker (--lane),
and how close a press must be to count (PERFECT_FRAMES and GOOD_FRAMES
below).

It first plays the song with no presses and checks that the notes fall in
time, in the right lanes and steadily. It then plays it again several times
with scripted button presses, reading the three counts off the screen.

Saves screenshot-play.png to OUTPUT_DIR: the screen part-way through the
song. Exits non-zero, saying why, when anything is not as designed.
"""

import argparse
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
# How long the markers and words are looked for at the start.
IMAGE_SEARCH_FRAMES = 120
# The game reads the buttons a little after the emulator is told of a press,
# so a scripted press is sent this many frames before it should count.
PRESS_FRAME_OFFSET = 0
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

# The game's timing windows, in frames either side of a note landing: a
# press this close is a perfect, or a good. The same two numbers are in
# src/game.c; change both together.
PERFECT_FRAMES = 3
GOOD_FRAMES = 7

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


def read_count(screen: np.ndarray, place: tuple[int, int], word_width: int, digits: np.ndarray) -> int | None:
    """Read the two-digit count drawn straight after a word on the screen."""
    top, left = place
    number = 0
    for position in range(2):
        x = left + word_width + 8 * position
        cell = screen[top:top + 8, x:x + 8]
        for digit in range(10):
            if np.array_equal(cell, digits[:, 8 * digit:8 * digit + 8]):
                number = number * 10 + digit
                break
        else:
            return None
    return number


def play(rom: Path, presses: dict[int, list[str]], last_frame: int, held: list[str] = ()) -> np.ndarray:
    """Play the ROM with scripted presses and return the screen at last_frame.

    presses says which buttons to tap before which frame. Buttons in held
    are pressed at the start and never let go.
    """
    pyboy = PyBoy(str(rom), window="null", sound_emulated=False)
    try:
        for button in held:
            pyboy.button_press(button)
        for frame in range(last_frame + 1):
            for button in presses.get(frame, []):
                pyboy.button(button)  # down for one frame, then released
            pyboy.tick(1, frame == last_frame)  # only the last frame is drawn
        return shades(np.asarray(pyboy.screen.ndarray)[:, :, 0])
    finally:
        pyboy.stop(save=False)


def main() -> int:
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("rom", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--falling", type=Path, required=True)
    parser.add_argument("--lane", action="append", required=True, metavar="PITCH=BUTTON=IMAGE")
    parser.add_argument("--perfect", type=Path, required=True)
    parser.add_argument("--good", type=Path, required=True)
    parser.add_argument("--miss", type=Path, required=True)
    parser.add_argument("--digits", type=Path, required=True)
    args = parser.parse_args()

    rom = args.rom
    falling_path = args.falling
    # For each pitch, in lane order: its button and its marker image.
    buttons: dict[str, str] = {}
    marker_paths: dict[str, Path] = {}
    for lane in args.lane:
        pitch, button, image = lane.split("=", 2)
        buttons[pitch] = button
        marker_paths[pitch] = Path(image)
    word_paths = {"perfect": args.perfect, "good": args.good, "miss": args.miss}
    screenshot_path = args.output_dir / "screenshot-play.png"

    for path in [rom, falling_path, args.digits, *marker_paths.values(), *word_paths.values()]:
        if not path.is_file():
            print(f"FAIL: file not found: {path}")
            return 1

    falling = load_shades(falling_path)
    digits = load_shades(args.digits)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # ---- First play: no presses. Are the notes in time, in lane, steady? ----

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

    # The markers and the count words are looked for in the first two
    # seconds, before any note has been judged; the ROM takes a moment to
    # draw its screen.
    def find_early(path: Path) -> tuple[int, int] | None:
        image = load_shades(path)
        for screen in frames[:IMAGE_SEARCH_FRAMES:5]:
            place = find_on(screen, image)
            if place is not None:
                return place
        print(f"FAIL: {path} was not found on screen; see {screenshot_path}")
        return None

    places: dict[str, tuple[int, int]] = {}
    for pitch, path in marker_paths.items():
        place = find_early(path)
        if place is None:
            return 1
        places[pitch] = place
    word_places: dict[str, tuple[int, int]] = {}
    for word, path in word_paths.items():
        place = find_early(path)
        if place is None:
            return 1
        word_places[word] = place
    word_width = load_shades(args.perfect).shape[1]

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

    # ---- Further plays: scripted presses. Are they judged as designed? ----

    # The song repeats for ever, so the counts are read at a quiet moment:
    # the middle of the longest gap between notes, when every earlier note
    # has been judged and the next is not yet near.
    gaps = [later - earlier for (earlier, _), (later, _) in zip(landings, landings[1:])]
    widest = max(range(len(gaps)), key=gaps.__getitem__)
    read_frame = landings[widest][0] + gaps[widest] // 2
    judged = landings[:widest + 1]
    total = len(judged)
    pitches = list(buttons)

    def taps(frames_late: int) -> dict[int, list[str]]:
        """Press each note's own button this many frames after it lands."""
        schedule: dict[int, list[str]] = {}
        for landing, pitch in judged:
            schedule.setdefault(landing + frames_late + PRESS_FRAME_OFFSET, []).append(buttons[pitch])
        return schedule

    # Stray presses: as each note lands, the next lane's button; and the
    # note's own button well after it has gone and before the next arrives.
    stray: dict[int, list[str]] = {}
    for landing, pitch in judged:
        wrong = buttons[pitches[(pitches.index(pitch) + 1) % len(pitches)]]
        stray.setdefault(landing + PRESS_FRAME_OFFSET, []).append(wrong)
        stray.setdefault(landing + GOOD_FRAMES + 3 + PRESS_FRAME_OFFSET, []).append(buttons[pitch])

    all_miss = {"perfect": 0, "good": 0, "miss": total}
    all_good = {"perfect": 0, "good": total, "miss": 0}
    all_perfect = {"perfect": total, "good": 0, "miss": 0}
    scenarios = [
        ("no presses", {}, (), all_miss),
        ("presses on time", taps(0), (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames late", taps(PERFECT_FRAMES), (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames early", taps(-PERFECT_FRAMES), (), all_perfect),
        (f"presses {PERFECT_FRAMES + 1} frames late", taps(PERFECT_FRAMES + 1), (), all_good),
        (f"presses {GOOD_FRAMES} frames late", taps(GOOD_FRAMES), (), all_good),
        (f"presses {GOOD_FRAMES} frames early", taps(-GOOD_FRAMES), (), all_good),
        (f"presses {GOOD_FRAMES + 1} frames late", taps(GOOD_FRAMES + 1), (), all_miss),
        ("stray presses", stray, (), all_miss),
        ("every button held down", {}, tuple(buttons.values()), all_miss),
    ]
    for name, presses, held, expected in scenarios:
        screen = play(rom, presses, read_frame, held)
        counts = {word: read_count(screen, word_places[word], word_width, digits) for word in word_places}
        if None in counts.values():
            print(f"FAIL: with {name}, a count on the screen could not be read")
            return 1
        if counts != expected:
            print(
                f"FAIL: with {name}, the first {total} notes should score "
                + ", ".join(f"{expected[word]} {word}" for word in expected)
                + " but the screen shows "
                + ", ".join(f"{counts[word]} {word}" for word in counts)
            )
            return 1

    # When the song starts again the score should too. In the first play,
    # just before the first note of the second time through lands, every
    # note of the first time has been counted and then the counts cleared.
    if widest + 1 < len(landings):
        screen = frames[landings[widest + 1][0] - 2]
        counts = {word: read_count(screen, word_places[word], word_width, digits) for word in word_places}
        if any(count != 0 for count in counts.values()):
            print(
                "FAIL: the counts should go back to zero when the song starts again, but the screen shows "
                + ", ".join(f"{counts[word]} {word}" for word in counts)
            )
            return 1

    print(
        f"PASS: {len(landings)} notes fell and {len(starts)} were heard, each on the marker for its pitch "
        f"within {worst} frame(s) of its sound, moving {step} pixels a frame; "
        f"{len(scenarios)} ways of pressing were judged as designed over the first {total} notes, "
        f"and the counts went back to zero when the song started again; "
        f"notes heard: {' '.join(notes)}; see {screenshot_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
