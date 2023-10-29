from pieces.piece import *
from pieces.useful_funcs import *


class King(Piece):

    def char(self):
        return 'K'

    def can_move(self, row, col):
        if not correct_coords(row, col):
            return False
        if abs(self.row - row) <= 1 and abs(self.col - col) <= 1:
            return True
        return False
