---
id: SPEC-publish
companions:
  - ../epic-dev-environment/spec-dev-environment/stack.md
sources: []
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. Source documents listed in frontmatter are for traceability — consult them only if you need narrative rationale or prose color this contract intentionally omits.

# Publishing gbRythm

## Why

An opportunity to capture. The game builds and checks itself on one Steam Deck, and nobody else can see it. Building it on GitHub proves the instructions work on a machine that has never seen the project, a published ROM lets anyone run it, and a play page lets anyone try it in a browser with one click from the README.

## Capabilities

- **CAP-1**
  - **intent:** Every push to main is built and checked on GitHub, on a machine that has never seen the project.
  - **success:** After a push, GitHub shows a pass when the ROM builds and the headless check passes, and a failure, naming the step, when either does not.
- **CAP-2**
  - **intent:** Pushing a version tag publishes a release anyone can download.
  - **success:** After a tag such as `v0.1.0` is pushed, a GitHub Release of that name exists with the ROM attached, and the ROM is the one that passed the check in that run.
- **CAP-3**
  - **intent:** Anyone can play the latest release in a desktop browser.
  - **success:** The play page loads the latest release's ROM, starts it after a key press or click, plays its sound, and responds to keys for the five lane buttons and Start; the song can be played through to its results.
- **CAP-4**
  - **intent:** The README leads straight to playing and to downloading.
  - **success:** The README has a link to the play page and a link to the latest release, each one click, and both work for someone not signed in to GitHub.
- **CAP-5**
  - **intent:** The repository says how its code may be reused.
  - **success:** An MIT licence file is at the repository's root, and GitHub shows the repository as MIT licensed.
- **CAP-6**
  - **intent:** The instructions explain how publishing works.
  - **success:** A reader learns from them what GitHub does on a push and on a tag, how to publish a release, and where the play page comes from.

## Constraints

- A failed build or check publishes nothing: no release, and no change to the play page.
- GitHub runs the same `make` commands a person runs, with the tools installed at the versions and checksums `docs/setup.md` pins. There is no separate build path for GitHub.
- The published ROM is the file that passed the check in that run, unchanged. The game is not altered for the web.
- The play page shows the latest release, not the latest push.
- The play page is static files on this repository's GitHub Pages: no server, no accounts, no tracking. Any third-party emulator is at a pinned version, with its licence recorded and compatible with publishing.
- Desktop browsers with a keyboard only. The page shows which keys are the five lane buttons and Start.
- Pushing, tagging and changing repository settings are the user's actions. The agent prepares the files and says what to do.

## Non-goals

- Phones and touch controls.
- Building pull requests.
- Version numbers or changelogs made automatically.
- Scores shared online.
- A custom web address.
- More than one emulator on the page.
- Running on real hardware.

## Success signal

- The user pushes a commit and GitHub shows a green check. The user pushes a version tag and a release appears with the ROM attached. Someone clicks the link in the README, presses a key, and plays the song in their browser.

## Assumptions

- GitHub runs both `make check` and `make check-debug`.
- Version tags look like `v0.1.0`.
- The MIT licence names Wayne Atkinson-Young and the year 2026.
- Java and Emulicious are not installed on GitHub; only the build and the headless check are needed there.
- The non-goals were proposed by the agent and have not been confirmed one by one.

## Open Questions

- Which browser emulator? It must run this ROM correctly, let keys be mapped to six buttons, be embeddable as static files, and carry a licence that allows it. Not yet researched.
- Do the licences of what is built into the ROM, GBDK's library code and hUGEDriver, allow publishing it? hUGEDriver is described as public domain in the research; GBDK's library terms have not been read.
- Does the headless check run unchanged on GitHub's machines? PyBoy has only ever run on this Steam Deck.
- How does the game feel in a browser? A browser emulator adds its own delay to keys and sound, and the timing windows were accepted in other emulators.
- GitHub Pages has to be switched on in the repository's settings, by the user; how depends on how the workflow is written.
