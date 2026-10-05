// The play screen: notes fall down five lanes and land on a marker as they
// sound. Each lane belongs to one button, and a note's pitch decides its
// lane. Pressing a lane's button as its note lands is judged perfect or
// good by how close the press was; a note nobody presses in time is a miss.
//
// The game waits for Start, plays the song once, and then shows the results
// until Start is pressed again.
//
// The file reads top to bottom: the settings and the game's state first,
// then drawing the counts, the falling notes, reading the song, judging,
// the clock and the music, starting and ending a play, and last what
// happens each frame.
//
// The falling notes are not a second copy of the tune. The game reads the
// song's own rows, the same data the music driver plays, but starts reading
// LEAD_FRAMES before the music starts. A note that begins on a row is
// dropped from the top when that row is read, falls for LEAD_FRAMES, and so
// lands just as the driver reaches the same row and plays it.

#include <gb/gb.h>
#include <stdint.h>

#include "digits.h"
#include "falling.h"
#include "game.h"
#include "lane_1_left.h"
#include "lane_2_up.h"
#include "lane_3_right.h"
#include "lane_4_b.h"
#include "lane_5_a.h"
#include "song.h"
#include "word_good.h"
#include "word_miss.h"
#include "word_perfect.h"
#include "word_results.h"
#include "word_start.h"

// The five lanes, left to right: the Left, Up and Right buttons, then B,
// then A. Each has a marker at the bottom showing its button.
#define LANES 5

// Where the markers sit, in pixels from the top left of the screen. All are
// multiples of 8 because a marker is a background tile.
#define TARGET_Y 104
static const uint8_t lane_x[LANES] = {32, 56, 80, 104, 128};

// The button for each lane, in the same order.
static const uint8_t lane_button[LANES] = {J_LEFT, J_UP, J_RIGHT, J_B, J_A};

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

// Sprites are placed by their bottom-right corner, so a sprite at the top
// left of the screen has x 8 and y 16. A falling note's height is kept in
// these sprite numbers: 0 is just above the top edge, out of sight.
#define SPRITE_X_OFFSET 8
#define SPRITE_Y_OFFSET 16
#define LANDED_Y (TARGET_Y + SPRITE_Y_OFFSET)

// How a note falls: FALL_SPEED pixels every frame for LEAD_FRAMES frames,
// which must bring it from just above the screen exactly onto its marker.
#define FALL_SPEED 2
#define LEAD_FRAMES 60
#define START_Y (LANDED_Y - FALL_SPEED * LEAD_FRAMES)

// How close a press must be to the frame the note lands, either side.
// Within PERFECT_FRAMES is a perfect; within GOOD_FRAMES is a good; any
// further and the press is ignored. A note that gets GOOD_FRAMES past its
// marker without a press is a miss. Notes move at a steady speed, so the
// game measures these as distances from the marker.
#define PERFECT_FRAMES 3
#define GOOD_FRAMES 7
#define PERFECT_PIXELS (PERFECT_FRAMES * FALL_SPEED)
#define GOOD_PIXELS (GOOD_FRAMES * FALL_SPEED)

// What the player sees is one frame behind the game. A sprite the game
// moves is only shown from the frame after next, because sprite positions
// are copied to the screen hardware once a frame. So when a note looks as
// if it is on its marker, the game already has it one step further down,
// and presses are judged against that height. Measured by the headless
// check, which presses relative to what is on the screen.
#define JUDGE_Y (LANDED_Y + FALL_SPEED)

// When the music starts, counted in frames from the frame Start was
// pressed. LEAD_FRAMES is the reader's head start, which gives a note time
// to fall. The extra frames are measured, not reasoned: a note is seen on
// its marker a few frames after the game puts it there, and the driver's
// first note sounds a frame after the driver is first run. With this value
// the headless check finds every note landing in the frame its sound starts.
#define MUSIC_START_FRAME (LEAD_FRAMES + 3)


// The most notes that can be falling at once. The quickest notes in the
// song are 20 frames apart and a note falls for 60, so 4; 8 leaves room.
#define MAX_FALLING 8

// How the song's rows are laid out; see song.c and hUGEDriver.h.
#define ROW_BYTES 3
#define ROWS_PER_PATTERN 64
#define NO_NOTE 90
#define EFFECT_PATTERN_BREAK 0x0D

// The three judgements, in the order their counts are kept.
#define PERFECT 0
#define GOOD 1
#define MISS 2
#define JUDGEMENTS 3

