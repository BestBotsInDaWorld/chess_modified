from chess import *
from leaderboards import *
from constructor import *
from settings import *
from soundpad import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main_menu.ui", self)
        self.initUI()
        play_sound("funny", 1)

    def initUI(self):
        self.bg.setPixmap(QPixmap(IMAGE_DIR + 'cool_chess.jpg'))
        for i in [self.game_start_btn, self.game_construct_btn, self.game_leaderboards_btn, self.game_exit_btn]:
            i.setIconSize(QSize(50, 50))
        self.game_start_btn.setIcon(QIcon(IMAGE_DIR + BUTTON_IMAGES['GAME']))
        self.game_construct_btn.setIcon(QIcon(IMAGE_DIR + BUTTON_IMAGES['CONSTRUCT']))
        self.game_leaderboards_btn.setIcon(QIcon(IMAGE_DIR + BUTTON_IMAGES['LEADERBOARDS']))
        self.game_exit_btn.setIcon(QIcon(IMAGE_DIR + BUTTON_IMAGES['EXIT']))
        self.game_start_btn.clicked.connect(self.game_settings)
        self.game_construct_btn.clicked.connect(self.game_construct)
        self.game_leaderboards_btn.clicked.connect(self.game_leaderboards)
        self.game_exit_btn.clicked.connect(self.game_exit)

    def game_settings(self):
        self.settings_game = Settings()
        self.settings_game.show()
        self.settings_game.back_to_menu_btn.clicked.connect(self.show)
        self.settings_game.apply_btn.clicked.connect(self.game_start)
        self.hide()

    def game_start(self):
        self.chess_game = Chess()
        update_abilities()
        self.chess_game.show()
        self.chess_game.back_to_menu_btn.clicked.connect(self.show)
        self.chess_game.new_game_btn.clicked.connect(self.game_start)

    def game_construct(self):
        self.constructor_game = Constructor()
        self.constructor_game.show()
        self.constructor_game.back_to_menu_btn.clicked.connect(self.show)
        self.hide()

    def game_leaderboards(self):
        self.leaderboards_game = Leaderboards()
        self.leaderboards_game.show()
        self.leaderboards_game.back_to_menu_btn.clicked.connect(self.show)
        self.hide()

    def game_exit(self):
        valid = QMessageBox.question(
            self, "", "Вы действительно хотите выйти?",
            QMessageBox.Yes, QMessageBox.No)
        if valid == QMessageBox.Yes:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_menu_game = MainMenu()
    main_menu_game.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
