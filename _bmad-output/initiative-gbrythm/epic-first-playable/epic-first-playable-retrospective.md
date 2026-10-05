---
epic: epic-first-playable
date: 2026-10-05
verdict: accepted-with-open-items
criteria: declared
headless: false
---

# Retrospective: The player plays Amazing Grace and is judged on timing

## Epic summary

The epic is `epic-first-playable`, the third in `initiative-gbrythm`. The user invoked the retrospective after its last story was marked done and its spec reconciled; it is the only epic with unreviewed work. The user was invited to name concerns and named none.

**Tickets.** All eight are `done`. None is unfinished and none is waiting at `built`.

| Ref | Title | Route | Range | Commits |
|---|---|---|---|---|
| 3.1 | The song's notes fall in time in one lane | full | `6333a17..ff5a779` | `ff5a779` |
| 3.2 | Notes fall in five lanes by pitch | oneshot | `ff5a779..2411fe3` | `2411fe3` |
| 3.3 | Presses are judged perfect, good or miss | full | `2b64256..c973662` | `c973662` (plan in `2b64256`) |
| 3.4 | Start begins the song and results follow it | full | `ed197d5..e7c2f30` | `e7c2f30` (plan in `ed197d5`) |
| 3.5 | The song is the full first verse | oneshot | `e7c2f30..43a15d9` | `43a15d9`, `49adf5d` |
| 3.6 | The timing windows feel fair | none | no range: closed with no build | `6a919e3` |
| 3.7 | Refactor sweep | full | `6a919e3..d826091` | `d826091` |
| 3.8 | The instructions explain the game and rebuild from nothing | oneshot | `d826091..` working tree (inferred; uncommitted when this was written) | none yet |

No merges. The spec reconciliation and story 3.8 were uncommitted when the evidence was read; they were read from the working tree.

**What the epic produced.** `src/game.c` is new, 574 lines. `scripts/check_rom.py` was rewritten twice and split: 567 lines, with `scripts/screen.py` (75) and `scripts/sound.py` (82). `src/song.c` grew from 132 to 169 lines. `docs/setup.md` grew from 311 to 463. Twelve images replaced two. The ROM uses 6,531 of 32,768 bytes.

**Evidence available.** The epic file with its Done when; the spec, reconciled on the day; eight plans with their notes and triage logs; all commits; the two previous retrospectives; `deferred-work.md`.

**Evidence missing.**

- No architecture or PRD document; the spec is the only contract.
- Session logs were not read. Process findings come from the plans, plus the retrospective session's own memory of building every story, flagged where used.
- `bmad-review` was not invoked, by the user's standing choice to work without subagents. The code lenses were run inline by the session that wrote the code. This is not an independent review.

## Findings

### Spec-to-implementation reconciliation

**F1. Changing the song's tempo breaks the check, though the instructions say it will not.** `docs/setup.md` says of the falling notes "Edit the song and the falling notes follow, with nothing else to change", and of the music "To change the speed, change the tempo number". With the tempo changed from 10 to 8 in `src/song.c` and nothing else, `make check` fails: "with stray presses, the 35 notes should score 0 perfect, 0 good, 35 miss but the screen shows 0 perfect, 1 good, 34 miss". At tempo 6 it fails earlier: "70 notes landed on a marker but 68 notes were heard" (both run during this retrospective at `d826091`, source restored). The game is right in both cases; the check is wrong. Its stray-press scenario presses a note's own button a fixed 10 frames after it lands (`scripts/check_rom.py`, `check_presses`), which at tempo 8 falls inside the window of the next note in the same lane; and its hearing misses a repeated note 12 frames after the first (`scripts/sound.py`, `LOUDNESS_JUMP`). The constraint that notes follow the song's data holds. The claim that the check needs no change does not.
Disposition: fix now, as a ticket. Prevention: when a document says "nothing else to change", the story should try a second value, not only the one in use. Story 3.1 tried adding a note; nobody tried the tempo until now.

