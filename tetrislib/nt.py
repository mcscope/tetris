import sys
import msvcrt

__all__ = ["get_input", "prepare_terminal"]

ARROW_CODES = {"H": "up", "P": "down", "M": "right", "K": "left"}

# Waits for a single character of input and returns the string
# "left", "down", "right", "up", "exit", or None.
def get_input():
    key = msvcrt.getwch()
    if key == "\xe0":
        character = msvcrt.getwch()
        return ARROW_CODES.get(character)
    elif key == "\x03":
        return "exit"
    return None

def prepare_terminal():
    pass
