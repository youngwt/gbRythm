---
title: 'Start begins the song and results follow it'
type: 'feature'
ticket: '4'
created: '2026-10-05'
status: 'ready-for-dev'
baseline_revision: ''
route: 'full'
route_source: 'auto'
risk: 'low'
review: ''
review_source: ''
lenses_ran: []
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The song starts by itself the moment the ROM opens and repeats for ever, wiping the score a few seconds after the last note. The player is never ready for the first note and never gets to see how they did.

**Approach:** Make the game wait for Start. When the song has played through once it stops, and a results screen shows the perfect, good and miss counts until Start is pressed again, which clears them and plays the song from the beginning.

## Boundaries & Constraints

**Always:**
- Nothing falls and no music plays until Start is pressed.
- The song plays exactly once per Start. When it ends the music is silent and no note starts again.
- The results show the same three counts the player watched during play, and they add up to the number of notes in the song.
- Start during play does nothing. Lane buttons while waiting or on the results do nothing.
- Judging, timing, lanes and steady motion stay as entries 1 to 3 left them. The check reads the screen and sound, with no window. ROM 32K or smaller; C rules in `stack.md`.
- Changes are left uncommitted for the user, with a suggested commit message.

**Never:**
- No title screen, menu, song choice, high score or fail state.
- No longer song and no tuning of windows: entries 5 and 6.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Waiting | ROM opened, Start not pressed | A "press Start" prompt; counts at zero; no falling notes; no music | No error expected |
| Play once | Start pressed | Notes and music as before; prompt gone | No error expected |
| Ending | The song's last row has played | Music stops and stays silent; results heading and prompt appear; counts stay | No error expected |
| Results add up | Any of entry 3's press scenarios | Counts on the results equal that scenario's expectation over all the song's notes | No error expected |
| Play again | Start on the results | Counts read zero, heading and prompt gone, song plays from the first note, and the second results match | No error expected |
| Start mid-song | Start pressed during play | No change | No error expected |
| Lanes while idle | Lane buttons before Start and on the results | No change to counts | No error expected |
| Ending broken | The game made to keep reading the song | `make check` fails | Source restored afterwards |

</frozen-after-approval>

## Code Map

- `src/game.c` -- `game_tick` does everything every frame; it gains three states: waiting, playing, results. `read_next_order` wraps to the start of the song and resets the counts there (the user's request in entry 3); with an ending, that wrap becomes "the song is over" and the reset moves to Start. `reset_counts`, `record_judgement` and the music start-up lines are reused.
- When the song is over: the reader reaches the end one lead time before the music does. The last row still lasts one row's time, so the music's end is the reader's end plus one row plus the lead. The driver is stopped with `remove_VBL(hUGE_dosound)` and the sound hardware switched off, or it would start the tune again.
- A note in the song's last rows could still be falling when the music ends; the results wait until no note is in play.
- `J_START` is the Start button. A press is detected the same way as lane presses.
- `scripts/check_rom.py` -- the first play records every frame; scenario plays press against its schedule and read counts at a "quiet moment", which becomes "on the results". The check for a reset when the song loops is replaced by the play-again check. Every play now needs a Start press first.
- `assets/` -- words are 5 by 7 letters with a grey underline, generated with Pillow; the letters A, U and L are not drawn yet. 30 of 128 tiles used.
- `docs/setup.md` -- "How judging works" describes the loop and reset; step 5 describes the check.

## Tasks & Acceptance

**Execution:**
- [ ] `assets/` -- images for "PRESS START" and "RESULTS".
- [ ] `src/game.c` -- the three states; Start to begin and to play again; the ending; the results heading and prompt; counts reset on Start, not on a loop.
- [ ] `scripts/check_rom.py` -- press Start in every play; check nothing happens before it; find the ending; read counts on the results; play a second time and check zero at its start and the same result at its end; scenarios for Start mid-song and lane buttons while idle. `Makefile` -- pass the two new images.
- [ ] `docs/setup.md`, `README.md` -- how a play starts and ends, and the check's new steps.
- [ ] Verify every matrix row, restoring the source after the deliberate break.

**Acceptance Criteria:**
- Given the ROM opened and left alone, when two seconds pass, then no note has fallen and no music has played.
- Given a play with no presses, when the song ends, then the results show misses equal to the notes that fell, and perfect and good at zero.
- Given the results, when Start is pressed, then within a few frames all three counts read zero.
- Given the song ended, when ten more seconds pass with no Start, then there is still no sound.
- Given `git status --short`, then nothing under `tools/` or `build/` is listed.

## Implementation Notes

## Plan Change Log

## Review Triage Log

## Design Notes

**The results screen is the play screen with a heading.** When the song ends, the markers and the three counts stay where the player has been watching them, a "RESULTS" heading and the "PRESS START" prompt appear in the empty space above, and nothing falls. A separate screen would mean drawing the counts a second way for no gain in a first playable; if the user wants a distinct screen, it is a small change later.

**The score reset from entry 3 moves.** It was tied to the song coming round. There is no coming round now, so the counts are cleared when Start is pressed, which is what the user's request amounts to once the song ends.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS mentioning Start, the ending and the second play
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- `make debug` -- expected: exit 0

**Manual checks (if no CLI):**
- None required; `make run` lets the user try it.
