---
title: 'Proof ROM reacts to a button and the check asserts it'
type: 'feature'
ticket: '2'
created: '2026-10-03'
status: 'built'
baseline_revision: '1202fe1fe2243ad111df4da18d37f762ff26dd5a'
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

**Problem:** The proof ROM only prints text, and the headless check only confirms the screen is not blank. Neither shows that button input reaches the C program, and the check cannot tell a working ROM from a broken one.

**Approach:** Make the ROM visibly change when a button is pressed, and extend the headless check to take a screenshot, press the button, take a second screenshot, and exit 0 only when the screen changed; update the setup instructions to match.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 50 changed lines across `src/main.c`, `scripts/check_rom.py`, `Makefile` and `docs/setup.md`, all building on story 1's files.

- The button is A. The ROM prints `PRESS A`, then adds `A PRESSED` once on the first press; a latch stops it reprinting every frame while held.
- The check now takes an output folder and writes `screenshot-before.png` and `screenshot-after.png`, replacing story 1's single `screenshot.png`. The blank-screen test is kept on the before image.
- PyBoy's `button("a")` presses and releases after one frame; 60 frames follow before the second screenshot.
- Verified: `make check` exit 0 on the ROM; with the button test replaced by `if (0)` it exits non-zero with `FAIL: pressing A did not change the screen`; source restored and re-checked. ROM is 32768 bytes.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer.

- low, patched: `a_was_pressed` relied on startup RAM clearing for its initial value; now set explicitly at the top of `main`.
- low, rejected: `build/screenshot.png` from story 1 is left behind in existing checkouts; it is ignored build output and `make clean` removes it.

## Verification

**Commands:**
- `make clean && make` -- expected: exit 0, `build/gbrythm.gb` at 32768 bytes or fewer
- `make check` -- expected: exit 0, PASS, before and after screenshots saved and different
- `make check` with the button handling removed from `src/main.c` -- expected: non-zero exit, FAIL naming the unchanged screen; source restored afterwards

**Manual checks (if no CLI):**
- Open the two screenshots: the after image shows text the before image does not.
