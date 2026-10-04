---
title: 'The ROM plays the opening of Amazing Grace'
type: 'feature'
ticket: '2'
created: '2026-10-04'
status: done
baseline_revision: '8774397853cc6fe2df8fdff90e68ce27977fcac2'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-music-proof/spec-music-proof.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The proof ROM plays a made-up run of notes, and the headless check only knows that there is sound. Neither shows that a real tune can be written by hand as a song file, or that the check would notice the music going wrong.

**Approach:** Replace the notes with the opening phrase of "Amazing Grace", written by hand in the C song file, and extend the headless check to work out which notes it hears and fail when they do not change over time. The user listens once in Emulicious to confirm the tune is recognisable.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 80 changed lines across `src/song.c`, `scripts/check_rom.py` and `docs/setup.md`.

No commit was made: the user commits their own work.

- `src/song.c`: the melody pattern is now "Amazing grace, how sweet the sound" in G major, D G B G B A G E D, with a quarter note as four rows, followed by a four-beat rest. Tempo 10, which is 90 beats a minute. The instrument now fades slowly so each note has a start. It was written as text; no tracker was used.
- The driver names octaves one higher than usual: its `D_5` sounds as D4. Found by measuring the pitch of story 2.1's notes, and recorded in the song file's comments.
- `scripts/check_rom.py` now runs the ROM for 600 frames in all, names the note sounding in each frame from the rate at which the tone switches on, reduces that to the notes played in order, and fails unless at least three different notes were heard. The pass message lists the notes. Story 2.1's count of frames with sound is replaced by this.
- Decision: the check does not compare against the expected tune. The ticket asks that the notes change over time; a copy of the melody in the check would have to be edited whenever the song is. The notes are printed so a reader or agent can compare them.
- The check takes about one second, up from 0.7.
- Limits of the note detection, not needed here: it reads one plain tone. Two channels sounding together, the noise channel, or notes below about 180 Hz would not be named reliably. The game's own spec should revisit this when songs use more than one channel.

Verified by running each case, restoring the source after each edit:

- `make check` with `DISPLAY` and `WAYLAND_DISPLAY` unset: PASS, `notes heard: D4 G4 B4 G4 B4 A4 G4 E4 D4`, which is the phrase as written. Measured note lengths were 40, 80, 20, 20, 80, 40, 80, 40 and 80 frames, matching the rows.
- Song reduced to one held note: `FAIL: the sound did not change note enough to be music; heard only G4`.
- Song reduced to two notes: same failure, `heard only D4 G4 D4`.
- Music start-up removed: `FAIL: no sound was produced`.
- A ROM ignoring A still fails on the button. ROM size 32768 bytes. `make debug` exits 0.
- Outstanding: the user listening in Emulicious and recognising the tune. This is the story's human step and has not happened yet.
- 2026-10-04, later: the user replied "approved". The reply does not say in so many words that they listened and recognised the tune; they have been asked.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. No findings beyond the detection limits recorded above, which do not affect this song.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS with `notes heard: D4 G4 B4 G4 B4 A4 G4 E4 D4`
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less

**Manual checks (if no CLI):**
- User: `make run`, listen, and recognise the opening of "Amazing Grace".
