# gbRythm

A rhythm game for the original Game Boy, written in C with GBDK-2020. So far the repository holds the development environment and the start of the game: press Start and the song plays once, its notes fall in five lanes, presses are judged perfect, good or miss, and the results follow.

**[Play it in your browser](https://youngwt.github.io/gbRythm/)** (needs a keyboard), or **[download the latest release](https://github.com/youngwt/gbRythm/releases/latest)** and open `gbrythm.gb` in any Game Boy emulator.

## Start here

Follow [docs/setup.md](docs/setup.md) once to install the tools. The same document explains how to play and how each part of the game works. They go into `tools/`, a folder git ignores, so a fresh checkout has none.

Then, from the repository root:

| Command | What it does |
|---|---|
| `make` | Builds the ROM, `build/gbrythm.gb` |
| `make check` | Builds, then runs the ROM with no window and reports `PASS` or `FAIL`; a screenshot lands in `build/` |
| `make check-debug` | The same check on the debug ROM, the one F5 runs |
| `make run` | Builds, then opens the ROM in Emulicious to play |
| `make page` | Builds, then assembles the page that plays the ROM in a browser, in `build/page/` |
| `make clean` | Deletes `build/` |

`make` and `make check` need no display and no interaction, so an agent can run them unaided. To step through the C source, press F5 in VS Code; `docs/setup.md` explains how that works.

## Layout

- `src/` — C source for the ROM, including the song in `song.c`
- `assets/` — PNG images, converted to C by the build
- `web/` — the page that plays the ROM in a browser
- `scripts/` — the headless check, the image converter's wrapper, and a helper that starts Java
- `docs/setup.md` — installing the tools, with the reason for each step, and how the images and the music work
- `_bmad-output/` — specs, plans and tickets

## Licence

The project's code is under the [MIT licence](LICENSE). The ROM also contains library code from GBDK-2020 and hUGEDriver; `docs/setup.md`, under "What was found", says what their terms are.
