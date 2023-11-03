from pieces.piece import *
from pieces.useful_funcs import *


class Knight(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.ability = Ability(get_ability(self.color_char()))

    def char(self):
        return 'N'

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def can_move(self, row, col):
        if abs(self.row - row) == 1 and abs(self.col - col) == 2 and correct_coords(row, col):
            return True
        if abs(self.row - row) == 2 and abs(self.col - col) == 1 and correct_coords(row, col):
            return True
        else:
            return False
