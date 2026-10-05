---
title: "The song's notes fall in time in one lane"
type: 'feature'
ticket: '1'
created: '2026-10-05'
status: done
baseline_revision: '6333a17ede871ce46de37e9957574e307bdef6ba'
route: 'full'
route_source: 'auto'
risk: 'medium'
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

**Problem:** The ROM plays a song and shows two pictures, but nothing moves and nothing follows the music. Whether notes can fall in time with the song, taken from the song's own data, inside 32K and at full speed, is unproven, and the rest of the game depends on it.

**Approach:** Replace the proof screen with a play screen: each note of the song already in the ROM falls down one lane and reaches a target line as it sounds. The falling notes are read from the song's data ahead of the music. The headless check measures the gap between each note's arrival and its sound, and the instructions record the size and speed findings.

## Boundaries & Constraints

**Always:**
- Falling notes come from the song's own data; no second copy of the tune anywhere, in C or in the check.
- The check runs with no window and judges what is on the screen and in the sound, not the program's memory.
- The ROM stays 32K or smaller with no mapper. C follows the rules in `stack.md`.
- If the game cannot hold 60 frames a second or does not fit, stop and report; do not add a mapper or lower the frame rate.
- Changes are left uncommitted for the user, with a suggested commit message.

**Never:**
- No lanes by pitch, no button input, no judging, no Start or results screen, no longer song: entries 2 to 5 own those.
- No change to the song's notes or tempo.
- No harmony, sound effects or new tools.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Notes in time | `make check` | PASS: one falling note per melody note, each arriving within two frames of its sound; the message gives the counts and the largest gap | No error expected |
| Notes late | Notes made to fall with a wrong lead time | FAIL naming the gap | Source restored afterwards |
| Note missing | A note that sounds but does not fall, or the reverse | FAIL naming the two counts | Source restored afterwards |
| Stutter | A falling note that does not move the same distance every frame | FAIL saying the frame rate did not hold | No change |
| Repeat | The song loops | The notes of the second time through are in time as well | No error expected |
| Silent ROM, one-note tune | As before | Still fail as before | No change |
| Size | `make` | 32768 bytes or fewer | No error expected |

</frozen-after-approval>

## Code Map

- `src/song.c` -- the tune is `proof_song`, reachable from other files through its `order1` list of patterns, its tempo and its instrument table. A row is three bytes: note in the low seven bits of the first (90 is "no note"); instrument from the first byte's top bit and the second byte's high half; effect code in the second byte's low half with its setting in the third. Effect `D` ends the pattern early. Instrument 2 has no volume and is the rest, so "is this a note" must also ask whether the instrument's starting volume is above zero. Not edited.
- `src/main.c` -- the proof screen: text, two images, an A-button message, then the music start. The music start-up lines are reused; the rest is replaced.
- Measured in the music epic: the driver plays row N exactly N times tempo frames after it starts; tempo is 10; the quickest notes are 20 frames apart.
- GBDK -- background and sprite tiles 128 to 255 share memory, so a tile from a converted PNG can be shown as a sprite with the same tile number. Sprite colour 0 (white in the PNG) is transparent. `add_VBL` runs a function every frame.
- `assets/arrow.png`, `assets/note.png` -- the proof images; removed. `scripts/convert-images.sh` and the Makefile rule stay as they are.
- `scripts/check_rom.py` -- reusable: `shades`, `appears_on`, `note_in`, `notes_heard`, the per-frame sound capture. Replaced: the "every image on the first screen" rule and the before-and-after A-press comparison, which belong to the proof screen.
- `tools/gbdk/bin/romusage build/gbrythm.gb` -- reports bytes used. Today: 6653.
- `docs/setup.md` -- step 5 describes the old check; "Adding or changing an image" names the old images.

## Tasks & Acceptance

**Execution:**
- [x] `assets/` -- remove the two proof images; add a target marker and a falling-note image, each one 8x8 tile, the falling note with no white so it hides the marker when it lands.
- [x] `src/game.c`, `src/game.h` -- a reader that walks the song's rows a fixed lead ahead of the music, following pattern breaks and the loop, and a small pool of sprites that fall at a steady speed to land on the marker.
- [x] `src/main.c` -- draw the play screen, count frames on the vertical blank, start the music one lead time after the reader, and drive the game from the frame count.
- [x] `scripts/check_rom.py` -- find the marker, track the falling note on screen every frame, find each note's start in the sound, and compare; check steady motion; keep the sound checks; save one screenshot mid-song. `Makefile` -- pass what the check now needs.
- [x] `docs/setup.md` -- rewrite the check's description, add a short "How the falling notes work", record size and speed under "What was found", fix the image section's examples.
- [x] Verify every matrix row, restoring the source after each deliberate break.

