WHITE = 1
BLACK = 2
color = WHITE

COLORING = {'b': BLACK, 'w': WHITE, }

COLORING_REVERSE = {BLACK: 'b', WHITE: 'w', }

IMAGE_DIR = 'pieces/piece_images/'

SOUND_DIR = 'pieces/piece_sounds/'

ABILITY_DIR = 'pieces/ability_images/'

BORDERS = "border-style: outset; border-width: 2px; border-color: black; "

PIECE_SOUNDS = {
    'MOVE': 'move.wav',
    'VICTORY': 'victory.wav',
}

BUTTON_IMAGES = {
    'GAME': 'horse.png',
    'CONSTRUCT': 'hammer.png',
    'LEADERBOARDS': 'crown.png',
    'EXIT': 'exit.png',
}

PIECE_IMAGES = {"bB": "bBishop.png", "bN": "bKnight.png", "bK": "bKing.png", "bQ": "bQueen.png",
                "bP": "bPawn.png", "bR": "bRook.png", "wB": "wBishop.png", "wN": "wKnight.png",
                "wK": "wKing.png", "wQ": "wQueen.png", "wP": "wPawn.png", "wR": "wRook.png",
                "death": "nuclear-explosion.png", }

SETTINGS = {
    "MAP": "original.txt",
    "ABILITIES": False,
}

ABILITY_RANGE = {
    "QUEEN_CARRY": [(0, -2), (0, 2), (-2, 0), (2, 0),
                    (-1, -1), (-1, 1), (1, -1), (1, 1),
                    (0, -1), (0, 1), (-1, 0), (1, 0)],
    "QUEEN_SHIELD": [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)],
    "ROOK_PIERCE": [(0, i) for i in range(-3, 4)] + [(i, 0) for i in range(-3, 4)],
    "BISHOP_REPLACE": [(i, i) for i in range(-3, 4)] + [(-i, i) for i in range(-3, 4)],
    "KNIGHT_ABSORB": [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)],
    "bPAWN_STOP": [(1, 0)],
    "wPAWN_STOP": [(-1, 0)],
}


def ability_info(name: str, use_count: int, ability_range: list, action: str, all_cells: bool, image: str):
    return {"NAME": name, "USE_COUNT": use_count, "RANGE": ability_range,  # получение словаря для описания способности
            "ACTION": action, "ALL_CELLS": all_cells, "IMAGE": ABILITY_DIR + image, }


ABILITIES = {
    "QUEEN_CARRY": ability_info("Перенос", 1, ABILITY_RANGE["QUEEN_CARRY"], "CARRY", True, "Piece_Carry.png"),
    "QUEEN_SHIELD": ability_info("Щит", 1, ABILITY_RANGE["QUEEN_SHIELD"], "SHIELD", True, "Piece_Shield.png"),
    "ROOK_PIERCE": ability_info("Пронзание", 1, ABILITY_RANGE["ROOK_PIERCE"], "PIERCE", False, "Piece_Pierce.png"),
    "BISHOP_REPLACE": ability_info("Замена", 1, ABILITY_RANGE["BISHOP_REPLACE"], "REPLACE", False, "Piece_Replace.png"),
    "KNIGHT_ABSORB": ability_info("Поглощение", 1, ABILITY_RANGE["KNIGHT_ABSORB"], "ABSORB", True, "Piece_Absorb.png"),
    "bPAWN_STOP": ability_info("Остановка", 1, ABILITY_RANGE["bPAWN_STOP"], "STOP", True, "Piece_Stop.png"),
    "wPAWN_STOP": ability_info("Остановка", 1, ABILITY_RANGE["wPAWN_STOP"], "STOP", True, "Piece_Stop.png"),
}

PIECE_ABILITIES = {
    "wQ": "QUEEN_CARRY", "bQ": "QUEEN_CARRY",
    "wR": "ROOK_PIERCE", "bR": "ROOK_PIERCE",
    "wB": "BISHOP_REPLACE", "bB": "BISHOP_REPLACE",
    "wN": "KNIGHT_ABSORB", "bN": "KNIGHT_ABSORB",
    "wP": "wPAWN_STOP", "bP": "bPAWN_STOP",
}

ABILITY_DESCRIPTION = {
    "Остановка": "Блокирует действия ВСЕХ ВРАЖЕСКИХ фигур \nв радиусе действия на 1 ход",
    "Перенос": "Отражает зеркально позиции ВСЕХ фигур в радиусе \nдействия относительно позиции выбранной фигуры",
    "Рывок": "Фигура перемещается на выбранную координату \nсогласно правилам. Ход продолжается.",
    "Поглощение": "Фигура уничтожает ВСЕ фигуры в радиусе \nдействия, жертвуя собой.",
    "Пронзание": "Фигура уничтожает ВРАЖЕСКУЮ фигуру, стоящую\n на выбранной координате, оставаясь на месте.",
    "Замена": "Фигура меняется местами с ЛЮБОЙ фигурой, \nстоящей на выбранной координате.",
    "Щит": "Защищает фигуру на 1 ход и все фигуры этого же\nцвета в радиусе на 2 хода"
}


def update_abilities():
    global PIECE_ABILITIES
    PIECE_ABILITIES = {
        "wQ": "QUEEN_CARRY", "bQ": "QUEEN_CARRY",
        "wR": "ROOK_PIERCE", "bR": "ROOK_PIERCE",
        "wB": "BISHOP_REPLACE", "bB": "BISHOP_REPLACE",
        "wN": "KNIGHT_ABSORB", "bN": "KNIGHT_ABSORB",
        "wP": "wPAWN_STOP", "bP": "bPAWN_STOP",
    }


def get_ability(color_char: str):  # возвращение соответствующей фигуре способности
    return ABILITIES[PIECE_ABILITIES[color_char]]


def opponent(color: int):  # возвращение противоположного цвета
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row: int, col: int):  # проверка правильности координат
    return 0 <= row < 8 and 0 <= col < 8


def print_board(board: list):  # вывод элементов класса Board
    for row in range(7, -1, -1):
        for col in range(8):
            print(board.cell(row, col), end=' ')
        print()
