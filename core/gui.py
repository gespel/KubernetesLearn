import os.path
import time

from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit
from PyQt6 import QtGui

import sys
import platform

from core.skubectrl import StensKubernetes


class MainWindow(QMainWindow):
    def __init__(self, core: StensKubernetes):
        super().__init__()
        self.core = core

        self.setWindowTitle("SKubeCtrl")
        self.setWindowIcon(QtGui.QIcon('klogo.png'))
        self.set_app_icon()

        button = QPushButton("Create yml", self)
        button2 = QPushButton("start job", self)
        button_mass_jobs = QPushButton("Start Massjob", self)
        clearjob_button = QPushButton("clear jobs", self)
        button_start_ems = QPushButton("Start EMS", self)

        button.pressed.connect(self.easy_yml)
        button2.pressed.connect(self.create_debian_job)
        button_mass_jobs.pressed.connect(self.mass_jobs)
        clearjob_button.pressed.connect(self.clear_jobs)
        button_start_ems.pressed.connect(self.start_ems)

        self.inputbox = QLineEdit(self)

        button.setGeometry(10, 10, 100, 50)
        button2.setGeometry(10, 60, 100, 50)
        button_mass_jobs.setGeometry(230, 10, 100, 50)
        clearjob_button.setGeometry(10, 110, 100, 50)
        button_start_ems.setGeometry(230, 60, 100, 50)
        self.inputbox.setGeometry(120, 60, 100, 50)

        self.show()

    def easy_yml(self):
        print(self.core.create_easy_yml("asd"))

    def create_debian_job(self):
        imagename = self.inputbox.text()
        try:
            #self.inputbox.setText("")
            self.core.create_job_and_execute_command("gui", imagename, [["echo", "Hello World"]])
        except Exception as e:
            print(e)

    def clear_jobs(self):
        self.core.delete_all_jobs("default")

    def mass_jobs(self):
        for i in range(0, 100):
            self.core.create_job_and_execute_command("gui", "debian:latest", [["echo", "Hello World"]])

    def start_ems(self):
        self.core.execute_yaml_file(os.path.join("kompose_ems", "env-configmap.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "postgres-claim0-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "psicontrol-claim0-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "psicontrol-claim1-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "redis-claim0-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "traefik-claim0-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "traefik-claim1-persistentvolumeclaim.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "postgres-deployment.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "postgres-service.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "redis-deployment.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "traefik-deployment.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "traefik-service.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "psicontrol-deployment.yaml"))
        self.core.execute_yaml_file(os.path.join("kompose_ems", "psicontrol-service.yaml"))

    def set_app_icon(self):
        if platform.system() == 'Windows':
            # Dieser Code ist spezifisch für Windows
            import ctypes
            myappid = 'stenheimbrodt.skuberctrl'  # Eindeutige Anwendungs-ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def start_gui(core: StensKubernetes):
    app = QApplication(sys.argv)
    w = MainWindow(core)
    w.setFixedSize(350, 200)
    app.exec()
