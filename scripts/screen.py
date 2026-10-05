"""Reading the Game Boy's screen: finding images on it and reading counts.

Everything here works on a screen, or a picture, reduced to the Game Boy's
four shades: a grid of numbers from 0 (white) to 3 (black).
"""

from pathlib import Path

import numpy as np
from PIL import Image


def shades(pixels: np.ndarray) -> np.ndarray:
    """Reduce a picture to the Game Boy's four shades, 0 (white) to 3 (black).

    The PNG and the emulator use slightly different greys for the same shade,
    so both are sorted into four brightness bands before they are compared.
    Takes a grid of brightness values, 0 to 255.
    """
    return (3 - (pixels >> 6)).astype(np.uint8)


def load_shades(path: Path) -> np.ndarray:
    # "L" is a picture as brightness alone.
    return shades(np.asarray(Image.open(path).convert("L")))


def find_on(screen: np.ndarray, image: np.ndarray) -> tuple[int, int] | None:
    """Where the image is, pixel for pixel, on the screen: (top, left)."""
    height, width = image.shape
    # Only places where the image's darkest pixel matches are worth a full
    # comparison; on a mostly white screen that rules out nearly all of them.
    dark_row, dark_column = np.unravel_index(image.argmax(), image.shape)
    rows, columns = screen.shape[0] - height + 1, screen.shape[1] - width + 1
    candidates = screen[dark_row:dark_row + rows, dark_column:dark_column + columns] == image.max()
    for top, left in np.argwhere(candidates):
        if np.array_equal(screen[top:top + height, left:left + width], image):
            return int(top), int(left)
    return None


def falling_notes_in(strip: np.ndarray, note: np.ndarray) -> list[int]:
    """How far down each falling note is, in the strip of screen under them.

    A falling note is a sprite, and the white parts of a sprite are
    see-through, so only its other pixels are compared. That finds it over
    any background, including when it sits on the marker.
    """
    solid = note > 0
    # Every note-sized window down the strip, compared in one go.
    windows = np.lib.stride_tricks.sliding_window_view(strip, note.shape)[:, 0]
    matches = (windows[:, solid] == note[solid]).all(axis=1)
    return [int(top) for top in np.flatnonzero(matches)]


def read_count(screen: np.ndarray, place: tuple[int, int], word_width: int, digits: np.ndarray) -> int | None:
    """Read the two-digit count drawn straight after a word on the screen."""
    top, left = place
    number = 0
    for position in range(2):
        x = left + word_width + 8 * position
        cell = screen[top:top + 8, x:x + 8]
        for digit in range(10):
            if np.array_equal(cell, digits[:, 8 * digit:8 * digit + 8]):
                number = number * 10 + digit
                break
        else:
            return None
    return number


def shows(screen: np.ndarray, image: np.ndarray, place: tuple[int, int]) -> bool:
    """Whether the image is on the screen at the place given."""
    top, left = place
    return np.array_equal(screen[top:top + image.shape[0], left:left + image.shape[1]], image)
