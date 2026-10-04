---
title: 'Two images can be shown at once'
type: 'feature'
ticket: '3'
created: '2026-10-04'
status: done
baseline_revision: 'a1a7a83987212cfa8fe55d7deac154966f454416'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/backlog/story-two-images-can-be-shown-at-once.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The build gives every image the same starting tile number, so two images shown together would overwrite each other's tiles. An image named like a C source file would also silently collide with it.

**Approach:** Convert the images in one pass that gives each the next free tile numbers after the one before, stops the build when tile space runs out or a name clashes, and add a second small image to the proof ROM so the headless check keeps proving it. The story file's six acceptance criteria, Boundaries and decisions are the contract.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 100 changed lines across a new `scripts/convert-images.sh`, `Makefile`, `src/main.c` and `docs/setup.md`, plus one new image.

- `scripts/convert-images.sh` converts every PNG in one run, in alphabetical order, starting at tile 128 and giving each image the tiles after the previous one's. It reads each image's tile count from the header the converter writes. It is a shell script, not Python, so building still needs only GBDK.
- `Makefile`: the per-image pattern rule is replaced by one grouped rule (`&:`, GNU make 4.3 or newer; this machine has 4.4.1) that runs the script for all images. Changing any PNG, or the script, reconverts all of them.
- `assets/note.png`: a 16x16 music note in four shades, generated with Pillow; the generator was a throwaway. `src/main.c` shows it to the right of the arrow. The arrow keeps tiles 128 to 138; the note gets 139 to 142.
- The name-clash check is in the script and names both files. It assumes sources live in `src/`.
- Found and fixed, outside the six criteria: a fifth colour placed in a tile of its own was accepted silently, by the old rule as well as the new one. The converter makes a second palette instead of reporting an error. The script now fails unless the image has exactly one palette. Story 1.3's five-colour test passed only because its fifth colour shared a tile with four others. This tightens an existing limit and does not change it.
- Not changed: removing a PNG does not renumber the remaining images until one of them changes or `make clean` runs. Harmless, since it only leaves a gap.
- Images share tiles 128 to 255 with sprites on the Game Boy. Sprites are out of scope by the story's decision; the game's spec will need to divide that space.
- This resolves the first entry in `deferred-work.md` and retrospective finding F12. Neither file was edited.
- No commit was made: the user commits their own work.

Verified by running each case, restoring files after each:

- Criterion 1: `make check` reports `PASS: 2 image(s) shown`; the check finds both PNGs on screen, and the screenshot was opened and shows the text, the arrow and the note.
- Criterion 2: with `note.png` removed and the baseline `src/main.c`, the ROM's sha256 is `26c228a0...`, the same as before the change, and both screenshots are byte-identical to the baseline's.
- Criterion 3: `note.png` was added with no number typed anywhere; the generated headers give origins 128 and 139.
- Criterion 4: a 96x96 noise image fails the build: "tile space ran out at assets/zbig.png: it needs 144 tiles and 113 are left of the 128 that images share".
- Criterion 5: `assets/main.png` fails the build: "assets/main.png and src/main.c share a name; rename the image".
- Criterion 6: the image section of `docs/setup.md` now explains the automatic numbering and the two new errors.
- Boundaries: a 30x30 image and five colours in one tile still fail with the converter's messages; the ROM is 32768 bytes; `make debug` builds; a repeat `make` does nothing.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 1, low 0, false 0, maybe-false 0.

- medium, patched: a five-colour image did not fail the build when the extra colour was alone in its tile (see "Found and fixed" above). Pre-existing, but the documented limit said it would fail, and the fix is three lines in the script this change adds.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, `PASS: 2 image(s) shown and screen changed after pressing A`
- `grep -h TILE_ORIGIN build/arrow.h build/note.h` -- expected: 128 and 139
- `stat -c %s build/gbrythm.gb` -- expected: 32768
- add `assets/main.png`, run `make` -- expected: non-zero, message naming the clash; file removed afterwards
