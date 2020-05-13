import os
import sys
import atexit
from subprocess import Popen, PIPE

__all__ = ["get_input", "prepare_terminal"]

ARROW_CODES = {"A": "up", "B": "down", "C": "right", "D": "left"}

# Waits for a single character of input and returns the string
# "left", "down", "right", "up", "exit", or None.


def get_input():
    key = sys.stdin.read(1)
    # The arrow keys are read from stdin as an escaped sequence of 3 bytes.
    if key == "\x1b":
        # The next two bytes will indicate which arrow key was pressed.
        character = sys.stdin.read(2)
        return ARROW_CODES.get(character[1])
    elif key == "\x03":
        return "exit"
    return key


def prepare_terminal():
    original_terminal_state = set_terminal_mode()
    atexit.register(restore_terminal, original_terminal_state)


def set_terminal_mode():
    original_terminal_state = Popen(b"stty -g", stdout=PIPE, shell=True).communicate()[0]
    os.system(b"stty -icanon -echo -isig")
    return original_terminal_state


def restore_terminal(state):
    os.system(b"stty " + state)
