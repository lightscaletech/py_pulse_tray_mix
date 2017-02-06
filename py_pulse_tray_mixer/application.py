import os
from PyQt5 import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon,
                             QDesktopWidget)

class Application(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.trayIcon = TrayIcon()
        self.mixWin = MixerWindow(self.trayIcon)

        self.trayIcon.activated.connect(self.mixWin.toggle)

    def __del__(self):
        del self.trayIcon
        del self.mixWin

class MixerWindow(QWidget):
    def __init__(self, trayicon, parent=None):
        QWidget.__init__(self, parent, Qt.Qt.Dialog | Qt.Qt.FramelessWindowHint)
        self.trayicon = trayicon
        self.setWindowTitle("Mixer")

    def reposition(self):
        pos = self.trayicon.getPos()
        print(pos)
        pass

    def toggle(self):
        if self.isVisible(): self.hide()
        else:
            self.reposition()
            self.show()

class TrayIcon(QSystemTrayIcon):

    class Possition:
        TOP    = 1
        LEFT   = 2
        BOTTOM = 4
        RIGHT  = 8

    def __init__(self, parent=None):
        icon = QIcon(os.path.dirname(__file__) + '/../img/trayicon.png')
        QSystemTrayIcon.__init__(self, icon, parent)
        self.show()

    def getPos(self):
        screenRect = QApplication.desktop().screenGeometry()
        iconRect = self.geometry()
        hheight = screenRect.height() / 2
        hwidth = screenRect.width() / 2
        iconX = iconRect.x()
        iconY = iconRect.y()
        res = 0
        if iconX < hwidth: res |= self.Possition.LEFT
        else: res |= self.Possition.RIGHT
        if iconY < hheight: res |= self.Possition.TOP
        else: res |= self.Possition.BOTTOM
        return res
