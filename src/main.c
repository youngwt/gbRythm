#include <gb/gb.h>

#include "game.h"

void main(void)
{
    game_init();

    while (1) {
        // Idle until the next vertical blank instead of spinning the CPU,
        // then let the game deal with the frame that has just passed.
        vsync();
        game_catch_up();
    }
}
