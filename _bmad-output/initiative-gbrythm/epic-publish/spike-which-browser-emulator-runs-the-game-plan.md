---
title: 'Which browser emulator runs the game'
type: 'chore'
ticket: '3'
created: '2026-10-05'
status: done
baseline_revision: '0e896618ab4de55573b2c52d89931c5681520924'
route: 'oneshot'
route_source: 'auto'
risk: 'low'
review: 'quick'
review_source: 'pinned'
lenses_ran: ['quick']
review_loop_iteration: 0
context:
  - '{project-root}/_bmad-output/initiative-gbrythm/spec-publish/spec-publish.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** The play page of entry 4 cannot be planned until a browser Game Boy emulator is chosen. It must run this ROM correctly, let keys be mapped to the six buttons the game uses (Left, Up, Right, B, A and Start), play the sound, be embeddable as static files on GitHub Pages at a pinned version, and carry a licence that allows publishing it. None has been researched.

**Approach:** Find the candidates, try the released ROM (`v0.1.0`) in each in a real browser, and compare them on correctness, key mapping, sound, licence and size. The user chooses one. The choice, its version and licence, and the evidence that it plays the song through with sound are recorded in the epic's Notes. No play page is built and the game does not change.

</frozen-after-approval>

## Implementation Notes

Oneshot route: the repository's change is a few lines in the epic's Notes. The trial pages and scripts are throwaway and stay out of the repository.

The ROM tried, 2026-10-05: `gbrythm.gb` from release `v0.1.0`, 32,768 bytes, SHA-256 `2f12b737…c092f9`.

How each was tried. A small page per emulator was served from this machine and opened in headless Chromium 145 by a script. The script read the emulator's canvas with the project's own `scripts/screen.py` and listened to the page's sound with `scripts/sound.py`. Play 1: press Start and nothing else. Play 2: press each lane's key, through the browser's keyboard, as its note reaches the marker.

| | binjgb v0.1.11 | WasmBoy 0.7.1 | EmulatorJS 4.2.3, Gambatte core |
|---|---|---|---|
| Picture | start screen, five markers, falling notes and results all found pixel for pixel | the same | the same |
| Play 1 | results after 33.2 s; perfect 0, good 0, miss 35 | 32.8 s; 0, 0, 35 | 33.0 s; 0, 0, 35 |
| Play 2, keys | perfect 35, good 0, miss 0 | perfect 34, good 1, miss 0 | perfect 35, good 0, miss 0 |
| Sound | silent before Start; D, E, G, A and B heard during the song; silent on the results | the same | the same |
| Keys | a table in the page's own script, any key to any button | built-in defaults, changed through its settings | built-in defaults, changed through a setting; has its own menus and Start Game button |
| Licence | MIT | GPL 3.0 or later | GPL 3.0; the core is GPL 2.0 |
| Size downloaded | 132 KB, two files | 361 KB, one file | about 1.4 MB, four files |
| Last release | August 2021; the repository was last changed September 2026 | May 2022 | July 2025 |

Not tried, and why:

- mGBA's web build (`@thenick775/mgba-wasm` 2.5.1, MPL 2.0): its README says the page must be served with two cross-origin isolation headers. GitHub Pages cannot set headers.
- `gameboy-emulator` 1.1.2 by roblouie: its README says sound needs the same two headers.
- gameboy.js by juchi (MIT): no release, tag or built file to pin.
- GameBoy-Online by taisel: no licence, unchanged since 2019.

Other findings:

- Under the rule real browsers apply, that sound needs a key press or click first, binjgb's and WasmBoy's sound was suspended before any key and running after Enter was pressed, in Chromium. Entry 4's page should still start the sound itself on the first key press and not rely on that.
- A key pressed and released inside one frame is not seen by the game in any of the three. A real key press lasts several frames, so this only matters to scripts.
- Firefox was not tried: it would not start inside this machine's sandbox. Nobody has listened to any of the three; the script measured pitch, not quality.
- The song took the same time in all three, about 33 seconds from Start to the results.
- In play 2 each emulator gave one stray pitch outside the five (C, G sharp, A sharp). Play 1, sampled more slowly, gave none. It is taken to be the listening window straddling two notes, and was not looked into further.

The choice: the user chose binjgb v0.1.11 on 2026-10-05, when shown the comparison above. It and its evidence are recorded in the epic's Notes. The user was offered the trial pages to try first and did not ask to.

No commit was made: the user commits their own work.

## Review Triage Log

Quick lens run inline by the implementing session, not by an independent reviewer. Counts: high 0, medium 0, low 1, false 0, maybe-false 0.

- low, patched: the table says only the five pitches were heard, but play 2 also gave one stray pitch per emulator; the note above now says so.
- Checked and found sound: every figure in the table and in the epic's Notes was read back from the trial's saved output; the two file sizes and the commit of the tag were read from GitHub; the ticket's `verify` is met by the two notes added to the epic.

## Verification

**Manual checks (if no CLI):**
- `_bmad-output/initiative-gbrythm/epic-publish/epic-publish.md`, Notes: names the chosen emulator, its version and licence, and the evidence that it plays the song through with sound; the "Unknown: which browser emulator" note is answered.
- `make check` is not rerun: no game code, build file or workflow changes.
