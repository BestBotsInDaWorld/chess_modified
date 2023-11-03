from PyQt5 import uic
import sys
from pieces.useful_funcs import *
from functools import partial
import sqlite3
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QButtonGroup, QPushButton, QWidget, QLabel


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
        self.abilities_button_yes.toggled.connect(self.ability_customisation)
        self.abilities_button_no.toggled.connect(self.ability_customisation)
        self.ability_choice_btns = []
        self.piece_labels = []
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

    def ability_customisation(self):
        if self.abilities_button_yes.isChecked():
            self.setGeometry(675, 70, 800, 900)
            self.make_ability_choice_btns()
            self.make_piece_labels()
        else:
            self.setGeometry(675, 70, 600, 900)
            self.make_ability_choice_btns("HIDE")
            self.make_piece_labels("HIDE")

    def make_ability_choice_btns(self, param="SHOW"):
        pieces = ["wQ", "bQ"]
        abilities = ["QUEEN_CARRY", "QUEEN_SHIELD"]
        ability_images = {"QUEEN_CARRY": "Piece_Carry.png",
                          "QUEEN_SHIELD": "Piece_Shield.png"}
        if not self.ability_choice_btns:
            for row in range(2):
                for col in range(2):
                    new_btn = QPushButton(self)
                    new_btn.move(680 + col * 64, 70 + row * 64)
                    new_btn.resize(64, 64)
                    if not col:
                        new_btn.setStyleSheet(BORDERS + "background-color: red;")
                    else:
                        new_btn.setStyleSheet(BORDERS + "background-color: blue;")
                    responding_ability = abilities[(row // 2 * 2) + col]
                    new_btn.setIcon(QIcon(ABILITY_DIR + ability_images[responding_ability]))
                    new_btn.setIconSize(QSize(50, 50))
                    new_btn.clicked.connect(partial(self.ability_set, pieces[row], responding_ability, row, col))
                    self.ability_choice_btns.append(new_btn)
        if param == "HIDE":
            for btn in self.ability_choice_btns:
                btn.hide()
        elif param == "SHOW":
            for btn in self.ability_choice_btns:
                btn.show()

    def ability_set(self, piece_name, ability_name, row, col):
        next_col = 1 if col == 0 else 0
        PIECE_ABILITIES[piece_name] = ability_name
        self.ability_choice_btns[row * 2 + col].setStyleSheet(BORDERS + "background-color: red;")
        self.ability_choice_btns[row * 2 + next_col].setStyleSheet(BORDERS + "background-color: blue;")

    def make_piece_labels(self, param="SHOW"):
        pieces = ["wQ", "bQ"]
        if not self.piece_labels:
            for row, element in enumerate(pieces):
                new_label = QLabel(self)
                new_label.setPixmap(QPixmap(IMAGE_DIR + PIECE_IMAGES[element]))
                new_label.move(610, 70 + row * 64)
                new_label.resize(64, 64)
                self.piece_labels.append(new_label)
        if param == "HIDE":
            for label in self.piece_labels:
                label.hide()
        elif param == "SHOW":
            for label in self.piece_labels:
                label.show()

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
