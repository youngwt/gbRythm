---
title: 'The instructions explain the game and rebuild from nothing'
type: 'chore'
ticket: '8'
created: '2026-10-05'
status: done
baseline_revision: 'd826091698c6629805fe07a9aa2c7a517ea439b8'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The instructions grew section by section as the game was built. Each part is explained, but nothing tells a newcomer how to play, the opening still describes a ROM that only makes screenshots, and the steps have not been followed from nothing since the game existed.

**Approach:** Complete `docs/setup.md` so a reader learns the lanes, the judging and how the falling notes follow the song, starting with how to play; correct what earlier stories left stale. Then delete `tools/` and `build/` and run every command in the instructions as written, in order, fixing every gap, until the headless check passes.

</frozen-after-approval>

## Implementation Notes

Oneshot route: a new "How to play" section and corrections in `docs/setup.md`, small updates to `README.md`, plus whatever the rebuild exposes.

No commit was made: the user commits their own work. The working tree was not clean at the start: the user had staged, but not committed, the "done" mark on story 3.7's plan. The build went ahead with that one line alongside.

The explanation:

- `docs/setup.md` has a new opening that says what the game is and that the document does two jobs: nine setup steps, then sections explaining how the game works.
- New section "How to play": Start, the five lanes and their buttons, pressing as a note lands, the three judgements, the results, and four things a player should know. It points on to the four sections that explain each part.
- The sections a newcomer needs were already written as each part was built: "How the falling notes work" (the lanes and how notes follow the song), "How judging works", "How a play starts and ends", "How the music works". Read through against the code: each still matches.
- Corrected: the check's description now says thirteen ways of pressing and lists the two-play one; the size finding gives the finished game's figure. `README.md` says the same document explains how to play.

The rebuild:

- `tools/` (292 MB) and `build/` were deleted; `make` then failed with the pointer to `docs/setup.md`.
- Every `sh` block in `docs/setup.md` was extracted by a script and run in order, unedited: 18 blocks. 17 exited 0, including all four checksum checks. `make run` was skipped because it opens a window.
- `make check` passed: 35 notes fell and were heard in each of two plays, and all thirteen ways of pressing were judged as designed. `make check-debug` passed too. The ROM is 32768 bytes; `tools/` is back to 292 MB.
- No command needed fixing.
- The user's `tools/emulicious/Emulicious.ini`, which holds their remapped Start key, was copied out before the delete and put back.
- Not re-proven: `make run`, F5, and the VS Code extension's install from nothing (it was already installed).
- Not tested: whether the explanation teaches someone new to it. Nobody but the session that wrote it has read it; the same was true in the two earlier epics.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. No findings.

## Verification

**Commands:**
- `rm -rf tools build`, then every `sh` block of `docs/setup.md` in order except `make run` -- expected: each exits 0
- `make check` -- expected: exit 0, PASS with 35 notes in each of two plays and 13 ways of pressing
- `make check-debug` -- expected: the same
