---
id: 3
type: story
title: "Two images can be shown at once"
parent: none
covers: [CAP-6]
after: []
assignee: ""
refined: false
hitl: false
risk: low
---

# Two images can be shown at once

## Description

The build can convert more than one PNG and the ROM can show them together without one corrupting the other. Today every image is given the same starting tile number, so a second image shown at the same time would overwrite the first one's tiles. The game will need several images, so this removes a trap before game work begins.

## Acceptance Criteria

1. **Two images appear together, both correct**
   **Given** two different PNGs in the images folder and a ROM that shows both
   **When** the headless check saves its screenshot
   **Then** both images appear as drawn in their PNGs, and the text is intact
2. **One image behaves as before**
   **Given** only the current image
   **When** the ROM is built and checked
   **Then** the screenshots are the same as before this change
3. **Adding an image needs no hand-picked numbers**
   **Given** a new PNG added to the images folder
   **When** the ROM is built
   **Then** the build gives its tiles a place that does not overlap any other image or the text font, with nothing typed in by hand
4. **Running out of tile space stops the build**
   **Given** images that together need more tiles than are available
   **When** the ROM is built
   **Then** the build fails with a message that says tile space ran out and which image did not fit
5. **An image named like a source file does not silently replace it**
   **Given** a PNG whose name matches a C source file's name
   **When** the ROM is built
   **Then** either both are built correctly, or the build stops with a message naming the clash
6. **The instructions match**
   **Given** the setup instructions' section on images
   **When** read after this change
   **Then** the note that a second image needs its own starting number is replaced by how it now works

## Boundaries

- Must not change: the image limits already documented (four shades, multiples of 8 pixels, screen size), the conversion errors that already stop the build, the ROM staying 32K or smaller with no mapper.

## References

- deferred work — _bmad-output/initiative-gbrythm/deferred-work.md, first entry
- retrospective — _bmad-output/initiative-gbrythm/epic-dev-environment/epic-dev-environment-retrospective.md, finding F12
- spec — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/spec-dev-environment.md, CAP-6

## Notes

- Assumption: this covers background images only. Moving objects (sprites) use a separate tile area and are left to the game's own spec.
- Assumption: the proof ROM gains a second small image permanently, so criterion 1 stays checked. The alternative is to prove it once and remove the second image.
- Assumption: this is worth doing before the game is specced. It could instead wait until the game's spec says how images are used, since that may change the right design; if so, this ticket should be parked, not built.
