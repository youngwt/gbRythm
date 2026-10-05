---
title: 'A version tag publishes a release'
type: 'feature'
ticket: '2'
created: '2026-10-05'
status: done
baseline_revision: '46b1f0c2967dff27a66e236305a04e6ee6008105'
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

**Problem:** GitHub builds and checks the game, but nobody can download it without building it themselves, and the repository does not say how its code may be reused. Before a ROM is published, it has to be known that the code built into it from other projects may be published.

**Approach:** Add the MIT licence, confirm from the licences of GBDK's library and hUGEDriver that the ROM may be published, and extend the workflow so that a pushed version tag whose build and checks pass creates a GitHub Release of that name with the ROM from that run attached. The user pushes the first tag; a tag on a deliberately broken commit is pushed once to show that nothing is published.

</frozen-after-approval>

## Implementation Notes

Oneshot route: about 80 lines across the licence file, one new job in the workflow, and notes in the README and `docs/setup.md`.

No commit was made: the user commits, tags and pushes their own work.

The licences of what is built into the ROM, read on 2026-10-05:

- GBDK's library, 4.5.0. `tools/gbdk/licenses/LICENSE_GPLV2_LE` is the GPL version 2 with a linking exception: "if you link this library with other files, to produce an executable, this library does not by itself cause the resulting executable to be covered by the GNU General Public License." So the ROM may be published, under any licence.
- The compiler's run-time library, which GBDK bundles from SDCC. `tools/gbdk/licenses/LICENSE_SDCC` lists "SDCC run-time libraries; (GPL+LE)", the same exception.
- hUGEDriver 6.1.3. Its README at that tag says "hUGETracker and hUGEDriver are dedicated to the public domain." The release has no licence file; that sentence is the whole statement.
- The tune, "Amazing Grace", dates from the 1700s and 1800s and is out of copyright. The images and the arrangement in `src/song.c` were made for this project.
- Answer to the epic's open question: yes, the ROM may be published. Nothing built into it places a condition on doing so.

What was built:

- `LICENSE` is the standard MIT text, naming Wayne Atkinson-Young and 2026, unaltered so GitHub recognises it.
- `.github/workflows/build.yml` now also runs when a tag beginning `v` and a digit, such as `v0.1.0`, is pushed. A second job, `release`, runs only for such a tag and only after the `build` job has passed. It downloads the ROM the `build` job kept and creates the release with GitHub's own `gh` command.
- Decision: one workflow file, not two. The release job needs the build job's result and its ROM; in a separate file the install and check steps would be copied, or the two would have to be chained across files.
- Decision: the release's file is named `gbrythm.gb` in every release, so the address of the latest one never changes. Entries 4 and 5 link to it.
- Decision: the release's notes are a fixed few lines, what the file is and how to run it. The spec rules out changelogs made automatically.
- Only the release job may write to the repository; the build job still only reads.
- `actions/download-artifact` v8 was looked up on 2026-10-05.
- The assumption the epic left for this plan stands: a release is made by pushing a tag from the user's machine.

Verified on this machine:

- The workflow file parses as YAML with the two jobs intended; the release job's condition and its dependence on `build` read as intended.
- `make check` and `make check-debug` still pass; no game code changed.

Not verifiable here, and the point of the story. Outstanding, in order, all the user's actions:

1. Commit and push to main; the run should pass as before and publish nothing.
2. Push a tag on a commit that fails the check; no release should appear.
3. Push `v0.1.0` on main; a release of that name should appear with `gbrythm.gb` attached, and GitHub should show the repository as MIT licensed.

On GitHub, 2026-10-05, read from its public API:

- Push to main, commit `6e93465`: run 37381520268 passed. The build job ran and the release job was skipped, so nothing was published.
- Tag `v0.0.0-broken` on commit `949b880`, the perfect window widened to 4 frames on a throwaway branch: run 37381809306 failed at "docs/setup.md step 5: run the headless check". The release job was skipped and no release was created.
- Tag `v0.1.0` on commit `6e93465`: run 37382033284 passed, both jobs. The release "gbRythm v0.1.0" exists with one file, `gbrythm.gb`, of 32,768 bytes, at `https://github.com/youngwt/gbRythm/releases/download/v0.1.0/gbrythm.gb`. The user confirmed "release works".
- GitHub reports the repository's licence as MIT.
- Left over: the tag `v0.0.0-broken` is still on GitHub and on the user's machine. It has no release. Removing it is the user's action.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the tag pattern `v*` would also have matched a tag such as `vendor-update`; it is now `v[0-9]*`.
- Checked and found sound: the ROM kept by the build job is `build/gbrythm.gb`, the ordinary ROM and not the debug one; the kept files' common folder is dropped, so the release job receives it as `gbrythm.gb`; a failed build job skips the release job even though the ROM is still kept.

## Verification

**Commands:**
- `make check && make check-debug` -- expected: both PASS
- after a tag is pushed: `curl -s https://api.github.com/repos/youngwt/gbRythm/releases/latest` -- expected: `tag_name` is the tag, and one asset named `gbrythm.gb` of 32768 bytes
- `curl -s https://api.github.com/repos/youngwt/gbRythm/license` -- expected: `spdx_id` is `MIT`

**Manual checks (if no CLI):**
- User: the three pushes listed above.
