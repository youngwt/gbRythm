---
title: 'The song is the full first verse'
type: 'feature'
ticket: '5'
created: '2026-10-05'
status: 'built'
baseline_revision: 'e7c2f3077b0b849e51f80fe0e792a5bc74c75b76'
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

**Problem:** The song stops half-way through the verse, at "that saved a wretch like me". A play lasts 17 seconds and 16 notes, which is short for finding out how the game feels.

**Approach:** Extend the song in the song file to the whole first verse of "Amazing Grace", through "was blind but now I see", written by hand like the first half. The falling notes, the judging and the headless check follow from the song's data, with no change to the game's code. The user listens and confirms the verse is recognisable.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 60 changed lines, nearly all in `src/song.c`, with small updates to the check and `docs/setup.md`.

No commit was made: the user commits their own work.

- `src/song.c`: the tune is now three patterns of 64 rows, 35 notes in all, ending as the third pattern ends. The second half is "I once was lost, but now am found, was blind but now I see": B D B D B G D E G G E D, then D G B G B A G. It adds dotted quarter notes (six rows) and a note that carries across a pattern boundary. The pattern-break effect is no longer needed, since the verse fills three patterns exactly. Written as text; no tracker.
- The melody is the agent's recollection of the standard tune ("New Britain"). The check confirms the ROM plays what the file says; only the user's ear confirms the file says the right tune.
- No change to `src/game.c`: the falling notes, lanes, judging, ending and results all followed from the song's data. The verse uses only the five mapped pitches.
- `scripts/check_rom.py`: one constant changed. Two of the new notes are the same pitch a third of a second apart, where the loudness only rises by 3; the check asked for a rise of 4 to count a repeated note and reported 68 notes heard against 70 fallen. It now asks for 2. Nothing else in the check changed: it found the longer song's end by itself.
- A play lasts 32 seconds. The check takes about six seconds. ROM use is 6,531 bytes of 32,768.

Verified:

- `make check` and `make check-debug`, no display: PASS. 35 notes fell and were heard in each of two plays, in lane, steady, within one frame; results 35 misses; second play from zero; all twelve press scenarios as designed, including the window edges on notes a third of a second apart.
- Notes heard, with repeated pitches shown once: D4 G4 B4 G4 B4 A4 G4 E4 D4 G4 B4 G4 B4 A4 D5 B4 D5 B4 D5 B4 G4 D4 E4 G4 E4 D4 G4 B4 G4 B4 A4 G4, which is the file as written.
- Outstanding: the user listening and recognising the whole verse. This is the story's human step.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the check missed a repeated note a third of a second after the first (see above).

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS with `35 notes fell and were heard in each of two plays`
- `make check-debug` -- expected: the same

**Manual checks (if no CLI):**
- User: `make run`, press Start, listen to the verse through, and say whether it is recognisably "Amazing Grace".
