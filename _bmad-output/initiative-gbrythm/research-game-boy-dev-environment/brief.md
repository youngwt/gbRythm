# Research brief: Game Boy dev environment

**Decision:** which development environment to set up for a DDR-style rhythm game on the original Game Boy.
**Type / shape:** technical / select.

## Requirements frame (agreed with user 2026-10-03)

Hard gates:
- Builds on Linux from a command line an agent can drive
- Game code written in C
- Produces a ROM that runs on an original Game Boy (DMG) from a flash cart; user will play it on a GBA
- Can play music and read button input with timing steady enough for a rhythm game

Weighted preferences: beginner-friendly (high), agent-friendly plain-text sources and scriptable build (high), practical music workflow (high), VS Code fit (medium), project health (medium), exit cost (low).

Flash cart: user has none; wants mid-priced, good quality, to be used in a GBA.

## Dimensions
1. Field of toolchains, screened to finalists
2. Finalists against the frame, current versions
3. Music: composing, playback driver, sync
4. Surrounding tools: emulator/debugger on Linux, VS Code, graphics conversion
5. Flash carts: buying recommendation and ROM requirements

Topology: breadth-first, run inline (no subagents). Preset standard, validation normal.
