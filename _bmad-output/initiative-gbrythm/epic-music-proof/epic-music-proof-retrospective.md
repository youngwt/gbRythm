---
epic: epic-music-proof
date: 2026-10-04
verdict: accepted-with-open-items
criteria: declared
headless: false
---

# Retrospective: The proof ROM plays Amazing Grace through hUGEDriver

## Epic summary

The epic is `epic-music-proof`, the second in `initiative-gbrythm`. The user invoked the retrospective straight after its last story was marked done; it is the only epic with unreviewed work. The user was invited to name concerns and named none.

**Tickets.** All three are `done`. None is unfinished and none is waiting at `built`.

| Ref | Title | Route | Range | Commits |
|---|---|---|---|---|
| 2.1 | The driver links and the check hears a sound | full | `5a72ba6..8774397` | `a69c373`, `8774397` |
| 2.2 | The ROM plays the opening of Amazing Grace | oneshot | `8774397..335aee1` | `a0a7674`, `335aee1` |
| 2.3 | The instructions explain the music and rebuild from nothing | oneshot | `335aee1..ccd78dc` (inferred: runs to HEAD) | `032ab89`, `ccd78dc` |

No merges, no binary files.

**What the epic changed.** `src/song.c` is new (132 lines) with `src/song.h`. `scripts/check_rom.py` grew from 109 to 196 lines. `docs/setup.md` grew from 243 to 311. `src/main.c`, `Makefile` and `README.md` took small changes.

**Evidence available.** The epic file with its Done when; the spec and its memory log; `tickets.toml`; three plans, each with a triage log; all commits; the previous retrospective.

**Evidence missing.**

- No architecture or PRD document; the spec is the only contract.
- Session logs were not read. Process findings come from the plans, plus the retrospective session's own memory of building all three stories, flagged where used.
- `bmad-review` was not invoked, in keeping with the user's standing choice to work without subagents. The code lenses were run inline by the session that wrote the code. This is not an independent review.

## Findings

### Spec-to-implementation reconciliation

**F1. The song is longer than the spec says, and the spec was not updated.** CAP-1 specifies "the opening phrase" and a non-goal rules out the full length (`spec-music-proof.md:20`, `:50`). After listening, the user asked for it to be "a little longer", and `ccd78dc` extended it to half a verse. That was the user's decision and is recorded in story 2.3's plan (`story-the-instructions-explain-the-music-and-rebuild-from-nothing-plan.md:57`). The spec still describes the shorter song.
Disposition: fix now, as a spec reconciliation for the user to apply with `bmad-spec`. Prevention: see F2.

**F2. The spec's two open questions are answered but still listed as open.** Both answers are in `docs/setup.md` under "What was found" and in the epic's notes; `spec-music-proof.md:66-67` is unchanged. The same thing happened in the previous epic (its finding F3) and its spec is still unreconciled (`spec-dev-environment.md:72-73`, `stack.md:16`). Two epics running, the spec has ended the epic out of date.
Disposition: fix now, with F1. Prevention: make "reconcile the spec" the last step of an epic, before the retrospective; it has been skipped twice when left as a follow-up.

**F3. The user has not confirmed hearing the song as it now stands.** Done when 3 is that the user listens and recognises the tune. The user said "it sounded great" about the opening phrase (`...rebuild-from-nothing-plan.md:56`), then asked for more, and the song was extended after that. Nothing records the user hearing the longer version. The agent's evidence for it is the check's note list, which matches the tune as written.
Disposition: closed. After reading this retrospective the user confirmed hearing the longer song: "sounds perfect to me, just the right length for a demo" (2026-10-04). Prevention: the previous retrospective's lesson, "do the human-only check last", held for the stories as planned; it was the follow-on request that came after. A change made after a human check needs that check again.

**F4. The check does not know which tune to expect.** With every G in the song replaced by F, `make check` still passed, listing the altered notes (run during this retrospective at `ccd78dc`, source restored). It requires three different notes and prints what it heard. This was a recorded decision in story 2.2 (`story-the-rom-plays-the-opening-of-amazing-grace-plan.md`, "the check does not compare against the expected tune"), made so the check need not be edited when the song is. It means Done when 1, "plays the opening of Amazing Grace", rests on a person or agent reading the printed notes.
Disposition: accept as-is for the proof. Prevention: the game's spec should decide whether a song's notes are checked against its source; with several songs, reading a printed list will not scale.

