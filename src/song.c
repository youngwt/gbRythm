// A song for the hUGEDriver music driver, written by hand.
//
// The Game Boy has four sound channels. A song gives each channel a list of
// patterns to play in order, and a pattern is 64 rows. The driver steps
// through the rows of all four channels together, one row every few frames.
//
// Each row is DN(note, instrument, effect):
//   note        C_3 to B_8, or ___ to leave the channel as it is
//   instrument  which entry of the instrument table to use, counting from 1;
//               0 means no change
//   effect      0x000 means none
// A note keeps sounding until another note replaces it.

#include <stddef.h>

#include "song.h"

// Channel 1: seven notes up and down a chord, eight rows apart, then silence
// in the last eight rows before the pattern repeats.
static const unsigned char melody[] = {
    DN(C_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(E_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(C_6,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(E_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(C_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // Instrument 2 has no volume, so this "note" is how the melody stops.
    DN(C_5,2,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
};

// The other three channels play nothing: 64 empty rows.
static const unsigned char silence[] = {
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
};

// The order: which pattern each channel plays, one entry per step of the
// song. This song has one step. The driver wants the count doubled.
static const unsigned char order_cnt = 2;
static const unsigned char* const order1[] = {melody};
static const unsigned char* const order2[] = {silence};
static const unsigned char* const order3[] = {silence};
static const unsigned char* const order4[] = {silence};

// Instruments for channels 1 and 2, which make a plain beep called a square
// wave. The fields are: pitch sweep (8 is off), wave shape (128 is an even
// square), volume envelope (the high four bits are the starting volume, 0
// to 15), an optional sub-pattern (none), and a flag byte the driver needs
// set to 128 to start the note.
static const hUGEDutyInstr_t duty_instruments[] = {
    {8, 128, 0xF0, NULL, 128},  // 1: full volume, held
    {8, 128, 0x00, NULL, 128},  // 2: no volume, used as a rest
};

// Channels 3 and 4 are unused, but the driver expects each table to exist.
static const hUGEWaveInstr_t wave_instruments[] = {
    {0, 32, 0, NULL, 128},
};
static const hUGENoiseInstr_t noise_instruments[] = {
    {0x00, NULL, 0, 0, 0},
};
static const unsigned char waves[] = {
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
};

// Tempo is the number of frames each row lasts. At 7, the eight rows between
// notes take just under a second.
const hUGESong_t proof_song = {
    7, &order_cnt, order1, order2, order3, order4,
    duty_instruments, wave_instruments, noise_instruments, NULL, waves
};
