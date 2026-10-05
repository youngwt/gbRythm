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

The work is in order below: record_run, find_layout, follow_notes,
check_notes, check_start_and_ending, check_presses. screen.py and sound.py
hold the helpers for reading the screen and the sound.
"""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from pyboy import PyBoy

from screen import falling_notes_in, find_on, load_shades, read_count, shades, shows
from sound import note_in, note_starts, notes_heard

# The Game Boy draws about 60 frames a second; the emulator runs them much
# faster than that.
# When Start is first pressed: a second and a half in, after a wait long
# enough to show that nothing happens without it. The ROM's screen is drawn
# well before this, so it is also how long the images are looked for.
START_FRAME = 90
# How long the results are left on screen before Start is pressed again: ten
# seconds, to show the music stays stopped.
RESULTS_FRAMES = 600
# The longest a play of the song may take before the check gives up on it
# ending: two minutes.
MAX_PLAY_FRAMES = 7200
# When to save the screenshot: five seconds in, with notes on their way down.
SCREENSHOT_FRAME = 300
# Sound in the first second is ignored. The ROM makes a short blip about
# half a second after starting even when it plays no music, so sound that
# early says nothing about the music.
SOUND_SETTLE_FRAMES = 60
# Music must use at least this many different notes: one held note is
# sound, but it is not a tune.
MIN_DIFFERENT_NOTES = 3
# A falling note should land on the marker in the frame its sound starts.
# This many frames either way, a thirtieth of a second, still counts.
MAX_GAP_FRAMES = 2
# The game's timing windows, in frames either side of a note landing: a
# press this close is a perfect, or a good. The same two numbers are in
# src/game.c; change both together.
PERFECT_FRAMES = 3
GOOD_FRAMES = 7

WORDS = ("perfect", "good", "miss")


class CheckFailed(Exception):
    """Something is not as designed. The message says what."""


@dataclass
class Design:
    """What the check is told: the ROM, the game's images, and the lanes."""

    rom: Path
    screenshot_path: Path
    falling: np.ndarray
    digits: np.ndarray
    prompt_path: Path
    heading_path: Path
    word_paths: dict[str, Path]
    # For each pitch, in lane order: its button and its marker image.
    buttons: dict[str, str]
    marker_paths: dict[str, Path]


@dataclass
class Run:
    """Everything recorded from the first run, frame by frame."""

    frames: list[np.ndarray]        # the screen in shades
    per_frame: list[str | None]     # the note sounding
    loudness: list[int]             # the loudest sample
    start_frames: list[int]         # the frames Start was pressed before
    results_frames: list[int]       # the frame each results heading appeared
    heading_place: tuple[int, int]


@dataclass
class Layout:
    """Where the game drew its images, found by looking."""

    markers: dict[str, tuple[int, int]]   # by pitch
    words: dict[str, tuple[int, int]]     # by judgement
    word_width: int
    prompt: tuple[int, int]
    target_top: int                       # how far down the row of markers is


@dataclass
class Notes:
    """The falling notes seen and the notes heard in the first run."""

    lanes: dict[str, list[list[int]]]     # by pitch, per frame: how far down each note is
    landings: list[tuple[int, str]]       # (frame, pitch of the marker landed on)
    starts: list[int]                     # the frame each note's sound started
    step: int                             # pixels a note moves each frame
    worst_gap: int


def read_design(arguments: list[str]) -> tuple[Design, Path]:
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
    args = parser.parse_args(arguments)

    buttons: dict[str, str] = {}
    marker_paths: dict[str, Path] = {}
    for lane in args.lane:
        pitch, button, image = lane.split("=", 2)
        buttons[pitch] = button
        marker_paths[pitch] = Path(image)
    word_paths = {"perfect": args.perfect, "good": args.good, "miss": args.miss}

    for path in [args.rom, args.falling, args.digits, args.start, args.results,
                 *marker_paths.values(), *word_paths.values()]:
        if not path.is_file():
            raise CheckFailed(f"file not found: {path}")

    design = Design(
        rom=args.rom,
        screenshot_path=args.output_dir / "screenshot-play.png",
        falling=load_shades(args.falling),
        digits=load_shades(args.digits),
        prompt_path=args.start,
        heading_path=args.results,
        word_paths=word_paths,
        buttons=buttons,
        marker_paths=marker_paths,
    )
    return design, args.output_dir


