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
//   effect      0x000 means none; the first digit picks an effect and the
//               other two are its setting
// A note keeps sounding until another note replaces it.

#include <stddef.h>

#include "song.h"

// Channel 1: the first verse of "Amazing Grace", in G major:
//
//   A - ma - zing  grace,  how  sweet  the  sound,
//   D   G    B G   B       A    G      E    D
//
//   that  saved  a    wretch  like  me.
//   D     G      B G  B       A     D (the D above)
//
//   I  once  was  lost,  but  now  am   found,
//   B  D B   D B  G      D    E G  G E  D        (D is the D above)
//
//   was  blind  but  now  I  see.
//   D    G      B G  B    A  G
//
// The tune has three beats to the bar. One beat, a quarter note, is four
// rows here, so a half note is eight rows, an eighth note is two, and a
// dotted quarter note is six. Where one word has two notes, both are shown.
//
// The driver names octaves one higher than usual: its D_5 is the D just
// above middle C, which most music calls D4.
//
// A pattern is always 64 rows, so the tune is split across three. A note
// that is still sounding when a pattern ends simply carries on into the
// next.
static const unsigned char melody_1[] = {
    // "A-", a quarter note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "-ma-", a half note
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "-zing", two eighth notes
    DN(B_5,1,0x000), DN(___,0,0x000),
    DN(G_5,1,0x000), DN(___,0,0x000),
    // "grace", a half note
    DN(B_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "how", a quarter note
    DN(A_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "sweet", a half note
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "the", a quarter note
    DN(E_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "sound", a half note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "that", a quarter note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "saved", a half note
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "a", two eighth notes
    DN(B_5,1,0x000), DN(___,0,0x000),
    DN(G_5,1,0x000), DN(___,0,0x000),
};

static const unsigned char melody_2[] = {
    // "wretch", a half note
    DN(B_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "like", a quarter note
    DN(A_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "me", held for five beats
    DN(D_6,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "I", a quarter note
    DN(B_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "once", a dotted quarter note and an eighth
    DN(D_6,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(B_5,1,0x000), DN(___,0,0x000),
    // "was", two eighth notes
    DN(D_6,1,0x000), DN(___,0,0x000),
    DN(B_5,1,0x000), DN(___,0,0x000),
    // "lost", a half note
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "but", a quarter note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "now", a dotted quarter note; its last two rows are at the top of the next pattern
    DN(E_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
};

static const unsigned char melody_3[] = {
    // "now" is still sounding
    DN(___,0,0x000), DN(___,0,0x000),
    // the eighth note that finishes "now"
    DN(G_5,1,0x000), DN(___,0,0x000),
    // "am", two eighth notes
    DN(G_5,1,0x000), DN(___,0,0x000),
    DN(E_5,1,0x000), DN(___,0,0x000),
    // "found", a half note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "was", a quarter note
    DN(D_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "blind", a half note
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "but", two eighth notes
    DN(B_5,1,0x000), DN(___,0,0x000),
    DN(G_5,1,0x000), DN(___,0,0x000),
    // "now", a half note
    DN(B_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "I", a quarter note
    DN(A_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    // "see", held for five beats, to the end of the song
    DN(G_5,1,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
    DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000), DN(___,0,0x000),
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
// song. This song has three steps. The driver wants the count doubled.
static const unsigned char order_cnt = 6;
static const unsigned char* const order1[] = {melody_1, melody_2, melody_3};
static const unsigned char* const order2[] = {silence, silence, silence};
static const unsigned char* const order3[] = {silence, silence, silence};
static const unsigned char* const order4[] = {silence, silence, silence};

// Instruments for channels 1 and 2, which make a plain beep called a square
// wave. The fields are: pitch sweep (8 is off), wave shape (128 is an even
// square), volume envelope (the high four bits are the starting volume, 0
// to 15; the low three are how slowly it fades, 0 for not at all), an
// optional sub-pattern (none), and a flag byte the driver needs set to 128
// to start the note.
static const hUGEDutyInstr_t duty_instruments[] = {
    {8, 128, 0xF7, NULL, 128},  // 1: starts at full volume and fades slowly
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

// Tempo is the number of frames each row lasts. At 10, a beat of four rows
// takes 40 frames, two thirds of a second: 90 beats a minute.
const hUGESong_t song_verse = {
    10, &order_cnt, order1, order2, order3, order4,
    duty_instruments, wave_instruments, noise_instruments, NULL, waves
};
