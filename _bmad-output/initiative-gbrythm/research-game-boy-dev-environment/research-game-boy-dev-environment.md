---
title: 'Technical research: Game Boy dev environment'
type: 'technical'
topic: 'Game Boy dev environment'
decision: 'Which development environment (toolchain, music tooling, emulator, flash cart) to set up for a C rhythm game on the original Game Boy, built on Linux with VS Code'
source: 'native run'
status: complete
preset: 'standard'
validation: 'normal'
claims_verified: 6
claims_unverified: 2
claims_disputed: 1
created: '2026-10-03'
updated: '2026-10-03'
---

# Technical research: Game Boy dev environment

**Decision this research serves:** Which development environment (toolchain, music tooling, emulator, flash cart) to set up for a C rhythm game on the original Game Boy, built on Linux with VS Code.

## Executive summary

**Set up GBDK-2020 4.5.0 with the hUGEDriver music driver, test in Emulicious and PyBoy, and buy an EverDrive-GB X3 or X5.**

Three findings drive that answer:

1. **GBDK-2020 is the only maintained C toolchain found for the Game Boy.** It ships Linux binaries, installs by unzipping, builds with `make`, and is actively developed [1][2]. The only other candidate that passes the "written in C" gate is CrossZGB, an engine built on top of GBDK [7].
2. **The hard part of a rhythm game is already solved in the open.** hUGEDriver plays music from a GBDK C program and has a "call routine" effect that runs your C function at chosen points in the song [9]. A GBDK maintainer published a small falling-note rhythm game that uses exactly this to spawn notes [11]. Songs export as plain C source files, which an agent can read and edit [10].
3. **A Game Boy cartridge flash cart will run in your GBA.** The original GBA and GBA SP play Game Boy cartridges; the Game Boy Micro does not [22]. EverDrive-GB carts cost $44 (X3), $59 (X5) and $134 (X7) from the maker [19].

**Biggest caveat:** the prebuilt music driver library was built against GBDK 4.1.1, and the rhythm example targets GBDK 4.0 [10][11]. Whether both work unchanged with GBDK 4.5.0 is unverified. Make "build a ROM that plays a hUGEDriver song" the first thing you build, before any game code.

**This is a selection report. Refresh it before acting on it after about April 2027.**

## 1. The field of toolchains

Requirements frame, agreed before research: builds on Linux from a command line; game code in C; ROM runs on an original Game Boy from a flash cart; music and input timing good enough for a rhythm game. Weighted preferences: beginner-friendly, agent-friendly and music workflow (high); VS Code fit and project health (medium); exit cost (low).

| Candidate | What it is | Outcome |
|---|---|---|
| **GBDK-2020** | C compiler (SDCC), assembler, linker and libraries [8] | **Finalist** |
| **CrossZGB** | Game engine on top of GBDK-2020; v2026.1 released 2026-03-13 [7] | **Finalist** |
| GB Studio | Drag-and-drop game creator with visual scripting; engine C code reachable only through plugins [6] | Cut: game is not written in C. Wildcard only |
| RGBDS | Assembly toolchain; v1.0.4 released 2026-09-22 [5] | Cut: assembly, not C |
| ZGB | Original C engine on GBDK; last release 2023-08, last push 2024-08 [7] | Cut: stale, superseded by CrossZGB |
| llvm-gbz80, gbdk-go, gbforth, Wiz, Turbo Rascal | Listed by gbdev.io [8] | Cut: not C, or no maintained repository located (low confidence, not investigated further) |

No second maintained C compiler for the Game Boy was found. That is an absence of evidence from a short search, not proof.

## 2. Finalists against the frame

Scores are 1–5. Weights: high = 3, medium = 2, low = 1.

| Criterion | Weight | GBDK-2020 | CrossZGB |
|---|---|---|---|
| Beginner-friendly | 3 | 4 | 3 |
| Agent-friendly | 3 | 5 | 4 |
| Music workflow | 3 | 4 | 4 |
| VS Code fit | 2 | 4 | 3 |
| Project health | 2 | 5 | 4 |
| Easy to leave | 1 | 4 | 2 |
| **Weighted total (max 70)** | | **61** | **49** |

**GBDK-2020 evidence.** Latest stable 4.5.0, published 2025-12-28, with Linux x64 and ARM64 binaries; previous releases 2025-05 and 2024-03; repository last pushed 2026-09-30 [1]. Setup is: download, unzip, run `make` in the examples folder, then copy a `template_` project [2]. The documentation links tutorials, a CI builder and a VS Code debugging path [4].

