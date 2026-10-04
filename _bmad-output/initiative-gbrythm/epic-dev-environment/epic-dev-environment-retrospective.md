---
epic: epic-dev-environment
date: 2026-10-04
verdict: accepted-with-open-items
criteria: declared
headless: false
---

# Retrospective: An agent can build, run and check a Game Boy ROM on this machine

## Epic summary

The epic is `epic-dev-environment`, the only epic in `initiative-gbrythm`. It was chosen because it is the only one and every ticket in it is finished. The user was invited to name concerns before analysis and named none.

**Tickets.** All six are at `built` (state `review`); none has been called done. None is unfinished.

| Ref | Title | Route | Range | Commits |
|---|---|---|---|---|
| 1.1 | Build and headless-run a minimal ROM | full | `4e16380..1202fe1` | `1202fe1` |
| 1.2 | Proof ROM reacts to a button and the check asserts it | oneshot | `1202fe1..b5d4b8c` | `b5d4b8c` |
| 1.3 | A PNG becomes graphics on screen | oneshot | `b5d4b8c..e9ab0fb` | `e9ab0fb` |
| 1.4 | Step through C in VS Code with Emulicious | full | `e9ab0fb..c931eef` | `e5906ae`, `c931eef` |
| 1.5 | Refactor sweep | oneshot | `c931eef..aa96fec` | `aa96fec` |
| 1.6 | Rebuild from the instructions alone | oneshot | `aa96fec..73103ba` (inferred: runs to HEAD) | `73103ba` |

Each range is one plan's `baseline_revision` to the next. There are no merges and no binary revisions except `assets/arrow.png`, whose churn is unmeasured.

**What the epic produced.** 539 lines outside BMad output: `docs/setup.md` (232), `Makefile` (100), `scripts/check_rom.py` (66), `src/main.c` (38), `README.md` (26), `scripts/java-host.sh` (22), four `.vscode/` files (36), `.gitignore` (19), and one image.

**Evidence available.** The epic file with its Done when; the spec and `stack.md`; `tickets.toml`; six plans, each with a triage log; all commits; `deferred-work.md`; the walkthrough log.

**Evidence missing.**

- The initiative file has no Requirements section, so `covers` points at the spec's CAP-1 to CAP-6 instead, as the epic file says.
- No architecture or PRD document exists. The spec is the only contract.
- No previous retrospective exists; this is the first epic.
- Session logs were not read. Process findings below come from what the plans record, plus the retrospective session's own memory of building 1.4 to 1.6, which is flagged where used.
- `bmad-review` was not invoked. The user chose inline work without subagents for story 1.4, and that choice was carried over here. The code lenses were run inline by the same session that built 1.4 to 1.6. Their scope is narrowed accordingly: this is not an independent review.

## Findings

### Spec-to-implementation reconciliation

**F1. The headless check does not check that the image is shown.** Done when 2 asks for a screenshot "showing a PNG-sourced graphic" (`epic-dev-environment.md:28`). `scripts/check_rom.py` asserts two things only: the screen is not one flat colour, and it changed after A was pressed. With the `set_bkg_tiles` call for the arrow commented out of `src/main.c`, `make check` still printed PASS (run during this retrospective at `73103ba`, source restored afterwards). The graphic is in the screenshot today, but only a reader opening the file would notice if it went missing. Story 1.3's own verify was met by comparing screenshots by hand, not by the check.
Disposition: fix as a separate task, by the user's decision on 2026-10-04; not a condition of accepting the epic. Prevention: when a Done when names something visible, the ticket's verify should say which command fails without it.

**F2. One of the epic's three open questions was not answered.** The epic notes say entry 4 "compares its screenshot with Emulicious" to settle whether PyBoy is accurate enough (`epic-dev-environment.md:54`). Story 1.4's plan split that out at the user's choice to keep the plan short (`story-step-through-c-in-vs-code-with-emulicious-plan.md:29`), and it sits in `deferred-work.md`. The headless check, which every later epic will lean on, still rests on an emulator nobody has compared with a second one.
Disposition: defer, already tracked. Prevention: a plan-size split can remove something the epic promised; when it does, the summary to the user should say which epic note it leaves open. It did say so here.

