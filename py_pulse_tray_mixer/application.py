from PyQt5 import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon, QIcon)

class Application(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.mixWin = MixerWindow()

class MixerWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.Qt.Dialog | Qt.Qt.FramelessWindowHint)
        self.setWindowTitle("Mixer")
        self.show()

class TrayIcon
