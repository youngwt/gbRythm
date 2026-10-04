---
id: 2
type: story
title: "PyBoy's picture is compared with Emulicious's"
parent: none
covers: [CAP-2]
after: []
assignee: ""
refined: false
hitl: true
risk: low
---

# PyBoy's picture is compared with Emulicious's

## Description

The proof ROM's screen in PyBoy is compared with the same screen in Emulicious, and the result is written down. This answers the question left open by the dev-environment epic: whether PyBoy, which every automated check relies on, draws what a more accurate emulator draws. A person must do one step: save a screenshot from the Emulicious window.

## Acceptance Criteria

1. **The two screens are compared at the same moment**
   **Given** the proof ROM after it has started and before A is pressed, in both emulators
   **When** the user saves a screenshot from Emulicious and the agent compares it with PyBoy's
   **Then** the comparison is pixel by pixel on the four Game Boy shades, ignoring the colours each emulator uses to display them and any window scaling
2. **A match is recorded**
   **Given** the two screens are the same
   **When** the comparison finishes
   **Then** the setup instructions say PyBoy matched Emulicious for this ROM, with the date and the versions of both
3. **A difference is recorded and judged**
   **Given** the two screens differ
   **When** the comparison finishes
   **Then** the setup instructions say where they differ and whether the difference could make the headless check pass or fail wrongly
4. **The open question is closed where it is listed**
   **Given** the comparison is recorded
   **When** a reader opens the "What was found" section of the setup instructions
   **Then** it no longer says the question is unanswered

## Boundaries

- Must not change: the headless check, the ROM, the build. A difference that matters becomes a new ticket; it is not fixed here.

## References

- epic — _bmad-output/initiative-gbrythm/epic-dev-environment/epic-dev-environment.md, Notes, the PyBoy open question
- retrospective — _bmad-output/initiative-gbrythm/epic-dev-environment/epic-dev-environment-retrospective.md, finding F2
- instructions — docs/setup.md, section "What was found"

## Notes

- Human step: open the ROM in Emulicious with `make run`, save a screenshot from its menu before pressing A, and tell the agent where it was saved.
- Assumption: comparing the one screen before A is pressed is enough for this ROM. Sound and timing are not compared; the game epics may need a wider comparison later.
- Open question: how Emulicious saves a screenshot and at what scale; found when the work starts.
