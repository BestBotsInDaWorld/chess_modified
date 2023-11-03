from pieces.piece import *
from pieces.useful_funcs import *


class Queen(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.ability = Ability(get_ability(self.color_char()))

    def char(self):
        return 'Q'

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def can_move(self, row, col):
        if not correct_coords(row, col):
            return False
        if self.row != row and self.col != col and abs(self.row - row) != abs(self.col - col):
            return False
        return True
