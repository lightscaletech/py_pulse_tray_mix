from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QWidget, QLabel, QSlider, QPushButton,
                             QHBoxLayout, QVBoxLayout)

class Slider(QWidget):

    shown = pyqtSignal()

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.control = QSlider(Qt.Vertical, self)
        self.icon = QLabel('Icon', self)
        self.title = QLabel('Title', self)
        self.muteBtn = QPushButton('M', self)
        self.muteBtn.setMaximumWidth(20)

        layout = QVBoxLayout()
        layout.addWidget(self.icon)
        layout.addWidget(self.control)
        layout.addWidget(self.title)

        botLayout = QHBoxLayout()
        botLayout.addWidget(self.muteBtn)

        layout.addLayout(botLayout)
        self.setLayout(layout)

    def setIcon(self, p):
        pix = QPixmap(p)
        self.icon.setPixmap(pix)

    def showEvent(self, event):
        self.shown.emit()
