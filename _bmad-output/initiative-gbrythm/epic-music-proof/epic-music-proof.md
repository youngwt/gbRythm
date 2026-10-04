---
type: epic
title: "The proof ROM plays Amazing Grace through hUGEDriver"
parent: initiative-gbrythm
covers: []
after: []
assignee: ""
risk: medium
---

# The proof ROM plays Amazing Grace through hUGEDriver

## Description

The proof ROM plays the opening phrase of "Amazing Grace" using the hUGEDriver music library under GBDK 4.5.0, the headless check can tell that it does, and the instructions explain how. The spec owns the capabilities, constraints and non-goals. This retires the one risk the research flagged before any game work depends on music.

## Outcome

For the user and the agents working in this repository, music is proven instead of assumed; the spec's success signal shows it worked.

## Requirements

The spec's capabilities CAP-1 to CAP-5 are the requirement ids. The initiative has no numbered requirements, so `covers` is empty.

## Done when

1. `make` builds a ROM of 32K or smaller that plays the opening of "Amazing Grace", and the existing checks still pass: the screen is not blank, both images are shown, and the screen changes when A is pressed.
2. `make check`, with no window opened, passes on that ROM and fails on a ROM built with the music left out.
3. The user listens in Emulicious and recognises the tune.
4. With the tools folder deleted, following the written instructions alone gets `make check` passing again.
5. The instructions state whether hUGEDriver's packaged library worked with GBDK 4.5.0, with the evidence, and what was done instead if it did not.

## Boundaries

Music in the existing proof ROM on this Steam Deck. Not gameplay, anything timed to the music, sound effects, a second song, the whole song, or the tracker editor; see the spec's Non-goals.

## References

- spec — _bmad-output/initiative-gbrythm/spec-music-proof/spec-music-proof.md
- constraint — the same spec, section Constraints
- stack — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md, tool versions, machine facts, C rules
- instructions — docs/setup.md, the install steps and headless check this epic extends
- research — _bmad-output/initiative-gbrythm/research-game-boy-dev-environment/research-game-boy-dev-environment.md, section 3, for history only

## Notes

- Decision: one epic, three stories, no closing refactor sweep because there are only three entries (2026-10-04, awaiting the user's approval of the breakdown).
- Decision: the tracer bullet is entry 1, the driver linked and one sound heard by the check; it crosses the driver install, the build, the C program, the headless check and the instructions, and it answers the compatibility question first (2026-10-04, awaiting approval).
- Decision: the entries run in sequence, because each edits the same build file, C source, check script and instructions (2026-10-04, awaiting approval).
- Decision: the spec stays where `bmad-spec` wrote it, beside this folder, and is referenced from here (2026-10-04, awaiting approval).
- Finding: PyBoy 2.7.0 can observe sound. With sound emulation on it exposes the audio samples of each frame and the sound registers; on the current, silent ROM the samples are all zero. Probed 2026-10-04. This answers the spec's first open question in principle; entry 1 proves it on real music. The spec itself has not been updated.
- Open question: whether hUGEDriver's packaged library links and runs under GBDK 4.5.0; entry 1 answers it. If it does not, the spec's constraint applies: rebuild with RGBDS in the tools folder, and stop and report if that fails.
- Assumption: the user's own no-commit preference applies to these builds; each story ends with changes left for the user to commit.
