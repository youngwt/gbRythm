# Walkthrough: the dev environment so far (stories 1 and 2)

Target: everything built in stories 1 and 2. Story 1 is commit `1202fe1` ("builds first rom"); story 2 is the uncommitted changes on top of it.

**Current block: 1**

Each block is ticked only when you say you are satisfied with it.

---

## - [ ] Block 1: Intent (in progress)

Pasted verbatim from the two story plans: [story 1 plan](../epic-dev-environment/story-build-and-headless-run-a-minimal-rom-plan.md) and [story 2 plan](../epic-dev-environment/story-proof-rom-reacts-to-a-button-and-the-check-asserts-it-plan.md).

**Story 1**

> **Problem:** The repository has no Game Boy toolchain, no source, and no way for an agent to build a ROM or see what it does. Nothing else in the epic can start until one thin path from C source to a checked screenshot exists.
>
> **Approach:** Install GBDK-2020 4.5.0 and PyBoy 2.7.0 into a git-ignored `tools/` folder, add a minimal C program that prints text, a Makefile that builds it with one command, a headless script that runs the ROM and saves a screenshot, and written setup instructions that explain each step.

**Story 2**

> **Problem:** The proof ROM only prints text, and the headless check only confirms the screen is not blank. Neither shows that button input reaches the C program, and the check cannot tell a working ROM from a broken one.
>
> **Approach:** Make the ROM visibly change when a button is pressed, and extend the headless check to take a screenshot, press the button, take a second screenshot, and exit 0 only when the screen changed; update the setup instructions to match.

---

## - [ ] Block 2: Broad strokes (unvisited)

The repository now turns a C file into a Game Boy ROM and proves, without a window, that the ROM draws to the screen and responds to a button. There are four places to open, in this order:

1. [docs/setup.md](../../../docs/setup.md): the written steps that install the two tools and explain why each exists.
2. [Makefile](../../../Makefile): the two commands, `make` (build) and `make check` (run and verify).
3. [src/main.c](../../../src/main.c): the whole Game Boy program, 26 lines.
4. [scripts/check_rom.py](../../../scripts/check_rom.py): the script that runs the ROM in an emulator and compares screenshots.

---

## - [ ] Block 3: Where the tools live (unvisited)

Two tools were downloaded: GBDK-2020, which compiles C into a Game Boy ROM, and PyBoy, a Game Boy emulator that can be driven from Python with no window. Both sit in a `tools/` folder inside the repository that git ignores. Nothing is installed system-wide, because SteamOS resets its system partition on updates. Everything that uses a tool names its full path, so it does not matter what the VS Code terminal has on its PATH.

- [.gitignore:12-13](../../../.gitignore#L12-L13): `tools/` is ignored, so the downloads are never committed.
- [docs/setup.md:14-42](../../../docs/setup.md#L14-L42): GBDK is downloaded, checked against a published checksum, and unpacked.
- [docs/setup.md:44-62](../../../docs/setup.md#L44-L62): PyBoy is installed into its own Python environment, with versions pinned.
- [Makefile:4-6](../../../Makefile#L4-L6): the build names the compiler and the Python interpreter by path.

---

## - [ ] Block 4: The build (unvisited)

`make` compiles each C file in `src/` into an object file in `build/`, then links the objects into `build/gbrythm.gb`. GBDK's `lcc` command does both jobs. Keeping the output in `build/` stops the compiler's by-products from cluttering `src/`. If a compile fails, `make` stops with the compiler's message and does not leave a ROM behind that looks current.

- [Makefile:8-12](../../../Makefile#L8-L12): where the ROM goes and which files are sources.
- [Makefile:27-28](../../../Makefile#L27-L28): compile one C file to one object. Every object also depends on every header file, so changing a header always triggers a rebuild.
- [Makefile:22-23](../../../Makefile#L22-L23): link the objects into the ROM.
- [Makefile:14-16](../../../Makefile#L14-L16): delete a half-written output when a step fails.
- [Makefile:39-43](../../../Makefile#L39-L43): if a tool is missing, say so and point at the setup instructions.

---

## - [ ] Block 5: The Game Boy program (unvisited)

The program prints two lines of text, then loops forever. Each time round the loop it reads the buttons, and the first time it sees A held down it prints a third line. Then it waits for the screen to finish drawing before going round again, which makes the loop run once per frame, about 60 times a second. That once-per-frame loop is the basic shape every Game Boy game has.

- [src/main.c:5-6](../../../src/main.c#L5-L6): the variables are global and 8 bits wide. Both are GBDK's advice for this processor: 8-bit values are fast, and globals are cheaper than locals.
- [src/main.c:12](../../../src/main.c#L12): `printf` works because GBDK supplies a font and a text routine.
- [src/main.c:16-21](../../../src/main.c#L16-L21): `joypad()` returns the state of all eight buttons as one byte; `J_A` picks out the A button. `a_was_pressed` remembers the press so the line is printed once, not every frame while A is held.
- [src/main.c:24](../../../src/main.c#L24): `vsync()` pauses until the screen has finished drawing a frame.

---

## - [ ] Block 6: The headless check (unvisited)

`make check` runs the ROM in PyBoy with no window. It lets the ROM run for two seconds of Game Boy time and saves a screenshot, taps A, runs one more second, and saves a second screenshot. It passes only if the first screenshot is not blank and the second differs from the first. This is how an agent can tell a working ROM from a broken one without anyone looking at a screen.

- [Makefile:33-34](../../../Makefile#L33-L34): `make check` builds the ROM first if needed, then runs the script.
- [scripts/check_rom.py:38](../../../scripts/check_rom.py#L38): `window="null"` is what makes the emulator run with no display.
- [scripts/check_rom.py:40-48](../../../scripts/check_rom.py#L40-L48): run, screenshot, tap A, run, screenshot.
- [scripts/check_rom.py:52-59](../../../scripts/check_rom.py#L52-L59): the two failure tests, blank screen and unchanged screen.
- [scripts/check_rom.py:15-18](../../../scripts/check_rom.py#L15-L18): the frame counts, as named constants.

---

## - [ ] Block 7: Periphery (unvisited)

- [docs/setup.md:64-90](../../../docs/setup.md#L64-L90): how to build and check, and what the screenshots should show.
- [docs/setup.md:92-101](../../../docs/setup.md#L92-L101): table of what each folder is and whether git tracks it.
- [story 1 plan](../epic-dev-environment/story-build-and-headless-run-a-minimal-rom-plan.md): implementation notes and review log for story 1.
- [story 2 plan](../epic-dev-environment/story-proof-rom-reacts-to-a-button-and-the-check-asserts-it-plan.md): the same for story 2.
