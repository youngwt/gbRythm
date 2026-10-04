---
title: 'Build and headless-run a minimal ROM'
type: 'feature'
ticket: '1'
created: '2026-10-03'
status: done
baseline_revision: '4e163800061245a53364113582a0495a11b625c2'
route: 'full'
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

**Problem:** The repository has no Game Boy toolchain, no source, and no way for an agent to build a ROM or see what it does. Nothing else in the epic can start until one thin path from C source to a checked screenshot exists.

**Approach:** Install GBDK-2020 4.5.0 and PyBoy 2.7.0 into a git-ignored `tools/` folder, add a minimal C program that prints text, a Makefile that builds it with one command, a headless script that runs the ROM and saves a screenshot, and written setup instructions that explain each step.

## Boundaries & Constraints

**Always:**
- Every tool lives under `tools/` in the repository; nothing is installed to the system, and `tools/` is never committed.
- The Makefile and script find tools by explicit path under `tools/`, never through PATH. `make` and `uv` are the only tools taken from the machine.
- Build and check run from the VS Code Flatpak terminal with no window, click, or prompt.
- Tool versions and the GBDK download checksum are pinned in the instructions.
- Each instruction step says why it exists, in plain language for someone new to Game Boy development.
- The ROM targets the original Game Boy, has no mapper, and is 32K or smaller.
- C follows the hardware rules in `stack.md`.

**Never:**
- No setup script: the instructions are commands a person or agent runs one at a time.
- No button handling, pass/fail assertion on behaviour, images, sound, Java, Emulicious, or debug build flags; later stories own those.
- No game engine, no Color-only features.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Build | `make`, tools installed | Exit 0; `build/gbrythm.gb` exists, 32768 bytes or fewer | No error expected |
| Syntax error | `make` with a C syntax error in `src/main.c` | Non-zero exit; compiler message names file and line | No ROM is left looking fresh: the stale `.gb` is not reported as built |
| Tools missing | `make` with no `tools/gbdk` | Non-zero exit | One-line message pointing at `docs/setup.md` |
| Headless check | `make check`, ROM built | Exit 0; `build/screenshot.png` written, 160×144, showing the text; no window | No error expected |
| ROM missing or blank | check script run with no ROM, or the screen is one flat colour | Non-zero exit | Message says which |

</frozen-after-approval>

## Code Map

Greenfield: the repository holds only `.gitignore` and BMad output. Nothing to reuse.

- `.gitignore` -- already ignores `build/`, `*.gb`, `*.o`, `*.lst`, `*.map`, `*.sym`; needs `tools/`.
- `tools/gbdk/` -- GBDK 4.5.0 from `https://github.com/gbdk-2020/gbdk-2020/releases/download/4.5.0/gbdk-linux64.tar.gz` (6,870,728 bytes, sha256 `d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c`). The archive unpacks to a `gbdk/` folder; the compiler driver is `bin/lcc`.
- `tools/venv/` -- Python environment made with `uv venv`, holding `pyboy==2.7.0` (PyPI has a Python 3.13 x86_64 wheel; depends on numpy and pysdl2). Screenshots through PyBoy's image API also need `pillow`.
- Machine: `make`, `tar`, `sha256sum`, `curl`, `uv` 0.12.22 and Python 3.13 are present; GitHub and PyPI are reachable from the Flatpak terminal.

## Tasks & Acceptance

**Execution:**
- [x] `.gitignore` -- add `tools/` -- tool binaries are never committed.
- [x] `docs/setup.md` -- write the setup instructions: download GBDK, verify the checksum, unpack to `tools/gbdk`; create `tools/venv` and install pinned PyBoy and Pillow; then build and check. Each step carries a short "why". Run every command exactly as written while writing it -- the instructions are the install, so they are proven as they are authored.
- [x] `src/main.c` -- minimal program that prints a line of text and idles -- gives the build and the check something visible.
- [x] `Makefile` -- default target builds `build/gbrythm.gb` from `src/*.c` with `tools/gbdk/bin/lcc`; `check` target runs the script with `tools/venv/bin/python`; `clean` removes `build/`; fail early with a pointer to `docs/setup.md` when a tool path is missing -- one command per capability.
- [x] `scripts/check_rom.py` -- load the ROM in PyBoy with no window, advance enough frames for the text to appear, save `build/screenshot.png`, exit non-zero when the ROM is missing or the screen is one flat colour -- the agent's eyes.
- [x] Verify the matrix -- run each row, including a deliberate syntax error that is reverted afterwards, and look at the screenshot.

