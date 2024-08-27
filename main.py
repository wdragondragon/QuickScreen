import sys

from PyQt5.QtWidgets import QApplication

from screen.HotKey import HotKey
from screen.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    hot_key = HotKey()
    hot_key.ShowWindow.connect(main.open_screen)
    hot_key.start()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