**F2. Changing how notes fall does work.** With `FALL_SPEED` 4 and `LEAD_FRAMES` 30, `make check` passes, reporting notes "moving 4 pixels a frame" (run during this retrospective, source restored). The windows are kept in frames and converted to distance, so they follow.
Disposition: accept as-is. Recorded as a checked claim.

**F3. CAP-6 was closed on one sentence.** Story 3.6 was to tune the windows with the user by play. It was closed with no build on "I think the timing is good enough" (`story-the-timing-windows-feel-fair-plan.md`). The epic had flagged the quick pairs of notes, a third of a second apart, as an open question; the user did not mention them, and the plan and the spec record "playable" as the agent's reading.
Disposition: accept as-is; the user's judgement is the test. Recorded so the next epic knows the windows were accepted, not tuned.

**F4. CAP-7's teaching half is untested for the third epic running.** Story 3.8 proved the commands by rebuilding from nothing. Whether the explanation teaches a newcomer has not been tested: nobody but the session that wrote it has read it (`story-the-instructions-explain-the-game-and-rebuild-from-nothing-plan.md`, "Not tested"). The two earlier retrospectives raised the same point (dev-environment F4, music-proof F5) and each asked the user to read a section; no evidence of either was found.
Disposition: defer, with a change of approach. Asking the user to read has not happened three times. A fresh agent session given only the repository and asked to explain the game back would test the same thing without waiting on the user.

**F5. All timing is calibrated against one emulator.** `MUSIC_START_FRAME` is `LEAD_FRAMES + 3` and `JUDGE_Y` is one step past the marker, both described in `src/game.c` as measured, not reasoned, and both measured in PyBoy. The user has played in Emulicious and one other emulator and found the timing good enough. Nothing has run on a real Game Boy, and the ticket to compare PyBoy with another emulator is still parked.
Disposition: defer. It becomes real when a flash cart is bought. The spec records it as an assumption.

### Duplication map

**F6. The lane design is written in five places.** `lane_of_pitch` in `src/game.c`; `CHECK_ARGS` in the `Makefile`; `lane-mapping.md` in the spec; and two tables in `docs/setup.md`, under "How to play" and "How the falling notes work". The first two are a deliberate pair (story 3.2: a check that read the mapping from the game could not catch the game getting it wrong). The two tables in one document are not deliberate; story 3.8 added the second.
Disposition: accept the pair; defer the document's duplicate to the next edit of that file.

**F7. `make check` and `make check-debug` are two commands.** The debug ROM once failed where the normal one passed (story 3.4), which is why the second command exists. Nothing makes anyone run it. It was run at the end of stories 3.5, 3.7 and 3.8 because the builder remembered.
Disposition: decided. The user chose to leave them as two commands (2026-10-05). The builder runs `make check-debug` at the end of any story that touches the game's code.

### Size growth

**F8. `docs/setup.md` grew by half, to 463 lines.** In the music-proof retrospective the user chose to keep it as one file "for now", to be re-raised if it grew substantially. It has, and story 3.8 retitled it "Setting up and understanding gbRythm" because it now does two jobs.
Disposition: decided. The user chose again to keep it as one file (2026-10-05); later retrospectives need not re-flag its length.

**F9. `src/game.c` is 574 lines and `check_start_and_ending` is the check's longest function.** Both were looked at in the sweep (story 3.7). The game was kept as one file by a recorded decision and reordered; the check was split. Read again for this retrospective: each still reads in one sitting.
Disposition: accept as-is. The next feature added to the game should prompt the question again.

### Pattern divergence

**F10. One commit carries another story's subject.** `43a15d9` is titled "feat: Start begins the song and results follow it", the same as `e7c2f30`, but its content is story 3.5: the full verse in `src/song.c` and that story's plan. A reader of the log sees story 3.4 twice and story 3.5 never.
Disposition: accept as-is; history is not rewritten. Prevention: the agent gives a commit message with each story, and the previous one was evidently still to hand.

