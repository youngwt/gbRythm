---
title: 'Presses are judged perfect, good or miss'
type: 'feature'
ticket: '3'
created: '2026-10-05'
status: done
baseline_revision: '2b642561fdbe1332cb3e9c9ea32f4d50448880c0'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-first-playable/lane-mapping.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Notes fall in the right lanes at the right time, but pressing a button does nothing. There is no game until a press is judged.

**Approach:** Read the five lane buttons. Grade each press against the nearest note in that lane as perfect or good by how close it is to landing, count a note nobody pressed in time as a miss, and show the latest judgement and running counts on screen. Presses with no note near are ignored. The headless check plays the song with scripted presses and reads the counts off the screen.

**Starting timing windows, to be tuned by play in entry 6:** perfect is within 3 frames either side of landing (a twentieth of a second); good is within 7 frames (about an eighth of a second); beyond that a press does nothing and the note becomes a miss.

## Boundaries & Constraints

**Always:**
- A press is judged once, on the frame the button goes down; holding it does nothing more.
- A note is judged once: perfect, good or miss. Counts only ever go up.
- A press with no note within the good window in that lane changes nothing, including a press of the wrong lane's button.
- The check judges what is on screen and in the sound, with no window, and reads counts from the screen, not from the program's memory.
- Notes stay in time, in lane and steady, as entries 1 and 2 left them. ROM 32K or smaller, no mapper; C rules in `stack.md`.
- Changes are left uncommitted for the user, with a suggested commit message.

**Never:**
- No Start, no results screen, no end to the song, no longer song, no window tuning by feel: entries 4 to 6.
- No points, combos, held notes, sound effects or fail state.

## I/O & Edge-Case Matrix

| Scenario | Presses | Expected counts | Error Handling |
|----------|---------|-----------------|----------------|
| No presses | none | every note a miss | No error expected |
| On time | each lane's button on the frame its note lands | every note perfect | No error expected |
| Edge of perfect | 3 frames late | every note perfect | No error expected |
| Just outside perfect | 4 frames late | every note good | No error expected |
| Edge of good | 7 frames late, and 7 early | every note good | No error expected |
| Too late | 8 frames late | every note a miss; perfect and good stay 0 | No error expected |
| Stray | a wrong lane's button as each note lands, and the right button far from any note | every note a miss; perfect and good stay 0 | No error expected |
| Held | every button held down throughout | every note a miss after the first press | No error expected |
| Judging broken | the perfect window widened in the C source | `make check` fails naming the scenario and the counts | Source restored afterwards |

</frozen-after-approval>

## Code Map

- `src/game.c` -- `game_tick` moves each note 2 pixels a frame and removes it the frame after it reaches the marker; that removal becomes "after the good window has passed", as a miss. `lane_x` and the sprite pool are reused. Notes currently start at the top of the screen and the markers are on row 15; see Design Notes for why both move.
- Distance is time: at 2 pixels a frame, 3 frames is 6 pixels and 7 frames is 14, so a press is judged by how far the note is from the marker.
- GBDK -- `joypad()` returns the buttons held; `J_LEFT`, `J_UP`, `J_RIGHT`, `J_B`, `J_A`. A new press is a button held now and not last frame.
- `scripts/check_rom.py` -- one run with no presses already yields each note's landing frame and lane; scripted runs press against that schedule. PyBoy: `pyboy.button(name)` presses for one frame; `tick(n, render=False)` runs without drawing. `find_on` locates an image on a screen.
- `scripts/convert-images.sh` -- an image must contain all four shades to be shown as drawn (deferred finding from entry 1); 128 tiles are available and 6 are used.
- Division and multiplication are avoided on this hardware: counts are kept as two digits each, not divided by ten.
- `docs/setup.md` -- step 5 describes the check; "How the falling notes work" describes the screen.

## Tasks & Acceptance

**Execution:**
- [x] `assets/` -- images for the words PERFECT, GOOD and MISS and the digits 0 to 9, so the check can find and read them like any other image.
- [x] `src/game.c` -- read new presses; judge against the nearest note in the lane; let notes fall on past the marker until the good window closes, then count a miss; draw the latest judgement and the three counts; move the markers up to make room.
- [x] `scripts/check_rom.py` -- play each matrix scenario with scripted presses and read the three counts from the screen at a quiet moment in the song; keep every existing check on the no-press run. `Makefile` -- pass the new images.
- [x] `docs/setup.md` -- how judging works, the windows and where to change them, the screen layout, and the check's scenarios.
- [x] Verify every matrix row, restoring the source after the deliberate break.

**Acceptance Criteria:**
- Given the built ROM, when `make check` runs with no display, then it passes and reports each scenario's counts.
- Given a note judged perfect or good, when it is judged, then it disappears and the latest-judgement word and its count change in the same frame.
- Given the windows changed in the C source, when checked, then it fails naming the scenario.
- Given the frame-rate check from entry 1, when judging and drawing happen in the same frame, then notes still move steadily.
- Given `git status --short`, then nothing under `tools/` or `build/` is listed.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits their own work.

