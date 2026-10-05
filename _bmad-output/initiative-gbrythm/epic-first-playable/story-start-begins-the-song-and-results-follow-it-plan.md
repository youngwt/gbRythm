---
title: 'Start begins the song and results follow it'
type: 'feature'
ticket: '4'
created: '2026-10-05'
status: done
baseline_revision: 'ed197d5a9602263afc8243723fb513cf672be48b'
route: 'full'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
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
- [x] `assets/` -- images for "PRESS START" and "RESULTS".
- [x] `src/game.c` -- the three states; Start to begin and to play again; the ending; the results heading and prompt; counts reset on Start, not on a loop.
- [x] `scripts/check_rom.py` -- press Start in every play; check nothing happens before it; find the ending; read counts on the results; play a second time and check zero at its start and the same result at its end; scenarios for Start mid-song and lane buttons while idle. `Makefile` -- pass the two new images.
- [x] `docs/setup.md`, `README.md` -- how a play starts and ends, and the check's new steps.
- [x] Verify every matrix row, restoring the source after the deliberate break.

**Acceptance Criteria:**
- Given the ROM opened and left alone, when two seconds pass, then no note has fallen and no music has played.
- Given a play with no presses, when the song ends, then the results show misses equal to the notes that fell, and perfect and good at zero.
- Given the results, when Start is pressed, then within a few frames all three counts read zero.
- Given the song ended, when ten more seconds pass with no Start, then there is still no sound.
- Given `git status --short`, then nothing under `tools/` or `build/` is listed.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits their own work.

- `src/game.c` has three states. Waiting and results only listen for Start. `start_play` clears the score and messages and restarts the reader; the music follows one lead time later as before. When the reader reaches the end of the last pattern it stops reading and starts a countdown; at zero the driver is taken off the frame signal and the sound hardware switched off; when no note is left in play the heading and prompt are drawn.
- The reset of the counts moved from the song's wrap to Start, as planned.
- `assets/word_start.png` ("PRESS START", 9 tiles) and `assets/word_results.png` ("RESULTS", 6 tiles), drawn like the other words. 45 of 128 tiles are used.
- `scripts/check_rom.py`: the recorded run now presses Start, watches for the results heading to know the song has ended, waits ten seconds, presses Start again and runs to the second results. It checks the waiting state, the ending, the silence, the results and the second play from that one run. Scenario plays press Start first and read the counts off the results; two scenarios were added. It is about 600 lines and takes about five seconds.
- Surprise: the countdown to the music's end was one frame short as first derived. Stopping one frame later is still silent and two frames later lets the tune's first note sound; the value is now the last silent frame, and the check fails one frame beyond it.
- The same pitch played twice in a row ("sound", "that") is sometimes heard one frame early by the check in the second play. It is the check's loudness-jump detection, within the two frames allowed; the falling note itself is on time.
- ROM use is 6,269 bytes of 32,768.

Verified by running each matrix row, restoring the source after each deliberate break:

- `make check` with no display: PASS. Nothing before Start; 16 notes in each of two plays, in lane, steady, within 1 frame; silence for ten seconds on the results; second play from zero with the same results; all twelve press scenarios as designed, including Start mid-song and lane buttons while idle.
- Start made not to clear the score: `FAIL: the results of the second play … show 0 perfect, 0 good, 32 miss`.
- Start made to restart the song mid-play: fails on that scenario.
- The game made to start without Start: fails, the prompt is not found.
- The song made never to end: `FAIL: assets/word_results.png did not appear within 7200 frames of Start being pressed`.
- Music stopped one frame too late: `FAIL: sound came back in frame 1153, after the last note had died away`.
- Perfect window widened: fails as in entry 3.
- Not caught: stopping the music early. This song ends on a rest, so cutting it short removes only silence. A song ending on a sounding note would need a check of its last note's length.
- Size 32768 bytes; `make debug` exits 0. Both screens were opened and look as described.
- Not done: `make run` and F5, which need a person at a window.

## Plan Change Log

After the build, the same day: a bug reported by the user from playing in Emulicious.

