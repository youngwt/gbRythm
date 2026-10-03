#include <gb/gb.h>
#include <stdint.h>
#include <stdio.h>

uint8_t keys;
uint8_t a_was_pressed;

void main(void)
{
    a_was_pressed = 0;

    printf("GBRYTHM\nPRESS A");

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
