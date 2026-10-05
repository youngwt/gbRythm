#include <gb/gb.h>
#include <stdint.h>

#include "game.h"

// The game's clock. frame_count goes up once every frame, on the vertical
// blank interrupt, whatever the main loop is doing. frames_done is how many
// of those frames the game has dealt with.
volatile uint8_t frame_count;
uint8_t frames_done;

void count_frame(void)
{
    frame_count++;
}

void main(void)
{
    game_init();

    frames_done = 0;
    __critical {
        frame_count = 0;
        add_VBL(count_frame);
    }

    while (1) {
        // Idle until the next vertical blank instead of spinning the CPU.
        vsync();

        // Normally this runs once. If the game ever took longer than a
        // frame, it runs again to catch up, so the falling notes stay in
        // step with the music, which never waits.
        while (frames_done != frame_count) {
            game_tick();
            frames_done++;
        }
    }
}
