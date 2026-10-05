#ifndef GAME_H
#define GAME_H

// Draw the play screen and get ready to read the song.
void game_init(void);

// Advance the game by one frame. Call once for every frame that has passed.
void game_tick(void);

#endif
