---
title: 'Build and headless-run a minimal ROM'
type: 'feature'
ticket: '1'
created: '2026-10-03'
status: 'draft'
baseline_revision: ''
route: 'full'
route_source: 'auto'
risk: 'low'
review: ''
review_source: ''
lenses_ran: []
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
- [ ] `.gitignore` -- add `tools/` -- tool binaries are never committed.
- [ ] `docs/setup.md` -- write the setup instructions: download GBDK, verify the checksum, unpack to `tools/gbdk`; create `tools/venv` and install pinned PyBoy and Pillow; then build and check. Each step carries a short "why". Run every command exactly as written while writing it -- the instructions are the install, so they are proven as they are authored.
- [ ] `src/main.c` -- minimal program that prints a line of text and idles -- gives the build and the check something visible.
- [ ] `Makefile` -- default target builds `build/gbrythm.gb` from `src/*.c` with `tools/gbdk/bin/lcc`; `check` target runs the script with `tools/venv/bin/python`; `clean` removes `build/`; fail early with a pointer to `docs/setup.md` when a tool path is missing -- one command per capability.
- [ ] `scripts/check_rom.py` -- load the ROM in PyBoy with no window, advance enough frames for the text to appear, save `build/screenshot.png`, exit non-zero when the ROM is missing or the screen is one flat colour -- the agent's eyes.
- [ ] Verify the matrix -- run each row, including a deliberate syntax error that is reverted afterwards, and look at the screenshot.

**Acceptance Criteria:**
- Given a checkout with `tools/` installed per `docs/setup.md`, when `make clean && make` runs, then it exits 0 and `build/gbrythm.gb` exists at 32768 bytes or fewer.
- Given a C syntax error in the source, when `make` runs, then it exits non-zero and prints the compiler's message.
- Given a built ROM, when `make check` runs in a terminal with no display, then it exits 0, opens no window, and `build/screenshot.png` shows the printed text.
- Given the finished work, when `git status` is read, then nothing under `tools/` or `build/` is tracked or listed.
- Given `docs/setup.md`, when a reader follows it, then every command is copy-runnable from the repository root and every step states why it exists.

## Implementation Notes

## Plan Change Log

## Review Triage Log

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
