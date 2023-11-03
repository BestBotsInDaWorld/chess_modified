from pieces.piece import *
from pieces.useful_funcs import *


class Pawn(Piece):
    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.ability = Ability(get_ability(self.color_char()))

    def char(self):
        return 'P'

    def color_char(self):
        return COLORING_REVERSE[self.color] + self.char()

    def can_move(self, row, col):
        if self.color == WHITE:
            direction = -1
            start_row = 6
        else:
            direction = 1
            start_row = 1

        if self.col != col:
            if abs(self.col - col) == 1 and self.row + direction == row:
                return True
            else:
                return False

        if self.row + direction == row:
            return True

        if self.row == start_row and self.row + 2 * direction == row:
            return True

        return False

    def check_promote(self, row):
        if self.color == WHITE:
            return row == 0
        else:
            return row == 7
