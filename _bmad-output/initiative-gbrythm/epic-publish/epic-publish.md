---
type: epic
title: "Anyone can download the game or play it in a browser"
parent: initiative-gbrythm
covers: []
after: []
assignee: ""
risk: medium
---

# Anyone can download the game or play it in a browser

## Description

GitHub builds and checks the game on every push, publishes the ROM as a release when a version is tagged, and serves a page where the latest release can be played in a desktop browser, linked from the README. The spec owns the capabilities, constraints and non-goals.

## Outcome

For anyone the user sends a link to, the game is one click from playable; for the user and the agents, every push is proven on a machine that has never seen the project. The spec's success signal shows it worked.

## Requirements

The spec's capabilities CAP-1 to CAP-6 are the requirement ids. The initiative has no numbered requirements, so `covers` is empty.

## Done when

1. A push to main shows a pass on GitHub when the ROM builds and both checks pass, and a push that breaks the check shows a failure naming the step.
2. Pushing a version tag creates a GitHub Release of that name with the ROM attached, and a tag on a commit that fails the check creates nothing.
3. The play page loads the latest release, and the song can be played through to its results in a desktop browser with the keyboard, with sound.
4. The README's links to the play page and to the latest release both work for someone not signed in to GitHub.
5. GitHub shows the repository as MIT licensed.
6. The instructions say what happens on a push and on a tag, how to publish a release, and where the play page comes from.

## Boundaries

Publishing from this repository on GitHub. Not phones, pull-request builds, automatic version numbers, online scores, a custom address or real hardware; see the spec's Non-goals. The game itself does not change.

## References

- spec — _bmad-output/initiative-gbrythm/spec-publish/spec-publish.md
- constraint — the same spec, section Constraints
- instructions — docs/setup.md, steps 1 to 5, the pinned downloads and checksums the workflow must match
- stack — _bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md, tool versions
- research — _bmad-output/initiative-gbrythm/research-game-boy-dev-environment/research-game-boy-dev-environment.md, source appendix, for the tools' licences and homes

## Notes

- Decision: one epic, six entries in sequence (2026-10-05, awaiting the user's approval of the breakdown).
- Decision: the tracer bullet is entry 1, the build and both checks running on GitHub for a push. Everything else publishes what that proves, and it answers whether the check runs away from this Steam Deck (2026-10-05, awaiting approval).
- Decision: choosing the browser emulator is a spike, entry 3, because the play page cannot be planned until it is chosen and the choice is the user's (2026-10-05, awaiting approval).
- Decision: a closing refactor sweep is included, as there are more than three entries; the workflows are likely to repeat their install steps (2026-10-05, awaiting approval).
- Decision: when the last entry is done, the spec is reconciled with `bmad-spec` before the retrospective, as in the previous epic (2026-10-05).
- Open question: do the licences of GBDK's library code and hUGEDriver, which are built into the ROM, allow publishing it? Entry 2 answers it before the first release; if either does not, work stops and the finding is reported.
- Open question: does the headless check run unchanged on GitHub's machines? Entry 1 answers it.
- Open question: how the game feels in a browser; entry 4 has the user try it. The spec does not make the user's verdict a condition.
- Unknown: which browser emulator; entry 4 waits on entry 3.
- Assumption: the user pushes, tags and changes repository settings; the agent prepares files, says what to do, and reads the public results. Builds leave their changes uncommitted with a suggested message, and a story is marked done before its commit.
- Decision: the user approved the breakdown as drafted, "I agree with the epic"; the four decisions above marked "awaiting approval" stand, including the refactor sweep and the licence being part of entry 2 (2026-10-05).
- Assumption: a release is made by pushing a version tag from the user's machine, and the workflow creates the release. The user asked how tagging works and was offered the alternative of making releases on GitHub's website; they did not choose it. Entry 2 confirms this in its plan.

