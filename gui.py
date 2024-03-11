from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton

import sys

import core


class MainWindow(QMainWindow):
    def __init__(self, core: core.StensKubernetes):
        super().__init__()
        self.core = core

        self.setWindowTitle("Hello World")

        button = QPushButton("My simple app.")
        button.pressed.connect(self.easy_yml)

        self.setCentralWidget(button)
        self.show()

    def easy_yml(self):
        print(self.core.create_easy_yml("asd"))


def start_gui(core: core.StensKubernetes):
    app = QApplication(sys.argv)
    w = MainWindow(core)
    app.exec()