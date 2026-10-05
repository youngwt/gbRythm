"""Listening to the Game Boy: naming the notes in the sound it makes.

The emulator gives each frame's sound as a list of numbers, all zero when
silent. These functions turn that into note names and the frames in which
notes start.
"""

import math

import numpy as np

# A note counts once it has lasted this many frames in a row; shorter runs
# are the clicks between notes.
MIN_NOTE_FRAMES = 5
# The same pitch played twice in a row still starts a new note. Each note
# starts at full loudness, 15, and only ever fades, so any rise in loudness
# marks the second one. A rise of 2 is asked for, to ignore a wobble of 1;
# two notes a third of a second apart differ by 3.
LOUDNESS_JUMP = 2

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


def note_starts(per_frame: list[str | None], loudness: list[int], first_frame: int) -> list[int]:
    """The frames, from first_frame on, in which a new note begins.

    A note begins when the pitch changes, when sound follows silence, or
    when the same pitch suddenly gets louder again.
    """
    starts = []
    for frame in range(first_frame, len(per_frame)):
        note, before = per_frame[frame], per_frame[frame - 1]
        if note is None:
            continue
        louder = loudness[frame] - loudness[frame - 1] >= LOUDNESS_JUMP
        if note != before or louder:
            # A pitch that changes for a single frame is a click, not a note.
            if frame + 1 < len(per_frame) and per_frame[frame + 1] == note:
                starts.append(frame)
    return starts
