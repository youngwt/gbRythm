---
type: epic
title: "An agent can build, run and check a Game Boy ROM on this machine"
parent: initiative-gbrythm
covers: []
after: []
assignee: ""
risk: low
---

# An agent can build, run and check a Game Boy ROM on this machine

## Description

The gbRythm repository holds a working Game Boy development environment: an agent builds a proof ROM with one command, runs it without a display, and checks the result; the user can step through the C source in VS Code. The spec owns the capabilities, constraints, and non-goals. Nothing of the game itself is built here.

## Outcome

For the user and the agents working in this repository, a ROM can be built and verified unaided; the spec's success signal shows it worked.

## Requirements

The spec's capabilities CAP-1 to CAP-6 are the requirement ids. The initiative has no numbered requirements yet, so `covers` is empty.

## Done when

1. One command builds the proof ROM from a clean checkout, and a C syntax error fails the build with the compiler's message.
2. The headless check passes and saves a screenshot showing a PNG-sourced graphic and a change after a button press, with no window opened.
3. The user hits a breakpoint on a C line in VS Code and sees variable values, with the ROM running in Emulicious.
4. With the tools folder deleted, following the written instructions alone gets checks 1 and 2 passing again.

## Boundaries

The development environment and its proof ROM on this Steam Deck. Not music, gameplay, finished art, real hardware, a setup script, other machines, or CI; see the spec's Non-goals.

## References

- spec — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/spec-dev-environment.md
- constraint — the same spec, section Constraints
- stack — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md, tool versions, machine facts, C rules
- research — _bmad-output/initiative-gbrythm/research-game-boy-dev-environment/research-game-boy-dev-environment.md, for history only

## Notes

- Decision: one epic, sliced along the spec's capabilities (2026-10-03).
- Decision: tracer bullet is entry 1, build and headless-run a minimal ROM; it crosses toolchain, build, headless emulator, and instructions (2026-10-03).
- Decision: the debugger story comes fourth, after the image story, so the agent-driven path finishes first (user's decision, 2026-10-03).
- Decision: entries 2, 3 and 4 run in sequence because each edits the same build file, C source, and instructions (2026-10-03).
- Decision: a closing Refactor sweep is included (user's decision, 2026-10-03). The rebuild from instructions runs after it as the closing end-to-end check.
- Decision: the spec folder lives inside this epic folder (user's decision, 2026-10-03).
- Parked: whether a headless Game Boy emulator can be driven from .NET; PyBoy and Python are used (user's decision, 2026-10-03).
- Open question: which Java version Emulicious needs, and whether a Java runtime unpacked in the repository opens a window from the VS Code Flatpak sandbox or must launch on the host; entry 4 answers it.
- Open question: whether the Emulicious VS Code debugger extension (last released 2023-11) still works with current Emulicious and VS Code; entry 4 answers it.
- Open question: whether PyBoy is accurate enough for the proof ROM checks; entry 4 compares its screenshot with Emulicious.