**F3. The spec still lists as open what the epic answered.** The spec's Open Questions on Java and the debugger extension (`spec-dev-environment.md:72-73`) and the "unresolved" Java row (`stack.md:16`) are unchanged. The answers are in `docs/setup.md` under "What was found", by the user's decision in story 1.4. A later session that reads the spec first will see them as unknown.
Disposition: fix now, as a spec reconciliation for the user to apply with `bmad-spec`. Prevention: none needed; this was a deliberate choice, and the retrospective is where it gets picked up.

**F4. The spec's success signal has not been exercised as written.** It calls for "a fresh agent session given only the repository" to build and check the ROM (`spec-dev-environment.md:63`). Story 1.6 rebuilt everything from `docs/setup.md` with every command taken from the file by a script, but it ran in the session that wrote those instructions. The root `README.md` that points a newcomer at the instructions was only added in that same story (`73103ba`), and no session has started from it cold.
Disposition: fix now; it is a check, not a code change. Prevention: a "from the instructions alone" ticket is strongest when a session with no history runs it.

**F5. Emulicious cannot be pinned to a version.** The spec says tool versions are pinned in the instructions. Emulicious publishes one unversioned download, so `docs/setup.md` pins a checksum and a date and says what to do when the checksum stops matching.
Disposition: accept as-is. Recorded so later retrospectives do not re-flag it.

### Duplication map

**F6. The command list exists in three places.** The `Makefile` header (`Makefile:4-8`), the "Everyday commands" table in `docs/setup.md` (around line 200) and the table in `README.md` (line 14) each list the make targets. The first two came from story 1.5 and the third from story 1.6. They already differ: `README.md` omits `make debug`. A new target has to be added in three files.
Disposition: defer. Prevention: nothing; small, and worth settling when the next target is added.

### Size growth

**F7. `docs/setup.md` is the largest file and holds four kinds of content.** It grew in every range: 95, +6, +17, +102, +12 lines, to 232. It now holds install steps, everyday usage, an explanation of how Game Boy images work, and the history of what was found. The file was opened and read: each part is clear, and the order was tidied in story 1.5. It is not yet a problem, but the next epic will add music tooling to the same file.
Disposition: accept as-is for now. Prevention: when the next epic adds a tool, decide whether usage and concepts move out of the install guide.

### Pattern divergence

**F8. Generated BMad render snapshots are tracked in git, and new ones dirty the tree.** 19 files under `_bmad/render/` are tracked, added in `4e16380` and `b5d4b8c`; story 1.2's commit carries 261 lines of walkthrough render files alongside its code. Running this retrospective created `_bmad/render/bmad-retrospective/` as untracked files. `bmad-build` halts on a dirty tree, so an untracked render folder will interrupt the next build until it is committed or ignored.
Disposition: fix now; the user decides whether `_bmad/render/` is ignored or committed. Prevention: settle it once in `.gitignore`.

