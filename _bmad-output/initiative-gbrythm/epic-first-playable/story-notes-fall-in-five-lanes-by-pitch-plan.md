---
title: 'Notes fall in five lanes by pitch'
type: 'feature'
ticket: '2'
created: '2026-10-05'
status: done
baseline_revision: 'ff5a77970dffd79ddfab530f6a0aecd4e5e4151a'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/lane-mapping.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Every note falls down the same lane, so the screen says when to press but not which button. The game's design is five lanes, one per button, with a note's lane decided by its pitch.

**Approach:** Give the play screen five lanes in the order Left, Up, Right, B, A, each with its own marker showing its button, and drop each note in the lane `lane-mapping.md` gives for its pitch, in any octave. The headless check confirms every note lands in the right lane.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 100 changed lines across `src/game.c`, `scripts/check_rom.py`, `Makefile` and `docs/setup.md`, plus five small images.

No commit was made: the user commits their own work.

- `src/game.c`: five lanes at 32, 56, 80, 104 and 128 pixels across. `lane_of_pitch` has an entry for each of the twelve pitches in an octave; the pitch is found by taking whole octaves off the note number, with a loop, since division is avoided on this hardware. Each falling note remembers its lane's column.
- A pitch outside the five has no lane and nothing falls. The spec puts such songs out of scope; this makes the case fail loudly in the check as a note heard with nothing falling.
- `assets/target.png` is replaced by five marker images, `lane_1_left.png` to `lane_5_a.png`, generated with Pillow. The number in each name keeps them in lane order. Each has a grey line along the bottom, which also gives every image all four shades; see the deferred finding on shades from story 3.1.
- `scripts/check_rom.py` now takes `PITCH=MARKER_IMAGE` pairs, finds each marker, follows the falling notes above each one, and requires every note to land on the marker for the pitch it heard. The pairs are `LANE_MARKERS` in the `Makefile`.
- Decision: the lane design is stated twice, in `lane_of_pitch` and in `LANE_MARKERS`. This is the one deliberate exception to "no second copy": a check that read the mapping from the game could not catch the game getting it wrong. The tune itself is still read only from the sound.
- Finding the first marker on a blank start-up screen made the check take 13 seconds; it now starts from each image's darkest pixel and takes about 2.
- ROM use is 7,357 bytes of 32,768.

Verified by running each case, restoring the source after each deliberate break:

- As built, no display: PASS, 23 notes fell and 23 were heard, each on the marker for its pitch, every gap 0 frames. The high D landed on the D marker.
- E and G swapped in `lane_of_pitch`: `FAIL: note 2 (G4) landed on assets/lane_2_up.png, but its pitch G belongs on assets/lane_3_right.png`.
- The note A sent to lane 5: `FAIL: note 6 (A4) landed on assets/lane_5_a.png, but its pitch A belongs on assets/lane_4_b.png`.
- One E changed to F in the song: `FAIL: 22 notes landed on a marker but 23 notes were heard`.
- Music started 5 frames early: fails on the gap, as before.
- One marker not drawn: `FAIL: assets/lane_4_b.png was not found on screen`.
- Size 32768 bytes; `make debug` exits 0. The screenshot was opened: five markers in a row and a note falling in the A lane.
- Not done: `make run` and F5, which need a person at a window.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the check took 13 seconds after the change (see above).

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS with `each on the marker for its pitch`
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- swap two entries of `lane_of_pitch`, run `make check` -- expected: non-zero, naming the note and both markers; source restored afterwards
