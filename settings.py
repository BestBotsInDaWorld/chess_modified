from PyQt5 import uic
import sys
from pieces.useful_funcs import *
import sqlite3
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QButtonGroup, QPushButton, QWidget


def check_zero(string):
    return string and string != "0"


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("settings.ui", self)
        self.abilities = False
        self.cell_layout = [[0 for _ in range(8)] for i in range(8)]
        self.initUI()

    def initUI(self):
        self.cells = self.chessboard(
            [[(28 + 64 * i, 270 + 64 * j, (i + 1) + (j + 1)) for i in range(8)] for j in range(8)])
        con = sqlite3.connect("games.sqlite")
        cur = con.cursor()
        self.existing_files.addItems(map(lambda x: str(x[0]), cur.execute("""SELECT name FROM maps""").fetchall()))
        con.close()
        self.group = QButtonGroup()
        self.group.setExclusive(True)
        self.group.addButton(self.abilities_button_no)
        self.group.addButton(self.abilities_button_yes)
        self.abilities_button_no.setChecked(True)
        self.back_to_menu_btn.clicked.connect(self.close)
        self.existing_files.currentTextChanged.connect(self.layout_loading)
        self.apply_btn.clicked.connect(self.apply)
        self.apply_btn.clicked.connect(self.close)
        self.layout_loading()

    def apply(self):
        SETTINGS["MAP"] = self.existing_files.currentText()
        if self.abilities_button_yes.isChecked():
            SETTINGS["ABILITIES"] = True
        else:
            SETTINGS["ABILITIES"] = False

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
                array[i].append(new_btn)
        return array

    def update_piece_image(self, row, col):
        if check_zero(self.cell_layout[row][col]):
            self.cells[row][col].setIcon(QIcon(IMAGE_DIR + PIECE_IMAGES[self.cell_layout[row][col]]))
            self.cells[row][col].setIconSize(QSize(50, 50))
        else:
            self.cells[row][col].setIcon(QIcon())


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
