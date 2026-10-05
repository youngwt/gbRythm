---
title: "The timing windows feel fair"
ticket: 6
status: done
---

## Implementation Notes

No build was run for this story and nothing was changed.

- After playing the full verse in stories 3.3 to 3.5, the user said on 2026-10-05: "I think the timing is good enough". The story's check is the user's judgement of the feel, so it is met as it stands.
- The values stay as built: perfect within 3 frames of a note landing, good within 7, in `src/game.c` and `scripts/check_rom.py`. The tempo stays at 10 frames a row, 90 beats a minute, and notes fall for one second at 2 pixels a frame.
- The user did not say anything about the quick pairs of notes a third of a second apart, which the epic had flagged as a question; "good enough" is taken to cover them. This reading is the agent's.
- `make check` and `make check-debug` passed with these values at the end of story 3.5 and no code has changed since.