**CrossZGB evidence is thin.** Only repository metadata was read: 73 stars, release v2026.1, pushed 2026-09 [7]. Its documentation, music support and learning curve were not examined, so its scores are estimates (low confidence). It loses mainly on the reasoning that an engine adds a layer to learn and to leave, which matters more for a first project than the scaffolding it provides.

**What C costs you on this hardware.** GBDK's own guidelines: prefer 8-bit unsigned values; no floating point; avoid multiplication, division and modulo except by powers of two; prefer global variables to locals; no recursion; write performance-critical functions in assembly [3]. These are constraints an agent must be told about, since they run against normal C habits.

## 3. Music and timing

**Driver.** hUGEDriver is the driver GBDK's documentation describes as "smaller, more efficient and more versatile than gbt_player" [4]. Use from C is `hUGE_init(&song)` once, then `hUGE_dosound` at a regular interval, normally registered on the vertical-blank interrupt with `add_VBL` [9][10]. Both tracker and driver are public domain [9].

**Songs are text.** hUGETracker exports a song as a C source file made of rows such as `DN(C_5,1,0x2FF)` (note, instrument, effect) [10]. A song is 64-row patterns [9]. A simple melody like "Amazing Grace" can therefore be written or edited directly as text, without the tracker.

**Sync.** Effect 6 is "Call routine" [9]. In the published rhythm example, each routine is a C function that sets a "pending note" flag, and the game loop turns that flag into a falling sprite [11]. GB Studio documents the same mechanism for running scripts in time with music [13] (medium confidence: search summary only).

**Timing source.** The Game Boy timer can interrupt at rates derived from 4096, 16384, 65536 or 262144 Hz [14], and the driver may be called from the timer interrupt instead of vertical blank [9]. No measured latency or jitter figures for a C rhythm game were found.

**Tracker on Linux.** hUGETracker v1.0.11 (2024-12-29) ships a Linux build [12]. No command-line converter from the tracker's own `.uge` file to C was found.

**Compatibility gap.** The v6.1.3 release (2024-07-14) includes a prebuilt `hUGEDriver.lib`, built in CI against GBDK 4.1.1 and RGBDS 0.6.1; the repository has newer, unreleased commits from 2025 and 2026 [10]. Whether that library links with GBDK 4.5.0 is **unverified**. If it does not, rebuilding it needs RGBDS as well [10].

## 4. Surrounding tools

| Need | Tool | Evidence |
|---|---|---|
| Interactive emulator and debugger | **Emulicious** | Runs on Linux via Java; breakpoints, profiler, remote debugging [15]. Its VS Code extension gives C source-level debugging [4][16]. The extension was last released 2023-11 [16] |
| Automated testing by an agent | **PyBoy** | `pip install pyboy`; headless; Python API for button presses, frame stepping, screenshots and memory reads [17]. Single source, accuracy and sound not assessed (unverified) |
| Graphics conversion | `png2asset`, bundled with GBDK | Converts PNG files to C [1] |
| ROM size checking | romusage | Reports bank usage and overflows [4] |
| Second-opinion emulator | mGBA 0.10.5 | Linux AppImage available [17] |

For debug builds, GBDK's documentation recommends `-Wf--max-allocs-per-node0` to make stepping through C easier [4].

## 5. Flash carts

**Use a Game Boy cartridge, not a GBA one.** The original GBA and GBA SP play Game Boy and Game Boy Color cartridges; the Micro does not [22] (secondary sources).

| Cart | Price | Notes |
|---|---|---|
| **EverDrive-GB X3** | $44 [19] | Saves need a reboot to the menu to be written to the SD card [19] |
| **EverDrive-GB X5** | $59 [19] | Same as X7 without save states, in-game menu and clock [19] |
| EverDrive-GB X7 | $134 [19] | Adds save states and a clock [19] |
| EZ-Flash Junior | **Disputed**: $53.97 at one reseller [20]; $59.99 in a 2021 review [21]; one listicle says $25–35 (low confidence) | Has a clock; does not work with Super Game Boy; a 2021 reviewer expected no further firmware updates [21] |

All EverDrive-GB X carts and the EZ-Flash Junior support mappers MBC1, MBC2, MBC3 and MBC5 with microSD storage [19][20]. Stock status at the maker's store could not be read.

