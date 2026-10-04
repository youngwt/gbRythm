#include <gb/gb.h>
#include <stdint.h>
#include <stdio.h>

#include "arrow.h"

// Where the arrow image goes on the background, in tiles from the top left.
#define ARROW_X 8
#define ARROW_Y 6

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