**F5. The rebuild from the instructions was again run by the session that wrote them.** Story 2.3 ran 17 of 18 command blocks, extracted by script, and the check passed. That is strong evidence the commands are complete. It is not evidence that the explanation teaches a newcomer, which is half of CAP-4's success test; no reader new to Game Boy music has read the section. The previous retrospective raised the same point about a fresh session (its F4) and nothing was done.
Disposition: fix now; the user reading "How the music works" and saying whether it made sense is the cheapest test. Prevention: none new.

### Size growth

**F6. `scripts/check_rom.py` nearly doubled and now does four jobs.** It went from 109 to 196 lines in this epic (+24, +73, +12 across the three ranges). It checks the screen, searches for images, tests the button, and analyses sound. The file was read: each part is clear and commented, and it runs in about a second. It is still one script with one `main`, and the next epic will add checks for gameplay.
Disposition: defer. Prevention: when the game's first check is added, decide whether sound and image analysis move into their own modules.

**F7. `docs/setup.md` grew again, to 311 lines.** The previous retrospective (its F7) said to decide, when the next epic added a tool, whether usage and concepts should move out of the install guide. The music section was added to the same file without that decision being put to the user.
Disposition: decided. The user chose to leave it as one file for now (2026-10-04); later retrospectives need not re-flag it unless it grows substantially. Prevention: a retrospective's "decide when X happens" items need an owner and a trigger someone will see; this one had neither.

### Duplication map

**F8. The check's listening time is tied to the song's length by hand.** `LISTEN_FRAMES = 1080` (`scripts/check_rom.py:34`) was chosen so the check hears the song once and stops just before it repeats at frame 1082. The song's length lives in `src/song.c` (rows, tempo, pattern break). Changing the tempo or adding a phrase leaves the check hearing part of the song or part of a repeat; it would still pass, but the printed notes would no longer be the tune once through.
Disposition: defer. It becomes real when there is more than one song.

### Pattern divergence

**F9. A change belonging to one story was recorded under another.** The longer song is a change to story 2.2's work, made while story 2.3 was open, and sits in 2.3's range and plan. The record is honest but a reader looking for the song's history in 2.2's plan will not find it.
Disposition: accept as-is. Prevention: a request that arrives mid-story and changes finished work is cleaner as its own small ticket.

### Architecture delta

Nothing to report. One C file and a header were added; `main.c` includes one more header and the build links one library. Checked by reading; no tool was run.

### Code lenses, run inline (narrowed scope)

**F10. Why a silent ROM makes a sound at start-up is unknown.** A ROM with no music produces sound in about frames 35 to 45 (`story-the-driver-links-and-the-check-hears-a-sound-plan.md`, Implementation Notes). The check works around it by ignoring the first 60 frames (`scripts/check_rom.py:31`). Whether it comes from the emulator or from GBDK's start-up code was not established, so it is not known whether a real Game Boy would do it, or whether 60 frames is always enough.
Disposition: defer. It belongs with the parked PyBoy accuracy ticket, which is about the same doubt.

**F11. Note detection reads one plain tone.** Recorded in story 2.2's plan: two channels together, the noise channel, or low notes would not be named reliably. It also reports a repeated pitch with no silence between as one note, so "sound" and "that" appear as a single D. The game will want harmony and drums.
Disposition: defer to the game's spec.

**F12. No story had an independent review.** All three triage logs say the review was inline. It was the user's choice. This time the one serious defect, a silent ROM passing the first version of the sound check, was caught by running the plan's matrix, not by review.
Disposition: accept as-is. The lesson worth keeping is that writing the failing case into the plan and running it found what a read-through would have missed.

### What went well, with sources

- The epic's main risk was retired before the first plan was approved: the packaged library was linked and run in a scratch folder during planning (`story-the-driver-links-and-the-check-hears-a-sound-plan.md`, Code Map).
- The previous retrospective's most important action, the image check, was built before this epic started and kept passing throughout.
- The check's output became evidence an agent can read: `notes heard: D4 G4 B4 …` let the song be verified, extended and re-verified without anyone listening.

