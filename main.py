import sys

from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class MainWindow(QMainWindow):
    """The first widget for Ethel application."""

    def __init__(self) -> None:
        super().__init__()

        text = QLabel("Welcome to Ethel!", alignment=QtCore.Qt.AlignCenter)
        self.setCentralWidget(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())
