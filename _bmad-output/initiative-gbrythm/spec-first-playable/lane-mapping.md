# Lane mapping

How melody notes map to lanes and buttons in SPEC-first-playable. The user's design: lowest pitch on the left, highest on the right, within one octave.

| Lane, left to right | Button | Note | In the song file |
|---|---|---|---|
| 1 | Left | D | `D_5`, and the high D, `D_6` |
| 2 | Up | E | `E_5` |
| 3 | Right | G | `G_5` |
| 4 | B | A | `A_5` |
| 5 | A | B | `B_5` |

- A pitch maps to the same lane in every octave. The high D of "like me" falls in lane 1 with the low D.
- Names collide: the note A is played with the B button, and the note B with the A button. Say "the note A" or "the B button", never a bare letter.
- The first verse of "Amazing Grace" uses only these five pitches. A song with other pitches is outside this spec.
- The driver names octaves one higher than usual: its `D_5` sounds as D4.
- Down, Select and Start are not lanes. Start begins a play, and begins another from the results; during a play it does nothing.
- A note whose pitch is not in the table has no lane and nothing falls for it; the headless check then fails, reporting a note heard with nothing falling.
