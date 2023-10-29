from pieces.piece import *
from pieces.useful_funcs import *


class Rook(Piece):
    def char(self):
        return 'R'

    def can_move(self, row, col):
        if self.row != row and self.col != col:
            return False
        return True