**Acceptance Criteria:**
- Given a checkout with `tools/` installed per `docs/setup.md`, when `make clean && make` runs, then it exits 0 and `build/gbrythm.gb` exists at 32768 bytes or fewer.
- Given a C syntax error in the source, when `make` runs, then it exits non-zero and prints the compiler's message.
- Given a built ROM, when `make check` runs in a terminal with no display, then it exits 0, opens no window, and `build/screenshot.png` shows the printed text.
- Given the finished work, when `git status` is read, then nothing under `tools/` or `build/` is tracked or listed.
- Given `docs/setup.md`, when a reader follows it, then every command is copy-runnable from the repository root and every step states why it exists.

## Implementation Notes

- Files: `.gitignore`, `Makefile`, `src/main.c`, `scripts/check_rom.py`, `docs/setup.md`. Installed `tools/gbdk` (checksum OK) and `tools/venv`.
- Objects compile to `build/` through a pattern rule so compiler by-products (`.asm`, `.lst`, `.sym`, `.ihx`) stay out of `src/`.
- `.DELETE_ON_ERROR` plus tool checks as order-only prerequisites: a failed compile leaves no fresh-looking ROM, and a missing tool gives the pointer to `docs/setup.md`.
- The venv uses the system Python 3.13 that `uv` finds; the plan named only `make` and `uv` as machine tools. `uv` downloads a Python when none exists, so the instructions still hold. Pillow pinned at 12.3.0.
- The ROM is exactly 32768 bytes: GBDK pads to the 32K minimum, so the size is the limit, not near-overflow.
- PyBoy refuses a file with a bad header checksum before running it, so the flat-colour row was verified with a real ROM that draws nothing.
- Matrix rows verified by hand, no automated test suite: build exit 0; syntax error exit 2 with `src/main.c:9: syntax error`; missing GBDK exit 2 with pointer; check exit 0 with `DISPLAY` unset, 160x144 screenshot showing `GBRYTHM / BUILD OK`; missing ROM exit 1; blank ROM exit 1.
- The venv was deleted and recreated with the exact commands in `docs/setup.md`; the GBDK commands were run as written the first time.

## Plan Change Log

## Review Triage Log

Pass 1 (quick lens, run inline by the implementing session, not by an independent reviewer; the user did not opt in to subagents). Verdicts: high 0, medium 0, low 2, false 1, maybe-false 0.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| `Makefile` object rule ignores header files, so editing a future `src/*.h` would not rebuild | low | patch | Real once a header exists (stories 2-3). Fixed: objects now depend on `$(wildcard src/*.h)`; build and check re-run clean. |
| `Makefile` with no `src/*.c` calls `lcc` with no inputs | low | rejected | Real but not reachable in everyday use; `src/main.c` always exists and a guard adds complexity. |
| `scripts/check_rom.py` flat-colour test misfires when `getcolors()` returns `None` | false | rejected | `None` means more than 256 colours, which is not flat; the code checks `is not None` before comparing. |

## Design Notes

PyBoy goes in a `uv venv` under `tools/` rather than being run through `uv run --with`, so the interpreter is at a fixed path inside the repository and deleting `tools/` removes it; story 6 depends on that.

The flat-colour test is the only assertion in the check. Asserting on behaviour belongs to story 2.

## Verification

**Commands:**
- `make clean && make` -- expected: exit 0, `build/gbrythm.gb` present
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- `make check` -- expected: exit 0, `build/screenshot.png` present
- `git status --short` -- expected: no `tools/` or `build/` paths

**Manual checks (if no CLI):**
- Open `build/screenshot.png`: the printed text is legible on a Game Boy screen.