- Report: "first time you press start after the results 16 sprites fall down quickly and the miss counter goes to 16, you then need to press start a second time for the scene to reset".
- Not reproduced. In PyBoy the second play is normal with single-frame and held presses of Start, Start pressed at 14 different moments around the end of the song, presses in the first play, in both plays, and with memory randomized at start-up. Emulicious's debug port was tried as a way to observe the game inside it and did not answer reliably enough to use.
- Found while looking: the debug ROM, the one F5 runs, failed the check. The tune's first note sounded for a frame at the end. The music was started and stopped from the game's per-frame code with `add_VBL` and `remove_VBL`, so its timing depended on how long that code took within a frame, and the slower debug build shifted it.
- Fixed: the music is now run from `game_frame`, on the vertical blank signal itself. It starts when the frame count reaches a booked value and stops after the driver has run exactly as many times as the song has frames, a total the reader adds up as it reads. No handler is added or removed during play. `src/main.c` is reduced to the loop. `MUSIC_START_FRAME` became `LEAD_FRAMES + 3`, measured by the check.
- `make check-debug` runs the same check on the debug ROM. Both ROMs pass.
- Whether this cures what the user saw is not known. It removes the one way found in which the two emulators could differ, and the report has gone back to the user to retest.
- The user's answers: during the quick run the music plays very quickly too; it lasts a second or two; they were using F5; the play after it is normal; it happens every time.
- Music playing fast rules out the game's own catch-up, which cannot speed the driver up. The whole emulator was running fast. The one thing the game did at the end of a song that it did not do at start-up was switch the sound hardware off (`NR52`). The likely cause, not confirmed: Emulicious keeps time by the sound it produces, falls behind while the sound hardware is off on the results screen, and races to catch up when it is switched back on.
- Changed: the sound hardware is left on. At the end of the song the driver stops being called and every channel is disconnected from both speakers (`NR51`), and they are reconnected on Start. Both ROMs pass the check. Not verified in Emulicious by the agent; the user has been asked to retest.
- The user then tried a second emulator, which they named as "GB+", and reported that the game "worked as expected on the prod and debug builds" there, concluding that it "looks like an issue with emulicious". Whether Emulicious still runs a play fast with the sound hardware left on has not been stated.
- The user retested in Emulicious: "emulicious still does it, now it even does it on the first press of start". So leaving the sound hardware on was not the cure, and that explanation was wrong.
- Measured inside Emulicious, through its debug port (which answers when the ROM is launched stopped at entry): a diagnostic build that starts a play by itself after three seconds of waiting, with no key pressed, ran at 60 to 66 frames a second through waiting, two full plays and the results between them, with Emulicious's sound both muted and on. The vertical blank handler always ran on the same screen line. The game does not make Emulicious run fast.
- So the fast play needs a real key press. Emulicious has a shortcut that toggles turbo, and its release notes give the Space key as the default (`WhatsNew.txt`: "toggling turbo via the SPACE key", and a later entry making the Toggle Turbo shortcut configurable). A toggle fits every observation: every other press of Start gives a fast play, the music races with it, the play after is normal, and which press is the fast one shifted between tests. Which key the user presses for Start has not been confirmed.
- Reverted: the sound hardware is switched off at the end of the song again, as first built. The diagnostic code is removed. `docs/setup.md` gains a note on Emulicious's turbo shortcut.
- Kept: the music run from the frame signal, and `make check-debug`. Those fixed a real defect, the debug ROM failing the check.
- The agent's runs of Emulicious added two entries to the recent-files list in `tools/emulicious/Emulicious.ini` and changed nothing else there.
- The user replied "lgtm" to the turbo explanation and the kept changes. They did not say which key they press for Start or whether Turbo was ticked, so the turbo shortcut remains the best explanation, not a confirmed one.
- Confirmed by the user afterwards: "it was the turbo, remapping start fixed it". The fast play was Emulicious's turbo shortcut sharing a key with Start. Not a defect in the game.
- The check's second play never follows a play with presses, and never has presses itself. Tried by hand in PyBoy and correct; not yet in the check.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 1, medium 0, low 3, false 0, false 1 (the user's report: Emulicious's turbo shortcut shared a key with Start; confirmed by the user after remapping).

- low, patched: the music's end was one frame early (see Surprise above).
- low, patched: the check did not notice the tune restarting for a frame or two at the end; a check for sound returning after the last note was added.
- high, patched after the build: the debug ROM failed the check because the music's timing depended on how long the game's code took (see the bug report above).
- low, deferred: an early stop of the music is not detectable with a song that ends on a rest. Logged in `deferred-work.md`.

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