// Where things are drawn below the markers, in tiles. The latest judgement
// has a line to itself. Each count is its word followed by two digits.
#define WORD_TILES 6
#define LATEST_X 7
#define LATEST_Y 15
static const uint8_t count_x[JUDGEMENTS] = {0, 10, 0};
static const uint8_t count_y[JUDGEMENTS] = {16, 16, 17};
static const unsigned char *const word_map[JUDGEMENTS] = {
    word_perfect_map, word_good_map, word_miss_map
};

// The "RESULTS" heading and the "PRESS START" prompt, in the empty space
// above the markers, in tiles.
#define HEADING_TILES 6
#define HEADING_X 7
#define HEADING_Y 5
#define PROMPT_TILES 9
#define PROMPT_X 5
#define PROMPT_Y 7

// What the game is doing: waiting for the first Start, playing the song, or
// showing the results after it.
#define WAITING 0
#define PLAYING 1
#define RESULTS 2
uint8_t state;

// One slot per sprite: whether a note is falling in it, which lane it is
// in, and how far down.
uint8_t falling_active[MAX_FALLING];
uint8_t falling_lane[MAX_FALLING];
uint8_t falling_y[MAX_FALLING];

// Each count is kept as two digits, tens and ones, because dividing by ten
// to show a number is slow on this hardware.
uint8_t count_tens[JUDGEMENTS];
uint8_t count_ones[JUDGEMENTS];

// The buttons held this frame and last, and those that went down just now.
uint8_t keys;
uint8_t keys_before;
uint8_t keys_pressed;

uint8_t lane;
uint8_t nearest;
uint8_t nearest_distance;
uint8_t distance;
uint8_t judged;

// The reader's place in the song: which step of the order, which row of
// that step's pattern, and a pointer to the row's three bytes.
uint8_t read_order;
uint8_t read_row;
const unsigned char *read_ptr;
uint8_t read_wait;        // frames until the next row is read
uint8_t read_instrument;  // the instrument the channel last used

// The game's clock. frame_count goes up once every frame, on the vertical
// blank signal, whatever the main loop is doing. frames_done is how many of
// those frames the game has dealt with.
volatile uint8_t frame_count;
uint8_t frames_done;

// The music is run from the same signal, in game_frame, so that it keeps
// exact time however long the rest of the game takes. It is off, waiting for
// its starting frame, or on.
#define MUSIC_OFF 0
#define MUSIC_WAITING 1
#define MUSIC_ON 2
volatile uint8_t music_state;
volatile uint8_t music_start_frame;   // the value of frame_count to start on
volatile uint16_t music_runs_done;    // times the driver has run this play
volatile uint16_t music_runs_total;   // times it should run, once known
volatile uint8_t music_total_known;

uint8_t song_read;        // the reader has reached the end of the song
uint16_t song_frames;     // how long the rows read so far last, in frames
uint8_t notes_in_play;

uint8_t i;
uint8_t row_note;
uint8_t row_instrument;
uint8_t row_effect;
uint8_t row_pitch;
uint8_t row_lane;

// ---- Drawing the counts ----

// Show a count's two digits after its word.
static void draw_count(void)
{
    set_bkg_tile_xy(count_x[judged] + WORD_TILES, count_y[judged], digits_map[count_tens[judged]]);
    set_bkg_tile_xy(count_x[judged] + WORD_TILES + 1, count_y[judged], digits_map[count_ones[judged]]);
}

// Set the three counts back to zero and clear the latest judgement. Tile 0
// is blank.
static void reset_counts(void)
{
    for (judged = 0; judged != JUDGEMENTS; judged++) {
        count_tens[judged] = 0;
        count_ones[judged] = 0;
        draw_count();
    }
    fill_bkg_rect(LATEST_X, LATEST_Y, WORD_TILES, 1, 0);
}

// ---- Falling notes ----

// Start a note falling from the top of lane row_lane, in the first free
// slot.
static void drop_note(void)
{
    for (i = 0; i != MAX_FALLING; i++) {
        if (!falling_active[i]) {
            falling_active[i] = 1;
            falling_lane[i] = row_lane;
            falling_y[i] = START_Y;
            move_sprite(i, lane_x[row_lane] + SPRITE_X_OFFSET, START_Y);
            return;
        }
    }
}

// Take a note out of play and hide its sprite.
static void remove_note(void)
{
    falling_active[i] = 0;
    move_sprite(i, 0, 0);
}

// ---- Reading the song ----

