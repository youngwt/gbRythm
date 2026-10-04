# gbRythm

A rhythm game for the original Game Boy, written in C with GBDK-2020. So far the repository holds the development environment and a small proof ROM; the game itself is not started.

## Start here

Follow [docs/setup.md](docs/setup.md) once to install the tools. They go into `tools/`, a folder git ignores, so a fresh checkout has none.

Then, from the repository root:

| Command | What it does |
|---|---|
| `make` | Builds the ROM, `build/gbrythm.gb` |
| `make check` | Builds, then runs the ROM with no window and reports `PASS` or `FAIL`; screenshots land in `build/` |
| `make run` | Builds, then opens the ROM in Emulicious to play |
| `make clean` | Deletes `build/` |

`make` and `make check` need no display and no interaction, so an agent can run them unaided. To step through the C source, press F5 in VS Code; `docs/setup.md` explains how that works.

## Layout

- `src/` — C source for the ROM, including the song in `song.c`
- `assets/` — PNG images, converted to C by the build
- `scripts/` — the headless check, and a helper that starts Java
- `docs/setup.md` — installing the tools, with the reason for each step, and how the images and the music work
- `_bmad-output/` — specs, plans and tickets