def record_run(design: Design) -> Run:
    """Press Start, let the song play, wait on the results, and do it again.

    Records the screen and the sound of every frame.
    """
    heading = load_shades(design.heading_path)
    # window="null" runs the emulator with no display at all. Sound is still
    # worked out, though nothing is played: after each frame the emulator
    # holds that frame's sound as a list of numbers, all zero when silent.
    pyboy = PyBoy(str(design.rom), window="null", sound_emulated=True)
    frames: list[np.ndarray] = []
    per_frame: list[str | None] = []
    loudness: list[int] = []
    start_frames = [START_FRAME]
    results_seen: list[int] = []       # roughly when each results heading appeared
    heading_place = None
    try:
        frame = 0
        while True:
            if frame == start_frames[-1]:
                pyboy.button("start")
            pyboy.tick()
            # The screen is grey, so one colour channel is its brightness.
            screen = shades(np.asarray(pyboy.screen.ndarray)[:, :, 0])
            frames.append(screen)
            # Both speakers carry the same sound here; the left is enough.
            samples = np.asarray(pyboy.sound.ndarray)[:, 0].astype(int)
            per_frame.append(note_in(samples, pyboy.sound.sample_rate))
            loudness.append(int(samples.max()))
            if frame == SCREENSHOT_FRAME:
                pyboy.screen.image.convert("RGB").save(design.screenshot_path)

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
                raise CheckFailed(
                    f"{design.heading_path} did not appear within {MAX_PLAY_FRAMES} frames of Start being "
                    f"pressed; the song should end and show its results; see {design.screenshot_path}"
                )
            # Stop a second after the second results appear.
            if len(results_seen) == 2 and frame > results_seen[1] + 60:
                break
            frame += 1
    finally:
        pyboy.stop(save=False)

    # The exact frame each results heading appeared.
    results_frames = [
        next(f for f in range(seen - 10, seen + 1) if shows(frames[f], heading, heading_place))
        for seen in results_seen
    ]
    return Run(frames, per_frame, loudness, start_frames, results_frames, heading_place)


def find_layout(design: Design, run: Run) -> Layout:
    """Find the markers, the count words and the prompt, before Start is pressed."""
    shown = run.frames[SCREENSHOT_FRAME]
    if shown.min() == shown.max():
        raise CheckFailed(f"screen is one flat colour; see {design.screenshot_path}")

    def find_early(path: Path) -> tuple[int, int]:
        image = load_shades(path)
        for screen in run.frames[:START_FRAME:5]:
            place = find_on(screen, image)
            if place is not None:
                return place
        raise CheckFailed(f"{path} was not found on screen; see {design.screenshot_path}")

    markers = {pitch: find_early(path) for pitch, path in design.marker_paths.items()}
    words = {word: find_early(path) for word, path in design.word_paths.items()}
    prompt = find_early(design.prompt_path)

    target_top = next(iter(markers.values()))[0]
    if any(top != target_top for top, _ in markers.values()):
        raise CheckFailed(f"the markers are not in one row; see {design.screenshot_path}")
    word_width = load_shades(design.word_paths["perfect"]).shape[1]
    return Layout(markers, words, word_width, prompt, target_top)


def counts_on(screen: np.ndarray, design: Design, layout: Layout) -> dict[str, int | None]:
    """Read the perfect, good and miss counts off a screen."""
    return {
        word: read_count(screen, layout.words[word], layout.word_width, design.digits)
        for word in WORDS
    }


def show_counts(counts: dict[str, int | None]) -> str:
    return ", ".join(f"{counts[word]} {word}" for word in WORDS)


def follow_notes(design: Design, run: Run, layout: Layout) -> Notes:
    """Work out where every falling note was in every frame, and when notes sounded."""
    # For each lane, in every frame, how far down each note is in the column
    # of screen above that lane's marker.
    width = design.falling.shape[1]
    lanes = {
        pitch: [falling_notes_in(screen[:, left:left + width], design.falling) for screen in run.frames]
        for pitch, (_, left) in layout.markers.items()
    }
    landings = sorted(
        (frame, pitch)
        for pitch, positions in lanes.items()
        for frame, tops in enumerate(positions)
        if layout.target_top in tops
    )
    starts = note_starts(run.per_frame, run.loudness, SOUND_SETTLE_FRAMES)
    return Notes(lanes, landings, starts, step=0, worst_gap=0)