**F11. The agent built over a dirty tree once, against the workflow's rule.** At the start of story 3.8 the user had staged, but not committed, the "done" mark for story 3.7. The build workflow says to stop and ask. The agent went ahead and said so (`story-the-instructions-explain-the-game-and-rebuild-from-nothing-plan.md`). At story 2.2 the same situation was handled by stopping.
Disposition: accept as-is; no harm followed. Prevention: the "done" mark is a second commit after every story. Marking a story done before the user commits it, so one commit covers both, removes the step that keeps catching. The user agreed to this (2026-10-05).

### Architecture delta

Nothing to report. The game is one C file with one header; the check is three Python files with no shared state. Checked by reading; no tool was run.

### Code lenses, run inline (narrowed scope)

**F12. A reported bug that was not one cost more than any story.** The user reported that the play after the results ran fast. It was Emulicious's turbo shortcut sharing a key with Start, confirmed by the user after remapping (`story-start-begins-the-song-and-results-follow-it-plan.md`, notes after the build). Before that was found, the agent made two changes on explanations it had not tested: leaving the sound hardware on, which the user's retest disproved and which was reverted. What settled it was measuring inside Emulicious: a ROM that started itself ran at normal speed, so the cause needed a key press. The search did find and fix a real fault, the debug ROM failing the check, and a real gap, the check's second play having no presses.
Disposition: accept as-is. Prevention: for a bug seen only in one emulator, measure in that emulator before changing code, and ask at the start which build, which emulator and which key. The way to do it is now written down for later sessions.

**F13. Start pressed just before the results appear is swallowed.** A press of Start held from five frames before the results heading appears, for eight frames, does not start a new play; the player must let go and press again (probe run in story 3.4's bug hunt, retrospective session's memory; the code is in `game_tick`, where a press is only the frame a button goes down, and that frame fell during play, when Start is ignored). A player keen to replay will press early.
Disposition: accept as-is. The user decided Start should not count if it is still held when the results appear (2026-10-05); a fresh press is required.

**F14. No story had an independent review.** All seven built stories record an inline review. The serious faults were found by other means: running the plan's failure cases (a silent ROM passing, story 2.1 pattern repeated in 3.3's off-centre windows), running the debug build, and the user playing. The inline reviews found small things.
Disposition: accept as-is, by the user's choice. The lesson from three epics is consistent: writing the failing cases into the plan and running them is what finds faults here.

**F15. The check cannot tell if the music stops early.** Already in `deferred-work.md` from story 3.4: the song ends on a rest, so cutting it short removes only silence. The full verse also ends on a faded note.
Disposition: defer, already tracked.

### What went well, with sources

- The thin first story did its job: it settled size, speed and timing before anything was built on them (`story-the-song-s-notes-fall-in-time-in-one-lane-plan.md`).
- Story 3.5 changed no game code. A song more than twice as long, with new rhythms, played correctly from its data alone (`story-the-song-is-the-full-first-verse-plan.md`).
- The sweep was verified by the six breaks earlier stories had proved, not by a checksum, and all six still failed as before (`story-refactor-sweep-plan.md`).
- The previous retrospective's process item landed: the spec was reconciled before this retrospective, not after.

## Behavior verification

Exercised at `d826091` plus the uncommitted document changes, from the VS Code Flatpak terminal:

- `make clean && make check` with `DISPLAY` and `WAYLAND_DISPLAY` unset: PASS. Nothing before Start; 35 notes fell and were heard in each of two plays, in lane, within 1 frame, moving 2 pixels a frame; silence on the results; second play from zero; 13 ways of pressing judged as designed.
- `make check-debug`: PASS. ROM 32768 bytes.
- Tempo 8 and tempo 6: the check fails, which is finding F1. Source restored.
- Fall speed doubled with the lead halved: PASS. Source restored.
- A lane swapped: fails naming the note and both markers. Source restored.

