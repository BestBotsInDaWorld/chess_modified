from pieces.piece import *
from pieces.useful_funcs import *


class Rook(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.ability = Ability(get_ability(self.color_char()))

    def char(self):
        return 'R'

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def can_move(self, row, col):
        if self.row != row and self.col != col:
            return False
        return True
