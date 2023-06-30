"""
A library for useful functions that it doesn't make sense to include in the
main emulator directory.
"""

import numpy as np
import sys

def high_byte(value: np.uint16) -> np.uint16:
    """
    Given a 16 bit value 0xABCD, returns 0xAB.
    """
    return np.uint16((value & 0xFF00) >> 8)


def low_byte(value: np.uint16) -> np.uint16:
    """
    Given a 16 bit value 0xABCD, returns 0xCD.
    """
    return np.uint16(value & 0xFF)


def concat(hb: np.uint8, lb: np.uint8) -> np.uint16:
    """
    Concatenates a high byte (hb) and a low byte (lb) into a word.
    """
    return np.uint16((hb << 8) | lb)


def get_nibble(value: np.uint16, n: int) -> np.uint16:
    """
    Returns the nth nibble of a number.
    example: get_nibble(0xABCD, 0) = 0xD
    """
    return np.uint16((value & (0xF << (4 * n))) >> (4 * n))


def to_hex(string : str) -> int:
    return int(string, 16)


def is_hex(string: str) -> bool:
    """
    Checks if a string is hexadecimal, returns true if so and false otherwise.
    """
    try:
        int(string, 16)
        return True
    except ValueError:
        return False


def to_words(value : int) -> list:
    """
    Splits an integer into its composite words and returns them in big endian manner.
    """
    rv = []
    while value > 0:
        rv.append(np.uint16(value & np.uint16(0xFFFF)))
        value >>= np.uint16(16)
    return list(reversed(rv))


# ANSI character escape sequence for making the terminal output emulator output
# in green.
GREEN = "\033[92m"
# ANSI escape sequence to tell console to stop printing in colour.
ENDC = "\033[0m"


def console_input(prompt_text: str) -> str:  # pragma: no cover
    """
    A wrapper function for python's input function to facilitate unit testing.
    """
    return input(GREEN + prompt_text + ENDC)


def console_output(text: str) -> None:  # pragma: no cover
    """
    A wrapper function for console printing to facilitate unit testing.
    """
    print(GREEN + text + ENDC)


def program_exit():  # pragma: no cover
    """
    A wrapper function for sys.exit.
    """
    sys.exit(0)
