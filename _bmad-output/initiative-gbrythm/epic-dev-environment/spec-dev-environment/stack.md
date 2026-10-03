# Stack

Tools, versions, machine facts, and C rules for SPEC-dev-environment. Versions were checked 2026-10-03; re-check GBDK and PyBoy after 2026-11-01.

## Tools

| Tool | Version | Used for | Capability | Get it from |
|---|---|---|---|---|
| GBDK-2020 | 4.5.0 (2025-12-28), Linux x64 binary | C compiler (SDCC), assembler, linker, libraries | CAP-1 | https://github.com/gbdk-2020/gbdk-2020/releases |
| `png2asset` | bundled with GBDK | PNG to C conversion | CAP-6 | inside GBDK |
| `make` | system, `/usr/bin/make` | Build driver | CAP-1 | already installed |
| PyBoy | 2.7.x | Headless emulator with Python API: button presses, frame stepping, screenshots, memory reads | CAP-2 | PyPI package `pyboy`, run through `uv` |
| `uv` | 0.12.22 | Runs Python tools without a system install | CAP-2 | already installed |
| Emulicious | current | Interactive emulator and debugger; needs Java | CAP-3 | https://emulicious.net/ |
| Emulicious Debugger | VS Code extension, last released 2023-11 | C source-level debugging | CAP-3 | https://github.com/Calindro/emulicious-debugger |
| Java runtime | unresolved (see spec Open Questions) | Runs Emulicious | CAP-3 | self-contained archive unpacked in the repository |

## Machine facts (verified 2026-10-03)

- Steam Deck, SteamOS, x86_64; `steamos-readonly` is enabled.
- The agent's terminal runs inside the VS Code Flatpak sandbox; `flatpak-spawn --host` reaches the host.
- No Java on the host or in the sandbox. No GBDK or SDCC installed.
- Python 3.13 and `make` are at `/usr/bin`.
- `/home` has 25 GB free.

## GBDK usage

- Install is download and unzip; projects start from a GBDK `template_` project and build with `make`.
- Debug builds pass `-Wf--max-allocs-per-node0` so stepping through C lines is easier.
- A ROM of 32K or less needs no mapper flags.
- Docs: https://gbdk.org/docs/api/docs_getting_started.html

## C rules on this hardware

From GBDK's coding guidelines (https://gbdk.org/docs/api/docs_coding_guidelines.html). These run against normal C habits.

- Prefer 8-bit unsigned values.
- No floating point.
- Avoid multiplication, division, and modulo except by powers of two.
- Prefer global variables to locals.
- No recursion.
