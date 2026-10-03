- source_plan: `_bmad-output/initiative-gbrythm/epic-dev-environment/story-a-png-becomes-graphics-on-screen-plan.md`
  summary: The build converts every PNG in `assets/` with tile origin 128, so two background images shown at once would overwrite each other's tiles.
  evidence: The Makefile's png2asset rule passes a fixed `-tile_origin 128`; the proof ROM has one image so it does not occur yet, but the game will need several.
