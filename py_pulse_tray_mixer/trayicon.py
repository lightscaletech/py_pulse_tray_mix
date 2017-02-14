import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon

class TrayIcon(QSystemTrayIcon):

    class Possition:
        TOP    = 1
        LEFT   = 2
        BOTTOM = 4
        RIGHT  = 8
        MASK   = 16

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
