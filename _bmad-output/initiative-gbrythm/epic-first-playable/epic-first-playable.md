---
type: epic
title: "The player plays Amazing Grace and is judged on timing"
parent: initiative-gbrythm
covers: []
after: []
assignee: ""
risk: medium
---

# The player plays Amazing Grace and is judged on timing

## Description

The ROM becomes a game. The player presses Start, the first verse of "Amazing Grace" plays, a note falls for each note of the tune in one of five lanes, presses are graded perfect, good or miss, and a results screen follows. The spec owns the capabilities, constraints and non-goals, and `lane-mapping.md` beside it owns which note falls where.

## Outcome

For the user, a rhythm game they can play and judge the feel of; for the agents, gameplay they can build and check unaided. The spec's success signal shows it worked.

## Requirements

The spec's capabilities CAP-1 to CAP-7 are the requirement ids. The initiative has no numbered requirements, so `covers` is empty.

## Done when

1. `make` builds a ROM of 32K or smaller in which, after Start, the full first verse plays and every melody note has one falling note, in its mapped lane, arriving as the note sounds.
2. `make check`, with no window, plays the song with scripted presses and passes only when on-time presses score all perfects, no presses score all misses, late presses score goods, and presses with no note near change nothing.
3. The results screen shows perfect, good and miss counts that add up to the number of notes, and Start plays the song again with the counts reset.
4. The user plays the song in Emulicious, recognises the verse, and says the judgements match their own sense of their timing.
5. With the tools folder deleted, following the written instructions alone gets `make check` passing again.

## Boundaries

One song, five lanes, three judgements, on this Steam Deck. Not a title screen, more songs, difficulty levels, held or simultaneous notes, points, sound effects, harmony, finished art or real hardware; see the spec's Non-goals.

## References

- spec — _bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md
- lanes — _bmad-output/initiative-gbrythm/spec-first-playable/lane-mapping.md, which note falls in which lane and on which button
- constraint — the same spec, section Constraints
- music — _bmad-output/initiative-gbrythm/spec-music-proof/spec-music-proof.md, the song and the sound check this epic builds on
- stack — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md, tool versions, machine facts, C rules
- instructions — docs/setup.md, sections "How the music works" and "Adding or changing an image"
- research — _bmad-output/initiative-gbrythm/research-game-boy-dev-environment/research-game-boy-dev-environment.md, section 3, the driver's way of calling C code in time with a song

## Notes

- Decision: one epic, eight stories in sequence, because each edits the same C source, check script and instructions (2026-10-05, awaiting the user's approval of the breakdown).
- Decision: the tracer bullet is entry 1: the song's own notes falling in a single lane and reaching the line in time, measured by the headless check. It crosses the song data, the game loop, the screen and the check, and it answers three of the spec's open questions before the rest is built (2026-10-05, awaiting approval).
- Decision: a closing refactor sweep is included, as there are more than three entries; the rebuild from the instructions runs after it as the closing end-to-end check (2026-10-05, awaiting approval).
- Decision: when the last story is done, the spec is reconciled with `bmad-spec` before the retrospective. Two retrospectives found the spec left out of date when this was a follow-up (2026-10-05).
- Decision: the spec stays where `bmad-spec` wrote it, beside this folder (2026-10-05, awaiting approval).
- Open question: does the game fit in 32K, and is C fast enough for falling notes at 60 frames a second? Entry 1 answers both. If either answer is no, work stops and the finding is reported; a mapper or a slower frame rate is the user's decision, not the builder's.
- Open question: are the two eighth notes of "-zing" playable at the current tempo? Entry 1 shows how they look; entry 6 settles it by play.
- Open question: starting widths for the perfect and good windows. Entry 3's builder proposes them in its plan; entry 6 tunes them with the user.
- Assumption: builds leave their changes uncommitted with a suggested message, by the user's standing preference.
