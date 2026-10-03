---
id: SPEC-dev-environment
companions:
  - stack.md
sources:
  - ../../research-game-boy-dev-environment/research-game-boy-dev-environment.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# gbRythm dev environment and proof ROM

## Why

An opportunity to capture. gbRythm is a hobby learning project with no deadline: one user, new to Game Boy development, using a rhythm game as the vehicle for learning agentic development. Before the game can be specced or built, an agent needs an environment it can drive from the command line to build a ROM, run it, and check the result unaided. The user steps in when something breaks and wants the workings visible, not hidden.

## Capabilities

- **CAP-1**
  - **intent:** An agent can build a Game Boy ROM from C source with one command.
  - **success:** From a clean checkout with tools installed, the build command exits 0 and produces a `.gb` file; a deliberate C syntax error makes it exit non-zero with the compiler's message.
- **CAP-2**
  - **intent:** An agent can run the ROM without a display and check what it did.
  - **success:** A scripted run loads the ROM, advances frames, presses a button, and saves a screenshot with no window opened; it exits 0 on pass and non-zero on fail.
- **CAP-3**
  - **intent:** The user can play the ROM in an emulator and step through its C source in VS Code.
  - **success:** A breakpoint set on a C line in VS Code stops execution in the emulator and shows variable values.
- **CAP-4**
  - **intent:** The environment can be rebuilt from the repository's written instructions alone.
  - **success:** After removing the installed tools, following the documented steps on this machine gets CAP-1 and CAP-2 passing again.
- **CAP-5**
  - **intent:** A proof ROM shows the toolchain works end to end by drawing to the screen and reacting to a button.
  - **success:** The ROM shows something on boot and visibly changes when a button is pressed, confirmed by the CAP-2 script.
- **CAP-6**
  - **intent:** An image file in the repository becomes graphics the ROM displays, converted as part of the build.
  - **success:** The proof ROM shows a graphic sourced from a PNG in the repository; editing the PNG and rebuilding changes the CAP-2 screenshot with no hand-edited C.

## Constraints

- Toolchain is GBDK-2020 4.5.0, plain, with no game engine; code is C and follows the hardware rules in `stack.md`.
- Target is the original Game Boy (DMG); no Color-only features.
- Nothing installs to the system partition: SteamOS's root is read-only and reset by OS updates.
- All tools (GBDK, Java runtime, emulators) live inside the repository in a git-ignored folder; tool binaries are never committed, and their versions are pinned in the instructions.
- Everything works from the VS Code Flatpak terminal, where the agent runs; tools are located by explicit path or project setting, never by assuming PATH.
- CAP-1 and CAP-2 are command-line only and non-interactive: no window, click, or prompt.
- Headless testing uses PyBoy run through `uv`; interactive debugging uses Emulicious with its VS Code extension.
- Image conversion uses `png2asset`, bundled with GBDK; source images fit DMG limits (4 shades, 8×8 tiles).
- Setup instructions explain why each step exists, not only the command.
- The proof ROM is 32K or smaller with no mapper, so it runs on any flash cart later.

## Non-goals

- Music and sound, including hUGEDriver and its GBDK 4.5.0 compatibility check (later spec).
- Any gameplay: falling arrows, hit detection, scoring, songs.
- Finished game art; CAP-6 proves the conversion route only.
- Running on real hardware, and buying a flash cart.
- A one-command setup script.
- Setup on other machines or operating systems.
- Continuous integration.

## Success signal

- In a fresh agent session given only the repository, the agent builds the proof ROM with one command, runs the headless check, and reports a pass with a screenshot showing a PNG-sourced graphic and a change after a button press. Separately, the user sets a breakpoint on a C line in VS Code and sees execution stop there in Emulicious.

## Assumptions

- Python is accepted for the headless test script because PyBoy's API is Python; the user prefers .NET where a choice exists, and no .NET alternative was researched.
- CAP-3 is verified by the user by hand; the agent cannot operate the VS Code debugger.

## Open Questions

- Which Java version does Emulicious need, and does a Java runtime unpacked inside the repository run and open a window from the VS Code Flatpak sandbox, or must it launch on the host via `flatpak-spawn`?
- Does the Emulicious VS Code debugger extension (last released 2023-11) still work with current Emulicious and VS Code?
- Is PyBoy accurate enough for the proof ROM checks? Its screenshot should be compared against Emulicious.
- Is there a headless Game Boy emulator drivable from .NET that would let the test script honour the user's .NET preference?
