---
title: 'Step through C in VS Code with Emulicious'
type: 'feature'
ticket: '4'
created: '2026-10-04'
status: 'built'
baseline_revision: 'e9ab0fba7323f95bb0457bb50b24f22f8fe5d2a9'
route: 'full'
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

**Problem:** The proof ROM can be built and checked by an agent, but the user cannot yet watch it run or step through its C source. When something breaks, there is no way to stop on a line and look at the variables.

**Approach:** Unpack a Java runtime and Emulicious into `tools/`, add a debug build and VS Code debug configuration so F5 builds the ROM and stops on breakpoints in C, and extend the setup instructions. The user confirms the breakpoint by hand.

**Decisions (2026-10-04):**
- The answers to the open questions about Java and the debugger extension are recorded in `docs/setup.md` only. The spec and epic are not edited.
- The PyBoy-versus-Emulicious screenshot comparison is split out to deferred work; this story does not answer the PyBoy accuracy question.
- Implementation and review run inline in one session, without subagents.

## Boundaries & Constraints

**Always:**
- Java and Emulicious live under `tools/`, are never committed, and are found by explicit path. Nothing is installed to the system.
- Download URLs, versions and checksums are pinned in the instructions; each step says why it exists.
- `make` and `make check` behave exactly as before: same flags, same ROM, 32K or smaller.
- The debug configuration works from the VS Code Flatpak, using workspace-relative paths only.

**Never:**
- No setup script; no changes to `src/main.c` or `scripts/check_rom.py`.
- No writes to ticket files, the epic file, or the spec.
- No refactoring of the existing Makefile rules; story 5 owns that.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Debug build | `make debug`, tools installed | Exit 0; `build/debug/gbrythm.gb` and `build/debug/gbrythm.cdb` exist | No error expected |
| Normal build untouched | `make clean && make && make check` after a debug build | PASS; `build/gbrythm.gb` byte-identical to the baseline ROM | No error expected |
| Emulicious missing | `make run` with no `tools/emulicious` | Non-zero exit | One-line message pointing at `docs/setup.md` |
| Breakpoint (user) | F5 with a breakpoint on `a_was_pressed = 1;`, then A pressed in Emulicious | Execution stops on that line; `keys` and `a_was_pressed` show values | User reports what happened if it does not stop |

</frozen-after-approval>

## Code Map

- `Makefile` -- `BUILD_DIR` (line 9) drives every output path and `lcc` is called on lines 30, 36 and 39 with no shared flags variable. Reuse the `require-gbdk` pattern (line 67). Do not restructure existing rules.
- `tools/gbdk/bin/lcc` -- `-debug` makes the compiler and linker write `.cdb` debug symbols; `-Wf--max-allocs-per-node0` makes stepping follow the C lines but grows the code.
- `src/main.c` -- globals `keys` and `a_was_pressed`; line 27 runs only after A is pressed, so it is the user's breakpoint. Not edited.
- `.gitignore` -- already ignores `tools/` and `build/`. `.vscode/` does not exist; its files are committed.
- `docs/setup.md` -- new sections follow section 4; "Where things are" gains rows.
- Emulicious -- `https://emulicious.net/download/emulicious/?wpdmdl=205`, a 2.5 MB zip with `Emulicious.jar`; needs "Java 1.6 or newer"; no versioned URL.
- Java -- Temurin 21 JRE, `https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jre_x64_linux_hotspot_21.0.12.1_1.tar.gz`, sha256 `2413149700df0f7d440500a84a8f764c535f21e5a5e87d38328b64eec2c5b500`.
- Extension -- `emulicious.emulicious-debugger` 1.3.0; VS Code here is 1.139.1. Launch properties: `type: emulicious`, `request: launch`, `program`, `port` (58870), `stopOnEntry`, `emuliciousPath`, `javaPath`, `additionalSrcFolders`. Reads the `.cdb` beside the ROM. VSIX fallback on open-vsx.org.
- Sandbox -- `DISPLAY` is empty in the Flatpak terminal; the host has `DISPLAY=:0`. Java may only open a window when started with `flatpak-spawn --host`. The network is shared, so the debugger port is reachable either way.

## Tasks & Acceptance

**Execution:**
- [x] `tools/java/`, `tools/emulicious/` -- download, verify and unpack both; record the Emulicious checksum -- the tools, kept out of git.
- [x] `scripts/java-host.sh` -- only if Java cannot open a window from the sandbox: run `tools/java/bin/java` on the host through `flatpak-spawn --host`, passing arguments through. Probe both ways first: does the process stay up and does port 58870 answer -- a `javaPath` that works from the Flatpak.
- [x] `Makefile` -- add `debug` (builds into `build/debug` with `-debug -Wf--max-allocs-per-node0`), `run` (opens the normal ROM in Emulicious) and `require-emulicious` -- a ROM for stepping that leaves the checked ROM unchanged.
- [x] `.vscode/launch.json`, `.vscode/tasks.json`, `.vscode/extensions.json` -- launch `build/debug/gbrythm.gb` with `emuliciousPath`, `javaPath`, `additionalSrcFolders` and a `preLaunchTask` running `make debug`; recommend the extension -- F5 builds and debugs with no per-user settings.
- [x] VS Code -- `code --install-extension emulicious.emulicious-debugger`, falling back to the VSIX -- the debugger itself.
- [x] `docs/setup.md` -- sections for Java, Emulicious, the extension, playing the ROM and debugging step by step; a "What was found" note answering the Java and extension questions; extend the table -- CAP-4 and the story's record.
- [x] User check -- hand over: press F5, set the breakpoint, press A in Emulicious.