**What the ROM needs.** A ROM of 32K or less needs no mapper. Beyond that, GBDK recommends MBC5, set with `-Wm-yt`, `-Wm-yo` and `-Wm-ya` [18]. Either choice is supported by every cart above [19][20].

## Cross-dimension insights

- **Agent-friendliness and the music workflow reinforce each other.** Because songs are C source [10] and sync points are effects inside that source [9], the song and its note chart can live in one text file that an agent edits and a build verifies.
- **The best-maintained piece and the least-maintained piece meet at the riskiest point.** GBDK is current [1]; the music driver's last packaged release is from 2024 [10] and the reference rhythm game from 2023 [11]. The integration between them is where a first build is most likely to fail.
- **Target and cart choice are decoupled.** A plain original-Game-Boy ROM runs on every cart considered [19][20], so the cart purchase does not constrain any code decision and can wait.

## Recommendations

1. **Toolchain: GBDK-2020 4.5.0, no engine.** Feeds the spec's technical constraints. Basis: verified version and activity [1]; CrossZGB comparison rests on low-confidence estimates.
   - *Runner-up:* CrossZGB wins if the game grows to many screens and sprite types and you want scene and sprite management provided.
   - *Strongest argument against:* SDCC's C is slow and restrictive [3], and a rhythm game is timing-sensitive; assembly (RGBDS) gives exact control. No red-team pass was run.
   - *Cheapest hedge:* keep the music driver and timing code behind one small C module, so it can be replaced with assembly without touching game logic.
2. **Music: hUGEDriver, with songs kept as C source and note spawning driven by call-routine effects.** Basis: verified from driver source and a working example [9][10][11].
3. **First build story: a ROM that plays a short hUGEDriver song under GBDK 4.5.0.** This resolves the one unverified claim the plan rests on [10].
4. **Testing: Emulicious for you, PyBoy for the agent.** Basis: Emulicious verified [15][4]; PyBoy single-source (unverified) [17].
5. **Flash cart: EverDrive-GB X5 at $59; X3 at $44 if the save limitation does not bother you.** Basis: maker's own prices and specifications [19]. The EZ-Flash Junior is a reasonable alternative at a similar price, but its price evidence is disputed and its firmware status rests on one 2021 review [20][21]. Buying can wait until the game runs in an emulator.

## Open questions

| Question | How to answer it |
|---|---|
| Does the prebuilt `hUGEDriver.lib` link with GBDK 4.5.0? | Build the driver's GBDK example; ten minutes |
| Is C timing tight enough for satisfying hit detection? | Prototype one falling arrow with a hit window and play it |
| Is PyBoy accurate enough, and does it expose audio, for automated tests? | Run the first ROM in it and compare with Emulicious |
| Does CrossZGB bundle music support and good documentation? | A Deepen pass on CrossZGB alone |
| How do GBA-slot flash carts run Game Boy ROMs? | Not researched; only relevant if you want one cart for both systems |
| Shipping, import cost and trustworthy sellers for your country | Check the maker's store and a local reseller at purchase time |
| Is there a text or command-line route from `.uge` files to C? | Search hUGETracker's repository and issue tracker |

## Source appendix

