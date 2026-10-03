---
title: 'A PNG becomes graphics on screen'
type: 'feature'
ticket: '3'
created: '2026-10-03'
status: 'built'
baseline_revision: 'b5d4b8c5d1975cf5613f6b35980186e152ea4fbe'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The proof ROM can only show text from GBDK's built-in font. The game will need its own graphics, and there is no proven route from an image file to pixels on the Game Boy screen.

**Approach:** Add an image file to the repository and have the build convert it to C with GBDK's `png2asset`, so the proof ROM displays it with no hand-edited C; keep the ROM at 32K or smaller and extend the setup instructions to explain the route and the limits an image must fit.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 50 changed lines across `Makefile`, `src/main.c` and `docs/setup.md`, plus one new image.

- `assets/arrow.png` is a 32x32 down arrow in the four Game Boy shades, generated with Pillow; the generator was a throwaway and is not in the repository.
- The image is shown as a background (`png2asset -map`): tiles plus a tile map, placed with `set_bkg_data` and `set_bkg_tiles`. Generated `.c`/`.h` go to `build/` and are compiled from there; `src` objects depend on them so the header exists before `main.c` compiles.
- Surprise: `png2asset` exits 0 when it reports "more than 4 colors" and still writes output. The rule now logs its output to `build/NAME.c.log` and fails on any "error" line.
- Surprise: make deleted `build/arrow.c` as an intermediate file, forcing a reconvert on every build. Fixed with `.SECONDARY`.
- `-keep_palette_order` was dropped: it needs indexed PNGs. Without it the converter sorts shades light to dark, which is what the Game Boy's default palette expects.
- Verified: build exit 0, ROM 32768 bytes; `make check` PASS with the arrow visible; flipping the PNG and running `make check` reconverted, rebuilt and produced a different screenshot; restoring it reproduced the original screenshot byte for byte; a 5-colour PNG and a 30x30 PNG each fail the build with the converter's message; a second `make` does nothing; no generated C in `git status`.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer.

- medium, patched: converter errors did not fail the build (see surprise above).
- low, patched: generated C deleted as intermediate (see surprise above).
- low, deferred: every image is converted with tile origin 128, so two images shown together would overwrite each other's tiles. One image needs nothing more; logged in `deferred-work.md` and documented in `docs/setup.md`.

## Verification

**Commands:**
- `make clean && make` -- expected: exit 0, `build/gbrythm.gb` at 32768 bytes or fewer
- `make check` -- expected: exit 0, PASS; `build/screenshot-before.png` shows the image
- edit the PNG, `make check`, compare screenshots -- expected: `make` reconverts and rebuilds on its own, the screenshot differs from the earlier one; PNG restored afterwards
- `git status --short` -- expected: no generated C listed

**Manual checks (if no CLI):**
- Open `build/screenshot-before.png`: the image is recognisable and the text is intact.
