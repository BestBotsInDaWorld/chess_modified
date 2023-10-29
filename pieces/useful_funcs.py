WHITE = 1
BLACK = 2
color = WHITE

COLORING = {'b': BLACK, 'w': WHITE, }

COLORING_REVERSE = {BLACK: 'b', WHITE: 'w', }

IMAGE_DIR = 'pieces/piece_images/'

SOUND_DIR = 'pieces/piece_sounds/'

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

ABILITY_RANGES = {
    "QUEEN_CARRY": [(0, -2), (0, 2), (-2, 0), (2, 0),
                    (-1, -1), (-1, 1), (1, -1), (1, 1),
                    (0, -1), (0, 1), (-1, 0), (1, 0)],
    "ROOK_PIERCE": [(0, i) for i in range(-3, 4)] + [(i, 0) for i in range(-3, 4)],
    "BISHOP_DASH": "NORMAL",
    "KNIGHT_ABSORB": [(2, 1), (2, -1), (1, 2), (1, -2), (-2, 1), (-2, -1), (-1, 2), (-1, -2)],
    "bPAWN_STOP": [(0, 1)],
    "wPAWN_STOP": [(0, -1)],
}


def opponent(color):
    if color == WHITE:
        return BLACK
    return WHITE


def correct_coords(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def print_board(board):
    for row in range(7, -1, -1):
        for col in range(8):
            print(board.cell(row, col), end=' ')
        print()
