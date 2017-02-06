import os
from PyQt5 import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon)

class Application(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.trayIcon = TrayIcon()
        self.mixWin = MixerWindow()

        self.trayIcon.activated.connect(self.mixWin.toggle)

    def __del__(self):
        del self.trayIcon
        del self.mixWin

class MixerWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent, Qt.Qt.Dialog | Qt.Qt.FramelessWindowHint)
        self.setWindowTitle("Mixer")
        self.show()

    def toggle(self):
        if self.isVisible(): self.hide()
        else: self.show()

class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = QIcon(os.path.dirname(__file__) + '/../img/trayicon.png')
        QSystemTrayIcon.__init__(self, icon, parent)
        self.show()
