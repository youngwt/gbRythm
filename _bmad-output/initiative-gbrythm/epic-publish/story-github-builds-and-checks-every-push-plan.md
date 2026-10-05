---
title: 'GitHub builds and checks every push'
type: 'feature'
ticket: '1'
created: '2026-10-05'
status: 'built'
baseline_revision: 'a4ce19d3b31f1fba41ffdbe8362e7050480d4492'
route: 'oneshot'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-publish/spec-publish.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The game has only ever been built and checked on one Steam Deck, by the sessions that wrote it. Nothing proves the instructions work on a machine that has never seen the project, and a push that breaks the game is not noticed until someone runs the check by hand.

**Approach:** Add a GitHub workflow that, on every push to main, installs the tools by running the commands in `docs/setup.md` as written, builds the ROM with `make`, and runs both headless checks. The user pushes it; the result is read from GitHub. A deliberately broken check is pushed once to show a failure, then put right.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 90 lines across a new workflow file, a small script that runs the instructions' commands, and a note in `docs/setup.md`.

No commit was made: the user commits and pushes their own work.

- `.github/workflows/build.yml` runs on every push to main, on GitHub's Ubuntu 24.04 machine: check out, install `uv` 0.12.22, then one workflow step for each of steps 1 to 5 of `docs/setup.md`, then `make check-debug`, then keep the ROM and the check's screenshot whether it passed or failed. It can only read the repository.
- Decision: the workflow has no copy of the install commands. `scripts/run-setup-steps.py` reads `docs/setup.md` and runs the command blocks of the numbered steps as written. This meets the spec's constraint that GitHub uses the versions and checksums the instructions pin, by using the instructions themselves; and it makes every push a test of the instructions, which was a manual story at the end of each earlier epic. It is not a setup script for people: the dev-environment spec ruled that out, and the instructions remain the commands a person runs.
- The script stops a block at its first failing command and names the step. It uses only Python's standard library, so it runs before anything is installed.
- Python is pinned to 3.13 on GitHub, as on the Steam Deck; `uv` downloads it.
- Action versions were looked up on 2026-10-05: `actions/checkout` v7 and `actions/upload-artifact` v7. `uv` is installed with `pipx`, which GitHub's machines have, to avoid depending on a third action.
- `docs/setup.md` says in its opening that GitHub follows steps 1 to 5, and lists the two new files. The fuller explanation of publishing is entry 5.

Verified on this machine, in a fresh clone of the repository with only the new files added:

- Steps 1 to 5 run through the script each exited 0; `make check` and `make check-debug` passed with 35 notes in each of two plays. This also shows every file the build needs is in git.
- A wrong checksum in step 1: the script stops with `FAIL: step 1 of docs/setup.md (Install GBDK-2020 (the compiler)) failed at the commands above`.
- A widened perfect window: step 5 fails with the check's own message, then the step's.
- The workflow file parses as YAML with the nine steps intended.

Not yet verified, and the point of the story: that it runs on GitHub. Outstanding, in order:

1. The user commits and pushes; the result is read from GitHub.
2. A deliberately broken check is pushed to show a failure naming its step.
3. The break is put right and pushed.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. No findings so far; the run on GitHub is the real review.

## Verification

**Commands:**
- in a fresh clone: `python3 scripts/run-setup-steps.py 1 5 && make check-debug` -- expected: exit 0, both checks PASS
- after a push: `curl -s https://api.github.com/repos/youngwt/gbRythm/actions/runs?per_page=1` -- expected: the run for that commit has conclusion `success`

**Manual checks (if no CLI):**
- User: commit and push; later push the prepared break and its repair.
