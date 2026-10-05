- source_plan: `_bmad-output/initiative-gbrythm/epic-dev-environment/story-a-png-becomes-graphics-on-screen-plan.md`
  summary: The build converts every PNG in `assets/` with tile origin 128, so two background images shown at once would overwrite each other's tiles.
  evidence: The Makefile's png2asset rule passes a fixed `-tile_origin 128`; the proof ROM has one image so it does not occur yet, but the game will need several.
- source_plan: `_bmad-output/initiative-gbrythm/epic-dev-environment/story-step-through-c-in-vs-code-with-emulicious-plan.md`
  summary: Compare PyBoy's screenshot of the proof ROM with one saved from Emulicious, to answer the epic's open question on whether PyBoy is accurate enough for the checks.
  evidence: Split from the debugger story on 2026-10-04 to keep its plan within the size guideline; it needs Emulicious installed, which that story delivers, and a screenshot the user saves by hand.
- source_plan: `_bmad-output/initiative-gbrythm/epic-dev-environment/story-refactor-sweep-plan.md`
  summary: The repository has no `README.md`, `AGENTS.md` or `CLAUDE.md`, so a fresh agent session has nothing at the root pointing it at `docs/setup.md` or the build and check commands.
  evidence: `ls` of the repository root on 2026-10-04 shows none of the three; the spec's success signal is a fresh agent given only the repository building and checking the ROM. Story 6 (rebuild from the instructions alone) is the natural place to add it.
- source_plan: `_bmad-output/initiative-gbrythm/epic-first-playable/story-the-song-s-notes-fall-in-time-in-one-lane-plan.md`
  summary: An image with no white pixel is converted with its lightest shade treated as white and the others shifted, and the build does not warn.
  evidence: Converting a three-shade copy of `assets/falling.png` on 2026-10-05 gave a palette starting at light grey. The converter numbers the shades it finds, lightest first. `docs/setup.md` now tells the reader to include white; the build could instead check for it or pass the converter a fixed palette.
- source_plan: `_bmad-output/initiative-gbrythm/epic-first-playable/story-start-begins-the-song-and-results-follow-it-plan.md`
  summary: The headless check cannot tell if the music is stopped too early at the end of the song, because the song ends on a rest.
  evidence: Stopping the driver ten frames early still passed `make check` on 2026-10-05; only silence was cut. A song whose last note sounds to the end would need the check to compare that note's length with its rows.
