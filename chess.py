import sys
import sqlite3
from soundpad import *
from functools import partial
from time import perf_counter, gmtime, strftime
from datetime import date
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget
from pieces.king import King
from pieces.rook import Rook
from pieces.knight import Knight
from pieces.queen import Queen
from pieces.pawn import Pawn
from pieces.bishop import Bishop
from pieces.useful_funcs import *


def route(row, col, row2, col2, field):  # функция проверки: не стоит ли на пути фигуры другая фигура
    if row - row2 == 0:
        r = 0
    elif row - row2 < 0:
        r = 1
    else:
        r = -1
    if col - col2 == 0:
        c = 0
    elif col - col2 < 0:
        c = 1
    else:
        c = -1
    for i in range(1, max(abs(row - row2), abs(col - col2))):  # проверка клеток поля на пути на наличие фигур
        if field[row + r * i][col + c * i] is not None:
            return False
    else:
        return True


def route_definition(row, col, row2, col2, field):
    route = []
    if row - row2 == 0:
        r = 0
    elif row - row2 < 0:
        r = 1
    else:
        r = -1
    if col - col2 == 0:
        c = 0
    elif col - col2 < 0:
        c = 1
    else:
        c = -1
    for i in range(0, max(abs(row - row2), abs(col - col2))):
        route.append((row + r * i, col + c * i))
    return route


color = WHITE
PIECES = {'P': Pawn, 'Q': Queen, 'K': King, 'N': Knight, 'R': Rook, 'B': Bishop}


def print_board(board):
    for row in range(7, -1, -1):
        for col in range(8):
            print(board.cell(row, col), end=' ')
        print()


