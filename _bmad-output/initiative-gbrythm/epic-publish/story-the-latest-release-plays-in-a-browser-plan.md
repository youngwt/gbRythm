---
title: 'The latest release plays in a browser'
type: 'feature'
ticket: '4'
created: '2026-10-05'
status: 'built'
baseline_revision: '4e937223b266c4a60b687451f71de98689ba2671'
route: 'full'
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

**Problem:** The released ROM can be downloaded, but playing it means finding a Game Boy emulator first. Nobody the user sends a link to can try the game in one click.

**Approach:** Build a play page around binjgb v0.1.11, the emulator chosen in entry 3, that runs the ROM in a desktop browser and shows which keys are the five lane buttons and Start. `make page` assembles it, so it can be tried on this machine. When a version tag is released, GitHub publishes the page, with that release's ROM, to GitHub Pages. The user switches Pages on, pushes a tag, and tries the page.

## Boundaries & Constraints

**Always:**
- The page's ROM is the file that passed the checks in that run, the same file the release attaches. The game is not altered for the web.
- The page is published only by a version tag, and only after the release was created. A push to main, or a tag that fails the check, leaves the page as it was.
- Keys: the arrow keys Left, Up and Right for lanes 1 to 3, Z for B, X for A, Enter for Start. The page shows them, and names the version it is playing.
- binjgb's two files are downloaded at a pinned commit with checksums, as the other tools are, by a numbered step in `docs/setup.md` that GitHub also follows. Its licence is published with the page and it is credited there.
- The page is static files: no server, accounts, tracking, or files loaded from another site.
- The page starts the sound itself on the first key press or click.
- Pushing, tagging and repository settings are the user's actions. Changes are left uncommitted with a suggested message.

**Never:**
- No touch controls, phone layout, save states, rewind, pause, palette choice or key remapping.
- No README links and no explanation of publishing in the instructions; those are entry 5.
- No change to the game, its checks, or the release job's behaviour.
- No automatic browser test added to the repository or to GitHub's run; the page is checked once on this machine and by the user.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Page on this machine | `make page`, served locally, headless Chromium | Start screen shown, silent; Enter starts the song with sound; the five lane keys pressed on time give 35 perfect at the results | No error expected |
| Released | A version tag pushed whose checks pass | Release created, then the page shows that version and its ROM is byte-for-byte the release's | No error expected |
| Push to main | An ordinary push | Build and checks run, `make page` runs; nothing is published | No error expected |
| Broken tag | A tag on a commit that fails the check | No release; the page still shows the previous version | Run shows the failed step |
| Emulator download changed | A wrong checksum for a binjgb file | The setup step fails, naming the step | Nothing built or published |
| Page keys | Arrow keys, Z, X, Enter pressed on the page | The page does not scroll or act on them itself | No error expected |

</frozen-after-approval>

## Code Map

- `.github/workflows/build.yml` -- jobs `build` (setup steps 1 to 5 through `scripts/run-setup-steps.py`, debug check, keeps `build/gbrythm.gb` as artifact `gbrythm`) and `release` (tags `v[0-9]*` only, `needs: build`, `contents: write`). Top-level permission is read only.
- `scripts/run-setup-steps.py` -- runs the ```` ```sh ```` blocks under numbered `## N.` headings of `docs/setup.md`; takes one step or a range. New steps need no change to it.
- `docs/setup.md` -- steps 1 to 9; steps 6 to 9 need a window and are not run on GitHub. "Everyday commands" and "Where things are" list commands and files. "How to play" names the Game Boy buttons.
- `Makefile` -- `ROM`, `BUILD_DIR`, `require-*` targets that say which setup step is missing; no page target.
- `README.md` -- command table.
- binjgb at commit `8abd0d38d5bf109d7c280b27d815a8b53168adde` (tag v0.1.11), folder `docs/`: `binjgb.js` 25,209 bytes, `binjgb.wasm` 106,593 bytes, and `simple.js`, the 570-line example page script (MIT, Ben Smith). `simple.js` fetches a ROM by name, holds the key table (`bindKeys`), creates the sound context when loaded and prevents the browser acting on mapped keys. It also has rewind (Backspace), pause (Space) and saved cartridge memory, which this game does not use.
- The spike's trial harness, outside the repository in that session's scratch folder (`spike/run.py`, `tap.js`, a Python environment with Playwright and Chromium 145): reads the page's canvas with `scripts/screen.py` and its sound with `scripts/sound.py`. Reused once for the first matrix row; if it has been cleared, it is rebuilt in this session's scratch folder.
- GitHub's Pages actions, looked up 2026-10-05: `actions/upload-pages-artifact` v5, `actions/deploy-pages` v5.

