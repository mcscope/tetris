# Set up the board.
# The board is represented as an array of arrays, with 10 rows and 10 columns.
from copy import deepcopy
import random
import time

BIG_BOARD = True
SMALL_BOARD = False


class GameLoss(Exception):
    pass


class Piece:
    _shapes = {
        "o": [
            (0, 0),
            (0, 1),
            (1, 0),
            (1, 1),
        ],
        "t": [
            (-1, 0),
            (0, 0),
            (+1, 0),
            (0, 1),
        ],
        "i": [
            (0, -1),
            (0, 0),
            (0, 1),
            (0, 2),
        ],
        "s": [
            (-1, +1),
            (0, 1),
            (0, 0),
            (+1, 0),
        ],
        "z": [
            (-1, 0),
            (0, 0),
            (0, 1),
            (1, 1),
        ],
        "j": [
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ],
        "l": [
            (-1, 1),
            (0, 1),
            (1, 0),
            (1, 1),
        ],
    }

    def __init__(self, shape=None):
        if not shape:
            shape = random.choice(list(self._shapes.keys()))
        self.shape = shape
        self.x = 5
        self.y = 1
        self.rot = 0  # 0-3 indicating number of times rotated

    def reset(self):
        self.x = 5
        self.y = 1
        self.rot = 0  # 0-3 indicating number of times rotated

    def locations(self):
        """
        To draw a piece will just return a list of the locations the
        piece occupies on the board.
        If these are out of bounds, colliding, etc
         that is the board's job to detect
        """
        # shapeshapeshapeshapeshapeSHAPESHAPESHAPESHAPE
        locs = self._shapes[self.shape]
        if self.rot in [1, 3]:
            # Flip
            locs = [(-y, x) for x, y in locs]
        if self.rot in [2, 3]:
            # invert
            locs = [(-x, -y) for x, y in locs]

        return [(self.x + dx, self.y + dy)
                for dx, dy in locs]

        raise Exception("Shape does not exist")


class Board:
    """Our gameboard
    This keeps an matrix of locations that are already 'full'
    from previous pieces.
    This does not include the current piece in-play.
    We'll handle the piece in play explictly
    """

    def __init__(self):
        self.board_size = {"x": 10, "y": 10}
        if BIG_BOARD:
            self.board_size = {"x": 20, "y": 20}
        if SMALL_BOARD:
            self.board_size = {"x": 8, "y": 8}

        self.board = [[False for _ in range(self.board_size["x"])]
                      for _ in range(self.board_size["y"])]

        self.piece = Piece()
        self.piece_queue = [Piece() for _ in "tetris"]
        self.score = 0

    def ghost_piece_locations(self):
        for drop in range(self.board_size['y']):
            self.piece.y += 1
            if self.detect_collision():
                self.piece.y -= 1
                # back to right before we collided
                ghost_loc = self.piece.locations()
                # put it back up in the air
                self.piece.y -= drop
                return ghost_loc

    def command(self, key, _retry=False):
        if key == "down":
            self.piece.y += 1
            if self.detect_collision():
                self.piece.y -= 1
                self.save_piece()

        if key in ["left", "right"]:
            old_x = self.piece.x
            direction = {"left": -1, "right": 1}
            self.piece.x += direction[key]
            if self.detect_collision():
                # disallow
                self.piece.x = old_x

        if key == "up":
            old_rot = self.piece.rot
            self.piece.rot = (self.piece.rot + 1) % 4
            if self.detect_collision():
                # disallow
                self.piece.rot = old_rot
                # wallkick
                if self.piece.x < self.board_size['x'] / 2:
                    self.piece.x += 1
                    if self.detect_collision():
                        self.piece.x -= 1

                if self.piece.x > self.board_size['x'] / 2:
                    self.piece.x -= 1
                    if self.detect_collision():
                        self.piece.x += 1
                # After wallkick, retry. Don't loop tho
                if not _retry:
                    self.command("up", _retry=True)

        if key == " ":
            # Drop it!
            for _ in range(self.board_size['y']):
                self.piece.y += 1
                if self.detect_collision():
                    self.piece.y -= 1
                    self.save_piece()
                    return

        if key == "`":
            cur_piece = self.piece
            self.nextPiece()
            self.piece_queue.insert(0, cur_piece)
            cur_piece.reset()

        if key == "=":
            # Cheat code!
            self.nextPiece()


# Draws the contents of the board with a border around it.

    def draw(self):
        # Clear screen! (unix only)
        ghost_loc = self.ghost_piece_locations()

        board_border = "".join(["*" for _ in range(self.board_size["x"] + 2)])
        printbuf = []
        printbuf.append(board_border)
        printbuf.append("|Score: {0} | Next: {1}".format(self.score,self.piece_queue[0].shape))
        printbuf.append(board_border)
        draw_buf = deepcopy(self.board)

        if self.detect_collision():
            raise Exception("collided while drawing")

        for x, y in self.piece.locations():
            draw_buf[y][x] = True

        for y in range(self.board_size["y"]):
            line = "|"
            for x in range(self.board_size["x"]):
                if draw_buf[y][x]:
                    line += '#'
                elif (x, y) in ghost_loc:
                    line += '.'
                else:
                    line += " "

            line += "|"
            printbuf.append(line)
        printbuf.append(board_border)
        # Move cursor to top of screen, so we can overwrite!
        print('\033[;H')

        print("\n".join(printbuf))

    def save_piece(self):
        "Save a piece to our permanent board"
        if self.detect_collision():
            raise Exception("Collision while saving")
        for x, y in self.piece.locations():
            self.board[y][x] = True

        self.clear_lines()
        self.nextPiece()

        if self.detect_collision():
            raise GameLoss()

    def detect_collision(self):
        """
        Return True if current board and piece result in a collsiion
        """
        for x, y in self.piece.locations():
            if not ((0 <= x < self.board_size["x"])
                    and (0 <= y < self.board_size["y"])):
                return True
            if self.board[y][x]:
                return True
        return False

    def clear_lines(self):
        """
        Check and delete any lines that are full, shifting down
        """
        to_clear = []
        for idx, xline in enumerate(self.board):
            if all(xline):
                to_clear.append(idx)

        if to_clear:
            for clear_idx in to_clear:
                del self.board[clear_idx]
                self.board.insert(0,
                                  [False for _ in range(self.board_size["x"])])

        self.score += len(to_clear)

    def nextPiece(self):
        self.piece = self.piece_queue.pop(0)
        self.piece_queue.append(Piece())
