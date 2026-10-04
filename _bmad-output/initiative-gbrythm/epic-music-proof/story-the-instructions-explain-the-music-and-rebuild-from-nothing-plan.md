---
title: 'The instructions explain the music and rebuild from nothing'
type: 'chore'
ticket: '3'
created: '2026-10-04'
status: done
baseline_revision: '335aee16f5eeb761a5ee7da5db203c39dd6eb8a8'
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

**Problem:** The instructions say how to install the music driver and what the check listens for, but not how Game Boy music works. A reader new to it cannot yet learn from them what the sound channels are or how the song file is laid out. And the driver's install step has only been run on a machine that already had every other tool.

**Approach:** Add a section to `docs/setup.md` that explains, from scratch, what a music driver is, what the four sound channels are, and how the song file is laid out and changed. Then delete `tools/` and `build/` and run every command in the instructions as written, in order, fixing every gap, until the headless check passes.

</frozen-after-approval>

## Implementation Notes

Oneshot route: a new section of about 40 lines in `docs/setup.md`, plus whatever the rebuild exposes.

No commit was made: the user commits their own work.

The explanation:

- `docs/setup.md` gains "How the music works": the four sound channels in a table, what the driver does and where `src/main.c` starts it, the song file's parts (pattern, order, instrument, tempo), how the melody's rows map to beats, the octave-naming trap, and how to change the tune and see the change in the check's output.
- Each claim about changing the tune was tried: `E_5` to `Fs5` changed the heard notes from `G4 E4 D4` to `G4 F#4 D4`, and halving the tempo number made the phrase play twice in the ten seconds. Source restored after each.
- `README.md` mentions the song and the new section.

Found and fixed while trying those:

- `scripts/check_rom.py` merged a note with the same note after a rest, so the phrase's last D and the repeat's first D were reported as one. It now treats the same note twice as one only when no real silence came between.

The rebuild:

- `tools/` (292 MB) and `build/` were deleted; `make` then failed with the pointer to `docs/setup.md`.
- Every `sh` block in `docs/setup.md` was extracted by a script and run in order, unedited, from the VS Code Flatpak terminal: 18 blocks. 17 exited 0, including the new hUGEDriver step and all four checksum checks. `make run` was skipped because it opens a window.
- `make check` passed with `notes heard: D4 G4 B4 G4 B4 A4 G4 E4 D4`. The ROM is 32768 bytes. `make debug` builds. `tools/` is back to 292 MB.
- No command needed fixing.
- The user's `tools/emulicious/Emulicious.ini` was copied out before the delete and put back.
- Not re-proven: `make run`, F5, and the VS Code extension's install from nothing (it was already installed).

After the build, the same day:

- The user listened in Emulicious and said "it sounded great". This is the human step story 2.2 was waiting on, and the epic's third Done when.
- The user then asked for the song to be "a little longer". `src/song.c` now holds the first half of the verse, adding "that saved a wretch like me": two patterns, with a pattern-break effect ending the second early. The check listens for 1080 frames (18 emulated seconds, about one real second) so it hears the song once through, and reports `D4 G4 B4 G4 B4 A4 G4 E4 D4 G4 B4 G4 B4 A4 D5`. `docs/setup.md` was updated to match. The ROM is still 32768 bytes.
- This goes past the spec's wording, "the opening phrase", and its non-goal about the full length. It is still not the full song. The spec has not been updated.
- Checked after the change: one held note still fails; the measured note lengths match the rows; the loop restarts where the pattern break says it should.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the check under-reported repeated notes across a rest (see above). It did not affect pass or fail for this song.

## Verification

**Commands:**
- `rm -rf tools build`, then every `sh` block of `docs/setup.md` in order except `make run` -- expected: each exits 0
- `make check` -- expected: exit 0, PASS with `notes heard: D4 G4 B4 G4 B4 A4 G4 E4 D4`
