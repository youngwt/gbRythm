---
title: 'Refactor sweep'
type: 'refactor'
ticket: '5'
created: '2026-10-04'
status: done
baseline_revision: 'c931eef2a291cfc0a376ed5d063e4ee4df47a84a'
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

**Problem:** Four stories each added to the same build file, C source, check script and instructions. Each addition was sound, but the files now show their layers: settings and sections sit in the order they arrived, and a few small inconsistencies were left behind.

**Approach:** Tidy the build file, C source, ignore file and instructions without changing what anything does: the normal and debug ROMs stay byte-identical, and the build and the headless check still pass. Behaviour changes found along the way are deferred, not made.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 60 changed lines across `Makefile`, `src/main.c`, `.gitignore` and `docs/setup.md`.

Scope, set from the four earlier plans, their review logs and `deferred-work.md`:

- `Makefile`: a header listing the five commands; tool paths grouped and aligned; `.PHONY` in the same order as the header. `require-emulicious` now checks only the Emulicious file, like the other two `require-` targets check one tool each; a missing Java is reported by `scripts/java-host.sh`, which already did so.
- `src/main.c`: the arrow's position is two named constants instead of bare numbers in the call.
- `.gitignore`: the tools comment names Java and Emulicious; the unused `obj/` pattern is gone.
- `docs/setup.md`: sections reordered so the numbered steps are followed by "Adding or changing an image", a new "Everyday commands" table, "Where things are", and "What was found" last, as the historical note it is. Nothing was reworded except two references to a line number.
- `scripts/check_rom.py`, `scripts/java-host.sh` and `.vscode/`: read, nothing worth changing.

Left alone on purpose:

- The fixed tile origin of 128 (already in `deferred-work.md`): fixing it changes how images are converted, and the right scheme depends on how the game uses images.
- The repository has no `README.md`, `AGENTS.md` or `CLAUDE.md`, so a fresh agent has nothing pointing it at `docs/setup.md`. This is new content, not cleanup; logged in `deferred-work.md`.
- Story 1's rejected finding (no `src/*.c` calls `lcc` with no inputs) stays rejected.

Found along the way: the debug ROM is byte-identical to the normal ROM. `-Wf--max-allocs-per-node0` does reach the compiler and does change the code of a less trivial test function; `main.c` is simply too small for it to matter. Debug symbols go in the `.cdb`, not the ROM.

Verified: after `make clean`, `make` and `make debug` both give sha256 `26c228a0...8803`, the same as before the change; `make check` passes; `build/debug/gbrythm.cdb` is written; `make run` with the Emulicious file missing exits non-zero with the pointer to `docs/setup.md`. `make run` and F5 were not run with a window.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer, as the user chose for story 4. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: naming the constants moved `a_was_pressed = 1;` from line 27 to line 31 of `src/main.c`, and `docs/setup.md` told the reader to set the breakpoint on "line 27". The instructions now name the line by its text.

## Verification

**Commands:**
- `make clean && make && make debug && sha256sum build/gbrythm.gb build/debug/gbrythm.gb` -- expected: both `26c228a02549cc939ed70c10cdba531a2e9247952c3bd3550cff8a8cd1b28803`
- `make check` -- expected: exit 0, PASS
- `git status --short` -- expected: no build or tools paths