def check_notes(design: Design, run: Run, layout: Layout, notes: Notes) -> None:
    """The notes are a tune, fall steadily, and land in time on the right markers."""
    run_frames = len(run.frames)
    heard = notes_heard(run.per_frame[SOUND_SETTLE_FRAMES:])
    if not heard:
        raise CheckFailed(f"no sound was produced between frames {SOUND_SETTLE_FRAMES} and {run_frames}")
    if len(set(heard)) < MIN_DIFFERENT_NOTES:
        raise CheckFailed(
            f"the sound did not change note enough to be music; heard only {' '.join(heard)}, "
            f"and a tune needs at least {MIN_DIFFERENT_NOTES} different notes"
        )

    # Steady motion: a note seen in one frame is the same distance further
    # down in the next. If the game ever fell behind and skipped a frame,
    # a note would stand still and then jump.
    moving = sorted(
        (frame, top, pitch)
        for pitch, positions in notes.lanes.items()
        for frame, tops in enumerate(positions)
        for top in tops
        if top < layout.target_top
    )
    if not moving:
        raise CheckFailed(f"no falling notes were seen above the markers; see {design.screenshot_path}")
    first_frame, first_top, first_pitch = moving[0]
    if first_frame < START_FRAME:
        raise CheckFailed("a note fell before Start was pressed")
    later = [top for top in notes.lanes[first_pitch][first_frame + 1] if top > first_top]
    notes.step = min(later) - first_top if later else 0
    for frame, top, pitch in moving:
        expected = top + notes.step
        if frame + 1 < run_frames and expected <= layout.target_top and expected not in notes.lanes[pitch][frame + 1]:
            raise CheckFailed(
                f"the frame rate did not hold: a note at {top} pixels down in frame {frame} "
                f"was not {notes.step} pixels further down in the next frame"
            )

    # Timing and lane: each note should be on a marker in the frame its
    # sound starts, and on the marker for its pitch.
    if len(notes.landings) != len(notes.starts):
        raise CheckFailed(
            f"{len(notes.landings)} notes landed on a marker but {len(notes.starts)} notes were heard; "
            f"every note of the tune should have one falling note"
        )
    for number, ((landing, lane), start) in enumerate(zip(notes.landings, notes.starts), 1):
        sounded = run.per_frame[start]
        # "F#4" is the pitch F# in octave 4; the lane depends on the pitch.
        pitch = sounded.rstrip("0123456789")
        gap = landing - start
        if abs(gap) > MAX_GAP_FRAMES:
            raise CheckFailed(
                f"note {number} ({sounded}) landed {abs(gap)} frames {'after' if gap > 0 else 'before'} "
                f"its sound started (frame {landing} against {start}); the most allowed is {MAX_GAP_FRAMES}"
            )
        if pitch not in design.marker_paths:
            raise CheckFailed(f"note {number} is {sounded}, and no marker was given for the pitch {pitch}")
        if lane != pitch:
            raise CheckFailed(
                f"note {number} ({sounded}) landed on {design.marker_paths[lane]}, "
                f"but its pitch {pitch} belongs on {design.marker_paths[pitch]}"
            )
        notes.worst_gap = max(notes.worst_gap, abs(gap))