**F9. Commit style changed mid-epic.** Stories 1.1 to 1.3 were committed by the user with free-form subjects; 1.4 to 1.6 were committed by the build workflow with conventional subjects and a body. The user noticed, asking why no changes showed in git after story 1.4 (retrospective session's memory, not a written record).
Disposition: accept as-is. Prevention: the user decides whether the build workflow should commit or leave changes for them; worth stating as a standing preference.

### Architecture delta

Nothing to report. The code is one C file, one Python script, one shell script and a `Makefile`; there is no dependency graph to draw. Checked by reading every file; no tool was run.

### Code lenses, run inline (narrowed scope)

**F10. Done when 3 was last confirmed two commits before the tools were reinstalled.** The user reported "F5 worked" at `c931eef` (`story-step-through-c-in-vs-code-with-emulicious-plan.md:100`). Since then story 1.5 moved the breakpoint line and story 1.6 deleted and reinstalled Java and Emulicious. At `73103ba` the agent confirmed only that the debug build writes its `.cdb` and that Emulicious starts through the wrapper. The report was also brief: it does not say whether variable values were shown, which Done when 3 requires.
Disposition: closed. After reading this retrospective the user re-ran the debugger at `73103ba` and reported "debugger still worked". Prevention: a check that only a person can run should be the last thing done in an epic, after any cleanup and rebuild.

**F11. No story had an independent review.** All six triage logs say the review was run inline by the implementing session (for example `story-build-and-headless-run-a-minimal-rom-plan.md:96`, `story-refactor-sweep-plan.md:53`). Those reviews logged thirteen findings in total, none graded above medium, and missed F1. This was the user's choice each time.
Disposition: accept as-is for this epic. Prevention: for stories that add checks other work will rely on, an independent review is worth its cost; F1 is the kind of gap a second reader finds.

**F12. An image and a source file with the same name would collide.** `assets/main.png` would be converted to `build/main.c` and compiled to `build/main.o`, the same object file as `src/main.c` (`Makefile:48-52`, two pattern rules with one target pattern). Not reachable with the one image present.
Disposition: defer. It belongs with the tile-origin item already deferred from story 1.3, since both are about handling more than one image.

**F13. The walkthrough was left open and is now out of date.** The log records that block 1 was presented and never answered, and that its line references predate story 1.3 (`walkthrough-dev-environment-so-far-log.md`, entry 2). Four more stories have landed since.
Disposition: defer; the user decides whether to restart it against the finished epic or drop it.

## Behavior verification

Exercised at `73103ba` during this retrospective, from the VS Code Flatpak terminal:

- `make clean && make`: exit 0, ROM 32768 bytes, sha256 `26c228a02549…`, the same as at every commit since story 1.3.
- A missing semicolon in `src/main.c`: `make` exit 2 with `src/main.c:18: syntax error`. Source restored.
- `make check` with `DISPLAY` and `WAYLAND_DISPLAY` unset: exit 0, PASS. `build/screenshot-after.png` was opened: it shows `GBRYTHM`, `PRESS A`, `A PRESSED` and the arrow.
- `make check` with the arrow's draw call removed: PASS, which is finding F1. Source restored.

Exercised in story 1.6, one commit earlier, and not repeated: deleting `tools/` and reinstalling from `docs/setup.md`.

Exercised by the user after this document was first written: the debugger in VS Code, reported as still working at `73103ba`.

Not exercised: `make run`, which needs a person at a window.

## Previous-retro follow-through

There is no previous retrospective file: this is the first epic in the initiative. Nothing to follow through on.

## Action items

All are proposals. Nothing below has been applied.

1. **Make the headless check fail when the image is missing** (F1). Owner: the user, to raise as a separate ticket with `bmad-ticket`; then a `bmad-build` session. The user confirmed on 2026-10-04 that this is separate work.
2. ~~Press F5 once more at the current commit~~ (F10). Done by the user on 2026-10-04: "debugger still worked".
3. **Run the build and check from a session with no history, starting from `README.md`** (F4). Owner: the user, by opening a fresh agent session.
4. **Reconcile the spec** (F3): resolve the Java and extension open questions in `spec-dev-environment.md` and the Java row in `stack.md`, citing `docs/setup.md`. Owner: the user, with `bmad-spec`. Spec reconciliation awaiting human application.
5. **Decide whether `_bmad/render/` is ignored or committed** (F8). Owner: the user.
6. **Process: do the human-only check last** (F10), and say whether the build workflow should commit (F9). Owner: the user, as standing preferences.

Deferred and already tracked in `deferred-work.md`: the PyBoy comparison (F2) and the fixed tile origin. Deferred and not yet tracked anywhere but here: F6, F12, F13.

## Acceptance verdict

**Accepted-with-open-items**, against criteria declared in the epic file. The user confirmed it on 2026-10-04: "Happy with the epic", with the image check (F1) to be handled as a separate task.

| Done when | Result | Evidence |
|---|---|---|
| 1. One command builds from a clean checkout; a syntax error fails with the compiler's message | Met | Behavior verification above |
| 2. The headless check passes and saves a screenshot showing a PNG-sourced graphic and a change after a button press, with no window | Met, with F1 open | The screenshot shows both; the check would not notice the graphic missing |
| 3. The user hits a breakpoint on a C line and sees variable values, in Emulicious | Met | The user's report at `c931eef`, and again at `73103ba` after the cleanup and reinstall |
| 4. With the tools folder deleted, the instructions alone restore checks 1 and 2 | Met | Story 1.6: 14 command blocks run as written, ROM byte-identical |

No ticket is unfinished. No finding blocks the next epic from starting, but F1 should be fixed before later work trusts `make check` to guard graphics.

## Open questions

- The user's two reports on the debugger were brief ("F5 worked", "debugger still worked"); neither says in so many words that variable values were shown.
- Should the build workflow commit, or leave changes for the user to commit?
- Should `_bmad/render/` be in git at all?