class Chess(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("chess.ui", self)
        self.board = Board()
        self.turn = 1
        self.cell_chosen = False
        self.chosen_cell_col = -1
        self.chosen_cell_row = -1
        self.game_ended = 0
        self.abilities = SETTINGS["ABILITIES"]
        self.map = SETTINGS["MAP"]
        self.initUI()
        self.start = perf_counter()

    def initUI(self):
        self.cells = self.btn_maker([[(288 + 64 * i, 64 * j, (i + 1) + (j + 1)) for i in range(8)] for j in range(8)])
        self.num_labels = self.label_maker([(str(8 - i), 240, 64 * i) for i in range(8)])
        self.let_labels = self.label_maker([("abcdefgh"[i], 310 + 64 * i, 512) for i in range(8)])
        self.pawn_recruit_choose.setIcon(QIcon(IMAGE_DIR + PIECE_IMAGES['wQ']))
        self.pawn_recruit_choose.clicked.connect(lambda: self.change_recruit(1))
        self.pawn_recruit_choose.setIconSize(QSize(50, 50))
        self.update_piece_images()
        self.new_game_btn.clicked.connect(self.close)
        self.back_to_menu_btn.clicked.connect(self.close)

    def change_recruit(self, param):
        color = self.board.current_player_color()
        self.board.recruits[color % 2] = (self.board.recruits[color % 2] + param) % 4
        img = IMAGE_DIR + PIECE_IMAGES[
            COLORING_REVERSE[color] + self.board.recruit_pieces[self.board.recruits[color % 2]]]
        self.pawn_recruit_choose.setIcon(QIcon(img))

    def update_piece_images(self):
        for i in range(8):
            for j in range(8):
                if self.board.field[i][j] is not None:
                    curr_icon = QIcon(IMAGE_DIR + PIECE_IMAGES[self.board.cell(i, j)])
                    self.cells[i][j].setIcon(curr_icon)
                    self.cells[i][j].setIconSize(QSize(50, 50))
                else:
                    self.cells[i][j].setIcon(QIcon())

    def btn_maker(self, args, x=64, y=64):
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
                new_btn.clicked.connect(partial(self.cell_choice, i, j))
                array[i].append(new_btn)
        return array

    def cell_choice(self, row, col):
        if self.game_ended:
            self.new_game_btn.clicked.emit()
        piece = self.board.field[row][col]
        if not self.cell_chosen:
            if piece is not None and piece.get_color() == self.board.current_player_color():
                self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(255, 0, 0);")
                self.cell_chosen = True
                self.chosen_cell_col = col
                self.chosen_cell_row = row
        else:
            if self.board.move_piece(self.chosen_cell_row, self.chosen_cell_col, row, col):
                self.change_recruit(0)
                self.update_piece_images()
                self.make_normal()
                self.error_label.setText('')
                if self.board.current_player_color() == WHITE:
                    self.turn += 1
                play_sound("MOVE")
            elif (row == self.chosen_cell_row) and (col == self.chosen_cell_col):
                self.make_normal()
            else:
                if piece is not None and self.board.current_player_color() == piece.get_color():
                    self.make_normal()
                    self.cell_choice(row, col)
                else:
                    self.error_label.setText(self.board.error_message)
        if self.board.checkmate:
            mate = self.board.checkmate
            if mate == WHITE:
                self.cells[self.board.white_king_row][self.board.white_king_col].setIcon(
                    QIcon(IMAGE_DIR + PIECE_IMAGES['death']))
                win = 'black'
                self.turn -= 1
            else:
                self.cells[self.board.black_king_row][self.board.black_king_col].setIcon(
                    QIcon(IMAGE_DIR + PIECE_IMAGES['death']))
                win = 'white'
            self.game_ended = 1
            end = perf_counter()
            convert = strftime("%H:%M:%S", gmtime(round(end - self.start)))
            con = sqlite3.connect('games.sqlite')
            cursor = con.cursor()
            cursor.execute(f"""
            INSERT INTO rounds(winner, map, turn, duration, date, abilities)
            VALUES('{win}', '{self.map}', {self.turn}, '{convert}', '{date.today()}', '{self.abilities}')
            """)
            con.commit()
            con.close()
            play_sound("VICTORY")

    def make_normal(self):
        self.cell_chosen = False
        x, y = self.chosen_cell_col, self.chosen_cell_row
        if not ((x + y) % 2):
            self.cells[y][x].setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
        else:
            self.cells[y][x].setStyleSheet(BORDERS + "background-color: rgb(23, 229, 30);")
        self.chosen_cell_col = -1
        self.chosen_cell_row = -1

    def label_maker(self, args, x=64, y=64):
        array = []
        for element in args:
            new_label = QLabel(self)
            new_label.setText(element[0])
            new_label.move(element[1], element[2])
            new_label.resize(x, y)
            new_label.setFont(QFont('Times font', 20))
            array.append(new_label)
        return array


class Board:
    def __init__(self):
        self.error_message = ''
        self.color = WHITE
        self.field = []
        self.castle_error = 0
        self.recruit_pieces = ['Q', 'N', 'R', 'B']
        self.recruits = [0, 0]
        self.white_king_row = -1
        self.white_king_col = -1
        self.black_king_row = -1
        self.black_king_col = -1
        self.checkmate = 0
        self.castle_positions = {'wK': [(7, 1), (7, 6)], 'bK': [(0, 1), (0, 6)]}
        for row in range(8):
            self.field.append([None] * 8)
        with open('layouts/' + SETTINGS["MAP"], 'r') as layout:
            data = list(map(lambda x: x.strip().split(), layout.readlines()))
            for row in range(8):
                for col in range(8):
                    if data[row][col] != '0':
                        color, piece = data[row][col]
                        color = COLORING[color]
                        self.field[row][col] = PIECES[piece](row, col, color)
                        if piece == 'K':
                            if color == WHITE:
                                self.white_king_row = row
                                self.white_king_col = col
                            else:
                                self.black_king_row = row
                                self.black_king_col = col

    def is_under_attack(self, row, col, opp_color):
        attacking_pieces = []
        for r in self.field:
            for element in r:
                if element is not None:
                    if element.can_move(row, col) and element.get_color() == opp_color:
                        if route(element.row, element.col, row, col, self.field):
                            if not isinstance(element, Knight) and not isinstance(element, Pawn):
                                attacking_pieces.append(element)
                        if isinstance(element, Knight):
                            attacking_pieces.append(element)
                        if route(element.row, element.col, row, col, self.field) and isinstance(element, Pawn):
                            if element.col != col:
                                attacking_pieces.append(element)
        return attacking_pieces

    def current_player_color(self):
        return self.color

    def cell(self, row, col):
        piece = self.field[row][col]
        if piece is None:
            return '0'
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def make_castle(self, row, col, row1, col1):
        if col1 == 1:
            flank = -1
        else:
            flank = 1
        king, rook = self.field[row][col], self.field[row1][col1 + flank]
        if king is None or rook is None:
            self.error_message = 'Рокировка невозможна!'
            return False
        if king.moved or rook.moved:
            self.error_message = 'Рокировка невозможна!'
            return False
        coords = route_definition(row, col, row1, col1 + flank, self.field)
        if self.is_under_attack(row, col, opponent(self.current_player_color())):
            self.error_message = 'Рокировка невозможна!'
            return False
        for i in coords[1:]:
            r, c = i
            if self.field[r][c] is not None or self.is_under_attack(r, c, opponent(self.current_player_color())):
                self.error_message = 'Рокировка невозможна!'
                return False
        king.set_position(row1, col1)
        rook.set_position(row1, col1 - flank)
        self.field[row][col] = None
        self.field[row1][col1 + flank] = None
        self.field[row1][col1] = king
        self.field[row1][col1 - flank] = rook
        return True

    def move_piece(self, row, col, row1, col1, mate_test=0):
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            self.error_message = 'Некорректные координаты'
            return False

        if row == row1 and col == col1:
            return False
        piece = self.field[row][col]
        if isinstance(piece, King) and not mate_test and (row1, col1) in self.castle_positions[self.cell(row, col)]:
            if self.make_castle(row, col, row1, col1):
                self.color = opponent(self.color)
                return True
            else:
                self.castle_error = 1
        if isinstance(piece, Pawn):  # ход пешки
            if col == col1:
                if piece.color == WHITE:
                    d = -1
                else:
                    d = 1
                if self.field[row1][col1] is not None or self.field[row + d][col1] is not None:
                    return False
            else:
                if self.field[row1][col1] is None:
                    return False

        if piece is None:
            self.error_message = 'Не выбрана фигура'
            return False
        if piece.get_color() != self.color:
            self.error_message = 'Не ваш ход'
            return False
        if not piece.can_move(row1, col1):
            if not self.castle_error:
                self.error_message = 'Фигура так ходить не может'
            self.castle_error = 0
            return False
        self.castle_error = 0
        if self.field[row1][col1] is not None:  # можно брать фигуры не своего цвета
            if self.field[row1][col1].color == piece.color:
                self.error_message = 'Нельзя брать свои фигуры'
                return False

        if not route(row, col, row1, col1, self.field) and not isinstance(piece, Knight):
            self.error_message = 'Путь перегорожен'
            return False

        color = piece.get_color()
        if isinstance(piece, King):
            piece_opp = self.field[row1][col1]
            self.field[row][col] = None
            self.field[row1][col1] = piece
            if self.is_under_attack(row1, col1, opponent(piece.color)):
                self.field[row][col] = piece
                self.field[row1][col1] = piece_opp
                self.error_message = 'Король не должен попадать под шах'
                return False
            else:
                if mate_test:
                    self.field[row][col] = piece
                    self.field[row1][col1] = piece_opp
                    return True
                self.field[row1][col1].moved = True
                if piece.get_color() == WHITE:
                    self.white_king_row = row1
                    self.white_king_col = col1
                else:
                    self.black_king_row = row1
                    self.black_king_col = col1
                piece.set_position(row1, col1)
                self.color = opponent(self.color)
                return True
        if color == WHITE:
            king_row = self.white_king_row
            king_col = self.white_king_col
            enemy_row = self.black_king_row
            enemy_col = self.black_king_col
        else:
            king_row = self.black_king_row
            king_col = self.black_king_col
            enemy_row = self.white_king_row
            enemy_col = self.white_king_col
        if mate_test:
            return True
        self.field[row][col] = None
        self.field[row1][col1] = piece
        if self.is_under_attack(king_row, king_col, opponent(color)):
            self.field[row][col] = piece
            self.field[row1][col1] = None
            self.error_message = 'Король не должен попадать под шах'
            return False
        piece.set_position(row1, col1)
        self.field[row1][col1].moved = True
        if isinstance(piece, Pawn) and piece.check_promote(row1):
            recr = PIECES[self.recruit_pieces[self.recruits[self.current_player_color() % 2]]]
            self.field[row1][col1] = recr(row1, col1, self.current_player_color())
        attacking_pieces = self.is_under_attack(enemy_row, enemy_col, color)
        self.color = opponent(self.color)
        if attacking_pieces:
            if self.check_mate(attacking_pieces, enemy_row, enemy_col):
                if self.color == WHITE:
                    self.checkmate = WHITE
                else:
                    self.checkmate = BLACK
        return True

    def check_mate(self, attacking_pieces, enemy_row, enemy_col):
        for i in range(8):
            for j in range(8):
                if self.move_piece(enemy_row, enemy_col, i, j, mate_test=1):  # тест короля
                    return False
        to_block = []
        for i in attacking_pieces:
            row, col = i.get_position()
            if (isinstance(i, Knight)):
                to_block.append((row, col))
                continue
            to_block.append(route_definition(row, col, enemy_row, enemy_col, self.field))
        final_coords = set(to_block[0])
        for i in to_block:
            final_coords = final_coords.intersection(set(i))
        final_coords = list(final_coords)
        for row, col in final_coords:
            for r in self.field:
                for element in r:
                    if element is not None:
                        el_row, el_col = element.get_position()
                        if self.move_piece(el_row, el_col, row, col, mate_test=1):
                            return False
        return True

    def __str__(self):
        print_board(self)
        return ''


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
