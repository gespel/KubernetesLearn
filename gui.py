from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit

import sys

import core


class MainWindow(QMainWindow):
    def __init__(self, core: core.StensKubernetes):
        super().__init__()
        self.core = core

        self.setWindowTitle("SKubeCtrl")

        button = QPushButton("Create yml", self)
        button2 = QPushButton("start job", self)
        button.pressed.connect(self.easy_yml)
        button2.pressed.connect(self.create_debian_job)
        clearjob_button = QPushButton("clear jobs", self)
        clearjob_button.pressed.connect(self.clear_jobs)

        self.inputbox = QLineEdit(self)

        button.setGeometry(10, 10, 100, 50)
        button2.setGeometry(10, 60, 100, 50)
        clearjob_button.setGeometry(10, 110, 100, 50)
        self.inputbox.setGeometry(120, 60, 100, 50)

        self.show()

    def easy_yml(self):
        print(self.core.create_easy_yml("asd"))

    def create_debian_job(self):
        imagename = self.inputbox.text()
        self.inputbox.setText("")
        self.core.create_job_and_execute_command("gui", imagename, [["echo", "Hello World"]])

    def clear_jobs(self):
        self.core.delete_all_local_jobs()


def start_gui(core: core.StensKubernetes):
    app = QApplication(sys.argv)
    w = MainWindow(core)
    w.setFixedSize(350, 200)
    app.exec()
