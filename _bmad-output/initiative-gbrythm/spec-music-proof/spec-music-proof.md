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
  - **intent:** The proof ROM plays the first half of a verse of "Amazing Grace" through hUGEDriver: "Amazing grace, how sweet the sound, that saved a wretch like me".
  - **success:** The existing one-command build produces a ROM that plays it in Emulicious, and the user recognises the tune.
- **CAP-2**
  - **intent:** An agent can check without a display that the ROM is playing music.
  - **success:** The headless check passes when the ROM produces sound whose notes change over time, reporting the notes it heard, and fails on a ROM built with the music left out.
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
- The packaged hUGEDriver 6.1.3 library is used as shipped. It links and runs under GBDK 4.5.0, so nothing is rebuilt and RGBDS is not installed.
- The headless check requires at least three different notes and prints the notes heard; it does not compare them with the song. It reads one plain tone, so it cannot name notes when channels sound together.
- The sound check is command-line only, with no window. The user listening once in Emulicious is the only human step.
- The instructions say why each step exists and explain music concepts from scratch.

## Non-goals

- Anything reacting in time with the music, including the driver's call-routine feature; the game's own spec proves that.
- Sound effects.
- More than one song.
- The full length of "Amazing Grace"; half a verse is enough.
- Installing or using the hUGETracker editor.
- Any gameplay.

## Success signal

- `make check` passes on a ROM that plays the first half of a verse of "Amazing Grace", and the user, listening in Emulicious, recognises the tune.

## Assumptions

- The melody of "Amazing Grace" is in the public domain, so the song file needs no licence note.
- PyBoy's sound is taken as close enough to a real Game Boy's for this check; the two have not been compared.
