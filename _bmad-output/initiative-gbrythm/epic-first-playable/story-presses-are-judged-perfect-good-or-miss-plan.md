---
title: 'Presses are judged perfect, good or miss'
type: 'feature'
ticket: '3'
created: '2026-10-05'
status: 'ready-for-dev'
baseline_revision: ''
route: 'full'
route_source: 'auto'
risk: 'medium'
review: ''
review_source: ''
lenses_ran: []
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
- [ ] `assets/` -- images for the words PERFECT, GOOD and MISS and the digits 0 to 9, so the check can find and read them like any other image.
- [ ] `src/game.c` -- read new presses; judge against the nearest note in the lane; let notes fall on past the marker until the good window closes, then count a miss; draw the latest judgement and the three counts; move the markers up to make room.
- [ ] `scripts/check_rom.py` -- play each matrix scenario with scripted presses and read the three counts from the screen at a quiet moment in the song; keep every existing check on the no-press run. `Makefile` -- pass the new images.
- [ ] `docs/setup.md` -- how judging works, the windows and where to change them, the screen layout, and the check's scenarios.
- [ ] Verify every matrix row, restoring the source after the deliberate break.

**Acceptance Criteria:**
- Given the built ROM, when `make check` runs with no display, then it passes and reports each scenario's counts.
- Given a note judged perfect or good, when it is judged, then it disappears and the latest-judgement word and its count change in the same frame.
- Given the windows changed in the C source, when checked, then it fails naming the scenario.
- Given the frame-rate check from entry 1, when judging and drawing happen in the same frame, then notes still move steadily.
- Given `git status --short`, then nothing under `tools/` or `build/` is listed.

## Implementation Notes

## Plan Change Log

## Review Triage Log

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
