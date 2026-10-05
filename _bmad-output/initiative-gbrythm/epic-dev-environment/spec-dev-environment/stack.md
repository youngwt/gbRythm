# Stack

Tools, versions, machine facts, and C rules for SPEC-dev-environment. Versions were checked 2026-10-03 and updated to what is installed on 2026-10-04; re-check GBDK and PyBoy after 2026-11-01. `docs/setup.md` holds the download addresses and checksums.

## Tools

| Tool | Version | Used for | Capability | Get it from |
|---|---|---|---|---|
| GBDK-2020 | 4.5.0 (2025-12-28), Linux x64 binary | C compiler (SDCC), assembler, linker, libraries | CAP-1 | https://github.com/gbdk-2020/gbdk-2020/releases |
| `png2asset` | bundled with GBDK | PNG to C conversion | CAP-6 | inside GBDK |
| `make` | system, `/usr/bin/make` | Build driver | CAP-1 | already installed |
| PyBoy | 2.7.0, with Pillow 12.3.0 and NumPy 2.5.3 | Headless emulator with Python API: button presses, frame stepping, screenshots, memory reads | CAP-2 | PyPI package `pyboy`, run through `uv` |
| `uv` | 0.12.22 | Runs Python tools without a system install | CAP-2 | already installed |
| Emulicious | release 2026-03-27; one unversioned download, pinned by checksum | Interactive emulator and debugger; needs Java | CAP-3 | https://emulicious.net/ |
| Emulicious Debugger | VS Code extension 1.3.0 (2023-11); works with VS Code 1.139.1 | C source-level debugging | CAP-3 | https://github.com/Calindro/emulicious-debugger |
| Java runtime | Eclipse Temurin 21 JRE, 21.0.12.1+1; Emulicious needs Java 6 or newer | Runs Emulicious | CAP-3 | https://adoptium.net/, unpacked in the repository |
| hUGEDriver | 6.1.3, packaged library | Music driver | music-proof spec, CAP-1 | https://github.com/SuperDisk/hUGEDriver/releases |

## Machine facts (verified 2026-10-03)

- Steam Deck, SteamOS, x86_64; `steamos-readonly` is enabled.
- The agent's terminal runs inside the VS Code Flatpak sandbox; `flatpak-spawn --host` reaches the host.
- No Java on the host or in the sandbox. No GBDK or SDCC installed.
- The sandbox has no X11 display. Java started there cannot open a window; started on the host with `flatpak-spawn --host` it can. `scripts/java-host.sh` does this.
- Python 3.13 and `make` are at `/usr/bin`.
- `/home` has 25 GB free.

## GBDK usage

- Install is download and unzip; projects start from a GBDK `template_` project and build with `make`.
- Debug builds pass `-debug -Wf--max-allocs-per-node0` so stepping through C lines is easier. They are a separate ROM in `build/debug`; the ROM that is checked is built without those flags.
- A ROM of 32K or less needs no mapper flags.
- Docs: https://gbdk.org/docs/api/docs_getting_started.html

## C rules on this hardware

From GBDK's coding guidelines (https://gbdk.org/docs/api/docs_coding_guidelines.html). These run against normal C habits.

- Prefer 8-bit unsigned values.
- No floating point.
- Avoid multiplication, division, and modulo except by powers of two.
- Prefer global variables to locals.
- No recursion.
