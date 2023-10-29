from pieces.piece import *
from pieces.useful_funcs import *


class Queen(Piece):
    def char(self):
        return 'Q'

    def can_move(self, row, col):
        if not correct_coords(row, col):
            return False
        if self.row != row and self.col != col and abs(self.row - row) != abs(self.col - col):
            return False
        return True
