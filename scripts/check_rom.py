"""Run the Game Boy ROM with no window and check the game plays as designed.

Usage: check_rom.py ROM OUTPUT_DIR --falling IMAGE --lane PITCH=BUTTON=IMAGE...
                    --perfect IMAGE --good IMAGE --miss IMAGE --digits IMAGE
                    --start IMAGE --results IMAGE

The check finds the game's images on the screen, so it needs no copy of
where they are drawn, and it reads the music from the sound, so it needs no
copy of the tune. What it is told is the game's design, which it exists to
hold the ROM to: which pitch belongs to which button and marker (--lane),
and how close a press must be to count (PERFECT_FRAMES and GOOD_FRAMES
below).

It first presses Start and lets the song play twice with no other presses,
checking that nothing happens before Start, that the notes fall in time, in
the right lanes and steadily, that the song ends in silence with the
results, and that Start plays it again from zero. It then plays the song
several more times with scripted button presses, reading the three counts
off the results.

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

# The Game Boy draws about 60 frames a second; the emulator runs them much
# faster than that.
# When Start is first pressed: a second and a half in, after a wait long
# enough to show that nothing happens without it.
START_FRAME = 90
# How long the results are left on screen before Start is pressed again: ten
# seconds, to show the music stays stopped.
RESULTS_FRAMES = 600
# The longest a play of the song may take before the check gives up on it
# ending: two minutes.
MAX_PLAY_FRAMES = 7200
# When to save the screenshot: five seconds in, with notes on their way down.
SCREENSHOT_FRAME = 300
# How long the markers and words are looked for at the start: up to the
# first press of Start. The ROM takes a moment to draw its screen.
IMAGE_SEARCH_FRAMES = START_FRAME
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


def shows(screen: np.ndarray, image: np.ndarray, place: tuple[int, int]) -> bool:
    """Whether the image is on the screen at the place given."""
    top, left = place
    return np.array_equal(screen[top:top + image.shape[0], left:left + image.shape[1]], image)


def play(rom: Path, presses: dict[int, list[str]], last_frame: int, held: list[str] = ()) -> np.ndarray:
    """Play the ROM with scripted presses and return the screen at last_frame.

    presses says which buttons to tap before which frame, Start included.
    Buttons in held are pressed at the start and never let go.
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
    parser.add_argument("--start", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
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

    for path in [rom, falling_path, args.digits, args.start, args.results, *marker_paths.values(), *word_paths.values()]:
        if not path.is_file():
            print(f"FAIL: file not found: {path}")
            return 1

    falling = load_shades(falling_path)
    digits = load_shades(args.digits)
    prompt = load_shades(args.start)
    heading = load_shades(args.results)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # ---- First run: Start, the song, the results, Start, the song again. ----

    # window="null" runs the emulator with no display at all. Sound is still
    # worked out, though nothing is played: after each frame the emulator
    # holds that frame's sound as a list of numbers, all zero when silent.
    pyboy = PyBoy(str(rom), window="null", sound_emulated=True)
    frames: list[np.ndarray] = []      # the screen in shades, one per frame
    per_frame: list[str | None] = []   # the note sounding, one per frame
    loudness: list[int] = []           # the loudest sample, one per frame
    start_frames = [START_FRAME]       # the frames Start is pressed before
    results_seen: list[int] = []       # roughly when each results heading appeared
    heading_place = None
    try:
        frame = 0
        while True:
            if frame == start_frames[-1]:
                pyboy.button("start")
            pyboy.tick()
            screen = shades(np.asarray(pyboy.screen.ndarray)[:, :, 0])
            frames.append(screen)
            # Both speakers carry the same sound here; the left is enough.
            samples = np.asarray(pyboy.sound.ndarray)[:, 0].astype(int)
            per_frame.append(note_in(samples, pyboy.sound.sample_rate))
            loudness.append(int(samples.max()))
            if frame == SCREENSHOT_FRAME:
                pyboy.screen.image.convert("RGB").save(screenshot_path)

            # Every few frames of a play, look for the results heading: that
            # is how the check knows the song has ended.
            playing = len(results_seen) < len(start_frames) and frame > start_frames[-1]
            if playing and frame % 10 == 0:
                place = find_on(screen, heading)
                if place is not None:
                    heading_place = place
                    results_seen.append(frame)
                    if len(results_seen) == 1:
                        start_frames.append(frame + RESULTS_FRAMES)
            if playing and frame - start_frames[-1] > MAX_PLAY_FRAMES:
                print(
                    f"FAIL: {args.results} did not appear within {MAX_PLAY_FRAMES} frames of Start being "
                    f"pressed; the song should end and show its results; see {screenshot_path}"
                )
                return 1
            # Stop a second after the second results appear.
            if len(results_seen) == 2 and frame > results_seen[1] + 60:
                break
            frame += 1
    finally:
        pyboy.stop(save=False)
    run_frames = len(frames)
    again_frame = start_frames[1]
    # The exact frame each results heading appeared.
    results_frames = [
        next(f for f in range(seen - 10, seen + 1) if shows(frames[f], heading, heading_place))
        for seen in results_seen
    ]

    shown = frames[SCREENSHOT_FRAME]
    if shown.min() == shown.max():
        print(f"FAIL: screen is one flat colour; see {screenshot_path}")
        return 1

    # The markers, the count words and the prompt are looked for before
    # Start is pressed.
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
    prompt_place = find_early(args.start)
    if prompt_place is None:
        return 1

    def counts_on(screen: np.ndarray) -> dict[str, int | None]:
        return {word: read_count(screen, word_places[word], word_width, digits) for word in word_places}

    target_top = next(iter(places.values()))[0]
    if any(top != target_top for top, _ in places.values()):
        print(f"FAIL: the markers are not in one row; see {screenshot_path}")
        return 1

    notes = notes_heard(per_frame[SOUND_SETTLE_FRAMES:])
    if not notes:
        print(f"FAIL: no sound was produced between frames {SOUND_SETTLE_FRAMES} and {run_frames}")
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
        if frame + 1 < run_frames and top + step <= target_top and top + step not in lanes[pitch][frame + 1]:
            print(
                f"FAIL: the frame rate did not hold: a note at {top} pixels down in frame {frame} "
                f"was not {step} pixels further down in the next frame"
            )
            return 1

    # Timing and lane: each note should be on a marker in the frame its
    # sound starts, and on the marker for its pitch.
    landings = sorted(
        (frame, pitch)
        for pitch, positions in lanes.items()
        for frame, tops in enumerate(positions)
        if target_top in tops
    )
    starts = note_starts(per_frame, loudness)
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

    # ---- Start, the ending and playing again, from the same run. ----

    # Before Start: the prompt is showing, nothing falls and nothing plays.
    if not all(shows(frames[f], prompt, prompt_place) for f in range(IMAGE_SEARCH_FRAMES - 10, START_FRAME)):
        print(f"FAIL: {args.start} should be on screen until Start is pressed; see {screenshot_path}")
        return 1
    if landings[0][0] < START_FRAME or any(frame < START_FRAME for frame, _, _ in moving):
        print("FAIL: a note fell before Start was pressed")
        return 1
    if any(note is not None for note in per_frame[SOUND_SETTLE_FRAMES:START_FRAME]):
        print("FAIL: music played before Start was pressed")
        return 1

    # Each play has the same notes; the first play's are the song.
    first = [(frame, pitch) for frame, pitch in landings if frame < results_frames[0]]
    second = [(frame, pitch) for frame, pitch in landings if frame > again_frame]
    total = len(first)
    if [pitch for _, pitch in first] != [pitch for _, pitch in second] or len(first) + len(second) != len(landings):
        print(
            f"FAIL: {total} notes fell in the first play and {len(second)} in the second, "
            f"out of {len(landings)} in all; every play should have the same notes"
        )
        return 1

    # During a play the prompt and heading are gone.
    for begun in start_frames:
        screen = frames[begun + 30]
        if shows(screen, prompt, prompt_place) or shows(screen, heading, heading_place):
            print(f"FAIL: the prompt or the results heading was still on screen after Start; see {screenshot_path}")
            return 1

    # The tune must not start again at the end, even for a frame. Once the
    # last note has died away, there should be no more sound.
    after_last = range(first[-1][0], results_frames[0])
    silent_from = next((f for f in after_last if loudness[f] == 0), None)
    if silent_from is not None and any(loudness[f] != 0 for f in range(silent_from, results_frames[0])):
        noisy = next(f for f in range(silent_from, results_frames[0]) if loudness[f] != 0)
        print(
            f"FAIL: sound came back in frame {noisy}, after the last note had died away; "
            f"the music should stop as the song ends, not start again"
        )
        return 1

    # After the song: the results stay, with the prompt, in silence.
    quiet = range(results_frames[0], again_frame)
    if any(per_frame[f] is not None or loudness[f] != 0 for f in quiet):
        noisy = next(f for f in quiet if per_frame[f] is not None or loudness[f] != 0)
        print(
            f"FAIL: there was sound in frame {noisy}, after the song ended in frame {results_frames[0]}; "
            f"the music should stop and stay stopped until Start is pressed"
        )
        return 1
    if any(tops for positions in lanes.values() for tops in positions[results_frames[0]:again_frame]):
        print("FAIL: a note was falling while the results were showing")
        return 1
    if not all(shows(frames[f], prompt, prompt_place) and shows(frames[f], heading, heading_place)
               for f in (results_frames[0] + 5, again_frame - 5)):
        print(f"FAIL: the results heading and the prompt should stay on screen until Start is pressed")
        return 1

    # The results, with no presses made: every note a miss, in both plays.
    all_miss = {"perfect": 0, "good": 0, "miss": total}
    for which, results_frame in zip(("first", "second"), results_frames):
        counts = counts_on(frames[results_frame + 5])
        if counts != all_miss:
            print(
                f"FAIL: the results of the {which} play, with no presses, should show 0 perfect, 0 good, "
                f"{total} miss but show " + ", ".join(f"{counts[word]} {word}" for word in counts)
            )
            return 1

    # Pressing Start again clears the score before the first note arrives.
    counts = counts_on(frames[again_frame + 30])
    if any(count != 0 for count in counts.values()):
        print(
            "FAIL: the counts should go back to zero when Start is pressed to play again, but the screen shows "
            + ", ".join(f"{counts[word]} {word}" for word in counts)
        )
        return 1

    # ---- Further plays: scripted presses. Are they judged as designed? ----

    # Each plays the song once and reads the counts off the results.
    judged = first
    read_frame = results_frames[0] + 5
    pitches = list(buttons)

    def taps(frames_late: int) -> dict[int, list[str]]:
        """Press Start, then each note's own button this many frames after it lands."""
        schedule: dict[int, list[str]] = {START_FRAME: ["start"]}
        for landing, pitch in judged:
            schedule.setdefault(landing + frames_late + PRESS_FRAME_OFFSET, []).append(buttons[pitch])
        return schedule

    # Stray presses: as each note lands, the next lane's button; and the
    # note's own button well after it has gone and before the next arrives.
    stray: dict[int, list[str]] = {START_FRAME: ["start"]}
    for landing, pitch in judged:
        wrong = buttons[pitches[(pitches.index(pitch) + 1) % len(pitches)]]
        stray.setdefault(landing + PRESS_FRAME_OFFSET, []).append(wrong)
        stray.setdefault(landing + GOOD_FRAMES + 3 + PRESS_FRAME_OFFSET, []).append(buttons[pitch])

    # Start pressed again in the middle of the song, between two notes.
    restart = taps(0)
    middle = len(judged) // 2
    restart.setdefault((judged[middle][0] + judged[middle + 1][0]) // 2, []).append("start")

    # Lane buttons pressed while waiting for Start and while the results are
    # showing; the counts are then read a little later than usual.
    idle: dict[int, list[str]] = {START_FRAME: ["start"]}
    for n, button in enumerate(buttons.values()):
        idle.setdefault(20 + 10 * n, []).append(button)
        idle.setdefault(read_frame + 10 + 10 * n, []).append(button)
    idle_read_frame = read_frame + 10 + 10 * len(buttons) + 10

    just_start = {START_FRAME: ["start"]}
    all_good = {"perfect": 0, "good": total, "miss": 0}
    all_perfect = {"perfect": total, "good": 0, "miss": 0}
    scenarios = [
        ("no presses", just_start, (), all_miss),
        ("presses on time", taps(0), (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames late", taps(PERFECT_FRAMES), (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames early", taps(-PERFECT_FRAMES), (), all_perfect),
        (f"presses {PERFECT_FRAMES + 1} frames late", taps(PERFECT_FRAMES + 1), (), all_good),
        (f"presses {GOOD_FRAMES} frames late", taps(GOOD_FRAMES), (), all_good),
        (f"presses {GOOD_FRAMES} frames early", taps(-GOOD_FRAMES), (), all_good),
        (f"presses {GOOD_FRAMES + 1} frames late", taps(GOOD_FRAMES + 1), (), all_miss),
        ("stray presses", stray, (), all_miss),
        ("every lane button held down", just_start, tuple(buttons.values()), all_miss),
        ("presses on time and Start pressed again mid-song", restart, (), all_perfect),
        ("lane buttons pressed only before Start and on the results", idle, (), all_miss),
    ]
    for name, presses, held, expected in scenarios:
        last_frame = idle_read_frame if presses is idle else read_frame
        screen = play(rom, presses, last_frame, held)
        if not shows(screen, heading, heading_place):
            print(f"FAIL: with {name}, the results were not showing by frame {last_frame}")
            return 1
        counts = counts_on(screen)
        if None in counts.values():
            print(f"FAIL: with {name}, a count on the screen could not be read")
            return 1
        if counts != expected:
            print(
                f"FAIL: with {name}, the {total} notes should score "
                + ", ".join(f"{expected[word]} {word}" for word in expected)
                + " but the screen shows "
                + ", ".join(f"{counts[word]} {word}" for word in counts)
            )
            return 1

    print(
        f"PASS: nothing happened before Start; {total} notes fell and were heard in each of two plays, "
        f"each on the marker for its pitch within {worst} frame(s) of its sound, moving {step} pixels a frame; "
        f"the song ended in silence with its results and Start played it again from zero; "
        f"{len(scenarios)} ways of pressing were judged as designed; "
        f"notes heard: {' '.join(notes_heard(per_frame[SOUND_SETTLE_FRAMES:results_frames[0]]))}; "
        f"see {screenshot_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
