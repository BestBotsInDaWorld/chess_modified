from pieces.piece import *
from pieces.useful_funcs import *


class Knight(Piece):
    def char(self):
        return 'N'

    def can_move(self, row, col):
        if abs(self.row - row) == 1 and abs(self.col - col) == 2 and correct_coords(row, col):
            return True
        if abs(self.row - row) == 2 and abs(self.col - col) == 1 and correct_coords(row, col):
            return True
        else:
            return False
