from PyQt5 import uic
import sys
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import QApplication, QWidget


class Leaderboards(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("leaderboards.ui", self)
        self.initUI()

    def initUI(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('games.sqlite')
        db.open()
        model = QSqlTableModel(self, db)
        model.setTable('rounds')
        model.select()
        self.leaderView.setModel(model)
        self.back_to_menu_btn.clicked.connect(self.close)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Leaderboards()
    ex.show()
    sys.exit(app.exec())