def check_start_and_ending(design: Design, run: Run, layout: Layout, notes: Notes) -> list[tuple[int, str]]:
    """Nothing before Start; the song ends in silence with its results; Start plays again.

    Returns the first play's notes: the frame each landed and its pitch.
    """
    frames, per_frame, loudness = run.frames, run.per_frame, run.loudness
    prompt = load_shades(design.prompt_path)
    heading = load_shades(design.heading_path)
    first_results, second_results = run.results_frames
    again_frame = run.start_frames[1]

    # Before Start: the prompt is showing and nothing plays. (That nothing
    # falls is checked with the notes.)
    if not all(shows(frames[f], prompt, layout.prompt) for f in range(START_FRAME - 10, START_FRAME)):
        raise CheckFailed(f"{design.prompt_path} should be on screen until Start is pressed; see {design.screenshot_path}")
    if any(note is not None for note in per_frame[SOUND_SETTLE_FRAMES:START_FRAME]):
        raise CheckFailed("music played before Start was pressed")

    # Each play has the same notes; the first play's are the song.
    first = [(frame, pitch) for frame, pitch in notes.landings if frame < first_results]
    second = [(frame, pitch) for frame, pitch in notes.landings if frame > again_frame]
    total = len(first)
    same_notes = [pitch for _, pitch in first] == [pitch for _, pitch in second]
    if not same_notes or len(first) + len(second) != len(notes.landings):
        raise CheckFailed(
            f"{total} notes fell in the first play and {len(second)} in the second, "
            f"out of {len(notes.landings)} in all; every play should have the same notes"
        )

    # During a play the prompt and heading are gone.
    for begun in run.start_frames:
        screen = frames[begun + 30]
        if shows(screen, prompt, layout.prompt) or shows(screen, heading, run.heading_place):
            raise CheckFailed(
                f"the prompt or the results heading was still on screen after Start; see {design.screenshot_path}"
            )

    # The tune must not start again at the end, even for a frame. Once the
    # last note has died away, there should be no more sound.
    after_last = range(first[-1][0], first_results)
    silent_from = next((f for f in after_last if loudness[f] == 0), None)
    if silent_from is not None:
        noisy = next((f for f in range(silent_from, first_results) if loudness[f] != 0), None)
        if noisy is not None:
            raise CheckFailed(
                f"sound came back in frame {noisy}, after the last note had died away; "
                f"the music should stop as the song ends, not start again"
            )

    # After the song: the results stay, with the prompt, in silence.
    quiet = range(first_results, again_frame)
    noisy = next((f for f in quiet if per_frame[f] is not None or loudness[f] != 0), None)
    if noisy is not None:
        raise CheckFailed(
            f"there was sound in frame {noisy}, after the song ended in frame {first_results}; "
            f"the music should stop and stay stopped until Start is pressed"
        )
    if any(tops for positions in notes.lanes.values() for tops in positions[first_results:again_frame]):
        raise CheckFailed("a note was falling while the results were showing")
    if not all(shows(frames[f], prompt, layout.prompt) and shows(frames[f], heading, run.heading_place)
               for f in (first_results + 5, again_frame - 5)):
        raise CheckFailed("the results heading and the prompt should stay on screen until Start is pressed")

    # The results, with no presses made: every note a miss, in both plays.
    all_miss = {"perfect": 0, "good": 0, "miss": total}
    for which, results_frame in (("first", first_results), ("second", second_results)):
        counts = counts_on(frames[results_frame + 5], design, layout)
        if counts != all_miss:
            raise CheckFailed(
                f"the results of the {which} play, with no presses, should show 0 perfect, 0 good, "
                f"{total} miss but show {show_counts(counts)}"
            )

    # Pressing Start again clears the score before the first note arrives.
    counts = counts_on(frames[again_frame + 30], design, layout)
    if any(count != 0 for count in counts.values()):
        raise CheckFailed(
            "the counts should go back to zero when Start is pressed to play again, "
            f"but the screen shows {show_counts(counts)}"
        )
    return first


def play(rom: Path, presses: dict[int, list[str]], read_frames: list[int], held: tuple[str, ...] = ()) -> list[np.ndarray]:
    """Play the ROM with scripted presses and return the screen at each of read_frames.

    presses says which buttons to tap before which frame, Start included.
    Buttons in held are pressed at the start and never let go.
    """
    pyboy = PyBoy(str(rom), window="null", sound_emulated=False)
    screens = []
    try:
        for button in held:
            pyboy.button_press(button)
        for frame in range(max(read_frames) + 1):
            for button in presses.get(frame, []):
                pyboy.button(button)  # down for one frame, then released
            wanted = frame in read_frames
            pyboy.tick(1, wanted)  # only the frames that are read are drawn
            if wanted:
                screens.append(shades(np.asarray(pyboy.screen.ndarray)[:, :, 0]))
        return screens
    finally:
        pyboy.stop(save=False)


