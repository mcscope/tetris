#!/usr/bin/env python

import time
from tetrislib import *
from queue import Queue
import threading
import sys
import os

RING_BELL = False
prepare_terminal()
playing = True
game_clock = 0.8


# class InputSpooler(threading.Thread):
def spool_input(queue):
    while playing:
        key = get_input()
        queue.put(key)
        time.sleep(0.001)


# class InputSpooler(threading.Thread):
def blockdown(queue):
    while playing:
        if RING_BELL:
            sys.stdout.write('\a')
            sys.stdout.flush()
        queue.put("down")
        time.sleep(game_clock)


def main():
    os.system('clear')

    global playing
    board = Board()
    try:
        game_loop(board)
    except:
        playing = False
        raise
# This code waits for input until the user hits a keystroke.
# get_input() returns one of "left", "up", "right", "down", "exit", or None
# (for all other keys).


def game_loop(board):
    global game_clock
    inputQ = Queue()
    key = ""
    input_thread = threading.Thread(target=spool_input, args=(inputQ,))
    input_thread.start()
    bdown_thread = threading.Thread(target=blockdown, args=(inputQ,))
    bdown_thread.start()

    while True:
        board.draw()
        # print(key)
        if inputQ.qsize() != 0:
            key = inputQ.get(block=False)
            if key:
                if key == "exit":
                    return
                try:
                    old_score = board.score
                    board.command(key)
                    if old_score != board.score:
                        # Difficulty increases!
                        # asymptotic get faster
                        game_clock = game_clock * 0.95
                except GameLoss:
                    print(f"You Lose! Score {board.score}")

                    return

        time.sleep(0.01)


if __name__ == '__main__':
    main()
    playing = False
