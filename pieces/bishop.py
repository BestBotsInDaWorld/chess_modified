from pieces.piece import *
from pieces.useful_funcs import *


class Bishop(Piece):
    def char(self):
        return 'B'

    def can_move(self, row, col):
        if 0 <= row < 8 and 0 <= col < 8 and abs(self.row - row) == abs(self.col - col):
            return True
        else:
            return False
