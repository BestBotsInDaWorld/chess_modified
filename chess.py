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


def route(row: int, col: int, row2: int, col2: int, field: list):  # не стоит ли на пути фигуры другая фигура
    if row - row2 == 0:
        row_direction = 0
    elif row - row2 < 0:
        row_direction = 1
    else:
        row_direction = -1
    if col - col2 == 0:
        col_direction = 0
    elif col - col2 < 0:
        col_direction = 1
    else:
        col_direction = -1
    for i in range(1, max(abs(row - row2), abs(col - col2))):  # проверка клеток поля на пути на наличие фигур
        if field[row + row_direction * i][col + col_direction * i] is not None:
            return False
    else:
        return True


def route_definition(row: int, col: int, row2: int, col2: int, field: list):  # определение пути фигуры ДО координаты
    route = []
    if row - row2 == 0:
        row_direction = 0
    elif row - row2 < 0:
        row_direction = 1
    else:
        row_direction = -1
    if col - col2 == 0:
        col_direction = 0
    elif col - col2 < 0:
        col_direction = 1
    else:
        col_direction = -1
    for i in range(0, max(abs(row - row2), abs(col - col2))):
        route.append((row + row_direction * i, col + col_direction * i))
    return route


color = WHITE
PIECES = {'P': Pawn, 'Q': Queen, 'K': King, 'N': Knight, 'R': Rook, 'B': Bishop}