// Point the reader at the first row of the current step's pattern.
static void read_from_pattern_start(void)
{
    read_row = 0;
    read_ptr = song_verse.order1[read_order];
}

// Move the reader to the next step of the song, wrapping to the first.
static void read_next_order(void)
{
    read_order++;
    // The song stores the count of steps doubled.
    if (read_order == (*song_verse.order_cnt >> 1)) {
        // That was the last step: the reader has reached the end of the
        // song, a second ahead of the music. It now knows how many frames
        // the song lasts: the driver must run exactly that many times, and
        // once more would start the tune again. The total is
        // written before the flag that says it is there, because the music
        // runs on an interrupt and could look at any moment.
        read_order = 0;
        song_read = 1;
        music_runs_total = song_frames;
        music_total_known = 1;
    }
    read_from_pattern_start();
}

// Read one row of the melody and drop a note if the row starts one.
static void read_one_row(void)
{
    // A row is DN(note, instrument, effect) packed into three bytes.
    song_frames += song_verse.tempo;
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
            (song_verse.duty_instruments[read_instrument - 1].envelope >> 4) != 0) {
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

// ---- Judging ----

// Record the judgement in `judged`: add one to its count and show its word.
static void record_judgement(void)
{
    count_ones[judged]++;
    if (count_ones[judged] == 10) {
        count_ones[judged] = 0;
        // The count stops at 99; the song has far fewer notes.
        if (count_tens[judged] != 9) {
            count_tens[judged]++;
        } else {
            count_ones[judged] = 9;
        }
    }
    draw_count();
    set_bkg_tiles(LATEST_X, LATEST_Y, WORD_TILES, 1, word_map[judged]);
}

// Judge a new press of lane `lane`'s button against the note in that lane
// nearest its marker. With no note within the good window, the press is
// ignored.
static void judge_press(void)
{
    nearest_distance = GOOD_PIXELS + 1;
    for (i = 0; i != MAX_FALLING; i++) {
        if (falling_active[i] && falling_lane[i] == lane) {
            if (falling_y[i] > JUDGE_Y) {
                distance = falling_y[i] - JUDGE_Y;
            } else {
                distance = JUDGE_Y - falling_y[i];
            }
            if (distance < nearest_distance) {
                nearest_distance = distance;
                nearest = i;
            }
        }
    }
    if (nearest_distance <= GOOD_PIXELS) {
        i = nearest;
        remove_note();
        judged = (nearest_distance <= PERFECT_PIXELS) ? PERFECT : GOOD;
        record_judgement();
    }
}

// ---- The clock and the music ----

// Run on every vertical blank, by interrupt. Counts the frame and runs the
// music. Keeping the music here, not in game_tick, means it starts and
// stops on exact frames even if the game is ever slow.
static void game_frame(void)
{
    frame_count++;

    if (music_state == MUSIC_WAITING && frame_count == music_start_frame) {
        music_state = MUSIC_ON;
    }
    if (music_state == MUSIC_ON) {
        if (music_total_known && music_runs_done == music_runs_total) {
            // The song is over. Left running, the driver would start the
            // tune again, so it is no longer called and the sound hardware
            // is switched off.
            NR52_REG = 0x00;
            music_state = MUSIC_OFF;
        } else {
            // The driver plays the next step of the song.
            hUGE_dosound();
            music_runs_done++;
        }
    }
}

// ---- Starting and ending a play ----

// Begin a play: clear the score and the messages, start reading the song
// from the top, and book the music to start MUSIC_START_FRAME frames from
// now.
static void start_play(void)
{
    reset_counts();
    fill_bkg_rect(HEADING_X, HEADING_Y, HEADING_TILES, 1, 0);
    fill_bkg_rect(PROMPT_X, PROMPT_Y, PROMPT_TILES, 1, 0);

    read_order = 0;
    read_from_pattern_start();
    read_wait = 0;
    read_instrument = 0;
    song_read = 0;
    song_frames = 0;

    // The three registers switch the sound hardware on, send every channel
    // to both speakers, and set the volume to full. The driver is given the
    // song now, but nothing calls it until its starting frame.
    NR52_REG = 0x80;
    NR51_REG = 0xFF;
    NR50_REG = 0x77;
    hUGE_init(&song_verse);
    music_runs_done = 0;
    music_total_known = 0;
    music_start_frame = frames_done + MUSIC_START_FRAME;
    music_state = MUSIC_WAITING;
    state = PLAYING;
}

// The song is over: show the heading and the prompt. The three counts stay
// where they are; they are the results.
static void show_results(void)
{
    set_bkg_tiles(HEADING_X, HEADING_Y, HEADING_TILES, 1, word_results_map);
    set_bkg_tiles(PROMPT_X, PROMPT_Y, PROMPT_TILES, 1, word_start_map);
    state = RESULTS;
}

void game_init(void)
{
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

    // The words and digits are images too, so that the headless check can
    // find and read them on the screen as it finds the markers. Each count
    // starts as its word and 00.
    set_bkg_data(word_perfect_TILE_ORIGIN, word_perfect_TILE_COUNT, word_perfect_tiles);
    set_bkg_data(word_good_TILE_ORIGIN, word_good_TILE_COUNT, word_good_tiles);
    set_bkg_data(word_miss_TILE_ORIGIN, word_miss_TILE_COUNT, word_miss_tiles);
    set_bkg_data(digits_TILE_ORIGIN, digits_TILE_COUNT, digits_tiles);
    set_bkg_data(word_results_TILE_ORIGIN, word_results_TILE_COUNT, word_results_tiles);
    set_bkg_data(word_start_TILE_ORIGIN, word_start_TILE_COUNT, word_start_tiles);
    for (judged = 0; judged != JUDGEMENTS; judged++) {
        set_bkg_tiles(count_x[judged], count_y[judged], WORD_TILES, 1, word_map[judged]);
    }
    reset_counts();
    keys_before = 0;

    // Sprite colours: the lightest is always see-through, then light grey,
    // dark grey and black, the same as the background's.
    OBP0_REG = DMG_PALETTE(DMG_WHITE, DMG_LITE_GRAY, DMG_DARK_GRAY, DMG_BLACK);
    for (i = 0; i != MAX_FALLING; i++) {
        falling_active[i] = 0;
        set_sprite_tile(i, falling_map[0]);
        move_sprite(i, 0, 0);  // off screen
    }
    // Nothing is drawn until each layer is switched on. The built-in text
    // routines used to switch the background on as a side effect; the game
    // no longer uses them, so it does it here.
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    // Nothing falls and nothing plays until Start is pressed.
    set_bkg_tiles(PROMPT_X, PROMPT_Y, PROMPT_TILES, 1, word_start_map);
    music_state = MUSIC_OFF;
    state = WAITING;

    // Start the clock. From here game_frame runs on every vertical blank.
    frames_done = 0;
    __critical {
        frame_count = 0;
        add_VBL(game_frame);
    }
}

// ---- Each frame ----

static void game_tick(void)
{
    // Read the buttons once per frame. A press counts on the frame the
    // button goes down: held now and not held the frame before. Presses
    // are judged before the notes move, against where the notes were drawn
    // in the frame the player was looking at.
    keys = joypad();
    keys_pressed = keys & ~keys_before;
    keys_before = keys;

    // Waiting, or showing the results: only Start does anything.
    if (state != PLAYING) {
        if (keys_pressed & J_START) {
            start_play();
        }
        return;
    }

    for (lane = 0; lane != LANES; lane++) {
        if (keys_pressed & lane_button[lane]) {
            judge_press();
        }
    }

    // Move every falling note down. A note carries on past its marker
    // while a late press could still count; after that it is a miss.
    notes_in_play = 0;
    for (i = 0; i != MAX_FALLING; i++) {
        if (falling_active[i]) {
            notes_in_play++;
            falling_y[i] += FALL_SPEED;
            if (falling_y[i] > JUDGE_Y + GOOD_PIXELS) {
                remove_note();
                judged = MISS;
                record_judgement();
            } else {
                move_sprite(i, lane_x[falling_lane[i]] + SPRITE_X_OFFSET, falling_y[i]);
            }
        }
    }

    if (!song_read) {
        // Read the next row every `tempo` frames, the same pace the driver
        // plays them at.
        if (read_wait == 0) {
            read_one_row();
            read_wait = song_verse.tempo;
        }
        read_wait--;
    } else if (music_state == MUSIC_OFF && notes_in_play == 0) {
        // The reader has finished, the music has stopped, and the last
        // note has been judged.
        show_results();
    }
}

// Deal with every frame that has passed since the last call. Normally that
// is one. If the game ever took longer than a frame, this runs it again to
// catch up, so the falling notes stay in step with the music.
void game_catch_up(void)
{
    while (frames_done != frame_count) {
        game_tick();
        frames_done++;
    }
}
