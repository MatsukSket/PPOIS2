import sys
from PySide6.QtWidgets import QApplication

from src.model import DatabaseModel
from src.view import MainWindow
from src.controller import Controller

if __name__ == "__main__":
    app = QApplication(sys.argv)

    model = DatabaseModel('students.db')
    view = MainWindow()
    controller = Controller(model, view)

    view.show()
    sys.exit(app.exec())