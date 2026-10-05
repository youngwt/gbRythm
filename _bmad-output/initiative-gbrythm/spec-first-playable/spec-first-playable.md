---
id: SPEC-first-playable
companions:
  - lane-mapping.md
  - ../epic-dev-environment/spec-dev-environment/stack.md
  - ../spec-music-proof/spec-music-proof.md
sources: []
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# gbRythm first playable

## Why

A vision to realize, and something to learn. Everything so far proved tools; this is the first time the ROM is a game. One song, played start to finish with notes to hit, shows whether a rhythm game written in C on the Game Boy feels right, before menus, more songs or polish are built on top.

## Capabilities

- **CAP-1**
  - **intent:** The player starts the song and, as it plays, one note falls for each note of the melody, in the lane its pitch maps to, reaching the target line as that note sounds.
  - **success:** Across the whole song every melody note has exactly one falling note, in the lane `lane-mapping.md` gives, arriving at the line within two frames of the note sounding.
- **CAP-2**
  - **intent:** The player presses a lane's button as its note arrives and is judged on timing.
  - **success:** A press is graded perfect or good by how close it is to the note's arrival; a note not pressed in time is a miss; each judgement is shown on screen as it happens. A press with no note near in that lane changes nothing.
- **CAP-3**
  - **intent:** When the song ends the player sees how they did and can play again.
  - **success:** A results screen shows the counts of perfects, goods and misses, they add up to the number of notes in the song, and pressing Start plays the song again from the beginning with the counts reset.
- **CAP-4**
  - **intent:** The song is the full first verse of "Amazing Grace".
  - **success:** The ROM plays the verse from "Amazing grace" to "but now I see", and the user recognises it.
- **CAP-5**
  - **intent:** An agent can check the game without a display by playing it with scripted presses.
  - **success:** The headless check plays the song three ways and passes only when presses timed on each note score all perfects, no presses score all misses, presses made a little late score goods, and presses with no note near leave the counts unchanged.
- **CAP-6**
  - **intent:** The timing windows are tuned so judgements feel fair.
  - **success:** The user plays the song in Emulicious and says the judgements match what they expected of their own timing.
- **CAP-7**
  - **intent:** The instructions explain how the game plays and how notes map to lanes.
  - **success:** After removing the installed tools, following the instructions alone gets the headless check passing again, and a reader learns from them the lanes, the judging and how the notes follow the song.

## Constraints

- Inherits the dev-environment and music-proof contracts: GBDK-2020 4.5.0, C, the original Game Boy, hUGEDriver 6.1.3, tools in `tools/`, a command-line build and check with no window, and the C rules in `stack.md`.
- Falling notes are derived from the song's own data, never from a second copy of the tune, so the notes and the music cannot drift apart when the song is edited.
- Five lanes in the fixed order Left, Up, Right, B, A. A pitch maps to the same lane in every octave. The table is in `lane-mapping.md`.
- The player cannot fail: the song always plays through, and misses are only counted.
- Stray presses are ignored. A press when no note is near in that lane, including a press of the wrong lane's button, does nothing and is not a miss.
- The melody stays a single line on one sound channel, so the headless check can still name the notes it hears.
- The ROM stays 32K or smaller with no mapper.
- The headless check and the user's play in Emulicious are both required. The user's play is the only human step.

## Non-goals

- A title screen or menus.
- More than one song, and any pitch outside the five in `lane-mapping.md`.
- Difficulty levels.
- Held notes, and two notes at once.
- Points, combos and saved scores; the three counts are the whole score.
- Sound effects, harmony and drums.
- Finished art.
- Running on real hardware.

## Success signal

- The user plays the song through in Emulicious: the notes arrive in time with the music, presses are judged as expected, and the results appear. Separately, `make check` plays it with no window: presses timed on each note score all perfects, and no presses score all misses.

## Assumptions

- The game replaces the proof ROM's current screen. The image route and the headless check are reused, with the check's expectations rewritten for the game.
- The game waits for Start before the song begins.
- Notes fall from the top to a target line near the bottom of the screen.
- "Within two frames" in CAP-1 is the agent's figure for in time.
- Graphics are simple placeholders made by the agent.
- The non-goals were proposed by the agent and have not been confirmed one by one.

## Open Questions

- How wide are the perfect and good windows to start with? CAP-6 tunes them by play, but the build needs starting values.
- Does the game fit in 32K with the driver, the verse and the graphics? If not, is a mapper acceptable?
- Is C fast enough for five lanes of falling notes with judged input at 60 frames a second? The research flagged this as unmeasured.
- The tune has two eighth notes a third of a second apart. Is that playable at the current tempo, or should the tempo drop?
