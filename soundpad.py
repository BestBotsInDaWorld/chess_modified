from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

SOUND_DIR = 'pieces/piece_sounds/'


def get_content(path):
    return QMediaContent(QUrl.fromLocalFile(SOUND_DIR + path))


PIECE_SOUNDS = {
    "VICTORY": get_content("chess_victory.mp3"),
    "MOVE": get_content("chess_move.mp3"),
    "funny": get_content("funny.mp3")
}

SOUNDPAD = QMediaPlayer()
SOUNDPAD_FUN = QMediaPlayer()
def play_sound(action, param=0):
    if param:
        SOUNDPAD_FUN.setMedia(PIECE_SOUNDS[action])
        SOUNDPAD_FUN.play()
    else:
        SOUNDPAD.setMedia(PIECE_SOUNDS[action])
        SOUNDPAD.play()
