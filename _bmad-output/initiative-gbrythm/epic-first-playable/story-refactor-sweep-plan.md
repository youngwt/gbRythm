---
title: 'Refactor sweep'
type: 'refactor'
ticket: '7'
created: '2026-10-05'
status: 'built'
baseline_revision: '6a919e3ed2d8d904d240097e4753ac67c0b615e1'
route: 'full'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Six stories each added to the same C file and the same check script. Both work, but they show their layers: the check's main routine is about 380 lines, the game's functions sit in the order they were written, and a few names and leftovers describe a ROM that no longer exists. Three small gaps found in review were also left for this sweep.

**Approach:** Tidy the check script, the game's C source and the files around them without changing how the game plays, and close the three review gaps. `make check` and `make check-debug` must pass before and after, with the same counts.

## Boundaries & Constraints

**Always:**
- The game plays the same: same notes, lanes, windows, timing, screens. Both checks pass with the same numbers as before the sweep.
- Every deliberate break that earlier stories proved the check catches is still caught.
- Each change is one of: moving code, renaming, removing something unused, correcting a comment or document, or one of the three named gaps.
- C rules in `stack.md`; ROM 32K or smaller; changes left uncommitted with a suggested commit message.

**Never:**
- No change to gameplay, the song, the images' look, the windows or the layout.
- No new features, and no work on the two deferred items that need a design decision: checking the music is not stopped early, and comparing PyBoy with another emulator.
- No splitting of `docs/setup.md`; the user decided to keep it as one file.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Unchanged play | `make check`, `make check-debug` | PASS with 35 notes in each of two plays and the same scenarios, plus the new one | No error expected |
| Breaks still caught | Six earlier breaks: lanes swapped, music early, a perfect window of 4, Start not clearing the score, the driver run once too often, a note dropped | Each fails with its earlier message | Source restored after each |
| Second play with presses (gap 1) | On-time presses in both of two plays | Both results read every note perfect | No error expected |
| Image missing a shade (gap 2) | A PNG with no white, or with only two shades | `make` fails, naming the image and the rule | Image removed afterwards |
| Cached files (gap 3) | `make check`, then `git status --short` | No Python cache folder listed | No error expected |

</frozen-after-approval>

## Code Map