**Acceptance Criteria:**
- Given the built ROM, when `make check` runs with no display, then it passes and reports as many falling notes as notes heard.
- Given a note added to or removed from the song file, when the ROM is rebuilt and checked, then it still passes with nothing else edited.
- Given the lead time changed in the C source, when checked, then it fails naming the gap.
- Given `romusage`, when run on the ROM, then the bytes used are recorded in the instructions.
- Given `git status --short`, then nothing under `tools/` or `build/` is listed.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits their own work.

- `src/game.c` and `src/game.h` are new: the song reader, a pool of eight sprites, and the play screen. `src/main.c` is now only the frame clock and the loop. `assets/arrow.png` and `assets/note.png` are removed; `assets/target.png` and `assets/falling.png` are new, 8x8, generated with Pillow.
- The reader walks `proof_song.order1` three bytes a row, follows the pattern-break effect and the loop, remembers the last instrument, and skips rows whose instrument has no starting volume, which is how the song writes a rest.
- Timing: the reader starts at once and the music starts `LEAD_FRAMES` (60) later. The first build started the music one frame earlier on a guess about the driver; the check measured every note landing one frame late, and with the music started at exactly `LEAD_FRAMES` every gap is zero.
- `scripts/check_rom.py` was rewritten around the game. It records every frame's screen and sound, finds the marker and the falling notes by looking for the two PNGs, finds note starts in the sound, and compares. It no longer takes a list of images to find, and no longer presses A. It saves one screenshot, `screenshot-play.png`. It is 270 lines and takes about two seconds.
- The falling note is matched on its non-white pixels only, since white is see-through on a sprite. The plan's idea of a falling note with no white was dropped: an image with no white is converted with its shades shifted (see below).
- A repeated pitch is detected as a new note by its jump in loudness.
- `docs/setup.md`: the check's description is rewritten, "How the falling notes work" is new, two findings are added, and the debugging steps point at a line in `src/game.c`, since the line they used is gone. `README.md` describes the current state.

Found along the way:

- The image converter numbers shades from the lightest one present, so an image with no white is shown with its lightest shade as white. This has been true since images were added. Both new images include white; the limit is now in the instructions and logged in `deferred-work.md`.

Findings the story was asked for:

- Size: 6,921 bytes used of 32,768.
- Speed: over 1,500 frames every falling note moved exactly 2 pixels in every frame, in PyBoy. One lane, no judging yet.

Verified by running each matrix row, restoring the source after each deliberate break:

- Notes in time: `make check` with no display, PASS, 23 notes fell and 23 were heard, every gap 0 frames, across the song's repeat.
- Notes late: music started 5 frames early, `FAIL: note 1 landed 5 frames after its sound started`.
- Note missing: a row made to drop nothing, `FAIL: 21 notes landed on the marker but 23 notes were heard`.
- Stutter: the game made to skip one frame in 256, `FAIL: the frame rate did not hold`.
- Song edited: one note added in `src/song.c` and nothing else, PASS with 25 and 25.
- One-note tune and music never started: fail as before.
- Size 32768 bytes; `make debug` exits 0.
- Not done: F5 with the new breakpoint line, and `make run`. Both need a person at a window.

## Plan Change Log

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 1, low 2, false 0, maybe-false 0.

- medium, patched: `docs/setup.md` told the reader to set a breakpoint on `a_was_pressed = 1;` in `src/main.c` and press A; that line was removed by this change. The steps now use a line in `src/game.c`. Not re-run by a person.
- low, patched: the first version of the check took 5.7 seconds, most of it searching blank start-up frames for the marker pixel by pixel. Now about 2.
- low, deferred: an image with no white is converted with its shades shifted. Pre-existing; documented and logged.

## Design Notes

**Reading ahead, not being told.** The game reads the song's rows itself, a fixed number of rows ahead of what is playing, and drops a note for each row that starts one. The music is started one lead time after the reader, so even the first note has time to fall. This keeps one source of truth and needs no markers added to the song. The driver's "call routine" effect was the alternative; it fires when a note plays, which is too late to start it falling.

**One clock.** A counter raised every vertical blank drives both the reader and the falling notes, and the game catches up if it ever runs behind, so falling notes cannot drift from the music.

**Starting numbers, to be tuned in entry 6:** notes fall 2 pixels a frame for 60 frames, one second, and land at the marker near the bottom of the screen.

**The check's file is not split yet.** It will pass 250 lines. The retrospective asked for a decision when gameplay checks arrived; entry 7, the sweep, makes it with the whole shape visible.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS with equal counts of notes fallen and heard
- `tools/gbdk/bin/romusage build/gbrythm.gb` -- expected: well under 32768
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- `make debug` -- expected: exit 0

**Manual checks (if no CLI):**
- None required. `make run` shows it; the user's play belongs to entries 5 and 6.