## Behavior verification

Exercised at `ccd78dc` during this retrospective, from the VS Code Flatpak terminal:

- `make clean && make`: exit 0, ROM 32768 bytes.
- `make check` with `DISPLAY` and `WAYLAND_DISPLAY` unset: PASS, `notes heard: D4 G4 B4 G4 B4 A4 G4 E4 D4 G4 B4 G4 B4 A4 D5`.
- Music start-up removed: `FAIL: no sound was produced between frames 60 and 1080`. Source restored.
- Every G changed to F: PASS with the altered notes, which is finding F4. Source restored.
- An image's draw call removed: still fails on the image. Source restored.
- `make debug`: exit 0.

Exercised in story 2.3 and not repeated: deleting `tools/` and reinstalling from `docs/setup.md`.

Exercised by the user after this document was first written: listening to the song as it now stands.

Not exercised: F5 in VS Code.

## Previous-retro follow-through

From `epic-dev-environment-retrospective.md`, Action items:

1. "Make the headless check fail when the image is missing" (the user, then a build session): landed. Commit `2dd8837`; `scripts/check_rom.py`, the image search; re-confirmed above.
2. "Press F5 once more at the current commit" (the user): landed at the time, recorded in that document.
3. "Run the build and check from a session with no history, starting from `README.md`" (the user): no evidence found.
4. "Reconcile the spec" (the user, with `bmad-spec`): not landed. `spec-dev-environment.md:72-73` and `stack.md:16` are unchanged.
5. "Decide whether `_bmad/render/` is ignored or committed" (the user): landed in practice as committed. 26 render files are tracked, including this skill's, and `.gitignore` does not list the folder. No written decision was found.
6. "Process: do the human-only check last, and say whether the build workflow should commit" (the user): half landed. The commit preference was stated and has been followed in every build since; no commit in this epic was made by the agent. The human check was last as planned, but see F3.

Its deferred items: the duplicated command list (its F6) is unchanged; the name clash (its F12) was fixed in `fb56da2`; the open walkthrough (its F13) is unchanged.

## Action items

All are proposals. Nothing below has been applied.

1. ~~Listen to the song as it now stands~~ (F3). Done by the user on 2026-10-04.
2. **Reconcile both specs** (F1, F2, and the previous retrospective's item 4): the music spec's song length and two open questions, and the dev-environment spec's Java and extension questions. Owner: the user, with `bmad-spec`. Spec reconciliation awaiting human application.
3. **Read "How the music works" and say whether it made sense** (F5). Owner: the user.
4. ~~Decide whether `docs/setup.md` is split~~ (F7). Decided by the user on 2026-10-04: one file for now.
5. **Process: reconcile the spec as the last step of an epic**, before its retrospective (F2). Owner: the user, as a standing preference.
6. **Carry three items into the game's spec** (F4, F8, F11): whether a song's notes are checked against its source, how the check learns a song's length, and how it handles more than one channel. Owner: the next `bmad-spec` session.

Deferred and not tracked anywhere but here: F6, F10.

## Acceptance verdict

**Accepted-with-open-items**, against criteria declared in the epic file. This is the machine verdict. The user read it on 2026-10-04, closed F3 and F7, and did not override it; they did not say "accepted" in so many words.

| Done when | Result | Evidence |
|---|---|---|
| 1. `make` builds a ROM of 32K or smaller that plays the opening of "Amazing Grace"; existing checks pass | Met, with F4 noted | Behavior verification; the check's note list matches the tune |
| 2. `make check`, with no window, passes on it and fails with the music left out | Met | Behavior verification |
| 3. The user listens in Emulicious and recognises the tune | Met | "It sounded great" for the opening phrase, and "sounds perfect to me" for the song as it now stands |
| 4. With the tools folder deleted, the instructions alone restore a passing check | Met | Story 2.3: 17 command blocks run as written |
| 5. The instructions state whether the packaged library worked, with evidence | Met | `docs/setup.md`, "What was found" |

No ticket is unfinished. No finding blocks the next epic.

## Open questions

- Does the start-up blip happen on a real Game Boy?
