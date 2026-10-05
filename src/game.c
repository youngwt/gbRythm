// The play screen: notes fall down five lanes and land on a marker as they
// sound. Each lane belongs to one button, and a note's pitch decides its
// lane.
//
// The falling notes are not a second copy of the tune. The game reads the
// song's own rows, the same data the music driver plays, but starts reading
// LEAD_FRAMES before the music starts. A note that begins on a row is
// dropped from the top when that row is read, falls for LEAD_FRAMES, and so
// lands just as the driver reaches the same row and plays it.

#include <gb/gb.h>
#include <gbdk/console.h>
#include <stdint.h>
#include <stdio.h>

#include "falling.h"
#include "game.h"
#include "lane_1_left.h"
#include "lane_2_up.h"
#include "lane_3_right.h"
#include "lane_4_b.h"
#include "lane_5_a.h"
#include "song.h"

// The five lanes, left to right: the Left, Up and Right buttons, then B,
// then A. Each has a marker at the bottom showing its button.
#define LANES 5

// Where the markers sit, in pixels from the top left of the screen. All are
// multiples of 8 because a marker is a background tile.
#define TARGET_Y 120
static const uint8_t lane_x[LANES] = {32, 56, 80, 104, 128};

// Which lane each of the twelve pitches in an octave falls in, counting
// from C. The tune uses five: D, E, G, A and B, lowest on the left. The
// names collide: the note A is on the B button, and the note B on the A
// button.
#define NO_LANE 0xFF
#define PITCHES_PER_OCTAVE 12
static const uint8_t lane_of_pitch[PITCHES_PER_OCTAVE] = {
    NO_LANE,  // C
    NO_LANE,  // C sharp
    0,        // D: the Left button
    NO_LANE,  // D sharp
    1,        // E: the Up button
    NO_LANE,  // F
    NO_LANE,  // F sharp
    2,        // G: the Right button
    NO_LANE,  // G sharp
    3,        // A: the B button
    NO_LANE,  // A sharp
    4,        // B: the A button
};

// How a note falls: FALL_SPEED pixels every frame for LEAD_FRAMES frames,
// which must bring it from the top of the screen exactly onto the marker.
#define FALL_SPEED 2
#define LEAD_FRAMES 60
#define START_Y (TARGET_Y - FALL_SPEED * LEAD_FRAMES)

// When the music starts, counted in frames from when the reader starts.
// The reader's head start is what gives a note time to fall. The headless
// check measures the result: with this value every note lands in the frame
// its sound starts.
#define MUSIC_START_FRAME LEAD_FRAMES

// The most notes that can be falling at once. The quickest notes in the
// song are 20 frames apart and a note falls for 60, so 4; 8 leaves room.
#define MAX_FALLING 8

// How the song's rows are laid out; see song.c and hUGEDriver.h.
#define ROW_BYTES 3
#define ROWS_PER_PATTERN 64
#define NO_NOTE 90
#define EFFECT_PATTERN_BREAK 0x0D

// Sprites are placed by their bottom-right corner, offset by these.
#define SPRITE_X_OFFSET 8
#define SPRITE_Y_OFFSET 16

// One slot per sprite: whether a note is falling in it, which lane's
// column it is in, and how far down.
uint8_t falling_active[MAX_FALLING];
uint8_t falling_x[MAX_FALLING];
uint8_t falling_y[MAX_FALLING];

// The reader's place in the song: which step of the order, which row of
// that step's pattern, and a pointer to the row's three bytes.
uint8_t read_order;
uint8_t read_row;
const unsigned char *read_ptr;
uint8_t read_wait;        // frames until the next row is read
uint8_t read_instrument;  // the instrument the channel last used

uint8_t music_wait;       // frames until the music starts
uint8_t music_started;

uint8_t i;
uint8_t row_note;
uint8_t row_instrument;
uint8_t row_effect;
uint8_t row_pitch;
uint8_t row_lane;

// Point the reader at the first row of the current step's pattern.
static void read_from_pattern_start(void)
{
    read_row = 0;
    read_ptr = proof_song.order1[read_order];
}

// Move the reader to the next step of the song, wrapping to the first.
static void read_next_order(void)
{
    read_order++;
    // The song stores the count of steps doubled.
    if (read_order == (*proof_song.order_cnt >> 1)) {
        read_order = 0;
    }
    read_from_pattern_start();
}

// Start a note falling from the top of lane row_lane, in the first free
// slot.
static void drop_note(void)
{
    for (i = 0; i != MAX_FALLING; i++) {
        if (!falling_active[i]) {
            falling_active[i] = 1;
            falling_x[i] = lane_x[row_lane];
            falling_y[i] = START_Y;
            move_sprite(i, falling_x[i] + SPRITE_X_OFFSET, START_Y + SPRITE_Y_OFFSET);
            return;
        }
    }
}