## Tasks & Acceptance

**Execution:**
- [x] `web/play.js` -- copy binjgb's `simple.js` and change only: the ROM's name, the key table (the six keys above; rewind, pause, Select and Down removed), and starting the sound on the first key press or click. Keep its copyright header and add a line saying what was changed.
- [x] `web/index.html` -- the page: the screen at three times size, the key table, the version line, how to play in two sentences, credit and licence links. No outside files.
- [x] `docs/setup.md` -- step 10, install binjgb into `tools/binjgb/` (two files and its licence, with checksums); step 11, `make page` and how to open the result locally; rows in "Everyday commands" and "Where things are".
- [x] `Makefile` -- `page` target: assemble `build/page/` from `web/`, `tools/binjgb/` and the ROM, stamping `VERSION` (default "development build"); a `require-binjgb` target naming step 10.
- [x] `README.md` -- `make page` in the command table.
- [x] `.github/workflows/build.yml` -- `build` job runs steps 10 and 11 on every push, with the tag as `VERSION` on a tag, and on a tag keeps `build/page` as the Pages artifact; new job `page`, after `release`, deploys it.
- [x] Verify the first, fifth and sixth matrix rows on this machine; `make check` and `make check-debug`; record the user's steps for the rest.

**Acceptance Criteria:**
- Given a fresh clone with steps 1 to 5 and 10 run, when `make page` runs, then `build/page/` holds the page, the two binjgb files, its licence and `gbrythm.gb`, and the ROM is identical to `build/gbrythm.gb`.
- Given the page served locally, when it is played by script with on-time presses, then the results read 35 perfect.
- Given the user has switched Pages on and pushed a version tag, when the run finishes, then the public page names that tag and its ROM's SHA-256 equals the release asset's.
- Given the user plays the page in their own browser, then they hear the song and reach the results.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits, tags and pushes their own work.

What was built:

- `web/index.html` and `web/play.js`; `make page`, which assembles `build/page/`; steps 10 and 11 in `docs/setup.md`; rows in the README and the instructions' tables.
- `.github/workflows/build.yml`: the `build` job runs steps 10 and 11 on every push and, on a version tag, keeps `build/page` in the form Pages takes; a new `page` job, after `release`, publishes it. Only that job may write to Pages.
- The version is passed to `make page` as the environment variable `PAGE_VERSION`, because GitHub runs step 11's command as written and cannot add an argument to it.

`web/play.js` differs from binjgb's `simple.js` in six places, not the three the task named. Each is marked `gbRythm:` in the file.

- As planned: the ROM's name, with a message on the page if it cannot be loaded; the key table; starting the sound on the first key press or click.
- Kept, against the task's wording: the down arrow stays mapped to Down, which the game ignores, so that pressing it by mistake does not scroll the page.
- Found: sound queued before the first key press plays late. A browser keeps the sound clock stopped until a key is pressed, and binjgb goes on queuing sound against that stopped clock, so everything after is late by as long as the page had been open. Measured in Chromium with the unchanged script: 2.1 seconds late after the page had been open 2 seconds. Now nothing is queued until the sound is running. The spike could not have seen this: its browser did not apply the rule.
- Found: with binjgb's own buffer sizes, a note is heard 0.11 to 0.19 seconds after it is seen to land. The game's window for a good press is 7 frames, 0.12 seconds, so a player pressing by ear would miss. The sizes are reduced, 4096 to 1024 samples a piece and 0.1 to 0.06 seconds queued ahead, giving 0.06 to 0.08 seconds. The risk is crackling on a slow machine; nobody has listened yet. This is the user's to judge by ear.
- Review: the script read saved cartridge memory from the browser's storage, which a browser that blocks storage refuses, stopping the page. The game saves nothing, so nothing is read.

