from PyQt5 import uic
import sys
import os
from pieces.useful_funcs import *
import sqlite3
from functools import partial
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QWidget

PIECE_CONFIGURATION = [
    'wK', 'bK',
    'wQ', 'bQ',
    'wR', 'bR',
    'wB', 'bB',
    'wN', 'bN',
    'wP', 'bP',
    ''
]


def check_zero(string):
    return string and string != "0"


class Constructor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("constructor.ui", self)
        self.cell_layout = [[0 for _ in range(8)] for i in range(8)]
        self.cur_piece = ""
        self.delete_row = -1
        self.delete_col = -1
        self.initUI()

    def initUI(self):
        self.choice_buttons = []
        self.cells = self.chessboard([[(288 + 64 * i, 64 * j, (i + 1) + (j + 1)) for i in range(8)] for j in range(8)])
        self.piece_choice_btns = self.btn_maker([[350 + 80 * (i // 2), 700 + 100 * (i % 2)] for i in range(12)], icon=1)
        con = sqlite3.connect("games.sqlite")
        cur = con.cursor()
        self.existing_files.addItems(map(lambda x: str(x[0]), cur.execute("""SELECT name FROM maps""").fetchall()))
        con.close()
        self.save_button.clicked.connect(self.layout_saving)
        self.load_button.clicked.connect(self.layout_loading)
        self.back_to_menu_btn.clicked.connect(self.close)

    def layout_loading(self):
        self.cell_layout = [[0 for _ in range(8)] for i in range(8)]
        for i in range(8):
            for j in range(8):
                self.update_piece_image(i, j)
        with open('layouts/' + self.existing_files.currentText(), 'r') as txtfile:
            self.cell_layout = list(map(lambda x: x.strip().split(), txtfile.readlines()))
            for i in range(8):
                for j in range(8):
                    self.update_piece_image(i, j)

    def layout_saving(self):
        filename = self.file_edit.text()
        if '.txt' not in filename:
            self.save_label.setText("")
            return 0
        con = sqlite3.connect("games.sqlite")
        cur = con.cursor()
        try:
            os.remove('layouts/' + filename)
            cur.execute(
                f"""DELETE FROM maps WHERE name = ?""", (str(filename),)
            )
            con.commit()
        except FileNotFoundError:
            pass
        with open(filename, 'w') as txtfile:
            for row in self.cell_layout:
                txtfile.write(" ".join(list(map(str, row))) + '\n')
        self.save_label.setText("Успешно сохранено!")
        os.rename(filename, 'layouts/' + filename)
        con = sqlite3.connect("games.sqlite")
        cur = con.cursor()
        cur.execute(
            f"""INSERT INTO maps(name) VALUES('{filename}')"""
        )
        con.commit()
        con.close()

    def chessboard(self, args, x=64, y=64):
        array = []
        for i in range(8):
            array.append([])
            for j, element in enumerate(args[i]):
                new_btn = QPushButton(self)
                new_btn.move(element[0], element[1])
                new_btn.resize(x, y)
                if not (element[2] % 2):
                    new_btn.setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
                else:
                    new_btn.setStyleSheet(BORDERS + "background-color: rgb(23, 229, 30);")
                new_btn.clicked.connect(partial(self.piece_set, i, j))
                array[i].append(new_btn)
        return array

    def btn_maker(self, args, x=64, y=64, icon=0):
        array = []
        for i, element in enumerate(args):
            new_btn = QPushButton(self)
            new_btn.move(element[0], element[1])
            new_btn.resize(x, y)
            new_btn.setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
            new_btn.clicked.connect(partial(self.piece_choice, i))
            if icon:
                new_btn.setIcon(QIcon(IMAGE_DIR + PIECE_IMAGES[PIECE_CONFIGURATION[i]]))
                new_btn.setIconSize(QSize(60, 60))
            array.append(new_btn)
        return array

    def piece_set(self, row, col):
        if self.delete_row == row and self.delete_col == col:
            self.cell_layout[row][col] = 0
            self.cells[row][col].setIcon(QIcon())
            self.make_normal()
        elif self.cur_piece and not check_zero(self.cell_layout[row][col]):
            self.cell_layout[row][col] = self.cur_piece
            self.make_normal()
            self.update_piece_image(row, col)
        elif check_zero(self.cell_layout[row][col]):
            self.make_normal()
            self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(255, 0, 0);")
            self.delete_col = col
            self.delete_row = row

    def make_normal(self):
        x, y = self.delete_col, self.delete_row
        if x == -1 or y == -1:
            return 0
        if not ((x + y) % 2):
            self.cells[y][x].setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
        else:
            self.cells[y][x].setStyleSheet(BORDERS + "background-color: rgb(23, 229, 30);")
        self.delete_row = -1
        self.delete_col = -1

    def piece_choice(self, index):
        self.cur_piece = PIECE_CONFIGURATION[index]
        self.l_piece_selection.setPixmap(QPixmap(IMAGE_DIR + PIECE_IMAGES[self.cur_piece]))

    def update_piece_image(self, row, col):
        if check_zero(self.cell_layout[row][col]):
            self.cells[row][col].setIcon(QIcon(IMAGE_DIR + PIECE_IMAGES[self.cell_layout[row][col]]))
            self.cells[row][col].setIconSize(QSize(50, 50))
        else:
            self.cells[row][col].setIcon(QIcon())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