**Acceptance Criteria:**
- Given tools installed, when `make debug` runs, then `build/debug/gbrythm.cdb` exists and names `main.c`.
- Given the baseline ROM's checksum, when `make clean && make` runs after this change, then `build/gbrythm.gb` has the same checksum and `make check` passes.
- Given the new tools, when `git status --short` runs, then no Java, Emulicious or build file is listed.
- Given Emulicious started the way the launch configuration starts it, when port 58870 is probed, then it accepts a connection.
- Given a breakpoint on `src/main.c` line 27, when the user presses F5 and then A in Emulicious, then VS Code stops on that line and shows `keys` and `a_was_pressed`.
- Given `docs/setup.md`, when read, then the Java and extension questions each have an answer with its evidence.

## Implementation Notes

Implemented inline, without a subagent, as the user chose.

- Installed: Temurin 21.0.12.1+1 JRE in `tools/java/`; Emulicious release 2026-03-27 in `tools/emulicious/` (zip sha256 `6e1c6d51...c0fc`, recorded in `docs/setup.md`); extension 1.3.0 from the marketplace, no VSIX needed.
- Sandbox probe: from the Flatpak terminal Emulicious throws `HeadlessException` (no X11 display) yet still opens port 58870; with `DISPLAY=:0` set by hand X refuses authorization; through `flatpak-spawn --host` it runs with no error. So `scripts/java-host.sh` was needed and is the `javaPath`.
- Surprise: the open port in the sandbox means "port answers" does not prove a window exists.
- The debugger type is `emulicious-debugger`, not `emulicious` as the Code Map says.
- `Makefile`: the three `lcc` lines gained `$(LCCFLAGS)`, empty by default; `debug` re-runs make with `BUILD_DIR=build/debug` and the debug flags.
- Added `.vscode/settings.json` (not in the task list) to raise the extension's connection attempts from 25 to 100.
- Verified: `make debug` writes `build/debug/gbrythm.gb` and `.cdb`, and the `.cdb` has a line record for `main.c` line 27; after `make clean && make` the normal ROM's sha256 is `26c228a0...8803`, the same as before the change, and `make check` passes; `make run` with the jar missing exits non-zero with the pointer to `docs/setup.md`; Emulicious started through the wrapper accepts a connection on 58870 and answers the debug protocol's `initialize` and `launch` requests.
- Not verified: a breakpoint stopping. A hand-written protocol client got "Adapter not ready" when setting a breakpoint and never received the adapter's ready event. That may be the client and not the setup; the user's F5 check settles it. The Emulicious window was not seen by the agent either.
- The user check task stays open.
- 2026-10-04, later: the user ran the F5 check and reported "F5 worked". The "Adapter not ready" result came from the hand-written client, not the setup.

## Plan Change Log

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 3, false 0, maybe-false 1.

- low, patched: `.vscode/launch.json` had `//` comments, so the plan's `python3 -m json.tool` check failed on it. Comments removed; the explanation is in `docs/setup.md`.
- low, patched: the extension gives up connecting after 25 tries of 0.1 s, which a slow Java start through `flatpak-spawn` could exceed. `.vscode/settings.json` sets 100.
- low, patched: `docs/setup.md` said steps 5 to 8 were "for a person, not an agent", which is wrong for the install steps. Reworded.
- maybe-false, deferred to the user check: breakpoints may not bind (see "Not verified" above). Would be high if true. Settled by the user pressing F5 with a breakpoint on `src/main.c` line 27.
- Follow-up to the row above: false. The user reported that F5 worked.

## Design Notes

A separate `build/debug` folder, not a flag on the normal build: the debug flags change the generated code, and the ROM that `make check` verifies should be the one that would ship. The `debug` target re-runs make with `BUILD_DIR` and extra `lcc` flags overridden, so no rule is duplicated.

Emulicious has no versioned download, so its pin is a checksum and a date; the instructions say what to do when the checksum stops matching.

## Verification

**Commands:**
- `make debug && ls build/debug/gbrythm.gb build/debug/gbrythm.cdb` -- expected: exit 0, both listed
- `make clean && make && sha256sum build/gbrythm.gb && make check` -- expected: checksum equals the baseline's, PASS
- `tools/java/bin/java -version` -- expected: version 21
- `python3 -m json.tool .vscode/launch.json` -- expected: valid JSON
- `git status --short` -- expected: only the planned source, config and docs files

**Manual checks (if no CLI):**
- User: F5 stops on the breakpoint with variable values shown.
