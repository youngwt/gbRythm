#ifndef GAME_H
#define GAME_H

// Draw the screen, wait for Start, and start the game's clock.
void game_init(void);

// Deal with every frame that has passed since the last call.
void game_catch_up(void);

#endif
