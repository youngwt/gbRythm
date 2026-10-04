#include <gb/gb.h>
#include <stdint.h>
#include <stdio.h>

#include "arrow.h"
#include "note.h"

// Where each image goes on the background, in tiles from the top left.
#define ARROW_X 8
#define ARROW_Y 6
#define NOTE_X 14
#define NOTE_Y 7

uint8_t keys;
uint8_t a_was_pressed;

void main(void)
{
    a_was_pressed = 0;

    printf("GBRYTHM\nPRESS A");

    // Show the image converted from assets/arrow.png: load its tiles into
    // video memory, then place them on the background. Sizes are in tiles,
    // so pixels >> 3.
    set_bkg_data(arrow_TILE_ORIGIN, arrow_TILE_COUNT, arrow_tiles);
    set_bkg_tiles(ARROW_X, ARROW_Y, arrow_WIDTH >> 3, arrow_HEIGHT >> 3, arrow_map);

    // A second image, from assets/note.png. The build gave its tiles the
    // numbers after the arrow's, so both can be on screen together.
    set_bkg_data(note_TILE_ORIGIN, note_TILE_COUNT, note_tiles);
    set_bkg_tiles(NOTE_X, NOTE_Y, note_WIDTH >> 3, note_HEIGHT >> 3, note_map);

    while (1) {
        // Read the buttons once per frame.
        keys = joypad();

        if ((keys & J_A) && !a_was_pressed) {
            a_was_pressed = 1;
            printf("\nA PRESSED");
        }

        // Idle until the next vertical blank instead of spinning the CPU.
        vsync();
    }
}
