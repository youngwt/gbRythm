# Setting up the gbRythm development environment

These steps take a fresh checkout to a built Game Boy ROM and screenshots of it running, and then to playing and debugging it in an emulator. Run every command from the repository root.

Everything is installed into `tools/`, a folder inside the repository that git ignores. Nothing is installed system-wide, because SteamOS keeps its system partition read-only and wipes changes to it on OS updates. To start again, delete `tools/` and repeat these steps.

## What you need already

- `make`, `curl`, `tar`, `unzip` and `sha256sum`, which SteamOS provides.
- [`uv`](https://docs.astral.sh/uv/), which manages the Python environment. Check with `uv --version`.

These must be reachable from the terminal you use. The VS Code Flatpak terminal has its own PATH, so check there if that is where you work.

## 1. Install GBDK-2020 (the compiler)

GBDK-2020 turns C source into a Game Boy ROM. It bundles the SDCC compiler, an assembler, a linker and the Game Boy libraries, with `lcc` as the single command that drives them. The version is pinned to 4.5.0 so every build uses the same compiler.

Download the Linux release:

```sh
mkdir -p tools
curl -sSL -o tools/gbdk-linux64.tar.gz https://github.com/gbdk-2020/gbdk-2020/releases/download/4.5.0/gbdk-linux64.tar.gz
```

Check the download is the file the GBDK project published. This catches a corrupt or tampered download before you run it; it must print `OK`:

```sh
echo "d7857a5f6d135ee4c249043ca26aad9f2ec8ab5d4106d97720d404114f42605c  tools/gbdk-linux64.tar.gz" | sha256sum -c -
```

Unpack it and remove the archive. The archive contains one folder, `gbdk/`, so this creates `tools/gbdk/`:

```sh
tar -xzf tools/gbdk-linux64.tar.gz -C tools
rm tools/gbdk-linux64.tar.gz
```

Confirm the compiler runs; it prints a version line dated 2025/12/28:

```sh
tools/gbdk/bin/lcc -v
```

## 2. Install PyBoy (the headless emulator)

PyBoy is a Game Boy emulator controlled from Python. It can run a ROM with no window, which lets an agent run the game and look at the screen without a person present.

Create a Python environment inside `tools/`. A separate environment keeps PyBoy and its dependencies out of the system Python and inside the folder you can delete:

```sh
uv venv tools/venv
```

`uv` uses the system's Python (3.13 here) for the environment, and downloads one itself if it finds none.

Install PyBoy and Pillow at pinned versions. Pillow is the image library PyBoy uses to hand over the screen as a picture:

```sh
uv pip install --python tools/venv/bin/python pyboy==2.7.0 pillow==12.3.0
```

`uv` may warn that hardlinking is not supported across filesystems. That is harmless: it copies the files instead.

## 3. Build the ROM

```sh
make
```

This converts each image in `assets/` to C (see "Adding or changing an image" below), compiles `src/*.c`, and writes the ROM to `build/gbrythm.gb`. The `Makefile` calls the compiler by its path in `tools/gbdk`, so it does not matter what is on your PATH. If a compile fails, `make` stops with the compiler's message, which names the file and line.

`make clean` deletes `build/`.

## 4. Run the headless check

```sh
make check
```

This builds the ROM if needed and runs it in PyBoy with no window. The check:

1. runs the ROM for 120 frames (about two seconds of Game Boy time) and saves the screen to `build/screenshot-before.png`;
2. taps the A button, runs 60 more frames, and saves the screen to `build/screenshot-after.png`;
3. compares the two.

It prints `PASS` and exits 0 when the screen changed. It prints `FAIL` and exits non-zero if the ROM is missing, the screen is blank, or pressing A changed nothing. Comparing before and after is what proves button input reaches the C program: a ROM that ignores the button fails.

PyBoy prints a warning about "SDL2 binaries from pysdl2-dll". It is informational and can be ignored.

Open the two screenshots to see what the ROM drew. Before shows `GBRYTHM` and `PRESS A` with a down arrow below them, drawn from `assets/arrow.png`; after adds a third line, `A PRESSED`.

## 5. Install Java (to run Emulicious)

Steps 5 to 8 set up an emulator with a window, so you can play the ROM and step through its C source. Building and `make check` do not need them.

Emulicious, the emulator installed in the next step, is a Java program, and SteamOS has no Java. This step unpacks a Java runtime into `tools/`. It is Eclipse Temurin 21, a free build of Java, in its "JRE" form, which runs Java programs and leaves out the developer tools.

Download it and check it is the file that was published; the check must print `OK`:

```sh
curl -sSL -o tools/java.tar.gz "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jre_x64_linux_hotspot_21.0.12.1_1.tar.gz"
echo "2413149700df0f7d440500a84a8f764c535f21e5a5e87d38328b64eec2c5b500  tools/java.tar.gz" | sha256sum -c -
```

Unpack it and remove the archive. The archive's top folder has the version in its name, so `--strip-components=1` drops that folder and puts the contents straight into `tools/java/`, a path that stays the same when the version changes:

```sh
mkdir -p tools/java
tar -xzf tools/java.tar.gz -C tools/java --strip-components=1
rm tools/java.tar.gz
```

Confirm it runs; it prints a version starting `21.0.12`:

```sh
tools/java/bin/java -version
```

## 6. Install Emulicious (the emulator with a debugger)

Emulicious is a Game Boy emulator with a window, and it has a debugger that VS Code can drive. PyBoy stays the emulator for automated checks; Emulicious is the one you look at.

Download it:

```sh
curl -sSL -o tools/emulicious.zip "https://emulicious.net/download/emulicious/?wpdmdl=205"
```

Emulicious publishes only its latest version, at one address, so there is no version number to pin. The checksum below is for the release dated 2026-03-27, downloaded 2026-10-04. It must print `OK`:

```sh
echo "6e1c6d511014033bbc2668360a0194389a5bad2bf6c5ffd0fe093b84da33c0fc  tools/emulicious.zip" | sha256sum -c -
```

If it prints `FAILED`, Emulicious has most likely released a new version. Check the date at https://emulicious.net/, and if there is a newer release, carry on and then update the checksum and date in this file. The debugging steps below were only tested with the 2026-03-27 release.

Unpack it and remove the archive:

```sh
mkdir -p tools/emulicious
unzip -q tools/emulicious.zip -d tools/emulicious
rm tools/emulicious.zip
```

## 7. Play the ROM

```sh
make run
```

This builds the ROM if needed and opens it in an Emulicious window. Emulicious's Options menu shows which keys act as the Game Boy's buttons and lets you change them.

`make run` starts Java through `scripts/java-host.sh` instead of directly. The reason is the VS Code Flatpak: programs started from its terminal run in a sandbox that has no X11 display, and Java needs one to open a window. The script asks Flatpak to start Java on the host, outside the sandbox, with `flatpak-spawn --host`. Outside a Flatpak it just runs Java.

## 8. Step through the C source in VS Code

This lets you stop the running ROM on a line of C and look at the variables.

Install the Emulicious Debugger extension, version 1.3.0. VS Code offers it when you open this folder, because `.vscode/extensions.json` recommends it, or install it from the terminal:

```sh
code --install-extension emulicious.emulicious-debugger
```

Then:

1. Open `src/main.c` and click to the left of a line number to set a breakpoint, shown as a red dot. Line 27, `a_was_pressed = 1;`, is a good first one: it only runs when A is pressed.
2. Press F5.
3. An Emulicious window opens with the ROM running. Press A in it.
4. VS Code stops on line 27. The Variables panel and hovering over `keys` or `a_was_pressed` show their values. F10 steps to the next line and F5 continues.

What F5 does is set out in `.vscode/launch.json`, with the build step in `.vscode/tasks.json`:

- It first runs `make debug`, which builds a second ROM in `build/debug/`. That build adds two compiler flags. `-debug` writes `gbrythm.cdb`, the file that tells the debugger which machine code came from which line of C. `-Wf--max-allocs-per-node0` turns off an optimisation that reorders code, so stepping follows the source line by line. The second flag makes the code bigger and slower, so the debug ROM is kept separate: the ROM that `make check` tests is always the normal one.
- It then starts Emulicious through `scripts/java-host.sh`, for the reason given in step 7, and connects to it on port 58870.

The extension tries to connect every tenth of a second and by default gives up after 25 tries, which a slow start of Java can exceed. `.vscode/settings.json` raises that to 100, about ten seconds. If F5 still reports that it could not connect, press F5 again.

## What was found

Two questions were open when this environment was planned. These are the answers, found on 2026-10-04.

**Which Java does Emulicious need, and can it open a window from the VS Code Flatpak?** Emulicious's `ReadMe.txt` says "Java 6 or newer", so any current Java works; Temurin 21, a long-term-support release, was chosen. Java unpacked inside the repository runs in the sandbox, but cannot open a window there: started from the Flatpak terminal, Emulicious fails with `HeadlessException: No X11 DISPLAY variable was set`, and setting `DISPLAY=:0` by hand fails with "Authorization required". Started on the host with `flatpak-spawn --host`, the same Java and the same files run without that error. So Java must launch on the host, which is what `scripts/java-host.sh` does. One trap: in the sandbox Emulicious still opens its debugger port even though it has no window, so a successful connection does not prove the window appeared.

**Does the Emulicious VS Code debugger extension, last released 2023-11, still work?** Version 1.3.0 installs without complaint on VS Code 1.139.1 from the marketplace. The extension is small: it starts Emulicious and hands VS Code the port, and Emulicious itself does the debugging, so the extension's age matters less than Emulicious's, which was last released 2026-03-27 and lists remote-debugger fixes in its `WhatsNew.txt`. The check that matters needs a person: on 2026-10-04 the user set a breakpoint in `src/main.c`, pressed F5, and reported that it worked. So yes, it still works.

A third question, whether PyBoy's picture matches Emulicious's closely enough to trust the headless check, has not been answered yet; it is recorded as deferred work.

## Adding or changing an image

The Game Boy cannot display a picture file. Its screen is built from 8×8 pixel squares called tiles, and a program supplies two things: the tiles themselves, and a map saying which tile goes at each position. GBDK's `png2asset` tool turns a PNG into exactly that pair, written as C.

The build runs it for you. Every `assets/NAME.png` becomes `build/NAME.c` and `build/NAME.h`, and the C program includes `NAME.h` to get the tiles (`NAME_tiles`), the map (`NAME_map`) and the sizes. The generated files are build output: they are not committed and are never edited by hand. To change what is on screen, edit the PNG and run `make`; it notices the PNG changed and reconverts it.

An image must fit what the original Game Boy can show:

- **Width and height are multiples of 8 pixels**, because the screen is made of 8×8 tiles.
- **At most four shades.** The original Game Boy has four: white, light grey, dark grey and black. Use `#FFFFFF`, `#AAAAAA`, `#555555` and `#000000`.
- **No larger than the screen**, which is 160×144 pixels.

If an image breaks the first two rules, `make` stops and prints the converter's error. The converter itself exits successfully even when it reports an error, so the `Makefile` checks its output; its full output is kept in `build/NAME.c.log`.

One limit to know about: the build gives every image tile numbers starting at 128, to stay clear of the text font in the lower numbers. That is fine for one image. Two images shown at once would overwrite each other's tiles, so a second image needs its own starting number.

## Where things are

| Path | What it is | In git? |
|---|---|---|
| `src/` | C source for the ROM | yes |
| `assets/` | PNG images shown by the ROM | yes |
| `Makefile` | Build and check commands | yes |
| `scripts/check_rom.py` | The headless check | yes |
| `scripts/java-host.sh` | Starts Java on the host so it can open a window | yes |
| `.vscode/` | VS Code debug configuration | yes |
| `tools/gbdk/` | GBDK-2020 4.5.0 | no |
| `tools/venv/` | Python environment with PyBoy | no |
| `tools/java/` | Java runtime, Temurin 21 | no |
| `tools/emulicious/` | Emulicious | no |
| `build/` | The ROM, screenshots, C generated from images, and compiler output | no |
| `build/debug/` | The debug ROM and its `.cdb` debug symbols | no |
