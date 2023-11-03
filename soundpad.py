from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

SOUND_DIR = 'pieces/piece_sounds/'


def get_content(path):
    return QMediaContent(QUrl.fromLocalFile(SOUND_DIR + path))


PIECE_SOUNDS = {
    "VICTORY": get_content("chess_victory.mp3"),
    "MOVE": get_content("chess_move.mp3"),
    "CARRY": get_content("chess_carry.mp3"),
    "PIERCE": get_content("chess_pierce.mp3"),
    "REPLACE": get_content("chess_replace.mp3"),
    "STOP": get_content("chess_stop.mp3"),
    "ABSORB": get_content("chess_absorb.mp3"),
    "SHIELD": get_content("chess_shield.mp3"),
    "funny": get_content("funny.mp3"),
}

SOUNDPAD = QMediaPlayer()
SOUNDPAD_FUN = QMediaPlayer()
SOUNDPAD_FUN.setVolume(30)
def play_sound(action, param=0):
    if param:
        SOUNDPAD_FUN.setMedia(PIECE_SOUNDS[action])
        SOUNDPAD_FUN.play()
    else:
        SOUNDPAD.setMedia(PIECE_SOUNDS[action])
        SOUNDPAD.play()
