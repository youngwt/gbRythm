---
title: 'The headless check fails when the image is missing'
type: 'feature'
ticket: '1'
created: '2026-10-04'
status: 'built'
baseline_revision: 'bcaa738c9042845825b218274459575e5e807067'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/backlog/story-the-headless-check-fails-when-the-image-is-missing.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The headless check passes on any screen that is not blank and that changes when A is pressed. A ROM that stopped drawing the image converted from the PNG would still pass, so a pass does not show the image route works.

**Approach:** Make the check look for each PNG from `assets/` on the screen it captures, working out the expected picture from the PNG itself, and fail with a message naming the image when it is not there. The story file's five acceptance criteria and its Boundaries are the contract.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 45 changed lines across `scripts/check_rom.py`, `Makefile` and `docs/setup.md`.

- `scripts/check_rom.py` takes the PNGs as extra arguments and searches the before-press screenshot for each one, at every pixel position. `Makefile` passes every PNG in `assets/`.
- Decision: search the whole screen instead of looking at a known position. The story allowed the check to know the position; searching means the position is written in one place only, the C source, and the check keeps working if the image moves.
- Both pictures are reduced to four brightness bands before comparing, because PyBoy's light grey (`#999999`) is not the PNG's (`#AAAAAA`).
- A PNG of one flat shade is refused: it would match any empty patch of screen.
- The search uses NumPy, which PyBoy already installs. It is now imported directly, so `docs/setup.md` pins it at the installed version, 2.5.3. The pinned install command was re-run and changed nothing.
- Consequence to know: `make check` now requires every PNG in `assets/` to be on the first screen. That is right for the proof ROM. A game with images that appear later will need the check to say which images it expects when.
- No commit was made: the user commits their own work.

Verified by running each case, restoring the source and PNG after each:

- Criterion 1: proof ROM, PASS, exit 0.
- Criterion 2: draw call commented out, `FAIL: assets/arrow.png was not found on screen`, non-zero.
- Criterion 3: the unchanged ROM checked against a flipped copy of the PNG, same failure, exit 1.
- Criterion 4: the PNG flipped, `make check` rebuilt and passed with nothing else edited.
- Criterion 5: `docs/setup.md` step 4 describes the image search and its failure message.
- Boundaries: button handling replaced by `if (0)` still fails on the button; a missing ROM still fails; both screenshots are still saved; the ROM's sha256 is unchanged (`26c228a0...`); the check takes about 0.7 seconds.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: a missing PNG file and an image missing from the screen printed near-identical messages ("image not found" and "was not found on screen"). The first now says "image file not found".

## Verification

**Commands:**
- `make check` -- expected: exit 0, `PASS: 1 image(s) shown and screen changed after pressing A`
- `make check` with the arrow's draw call removed from `src/main.c` -- expected: non-zero, `FAIL: assets/arrow.png was not found on screen`; source restored afterwards
- `sha256sum build/gbrythm.gb` -- expected: `26c228a02549cc939ed70c10cdba531a2e9247952c3bd3550cff8a8cd1b28803`