- `src/game.c`: reads new presses each frame, judges each against the nearest note in its lane, removes judged notes, lets unpressed notes run 7 frames past the marker and then counts a miss, and draws the latest word and the three two-digit counts. Markers moved from row 15 to row 13; notes start just above the top edge. The title and the built-in text routines are gone.
- Windows as approved: perfect 3 frames, good 7, in `src/game.c` and `scripts/check_rom.py`.
- `assets/`: `word_perfect.png`, `word_good.png`, `word_miss.png` (all 48 pixels wide so one replaces another cleanly) and `digits.png`, drawn with Pillow in a 5 by 7 letter shape with the same grey underline as the markers.
- `scripts/check_rom.py` takes named arguments now. After the no-press play it plays ten scenarios with scripted presses, taking each note's landing frame and lane from the first play, and reads the counts from the screen by matching digit tiles.
- Surprise: without the text routines nothing was drawn but sprites. They had been switching the background on. The game now does it itself.
- Surprise, and the main finding: what the player sees is a frame behind the game. Sprite positions reach the screen one frame later than background changes. The first version judged against the game's own position and the probe showed the windows off-centre: 4 frames early to 2 late for perfect. Presses are now judged before notes move and against a height one step past the marker; the probe then showed perfect from 3 early to 3 late and good to 7 either side, measured against what is on screen.
- The song has 16 notes, not 15: "sound" and "that" are the same pitch and earlier lists merged them. The check's landings count them separately.
- ROM use fell to 5,641 bytes with the text routines gone.

Verified by running each matrix row, restoring the source after each deliberate break:

- `make check` with no display: PASS; all ten scenarios scored as the matrix says over the first 16 notes; the no-press play still has every note in lane, steady, and landing in the frame its sound starts.
- Perfect window widened to 4 in C only: `FAIL: with presses 4 frames late … shows 16 perfect`.
- Good window narrowed to 6: fails on presses 7 frames late.
- Press detection changed to "held": fails on every button held down.
- Stray presses made to count as misses: fails, showing 32 misses.
- Lanes swapped, and notes made late: fail as in entries 1 and 2.
- Size 32768 bytes; `make debug` exits 0. The screen after a press was opened and shows the markers, the latest word and the counts.
- One acceptance criterion is met only to within a frame: after an on-time press the word and count change together, and the note disappears one frame later. This is the sprite lag described above.
- Not done: `make run` and F5, which need a person at a window. The feel of the windows is entry 6.

## Plan Change Log

After the build, the same day, at the user's request ("reset the score when the song loops over"):

- The three counts go back to zero and the latest judgement is cleared when the song starts again. The reset is done when the reader wraps to the start of the song, which is the moment the first note of the new time through begins to fall, one second before the music restarts. Resetting when the music itself restarts would wipe an early press on that first note.
- This goes beyond the frozen intent, which said counts only ever go up; the change is the user's.
- The check reads the counts just before the first note of the second time through lands and requires all three to be zero. With the reset removed it fails: "the counts should go back to zero when the song starts again, but the screen shows 0 perfect, 0 good, 16 miss".
- A note from the end of one time through that is still falling when the reader wraps would be counted in the new score. No note in this song is that late. Entry 4 replaces the loop with an ending, which removes the case.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 1, medium 0, low 1, false 0, maybe-false 0.

- high, patched during implementation: presses were judged a frame late relative to the screen (see the main finding above). Found by probing every press timing from 10 frames early to 10 late, fixed, and now held by the check's edge scenarios.
- low, accepted: a judged note disappears one frame after its word and count change. Fixing it would mean delaying the background writes by a frame; a sixtieth of a second is not worth the complication. Recorded in `docs/setup.md`.

## Design Notes

**Screen layout.** The markers move up two rows so a late note has room to carry on below them without running into the text. Below the markers: one line for the latest judgement word, then the three counts, each labelled with its word. The `GBRYTHM` title is dropped; the lines are needed and a title screen is out of scope. Notes now start just above the top edge, so they still take one second to reach the markers.

**Words and digits are images.** The check reads the screen by finding PNGs on it. Drawing the words and digits from PNGs, not the built-in text font, lets it read counts the same way it finds markers. They are placeholders drawn by the agent.

**The windows are stated twice,** in the C source and in the check, like the lanes: the check has to know the design to hold the ROM to it.

**Reading counts at a quiet moment.** The song still loops, so the check reads the counts in the middle of the longest gap between notes, when every earlier note has been judged and the next is not yet near.

**If drawing a judgement makes the game miss a frame,** the steady-motion check will say so; the fix is then to draw less per frame, and the finding is recorded.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS listing each scenario
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- `make debug` -- expected: exit 0

**Manual checks (if no CLI):**
- None required; `make run` lets the user try it, and tuning by feel is entry 6.
