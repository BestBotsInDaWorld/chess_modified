from pieces.piece import *
from pieces.useful_funcs import *


class King(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.affectable = False
        self.ability = None

    def char(self):
        return 'K'

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def can_move(self, row, col):
        if not correct_coords(row, col):
            return False
        if abs(self.row - row) <= 1 and abs(self.col - col) <= 1:
            return True
        return False
