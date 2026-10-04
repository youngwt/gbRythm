---
id: 1
type: story
title: "The headless check fails when the image is missing"
parent: none
covers: [CAP-2, CAP-6]
after: []
assignee: ""
refined: false
hitl: false
risk: low
---

# The headless check fails when the image is missing

## Description

The headless check confirms that the graphic converted from the PNG is on the screen, and fails when it is not. Today it passes on any screen that is not blank and that changes when A is pressed, so a ROM that stopped drawing the image would still pass. After this, an agent can trust a pass to mean the image route still works.

## Acceptance Criteria

1. **The proof ROM passes**
   **Given** the proof ROM as it is, drawing the image
   **When** the headless check runs
   **Then** it reports a pass and exits 0
2. **A ROM that does not draw the image fails**
   **Given** a ROM built with the image not drawn
   **When** the headless check runs
   **Then** it reports a failure that says the image was not found on screen, and exits non-zero
3. **A wrong image fails**
   **Given** a ROM that draws something other than the current PNG in the image's place
   **When** the headless check runs
   **Then** it reports the same failure
4. **Editing the PNG needs no change to the check**
   **Given** the PNG edited within the limits the instructions state
   **When** the ROM is rebuilt and the headless check runs
   **Then** it passes without the check or any expected-output file being edited by hand
5. **The instructions describe the new check**
   **Given** the setup instructions
   **When** a reader reaches the headless check
   **Then** they say the check looks for the image and what a failure means

## Boundaries

- Must not change: the button check (a ROM that ignores A still fails), the blank-screen check, the two saved screenshots, running with no window, the ROM itself.

## References

- retrospective — _bmad-output/initiative-gbrythm/epic-dev-environment/epic-dev-environment-retrospective.md, finding F1
- spec — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/spec-dev-environment.md, CAP-2 and CAP-6

## Notes

- Decision: raised as separate work, not a condition of accepting the dev-environment epic (user, 2026-10-04).
- Assumption: the check works out what the image should look like from the PNG itself, which is what criterion 4 requires. The alternative is a stored reference screenshot that is regenerated on purpose when the image changes; simpler, but an edit to the PNG then needs a second step.
- Assumption: the check knows where on screen the image is placed. If the position should not be duplicated between the ROM and the check, say so and the ticket changes.