Exercised in story 3.8 and not repeated: deleting `tools/` and reinstalling from `docs/setup.md`.

Exercised by the user during the epic: playing in Emulicious and in a second emulator; listening to the verse.

Not exercised: a real Game Boy.

## Previous-retro follow-through

From `epic-music-proof-retrospective.md`, Action items:

1. "Listen to the song as it now stands" (the user): landed, recorded in that document.
2. "Reconcile both specs" (the user, with `bmad-spec`): landed. Commit `01e8f7d`; both specs' open questions were resolved.
3. "Read 'How the music works' and say whether it made sense" (the user): no evidence found. See F4.
4. "Decide whether `docs/setup.md` is split" (the user): landed as "one file for now". Reopened by F8.
5. "Process: reconcile the spec as the last step of an epic" (the user): landed. The epic file carries it as a decision, and `spec-first-playable.md` was reconciled before this retrospective.
6. "Carry three items into the game's spec" (the next `bmad-spec` session): landed. Notes come from the song's data and the melody stays on one channel, as constraints in `spec-first-playable.md`; the check learns a song's length by watching for the results heading (`scripts/check_rom.py`, `record_run`).

Its deferred items: the check script's shape (its F6) was settled in story 3.7; the start-up blip (its F10) is unchanged and unexplained.

From `epic-dev-environment-retrospective.md`, still open: "Run the build and check from a session with no history" (the user): no evidence found, now three epics old. See F4.

## Action items

All are proposals. Nothing below has been applied.

1. **Make the check survive a change of tempo** (F1): time the stray press between notes instead of a fixed 10 frames after one, and say in the instructions what tempos the check's hearing can follow. Owner: the user, to raise with `bmad-ticket`; then a build session.
2. ~~Decide whether `make check` runs the debug ROM too~~ (F7). Decided by the user: no.
3. ~~Decide whether `docs/setup.md` is split~~ (F8). Decided by the user: no.
4. **Test the instructions with a fresh agent session**, given only the repository, asked to build, check, and explain the game back (F4, and the oldest open item from the first retrospective). Owner: the user, by opening a session; no reading required.
5. ~~Decide whether Start held when the results appear should count~~ (F13). Decided by the user: no.
6. **Process: mark a story done before it is committed**, so one commit covers the work and the mark (F11). Agreed by the user; the agent does this from the next story on.
7. **Process: for a bug seen in one emulator, measure there first** (F12). Owner: the agent; recorded for later sessions.

Deferred and already tracked in `deferred-work.md` or the backlog: the early-stop check (F15), the PyBoy comparison (F5). Deferred and tracked only here: F6's duplicate table.

## Acceptance verdict

**Accepted-with-open-items**, against criteria declared in the epic file. The user confirmed it on 2026-10-05, answering "yes" to accepting the epic with these items open.

| Done when | Result | Evidence |
|---|---|---|
| 1. `make` builds a ROM of 32K or smaller; after Start the full verse plays with one falling note per melody note, in its lane, arriving as it sounds | Met | Behavior verification: 35 notes, in lane, within 1 frame; 32768 bytes |
| 2. `make check`, with no window, scores on-time, absent, late and stray presses as designed | Met, with F1 noted | 13 ways of pressing; fails only when the tempo is changed |
| 3. The results show counts that add up to the number of notes, and Start plays again with the counts reset | Met | Results read 35 in every scenario; second play from zero |
| 4. The user plays, recognises the verse, and says the judgements match their sense of their timing | Met | "its good" on the verse; "I think the timing is good enough"; see F3 |
| 5. With the tools folder deleted, the instructions alone restore a passing check | Met | Story 3.8: 17 command blocks run as written |

No ticket is unfinished. No finding blocks the next epic. F1 should be fixed before a second song is added, since a second song will have its own tempo.

## Open questions

- What comes next: a second song, a title screen, real hardware, or something else? The first three each make one of the deferred items real: F1, F8 or F5.
