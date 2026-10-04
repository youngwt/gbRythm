---
title: 'The driver links and the check hears a sound'
type: 'feature'
ticket: '1'
created: '2026-10-04'
status: done
baseline_revision: '5a72ba618c3d0e549e64f7631abf6eb34df802e2'
route: 'full'
route_source: 'auto'
risk: 'medium'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-music-proof/spec-music-proof.md'
  - '{project-root}/_bmad-output/initiative-gbrythm/epic-dev-environment/spec-dev-environment/stack.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The game depends on the hUGEDriver music library, whose packaged build was made for GBDK 4.1.1. Nothing in this repository plays a sound, and the headless check cannot tell a ROM with music from a silent one.

**Approach:** Install the packaged hUGEDriver 6.1.3 into `tools/`, link it into the proof ROM with a hand-written song of a few notes, make the headless check fail when no sound is produced, and write down in the instructions how the driver is installed and whether the packaged library worked with GBDK 4.5.0.

## Boundaries & Constraints

**Always:**
- The driver lives under `tools/`, is never committed, is found by explicit path, and its version and checksum are pinned in the instructions. Each instruction step says why it exists.
- The existing checks keep passing: screen not blank, both images shown, screen changes on A. The ROM stays 32K or smaller with no mapper.
- The sound check runs with no window.
- C follows the hardware rules in `stack.md`.
- Changes are left uncommitted for the user, with a suggested commit message.

**Never:**
- No other music driver and no change to the driver's source.
- No Amazing Grace yet, no check that notes change over time, no full explanation of Game Boy music: entries 2 and 3 own those.
- Nothing timed to the music, no sound effects, no tracker.
- No build switch for a silent ROM; the silent case is proven by a temporary source edit, as earlier stories did.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Music plays | `make check`, tools installed | PASS, exit 0; the message says sound was heard | No error expected |
| Silent ROM | ROM built with the music start-up removed from the C source | FAIL saying no sound was produced, non-zero exit | Source restored afterwards |
| Existing checks | A ROM that ignores A, or does not draw an image | Still fails as before | No change |
| Driver missing | `make` with no `tools/hugedriver` | Non-zero exit | One-line message pointing at `docs/setup.md` |
| Size | `make` | `build/gbrythm.gb` is 32768 bytes or fewer | No error expected |

</frozen-after-approval>

## Code Map

Found during planning, in a scratch folder outside the repository:

- hUGEDriver 6.1.3 -- `https://github.com/SuperDisk/hUGEDriver/releases/download/v6.1.3/hUGEDriver-6.1.3.zip`, sha256 `587f108681d49104349d8f9ea4db4be5fbeca70b09d66a3037db767b2e1c2c82`. Holds `gbdk/hUGEDriver.lib` and `include/hUGEDriver.h`; the rest is for a different toolchain.
- Compatibility, already answered: the driver's own GBDK example links against this library with GBDK 4.5.0 (`lcc -Iinclude -Wl-l<path>/hUGEDriver.lib`), and in PyBoy with sound emulation on it produced sound in 185 of 240 frames. The packaged library works; RGBDS is not needed. Record this, with the commands, in the instructions.
- Driver use from C (from the example): switch sound on with `NR52_REG = 0x80; NR51_REG = 0xFF; NR50_REG = 0x77;`, then inside `__critical { }` call `hUGE_init(&song)` and `add_VBL(hUGE_dosound)`.
- Song format (`hUGEDriver.h`): a `hUGESong_t` of tempo, `order_cnt` (twice the number of patterns in the order), four order lists of pattern pointers, three instrument tables, routines (`NULL`), and wave data. A pattern is 64 rows of `DN(note, instrument, effect)`; `___` is no note. The example's `sample_song.c` shows every part; do not copy the song itself.
- `Makefile` -- `lcc` is called on three lines, all taking `$(LCCFLAGS)`; reuse the `require-` pattern. The debug build re-runs the same rules, so it must link the driver too.
- `src/main.c` -- start the music after the images are drawn; the main loop already waits on `vsync()`.
- `scripts/check_rom.py` -- creates PyBoy with `sound_emulated=False`. With it `True`, `pyboy.sound.ndarray` is the current frame's samples (801 by 2, `int8`), all zero when silent. Sound registers read back as `0xFF`, so pitch cannot be read from them.
- `docs/setup.md` -- the build needs the driver, so its install step goes before "Build the ROM"; later steps renumber, and the text refers to steps by number in places. "What was found" takes the compatibility answer.

## Tasks & Acceptance