def check_presses(design: Design, run: Run, layout: Layout, notes: Notes, song: list[tuple[int, str]]) -> int:
    """Play the song with scripted presses and read the counts off the results.

    The first run gave each note's landing frame and lane; the emulator
    plays the same way every time, so presses can be timed against them.
    Returns how many ways of pressing were tried.
    """
    heading = load_shades(design.heading_path)
    buttons = design.buttons
    pitches = list(buttons)
    total = len(song)
    read_frame = run.results_frames[0] + 5
    just_start = {START_FRAME: ["start"]}

    def taps(frames_late: int, notes_to_press: list[tuple[int, str]] = song) -> dict[int, list[str]]:
        """Press Start, then each note's own button this many frames after it lands."""
        schedule: dict[int, list[str]] = {START_FRAME: ["start"]}
        for landing, pitch in notes_to_press:
            schedule.setdefault(landing + frames_late, []).append(buttons[pitch])
        return schedule

    # Stray presses: as each note lands, the next lane's button; and the
    # note's own button well after it has gone and before the next arrives.
    stray: dict[int, list[str]] = {START_FRAME: ["start"]}
    for landing, pitch in song:
        wrong = buttons[pitches[(pitches.index(pitch) + 1) % len(pitches)]]
        stray.setdefault(landing, []).append(wrong)
        stray.setdefault(landing + GOOD_FRAMES + 3, []).append(buttons[pitch])

    # Start pressed again in the middle of the song, between two notes.
    restart = taps(0)
    middle = total // 2
    restart.setdefault((song[middle][0] + song[middle + 1][0]) // 2, []).append("start")

    # Lane buttons pressed while waiting for Start and while the results are
    # showing; the counts are then read a little later than usual.
    idle: dict[int, list[str]] = {START_FRAME: ["start"]}
    for n, button in enumerate(buttons.values()):
        idle.setdefault(20 + 10 * n, []).append(button)
        idle.setdefault(read_frame + 10 + 10 * n, []).append(button)
    idle_read_frame = read_frame + 10 + 10 * len(buttons) + 10

    # Two plays with presses on time in both: Start again as the first run
    # did, and every note of both plays pressed.
    twice = taps(0, notes.landings)
    twice.setdefault(run.start_frames[1], []).append("start")
    both_reads = [read_frame, run.results_frames[1] + 5]

    all_miss = {"perfect": 0, "good": 0, "miss": total}
    all_good = {"perfect": 0, "good": total, "miss": 0}
    all_perfect = {"perfect": total, "good": 0, "miss": 0}
    # Each: its name, the presses, the frames to read the counts at, any
    # buttons held throughout, and what every reading should show.
    scenarios = [
        ("no presses", just_start, [read_frame], (), all_miss),
        ("presses on time", taps(0), [read_frame], (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames late", taps(PERFECT_FRAMES), [read_frame], (), all_perfect),
        (f"presses {PERFECT_FRAMES} frames early", taps(-PERFECT_FRAMES), [read_frame], (), all_perfect),
        (f"presses {PERFECT_FRAMES + 1} frames late", taps(PERFECT_FRAMES + 1), [read_frame], (), all_good),
        (f"presses {GOOD_FRAMES} frames late", taps(GOOD_FRAMES), [read_frame], (), all_good),
        (f"presses {GOOD_FRAMES} frames early", taps(-GOOD_FRAMES), [read_frame], (), all_good),
        (f"presses {GOOD_FRAMES + 1} frames late", taps(GOOD_FRAMES + 1), [read_frame], (), all_miss),
        ("stray presses", stray, [read_frame], (), all_miss),
        ("every lane button held down", just_start, [read_frame], tuple(buttons.values()), all_miss),
        ("presses on time and Start pressed again mid-song", restart, [read_frame], (), all_perfect),
        ("lane buttons pressed only before Start and on the results", idle, [idle_read_frame], (), all_miss),
        ("presses on time in two plays, one after the other", twice, both_reads, (), all_perfect),
    ]
    for name, presses, read_frames, held, expected in scenarios:
        for which, screen in enumerate(play(design.rom, presses, read_frames, held), 1):
            where = f"with {name}" + (f", play {which}" if len(read_frames) > 1 else "")
            if not shows(screen, heading, run.heading_place):
                raise CheckFailed(f"{where}, the results were not showing by frame {read_frames[which - 1]}")
            counts = counts_on(screen, design, layout)
            if None in counts.values():
                raise CheckFailed(f"{where}, a count on the screen could not be read")
            if counts != expected:
                raise CheckFailed(
                    f"{where}, the {total} notes should score {show_counts(expected)} "
                    f"but the screen shows {show_counts(counts)}"
                )
    return len(scenarios)


def main() -> int:
    try:
        design, output_dir = read_design(sys.argv[1:])
        output_dir.mkdir(parents=True, exist_ok=True)
        run = record_run(design)
        layout = find_layout(design, run)
        notes = follow_notes(design, run, layout)
        check_notes(design, run, layout, notes)
        song = check_start_and_ending(design, run, layout, notes)
        ways = check_presses(design, run, layout, notes, song)
    except CheckFailed as failure:
        print(f"FAIL: {failure}")
        return 1

    heard = notes_heard(run.per_frame[SOUND_SETTLE_FRAMES:run.results_frames[0]])
    print(
        f"PASS: nothing happened before Start; {len(song)} notes fell and were heard in each of two plays, "
        f"each on the marker for its pitch within {notes.worst_gap} frame(s) of its sound, "
        f"moving {notes.step} pixels a frame; "
        f"the song ended in silence with its results and Start played it again from zero; "
        f"{ways} ways of pressing were judged as designed; "
        f"notes heard: {' '.join(heard)}; see {design.screenshot_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
