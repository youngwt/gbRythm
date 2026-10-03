# Setting up the gbRythm development environment

These steps take a fresh checkout to a built Game Boy ROM and screenshots of it running. Run every command from the repository root.

Everything is installed into `tools/`, a folder inside the repository that git ignores. Nothing is installed system-wide, because SteamOS keeps its system partition read-only and wipes changes to it on OS updates. To start again, delete `tools/` and repeat these steps.

## What you need already

- `make`, `curl`, `tar` and `sha256sum`, which SteamOS provides.
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
| `tools/gbdk/` | GBDK-2020 4.5.0 | no |
| `tools/venv/` | Python environment with PyBoy | no |
| `build/` | The ROM, screenshots, C generated from images, and compiler output | no |
