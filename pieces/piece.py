from pieces.ability import *


class Piece:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.moved = False
        self.abilities = False
        self.stopped = False
        self.shielded = 0
        self.affectable = True

    def get_color(self):
        return self.color

    def set_position(self, row, col):
        self.row = row
        self.col = col

    def get_position(self):
        return (self.row, self.col)
