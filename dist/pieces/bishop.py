from pieces.piece import *
from pieces.useful_funcs import *


class Bishop(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.ability = Ability(get_ability(self.color_char()))

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def char(self):
        return 'B'

    def can_move(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8 and abs(self.row - row) == abs(self.col - col):
            return True
        else:
            return False
