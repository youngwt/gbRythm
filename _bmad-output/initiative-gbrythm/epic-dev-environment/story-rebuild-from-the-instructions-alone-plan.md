---
title: 'Rebuild from the instructions alone'
type: 'chore'
ticket: '6'
created: '2026-10-04'
status: 'built'
baseline_revision: 'aa96fec9417fbfdda8a9173b46b771c8db3d1557'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The setup instructions were written while the tools were being installed, by the session that installed them. Nobody has yet followed them from nothing, so a missing step or a command that only worked because of earlier state would go unnoticed until the environment is needed and broken.

**Approach:** Delete `tools/` and `build/`, then run the commands in `docs/setup.md` exactly as written, in order, with no step taken from memory. Fix every gap found in the instructions, make sure each step says why it exists, and finish with the build and the headless check passing.

</frozen-after-approval>

## Implementation Notes

Oneshot route: the change is corrections to `docs/setup.md` and whatever small gaps the rebuild exposes.

The rebuild:

- `tools/` (292 MB) and `build/` were deleted. `make` then failed as intended, with the pointer to `docs/setup.md`.
- Every `sh` block in `docs/setup.md` was extracted from the file by a script and run in order, unedited, from the VS Code Flatpak terminal: 14 blocks covering GBDK, PyBoy, `make`, `make check`, Java and Emulicious. All exited 0; all three checksum steps printed `OK`; the version lines matched what the instructions say to expect.
- Result: `make check` passed, and the ROM's sha256 is `26c228a0...8803`, identical to the ROM built before the tools were deleted. `tools/` is back to 292 MB.
- Beyond the story's verify: `make debug` wrote `build/debug/gbrythm.cdb`; Emulicious started through `scripts/java-host.sh` with the ROM stayed up with no error until stopped; the extension install command ran and reported 1.3.0 already installed.
- Not run: `make run` as written and F5, which need a person at a window. The VS Code extension was not uninstalled first, so its install from nothing was not re-proven.

Gaps found and fixed:

- No command in the instructions failed or needed anything from memory.
- Deleting `tools/` also deletes `tools/emulicious/Emulicious.ini`, the user's Emulicious settings, and the instructions did not say so. They now do. The existing file was copied out before the delete and put back afterwards.
- The extension install command did not pin a version, against the rule that versions are pinned. It now installs `@1.3.0`.
- The repository root had nothing pointing a newcomer or a fresh agent at the instructions (logged as deferred work by story 5). Added `README.md`: what the repository is, the pointer to `docs/setup.md`, and the commands.
- "Each step says why it exists": read through all eight steps; each does. No rewording needed.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. No findings: the diff is `README.md` and two sentences in `docs/setup.md`, each checked against the files they describe.

## Verification

**Commands:**
- `rm -rf tools build`, then every `sh` block of `docs/setup.md` in order -- expected: each exits 0
- `make check` -- expected: exit 0, PASS
- `sha256sum build/gbrythm.gb` -- expected: `26c228a02549cc939ed70c10cdba531a2e9247952c3bd3550cff8a8cd1b28803`
