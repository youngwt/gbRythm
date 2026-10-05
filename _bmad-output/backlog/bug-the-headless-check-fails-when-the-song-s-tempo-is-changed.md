---
id: 4
type: bug
title: "The headless check fails when the song's tempo is changed"
parent: none
covers: []
after: []
assignee: ""
refined: false
hitl: false
risk: low
severity: P2
---

# The headless check fails when the song's tempo is changed

## Description

Changing the song's tempo, and nothing else, makes `make check` fail, although the game plays the faster song correctly. The instructions say the tempo number is all that needs changing, and that the check follows the song. After this, a song at a different tempo passes the check with no edit to the check, or the check says plainly that the tempo is beyond what it can hear.

## Reproduction

In the song file, change the tempo at the bottom from 10 to 8. Run `make check`.

- Actual: `FAIL: with stray presses, the 35 notes should score 0 perfect, 0 good, 35 miss but the screen shows 0 perfect, 1 good, 34 miss`.
- Expected: PASS, as at tempo 10. The game is behaving as designed; the timing, lane and other press scenarios pass before this one fails.

With the tempo at 6:

- Actual: `FAIL: 70 notes landed on a marker but 68 notes were heard; every note of the tune should have one falling note`.
- Expected: PASS, or a failure that says the check cannot follow notes this close together.

Both were run on 2026-10-05 at commit `d826091`. Restore the tempo afterwards.

## Cause Hypothesis

Two separate limits in the check, neither in the game.

At tempo 8 the tune's quickest notes are 16 frames apart. The stray-press scenario presses a note's own button a fixed number of frames after it lands, to show that a press with no note near is ignored. At 16 frames apart that press is within the good window of the next note in the same lane, so the game rightly scores it.

At tempo 6 those notes are 12 frames apart, and two of them are the same pitch. The check tells a repeated note from a held one by a rise in loudness as the new note starts. A note fades slowly, so after 12 frames the rise is too small to count.

## Acceptance Criteria

1. **A faster song passes**
   **Given** the song with its tempo changed from 10 to 8 and nothing else edited
   **When** `make check` runs
   **Then** it passes, with the same count of notes and every way of pressing judged as designed
2. **A slower song passes**
   **Given** the song with its tempo changed from 10 to 14
   **When** `make check` runs
   **Then** it passes
3. **Too fast to hear is said plainly**
   **Given** a tempo at which the check can no longer tell a repeated note from a held one
   **When** `make check` runs
   **Then** it either passes, or fails with a message that says the notes are too close together for the check to follow, not that the game dropped a note
4. **Stray presses are still tested**
   **Given** the game changed so that a press with no note near counts as a miss
   **When** `make check` runs at tempo 10 and at tempo 8
   **Then** it fails at both
5. **The instructions match**
   **Given** the setup instructions' sections on changing the tune and on the check
   **When** read after this change
   **Then** they say which tempos the check can follow, and no longer promise more than that
6. **Or: no change is needed, with proof**
   **Given** the reproduction
   **When** it is run on the current code
   **Then** the check already passes at tempo 8, with the evidence recorded in Notes; this supersedes 1 to 5

## Boundaries

- Must not change: the game itself, the song as committed (tempo 10), the timing windows, and every failure the check reports today at tempo 10.

## References

- retrospective — _bmad-output/initiative-gbrythm/epic-first-playable/epic-first-playable-retrospective.md, finding F1
- instructions — docs/setup.md, sections "How the falling notes work" and "How the music works", the paragraphs on changing them
- spec — _bmad-output/initiative-gbrythm/spec-first-playable/spec-first-playable.md, the constraint that falling notes are derived from the song's data

## Notes

- Decision: raised from the first-playable retrospective as its one fix-now item; to be done before a second song is added, since a second song brings its own tempo (2026-10-05).
- Assumption: tempo 8 must pass outright, and anything faster may fail as long as it fails honestly. Tempo 8 puts the quickest notes about a quarter of a second apart, which is already fast to play.
- Open question: whether the check's hearing can be made to follow closer repeated notes cheaply, or whether saying so is enough.