def print_board(board):
    for row in range(7, -1, -1):
        for col in range(8):
            if board.field[row][col] is None:
                pos = (row, col)
            else:
                pos = board.field[row][col].get_position()
            print(board.cell(row, col), pos, end=' ')
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
        self.ability_activated = 0
        self.game_ended = 0
        self.abilities_on = SETTINGS["ABILITIES"]
        self.ability_range_cell_coords = []
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
        self.toggle_ability_widgets("HIDE")
        self.ability_use_btn.clicked.connect(self.ability_range_show)

    def change_recruit(self, param: int):
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

    def cell_choice(self, row: int, col: int):
        end_toggle = "HIDE"
        if self.game_ended:
            self.new_game_btn.clicked.emit()
        piece = self.board.field[row][col]
        if self.ability_activated:
            backup_field = [[el for el in row] for row in self.board.field]
            centre_row, centre_col = self.chosen_cell_row, self.chosen_cell_col
            piece = self.board.field[centre_row][centre_col]
            if piece.stopped:
                self.error_label.setText('Фигура остановлена')
                return False
            delta = (row - centre_row, col - centre_col)
            if piece.ability.is_all_cells() and delta in piece.ability.get_ability_range():
                ability_range = piece.ability.get_ability_range()
            elif not piece.ability.is_all_cells() and delta in piece.ability.get_ability_range():
                ability_range = [(row, col)]
            else:
                self.error_label.setText('Выберите одну из отмеченных клеток')
                return False
            result = piece.ability.use(centre_row, centre_col, ability_range, self.board.field, test=True)
            self.board.recruit_set()
            if self.board.current_player_color() == WHITE:
                king_row, king_col = self.board.white_king_row, self.board.white_king_col
            else:
                king_row, king_col = self.board.black_king_row, self.board.black_king_col
            if result:
                if not self.board.is_under_attack(king_row, king_col, opponent(self.board.current_player_color())):
                    piece.ability.update_counter()
                    self.board.color = opponent(self.board.color)
                    self.change_recruit(0)
                    self.update_piece_images()
                    self.make_normal()
                    self.error_label.setText('')
                    if self.board.current_player_color() == WHITE:
                        self.turn += 1
                    self.clear_ability()
                    self.toggle_ability_widgets("HIDE")
                    play_sound(piece.ability.info["ACTION"])
                    if self.board.get_ability_mate():
                        self.checkmate_declaration()
                    return True
                else:
                    self.board.field = backup_field
                    for i, row in enumerate(self.board.field):
                        for j, el in enumerate(row):
                            if el is not None:
                                el.set_position(i, j)
                    self.clear_ability()
                    self.error_label.setText('Король не должен попадать под шах')
                    return False
            else:
                self.clear_ability()
                self.error_label.setText('Способность неприменима')
                return False
        if not self.cell_chosen:
            if piece is not None and piece.get_color() == self.board.current_player_color():
                self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(255, 0, 0);")
                self.cell_chosen = True
                self.chosen_cell_col = col
                self.chosen_cell_row = row
                if self.abilities_on and piece.ability is not None:
                    self.toggle_ability_widgets("SHOW")
                    self.ability_info_show(piece)
                    end_toggle = None
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
                self.error_label.setText("")
            else:
                if piece is not None and self.board.current_player_color() == piece.get_color():
                    self.make_normal()
                    self.cell_choice(row, col)
                    self.error_label.setText("")
                else:
                    self.error_label.setText(self.board.error_message)
                end_toggle = None
        if self.board.checkmate:
            self.checkmate_declaration()
        if self.abilities_on:
            self.toggle_ability_widgets(end_toggle)
        self.clear_ability()

    def toggle_ability_widgets(self, param: str):
        if param == "SHOW":
            self.ability_use_btn.show()
            self.ability_name_label.show()
            self.ability_info_label.show()
            self.ability_use_count_label.show()
            row, col = self.chosen_cell_row, self.chosen_cell_col
            self.ability_use_btn.setIconSize(QSize(50, 50))
            self.ability_use_btn.setIcon(QIcon(self.board.field[row][col].ability.get_image()))
        elif param == "HIDE":
            self.ability_use_btn.hide()
            self.ability_name_label.hide()
            self.ability_info_label.hide()
            self.ability_use_count_label.hide()

    def ability_info_show(self, piece):
        ability = piece.ability
        text_info = ability.text_info()
        self.ability_use_count_label.setText(f"Осталось применений: {str(ability.get_use_count())}")
        self.ability_name_label.setText(text_info[0])
        self.ability_info_label.setText(text_info[1])
        self.ability_use_btn.setIcon(QIcon(ability.info["IMAGE"]))

    def ability_range_show(self):
        if self.ability_activated:
            self.clear_ability()
            return 0
        row, col = self.chosen_cell_row, self.chosen_cell_col
        ability = self.board.field[row][col].ability
        if ability.is_all_cells():
            color = BORDERS + "background-color: rgb(52, 37, 255);"
        else:
            color = BORDERS + "background-color: rgb(170, 0, 255);"
        for row_delta, col_delta in ability.get_ability_range():
            if row_delta == col_delta == 0 or not correct_coords(row + row_delta, col + col_delta):
                continue
            else:
                self.cells[row + row_delta][col + col_delta].setStyleSheet(color)
                self.ability_range_cell_coords.append((row + row_delta, col + col_delta))
        self.ability_use_btn.setStyleSheet(BORDERS + "background-color: red")
        self.ability_activated = 1

    def clear_ability(self):
        for row, col in self.ability_range_cell_coords:
            if not ((row + col) % 2):
                self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
            else:
                self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(23, 229, 30);")
        self.ability_range_cell_coords = []
        self.ability_use_btn.setStyleSheet(BORDERS + "background-color: blue")
        self.ability_activated = 0

    def make_normal(self):
        self.cell_chosen = False
        row, col = self.chosen_cell_row, self.chosen_cell_col
        if not ((row + col) % 2):
            self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(222, 222, 222);")
        else:
            self.cells[row][col].setStyleSheet(BORDERS + "background-color: rgb(23, 229, 30);")
        self.chosen_cell_col = -1
        self.chosen_cell_row = -1

    def checkmate_declaration(self):
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
        VALUES('{win}', '{self.map}', {self.turn}, '{convert}', '{date.today()}', '{self.abilities_on}')
        """)
        con.commit()
        con.close()
        play_sound("VICTORY")

    def btn_maker(self, args: list, x=64, y=64):
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

    def label_maker(self, args: list, x=64, y=64):
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
                        if self.field[row][col].ability is not None:
                            self.field[row][col].ability.info["USE_COUNT"] = 1
                        if piece == 'K':
                            if color == WHITE:
                                self.white_king_row = row
                                self.white_king_col = col
                            else:
                                self.black_king_row = row
                                self.black_king_col = col

    def is_under_attack(self, row: int, col: int, opp_color: int):
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

    def cell(self, row: int, col: int):
        piece = self.field[row][col]
        if piece is None:
            return '0'
        color = piece.get_color()
        c = 'w' if color == WHITE else 'b'
        return c + piece.char()

    def make_castle(self, row: int, col: int, row1: int, col1: int):
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

    def move_piece(self, row: int, col: int, row1: int, col1: int, mate_test=0):
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            self.error_message = 'Некорректные координаты'
            return False

        if row == row1 and col == col1:
            return False
        piece = self.field[row][col]

        if piece is None:
            self.error_message = 'Не выбрана фигура'
            return False

        if piece.get_color() != self.color:
            self.error_message = 'Не ваш ход'
            return False

        if piece.stopped:
            self.error_message = 'Фигура остановлена'
            return False

        if self.field[row1][col1] is not None and self.field[row1][col1].shielded:
            self.error_message = 'Вражеская фигура под защитой'
            return False

        if isinstance(piece, King) and not mate_test and (row1, col1) in self.castle_positions[self.cell(row, col)]:
            if self.make_castle(row, col, row1, col1):
                self.color = opponent(self.color)
                return True
            else:
                self.castle_error = 1

        if not self.check_pawn_move(piece, row, col, row1, col1):
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

        king_row, king_col, enemy_row, enemy_col = self.get_kings()
        if mate_test:
            return True

        opponent_piece = self.field[row1][col1]
        self.field[row][col] = None
        self.field[row1][col1] = piece

        if self.is_under_attack(king_row, king_col, opponent(color)):
            self.field[row][col] = piece
            self.field[row1][col1] = opponent_piece
            self.error_message = 'Король не должен попадать под шах'
            return False

        piece.set_position(row1, col1)
        self.field[row1][col1].moved = True

        if isinstance(piece, Pawn) and piece.check_promote(row1):
            recr = PIECES[self.recruit_pieces[self.recruits[self.current_player_color() % 2]]]
            self.field[row1][col1] = recr(row1, col1, self.current_player_color())
        attacking_pieces = self.is_under_attack(enemy_row, enemy_col, color)

        self.clear_piece_effects()

        self.color = opponent(self.color)
        if attacking_pieces:
            if self.check_mate(attacking_pieces, enemy_row, enemy_col):
                if self.color == WHITE:
                    self.checkmate = WHITE
                else:
                    self.checkmate = BLACK
        return True

    def check_pawn_move(self, piece, row, col, row1, col1):
        if isinstance(piece, Pawn):  # ход пешки
            if col == col1:
                if piece.color == WHITE:
                    d = -1
                else:
                    d = 1
                if self.field[row1][col1] is not None or self.field[row + d][col1] is not None:
                    return False
                return True
            else:
                if self.field[row1][col1] is None:
                    return False
                return True
        else:
            return True

    def clear_piece_effects(self):
        for row in self.field:
            for el in row:
                if el is not None and el.color == self.color and el.stopped:
                    el.stopped = False
                elif el is not None and el.color != self.color and el.shielded:
                    el.shielded -= 1
                    if el.shielded < 0:
                        el.shielded = 0

    def get_ability_mate(self):
        if self.color == BLACK:
            enemy_row = self.black_king_row
            enemy_col = self.black_king_col
        else:
            enemy_row = self.white_king_row
            enemy_col = self.white_king_col
        attacking_pieces = self.is_under_attack(enemy_row, enemy_col, opponent(self.color))
        if attacking_pieces:
            if self.check_mate(attacking_pieces, enemy_row, enemy_col):
                if self.color == WHITE:
                    self.checkmate = WHITE
                else:
                    self.checkmate = BLACK
                return True
        return False

    def get_kings(self):
        if self.color == WHITE:
            king_row = self.white_king_row
            king_col = self.white_king_col
            enemy_row = self.black_king_row
            enemy_col = self.black_king_col
        else:
            king_row = self.black_king_row
            king_col = self.black_king_col
            enemy_row = self.white_king_row
            enemy_col = self.white_king_col
        return [king_row, king_col, enemy_row, enemy_col]

    def recruit_set(self):
        for i in range(8):
            bpiece = self.field[7][i]
            wpiece = self.field[0][i]
            if bpiece is not None and isinstance(bpiece, Pawn) and bpiece.color == BLACK:
                recr = PIECES[self.recruit_pieces[self.recruits[BLACK]]]
                self.field[7][i] = recr(7, i, BLACK)
            elif wpiece is not None and isinstance(wpiece, Pawn) and wpiece.color == WHITE:
                recr = PIECES[self.recruit_pieces[self.recruits[WHITE]]]
                self.field[0][i] = recr(0, i, WHITE)

    def check_mate(self, attacking_pieces: list, enemy_row: int, enemy_col: int):
        for i in range(8):
            for j in range(8):
                if self.move_piece(enemy_row, enemy_col, i, j, mate_test=1):  # тест короля
                    return False
        to_block = []
        for i in attacking_pieces:
            row, col = i.get_position()
            if (isinstance(i, Knight)):
                to_block.append([(row, col)])
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