// Read one row of the melody and drop a note if the row starts one.
static void read_one_row(void)
{
    // A row is DN(note, instrument, effect) packed into three bytes.
    row_note = read_ptr[0] & 0x7F;
    row_instrument = ((read_ptr[0] & 0x80) >> 3) | (read_ptr[1] >> 4);
    row_effect = read_ptr[1] & 0x0F;

    if (row_note != NO_NOTE) {
        // Instrument 0 means "the same as before".
        if (row_instrument != 0) {
            read_instrument = row_instrument;
        }
        // An instrument with no starting volume is how the song writes a
        // rest, so it is not a note to play.
        if (read_instrument != 0 &&
            (proof_song.duty_instruments[read_instrument - 1].envelope >> 4) != 0) {
            // Notes are numbered up from C in the lowest octave, twelve to
            // an octave, so taking away whole octaves leaves the pitch. The
            // same pitch lands in the same lane in every octave.
            row_pitch = row_note;
            while (row_pitch >= PITCHES_PER_OCTAVE) {
                row_pitch -= PITCHES_PER_OCTAVE;
            }
            row_lane = lane_of_pitch[row_pitch];
            // A pitch outside the five has no lane and nothing falls.
            if (row_lane != NO_LANE) {
                drop_note();
            }
        }
    }

    if (row_effect == EFFECT_PATTERN_BREAK) {
        // The pattern ends here and the song goes on to the next step.
        read_next_order();
    } else {
        read_row++;
        read_ptr += ROW_BYTES;
        if (read_row == ROWS_PER_PATTERN) {
            read_next_order();
        }
    }
}

void game_init(void)
{
    // The title, on the bottom line where no note falls.
    gotoxy(0, 17);
    printf("GBRYTHM");

    // The markers are background tiles, one image per lane. The falling
    // note is a sprite, a small picture that moves freely over the
    // background. Sprites can use the same tiles as background images, so
    // all of these come from PNGs in assets/.
    set_bkg_data(lane_1_left_TILE_ORIGIN, lane_1_left_TILE_COUNT, lane_1_left_tiles);
    set_bkg_tiles(lane_x[0] >> 3, TARGET_Y >> 3, 1, 1, lane_1_left_map);
    set_bkg_data(lane_2_up_TILE_ORIGIN, lane_2_up_TILE_COUNT, lane_2_up_tiles);
    set_bkg_tiles(lane_x[1] >> 3, TARGET_Y >> 3, 1, 1, lane_2_up_map);
    set_bkg_data(lane_3_right_TILE_ORIGIN, lane_3_right_TILE_COUNT, lane_3_right_tiles);
    set_bkg_tiles(lane_x[2] >> 3, TARGET_Y >> 3, 1, 1, lane_3_right_map);
    set_bkg_data(lane_4_b_TILE_ORIGIN, lane_4_b_TILE_COUNT, lane_4_b_tiles);
    set_bkg_tiles(lane_x[3] >> 3, TARGET_Y >> 3, 1, 1, lane_4_b_map);
    set_bkg_data(lane_5_a_TILE_ORIGIN, lane_5_a_TILE_COUNT, lane_5_a_tiles);
    set_bkg_tiles(lane_x[4] >> 3, TARGET_Y >> 3, 1, 1, lane_5_a_map);
    set_bkg_data(falling_TILE_ORIGIN, falling_TILE_COUNT, falling_tiles);

    // Sprite colours: the lightest is always see-through, then light grey,
    // dark grey and black, the same as the background's.
    OBP0_REG = DMG_PALETTE(DMG_WHITE, DMG_LITE_GRAY, DMG_DARK_GRAY, DMG_BLACK);
    for (i = 0; i != MAX_FALLING; i++) {
        falling_active[i] = 0;
        set_sprite_tile(i, falling_map[0]);
        move_sprite(i, 0, 0);  // off screen
    }
    SHOW_SPRITES;

    read_order = 0;
    read_from_pattern_start();
    read_wait = 0;
    read_instrument = 0;
    music_wait = MUSIC_START_FRAME;
    music_started = 0;
}

void game_tick(void)
{
    // Move every falling note down. A note is shown on the marker for one
    // frame, the frame its sound starts, and then removed.
    for (i = 0; i != MAX_FALLING; i++) {
        if (falling_active[i]) {
            if (falling_y[i] == TARGET_Y) {
                falling_active[i] = 0;
                move_sprite(i, 0, 0);
            } else {
                falling_y[i] += FALL_SPEED;
                move_sprite(i, falling_x[i] + SPRITE_X_OFFSET, falling_y[i] + SPRITE_Y_OFFSET);
            }
        }
    }

    // Start the music once the reader has its head start. The three
    // registers switch the sound hardware on, send every channel to both
    // speakers, and set the volume to full. The driver is then given the
    // song and asked to run once per frame; __critical holds interrupts off
    // while that is set up.
    if (!music_started) {
        if (music_wait == 0) {
            music_started = 1;
            NR52_REG = 0x80;
            NR51_REG = 0xFF;
            NR50_REG = 0x77;
            __critical {
                hUGE_init(&proof_song);
                add_VBL(hUGE_dosound);
            }
        } else {
            music_wait--;
        }
    }

    // Read the next row every `tempo` frames, the same pace the driver
    // plays them at.
    if (read_wait == 0) {
        read_one_row();
        read_wait = proof_song.tempo;
    }
    read_wait--;
}
