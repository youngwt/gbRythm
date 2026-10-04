---
id: SPEC-music-proof
companions:
  - ../epic-dev-environment/spec-dev-environment/stack.md
sources:
  - ../research-game-boy-dev-environment/research-game-boy-dev-environment.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# gbRythm music proof

## Why

A risk to retire, and something to learn. The rhythm game depends on the hUGEDriver music library, whose packaged build was made for GBDK 4.1.1; this project uses 4.5.0, and nobody has checked the two work together. Proving it now, with one short song and no gameplay, lets the game's spec rely on music instead of assuming it. It is also where the user and the agents first meet Game Boy music, so the explanations matter as much as the result.

## Capabilities

- **CAP-1**
  - **intent:** The proof ROM plays the opening phrase of "Amazing Grace" through hUGEDriver.
  - **success:** The existing one-command build produces a ROM that plays the phrase in Emulicious, and the user recognises the tune.
- **CAP-2**
  - **intent:** An agent can check without a display that the ROM is playing music.
  - **success:** The headless check passes when the ROM produces sound whose notes change over time, and fails on a ROM built with the music left out.
- **CAP-3**
  - **intent:** The song lives in the repository as C source an agent can read, written by hand without a tracker program.
  - **success:** The song file is committed, the build compiles it into the ROM, and no tracker was used to produce it.
- **CAP-4**
  - **intent:** The setup instructions cover installing the music driver and explain how Game Boy music works.
  - **success:** After removing the installed tools, following the instructions alone gets the headless check passing again; a reader new to Game Boy music learns from them what a music driver is, what the sound channels are, and how the song file is laid out.
- **CAP-5**
  - **intent:** The answer to whether hUGEDriver's packaged library works with GBDK 4.5.0 is recorded.
  - **success:** The instructions state the answer with the evidence for it, and name what was done instead if it did not work.

## Constraints

- Inherits the dev-environment contract: GBDK-2020 4.5.0, C, the original Game Boy, tools in the git-ignored `tools/` folder found by explicit path with versions pinned, nothing installed on the system partition, everything working from the VS Code Flatpak terminal, and the C rules in `stack.md`.
- The music goes into the existing proof ROM. Its existing checks keep passing: the screen is not blank, both images are shown, and the screen changes when A is pressed.
- The ROM stays 32K or smaller with no mapper.
- The driver is hUGEDriver. No other music driver, and no patching of the driver's source.
- If the packaged library does not work with GBDK 4.5.0, the driver is rebuilt from its source, with RGBDS installed into `tools/`. If that also fails, work stops and the finding is reported.
- The sound check is command-line only, with no window. The user listening once in Emulicious is the only human step.
- The instructions say why each step exists and explain music concepts from scratch.

## Non-goals

- Anything reacting in time with the music, including the driver's call-routine feature; the game's own spec proves that.
- Sound effects.
- More than one song.
- The full length of "Amazing Grace"; the opening phrase is enough.
- Installing or using the hUGETracker editor.
- Any gameplay.

## Success signal

- `make check` passes on a ROM that plays the opening of "Amazing Grace", and the user, listening in Emulicious, recognises the tune.

## Assumptions

- The packaged release v6.1.3 (2024-07-14) is tried first, as the latest release; the repository has newer, unreleased commits.
- The phrase is a single melody line on one sound channel, with no harmony.
- The melody of "Amazing Grace" is in the public domain, so the song file needs no licence note.

## Open Questions

- Can PyBoy observe sound well enough for CAP-2? The current check runs it with sound emulation off, and the research did not assess PyBoy's audio. If it cannot, CAP-2 needs another route.
- Does hUGEDriver's packaged library link and run under GBDK 4.5.0? Answering this is the purpose of the spec (CAP-5).
