#include <gb/gb.h>
#include <stdio.h>

void main(void)
{
    printf("GBRYTHM\nBUILD OK");

    // Idle until the next vertical blank instead of spinning the CPU.
    while (1) {
        vsync();
    }
}