Verified on this machine, 2026-10-06, in headless Chromium 145 started with the rule that sound needs a key press first, the page served from a local web server, the screen read with `scripts/screen.py` and the sound with `scripts/sound.py`:

- Before any key: the start screen and all five markers found, sound suspended and silent, the version line reading "development build".
- Down and Up arrows pressed with the window shorter than the page: the page did not scroll.
- Enter, after a 6 second wait: sound running; first note landed 0.98 seconds later and first sound was heard at 1.06; D, E, G, A and B heard; results after 33.2 seconds reading perfect 35, good 0, miss 0, with each lane's key pressed as its note landed; silent on the results. No requests to other sites and no script errors.
- With the ROM removed from the page's folder, the page says "The game could not be loaded."
- `python3 scripts/run-setup-steps.py 10 11` exits 0; the page's ROM is identical to `build/gbrythm.gb`, SHA-256 `2f12b737…c092f9`, the same as release `v0.1.0`. With `PAGE_VERSION=v9.9.9` the page names that version.
- A wrong checksum for `binjgb.wasm` in step 10: `FAIL: step 10 of docs/setup.md (Install binjgb (the browser emulator)) failed at the commands above`.
- `make check` and `make check-debug` pass. The workflow file parses with the three jobs and conditions intended.

Matrix rows covered here: 1, 5 and 6. Rows 2, 3 and 4 need GitHub and are the user's steps below. The trial script is not in the repository, as the plan's boundary says.

Not verified: anything on GitHub, any browser but Chromium, and how it sounds. Outstanding, in order, all the user's actions:

1. On GitHub, Settings, Pages: set Source to "GitHub Actions".
2. Commit and push to main. The run should pass, with the two new steps, and publish nothing.
3. On GitHub, Settings, Environments, `github-pages`: under deployment branches and tags, add a tag rule `v*`. The environment appears once Pages is switched on.
4. Push `v0.1.1`. A release should appear, then the page at `https://youngwt.github.io/gbRythm/`, naming v0.1.1.
5. Play the page with sound.
6. Optionally, push a tag on a broken commit, as in entry 2; the page should still name v0.1.1.

## Plan Change Log

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 1, low 2, false 0, maybe-false 0.

- medium, patched: `web/play.js` read `localStorage` when loading the ROM; a browser set to block site storage throws there and the game never starts. Replaced with an empty buffer; the game has no save memory.
- low, patched: `make page` stamped the version with `sed` using `/` as its separator, which a tag containing `/` would break; the separator is now `|`.
- low, rejected: if the ROM request fails at the network level, not with an error status, no message is shown. The ROM is served from the same place as the page that just loaded, and handling it means wrapping binjgb's loading code further.
- Checked and found sound: a skipped `release` job skips `page`; the Pages artifact and the ROM artifact have different names; `make page` does not rebuild the ROM after the debug check, so the page's ROM is the checked file.

## Design Notes

**The page is built in the `build` job, not the `page` job.** That job already has the ROM and the tools, and `make page` then runs on every push, so a broken page is found before a release. The `page` job only deploys what was kept.

**Deploying with GitHub's Pages actions, not a `gh-pages` branch.** No generated files are committed anywhere. The cost is two settings for the user instead of one: Pages' source set to "GitHub Actions", and the `github-pages` environment allowed to deploy from `v*` tags; by default GitHub only lets the main branch deploy, and this deploy runs from a tag.

**`play.js` is kept in the repository; the other two binjgb files are downloaded.** `play.js` is changed, so it must be kept. The other two are unchanged and one is a binary, so they are pinned like the other tools.

**`v0.1.0` gets no page.** Its tag predates this work. The first page comes from the next tag, `v0.1.1`.

## Verification

**Commands:**
- `python3 scripts/run-setup-steps.py 10 11` -- expected: exit 0, `build/page/index.html` exists
- `cmp build/gbrythm.gb build/page/gbrythm.gb` -- expected: identical
- `make check && make check-debug` -- expected: both PASS
- after a tag: `curl -sL https://youngwt.github.io/gbRythm/gbrythm.gb | sha256sum` -- expected: the release asset's digest

**Manual checks (if no CLI):**
- User: set Pages' source to "GitHub Actions" and allow `v*` tags on the `github-pages` environment; push `v0.1.1`; open the page, press Enter, play the song with sound to its results.