- `scripts/check_rom.py` (604 lines) -- helpers for the screen (`shades`, `load_shades`, `find_on`, `falling_notes_in`, `read_count`, `shows`), for sound (`note_in`, `notes_heard`, `note_starts`), `play`, and a `main` of about 380 lines that does six jobs in sequence: record the run, find the images, check before Start, check the notes, check the ending and second play, run the press scenarios. `PRESS_FRAME_OFFSET` is 0 and adds nothing.
- `src/game.c` (557 lines) -- one file with every part of the game. `draw_count` and `reset_counts` were hoisted above the song reader when the reset was added, and `game_tick` needs a forward declaration because `game_catch_up` was added above it. The song is still called `proof_song`.
- `src/main.c` (15 lines), `src/game.h`, `src/song.h`, `src/song.c` -- small; only the song's name changes.
- `scripts/convert-images.sh` -- already fails on more than four shades by reading the palette count from the generated header; the generated `.c` lists the palette's colours, lightest first.
- `README.md` -- its command table lacks `make check-debug`. `Makefile` header lists the commands too.
- `.gitignore` -- no entry for Python's cache folder; importing a module from `scripts/` creates one.
- Deferred findings feeding this sweep: story 1 (an image with no white is shown with shifted shades), story 4 (the check's second play has no presses), and the music epic's retrospective F6 (decide the check script's shape when gameplay checks arrive).

## Tasks & Acceptance

**Execution:**
- [x] `scripts/screen.py`, `scripts/sound.py`, `scripts/check_rom.py` -- move the screen helpers and the sound helpers into their own files; break `main` into one function per job, each returning a failure message or what the next needs; remove `PRESS_FRAME_OFFSET`.
- [x] `scripts/check_rom.py` -- gap 1: a scenario with on-time presses in two plays, read at both results.
- [x] `src/game.c` -- reorder into sections that read top to bottom (settings, state, drawing, falling notes, reading the song, judging, the clock and music, starting and ending a play, the frame) with no forward declaration; rename `proof_song` to `song_verse` here and in `src/song.c`, `src/song.h`.
- [x] `scripts/convert-images.sh` -- gap 2: fail unless an image uses all four shades, with a message saying why. `docs/setup.md` -- state the rule in place of "include some white".
- [x] `.gitignore` -- gap 3: ignore `__pycache__/`.
- [x] `README.md`, `Makefile`, `docs/setup.md` -- add `make check-debug` where commands are listed; correct anything the moves made stale.
- [x] Verify the matrix; record the before and after numbers.

**Acceptance Criteria:**
- Given the sweep, when `make clean && make check && make check-debug` run, then both pass with 35 notes in each of two plays.
- Given each of the six earlier breaks, when applied and checked, then the check fails as it did before.
- Given `src/game.c`, when read top to bottom, then no function is used before it is defined and no forward declaration remains.
- Given `git status --short` after a check, then no cache folder and nothing under `tools/` or `build/` is listed.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits their own work.

Tidying:

- `scripts/screen.py` and `scripts/sound.py` are new and hold the helpers, moved unchanged apart from `note_starts` taking its first frame as an argument. `scripts/check_rom.py` keeps the check itself: `main` is now eight lines that call `record_run`, `find_layout`, `follow_notes`, `check_notes`, `check_start_and_ending` and `check_presses` in turn. A failure is raised as `CheckFailed` and printed in one place. What was recorded and found is passed between them in four small records. `PRESS_FRAME_OFFSET` is gone.
- `src/game.c` is reordered under seven headings, with the forward declaration removed and `game_frame` made private to the file. The song is `song_verse` in `src/game.c`, `src/song.c` and `src/song.h`. No statement inside any function changed.
- `README.md` lists `make check-debug`; `docs/setup.md` lists the two new script files.

The three gaps:

- Gap 1: the check has a thirteenth way of pressing, on time in two plays one after the other, read at both results. This is the case the user's turbo report showed was untested.
- Gap 2: `scripts/convert-images.sh` fails unless an image uses all four shades, saying how many it found. `docs/setup.md` states the rule. This resolves the deferred finding from story 1.
- Gap 3: `.gitignore` has `__pycache__/`.

Found along the way:

- The image converter crashes, with no message, on an 8 by 8 image with five colours. The build already stopped on its exit status but said nothing; it now says the converter failed and what to check.

Before and after:

- `make check` and `make check-debug` printed the same PASS line before and after the sweep, apart from "12 ways" becoming "13 ways": 35 notes in each of two plays, each within 1 frame, moving 2 pixels a frame, with the same notes heard.
- ROM use is 6,531 bytes before and after; the ROM is 32768 bytes. The ROM is not byte-identical, as expected from reordering.
- The six earlier breaks, each applied and then restored, fail with their earlier messages: lanes swapped; music started 3 frames early; a perfect window of 4; Start not clearing the score; the driver run once too often; a row made to drop nothing.
- Gap 2: an image with no white and an image with two shades each fail the build with the new message.
- `git status --short` after a check lists no cache folder.
- Not done: `make run` and F5, which need a person at a window. Nothing a player sees was meant to change.

## Plan Change Log

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the build gave no message when the image converter crashed (see above).

## Design Notes

**The game stays in one C file.** At 557 lines it reads in one sitting, and its parts share state that this hardware wants as plain globals; splitting it would trade one long file for several files full of shared declarations. It is reordered instead. The check script is different: its helpers do not share state, so they split cleanly.

**The ROM will not be byte-identical.** Reordering functions moves code around inside the ROM. The proof that nothing changed is the two checks and the six breaks, not a checksum.

**Gap 2 tightens a rule the instructions already state.** Images were always meant to use the Game Boy's four shades; an image that skips one is shown with its shades shifted. Failing the build is the same kind of fix made for a fifth shade in the dev-environment epic.

## Verification

**Commands:**
- `make clean && make check && make check-debug` -- expected: both PASS, 35 notes in each of two plays
- `git status --short` -- expected: only source, script, docs and plan files
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