| Ref | Supports | Publisher | Published | Accessed | Confidence |
|---|---|---|---|---|---|
| [1] | GBDK-2020 releases, binaries, activity, png2asset | [GitHub, gbdk-2020](https://github.com/gbdk-2020/gbdk-2020/releases) | 2025-12 | 2026-10-03 | high |
| [2] | GBDK install and template workflow | [GBDK docs, Getting Started](https://gbdk.org/docs/api/docs_getting_started.html) | undated | 2026-10-03 | high |
| [3] | C restrictions and performance guidance | [GBDK docs, Coding Guidelines](https://gbdk.org/docs/api/docs_coding_guidelines.html) | undated | 2026-10-03 | high |
| [4] | Recommended music, debugging and CI tools | [GBDK docs, Links and Tools](https://gbdk.org/docs/api/docs_links_and_tools.html) | undated | 2026-10-03 | high |
| [5] | RGBDS version and activity | [GitHub, gbdev/rgbds](https://github.com/gbdev/rgbds/releases) | 2026-09 | 2026-10-03 | high |
| [6] | GB Studio is visual, C via plugins | [GB Studio docs](https://www.gbstudio.dev/docs/) | undated | 2026-10-03 | medium |
| [7] | ZGB stale; CrossZGB active | [GitHub, gbdk-2020/CrossZGB](https://github.com/gbdk-2020/CrossZGB) and [Zal0/ZGB](https://github.com/Zal0/ZGB) | 2026-03 | 2026-10-03 | high |
| [8] | List of compilers and engines | [gbdev.io resources](https://gbdev.io/resources.html) | undated | 2026-10-03 | medium |
| [9] | hUGEDriver usage, effects, licence | [GitHub, SuperDisk/hUGEDriver](https://github.com/SuperDisk/hUGEDriver) | 2026-08 | 2026-10-03 | high |
| [10] | Song C format, prebuilt library, CI versions | [hUGEDriver GBDK example and v6.1.3 release](https://github.com/SuperDisk/hUGEDriver/releases) | 2024-07 | 2026-10-03 | high |
| [11] | Working C rhythm game using routines | [GitHub, untoxa/rhythm](https://github.com/untoxa/rhythm) | 2023-02 | 2026-10-03 | high |
| [12] | hUGETracker Linux build | [GitHub, SuperDisk/hUGETracker](https://github.com/SuperDisk/hUGETracker/releases) | 2024-12 | 2026-10-03 | high |
| [13] | Music routines trigger scripts | [GB Studio docs, hUGE Driver](https://www.gbstudio.dev/docs/assets/music/music-huge) | undated | 2026-10-03 | medium |
| [14] | Timer frequencies | [Pan Docs, Timer and Divider Registers](https://gbdev.io/pandocs/Timer_and_Divider_Registers.html) | undated | 2026-10-03 | high |
| [15] | Emulicious platforms and debugger | [emulicious.net](https://emulicious.net/) | 2026-03 | 2026-10-03 | high |
| [16] | VS Code debugger extension release | [GitHub, Calindro/emulicious-debugger](https://github.com/Calindro/emulicious-debugger) | 2023-11 | 2026-10-03 | high |
| [17] | PyBoy API; mGBA Linux build | [GitHub, Baekalfen/PyBoy](https://github.com/Baekalfen/PyBoy) and [mgba-emu/mgba](https://github.com/mgba-emu/mgba/releases) | 2026-05 | 2026-10-03 | medium |
| [18] | Mapper guidance and flags | [GBDK docs, ROM/RAM Banking and MBCs](https://gbdk.org/docs/api/docs_rombanking_mbcs.html) | undated | 2026-10-03 | high |
| [19] | EverDrive-GB prices and features | [Krikzz store, EverDrive-GB X5](https://krikzz.com/our-products/cartridges/everdrive-gb-x5.html) | 2026-10 | 2026-10-03 | high |
| [20] | EZ-Flash Junior price and features | [ezflashomega.com (reseller)](https://www.ezflashomega.com/products/EZ-Flash-Junior.html) | 2026-10 | 2026-10-03 | medium |
| [21] | EZ-Flash Junior review | [GB Studio Central](https://gbstudiocentral.com/spotlight/ez-flash-junior/) | 2021-06 | 2026-10-03 | low (stale) |
| [22] | GBA plays Game Boy cartridges | [Wikipedia, Game Boy Game Pak](https://en.wikipedia.org/wiki/Game_Boy_Game_Pak) | undated | 2026-10-03 | medium |

## Staleness map

| Claim | Class | Re-check by |
|---|---|---|
| Emulicious and its VS Code debugger are maintained | ecosystem | **2026-09-01 (already due)**: the source is dated 2026-03 |
| GBDK-2020 4.5.0 is the latest stable release | version | 2026-11-01 |
| hUGEDriver v6.1.3 is the latest packaged release | version | 2026-11-01 |
| PyBoy headless API (v2.7.x) | ecosystem | 2026-11-01 |
| EverDrive-GB prices | pricing | 2027-01-01 |
| EZ-Flash Junior price | pricing | 2027-01-01 |
| GBDK-2020 is the only maintained C toolchain | landscape | 2027-10-01 |

Earliest re-check: the Emulicious claim is already past its window. Version claims are next, on 2026-11-01.

## Method notes

Run by a single researcher without assistants. No red-team pass, no independent citation re-read, and no HTML briefing were produced. One fetched summary of the GBDK releases page gave release dates a year early; the GitHub API was used instead.