**Execution:**
- [x] `tools/hugedriver/` -- download, verify and unpack the release -- the driver, kept out of git.
- [x] `src/song.c`, `src/song.h` -- a song of a few notes on one channel, written by hand with comments on each part -- something to hear, and the first worked example of the format.
- [x] `src/main.c` -- switch sound on and start the driver -- the ROM plays.
- [x] `Makefile` -- add the driver's include path and library to compile and link, and `require-hugedriver` -- one command still builds, normal and debug.
- [x] `scripts/check_rom.py` -- turn sound emulation on, count frames with sound before A is pressed, fail when there are none -- the check hears.
- [x] `docs/setup.md` -- the install step with its reason, a short note on what the driver is and how the check hears, the compatibility answer in "What was found", the table row, and renumbered steps.
- [x] Verify every matrix row, restoring the source after the silent case.

**Acceptance Criteria:**
- Given tools installed, when `make check` runs with no display, then it passes and reports sound.
- Given the music start-up removed from the source, when `make check` runs, then it fails naming the missing sound.
- Given the finished work, when `git status --short` runs, then nothing under `tools/` or `build/` is listed.
- Given `docs/setup.md`, when its driver step is run as written from a checkout without the driver, then `make check` passes.
- Given `docs/setup.md`, when read, then it states that the packaged library worked with GBDK 4.5.0 and how that was shown.
- Given `make debug`, when it runs, then the debug ROM builds with the driver linked.

## Implementation Notes

Implemented inline, without a subagent, by the user's standing choice. No commit was made: the user commits their own work.

- Installed hUGEDriver 6.1.3 in `tools/hugedriver/` (checksum OK). `Makefile` adds its include path to the compile of `src/` files and `-Wl-l<library>` to the link, plus `require-hugedriver`. The debug build links it through the same rules.
- `src/song.c` and `src/song.h`: one 64-row pattern on channel 1, seven notes up and down a C chord eight rows apart, then a rest; the other three channels play an empty pattern. Tempo 7. The rest is a note on an instrument with no volume, since a pattern row cannot say "stop". Every part of the format is commented.
- `src/main.c` switches sound on and starts the driver after the images are drawn.
- Surprise: a ROM with no music still produces sound in 11 frames, about frames 35 to 45 after start. "Any sound at all" would therefore pass a silent ROM, and did on the first run. The check now ignores the first 60 frames. Where the blip comes from (the emulator's start-up state or GBDK's own start-up code) was not established.
- Surprise: the music does not start until about frame 82, after the text and images are drawn, so the check hears it in 38 of the 60 frames it listens to.
- The Design Notes' "fail on zero frames" holds, with the listening window narrowed as above.
- The ROM is still exactly 32768 bytes: the driver and song fit in the padding.
- `docs/setup.md`: new step 3 for the driver, later steps renumbered 4 to 9 with the two in-text step references updated, the check's description extended, two answers added to "What was found", two table rows.

Verified by running each matrix row, restoring the source after each edit:

- Music plays: `make check` with `DISPLAY` and `WAYLAND_DISPLAY` unset, PASS, "sound heard in 38 of 60 frames".
- Silent ROM: music start-up removed, `FAIL: no sound was produced between frames 60 and 120`, non-zero. Also fails the same way with the driver running but the sound hardware left off.
- Existing checks: a ROM ignoring A fails on the button; a ROM not drawing the note image fails on the image.
- Driver missing: `make` exits non-zero with the pointer to `docs/setup.md`.
- Size: 32768 bytes. `make debug` exits 0 and writes its `.cdb`.
- The driver step in `docs/setup.md` was run as written after deleting `tools/hugedriver` and `build`; `make check` then passed.
- Not done: nobody has listened to it. That is entry 2's human step, though `make run` plays these notes now.

## Plan Change Log

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 1, medium 0, low 1, false 0, maybe-false 0.

- high, patched during implementation: the sound check passed a silent ROM because of the start-up blip (see Surprise above). Fixed by ignoring the first 60 frames; the silent case now fails.
- low, patched: a sentence in `docs/setup.md` about the remaining open question was left ungrammatical by an edit. Rewritten.

## Design Notes

The check counts frames with any non-zero sample and fails on zero. It does not judge what the sound is; entry 2 adds that the notes change. Keeping the threshold at "any sound" avoids a number that would need tuning when the song changes.

## Verification

**Commands:**
- `make clean && make check` -- expected: exit 0, PASS mentioning sound
- `stat -c %s build/gbrythm.gb` -- expected: 32768 or less
- `make debug` -- expected: exit 0
- `git status --short` -- expected: only source, script, docs and plan files

**Manual checks (if no CLI):**
- None required. Listening in Emulicious belongs to entry 2, though `make run` will already play the notes.
