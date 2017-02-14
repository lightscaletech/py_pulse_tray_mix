from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QSlider,
                             QPushButton, QHBoxLayout, QVBoxLayout)
from py_pulse_tray_mixer import pulse

class Slider(QWidget):

    shown = pyqtSignal()
    mute = pyqtSignal(bool)
    volumeChange = pyqtSignal(int)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.volMouseDown = False

        self.control = QSlider(Qt.Vertical, self)
        self.control.valueChanged.connect(
            lambda val, fun=self.volumeChange.emit:
            self.volMouseDown and fun(val))
        self.control.sliderPressed.connect(self.volumeMouseDown)
        self.control.sliderReleased.connect(self.volumeMouseUp)

        self.icon = QLabel('Icon', self)
        self.title = QLabel('Title', self)
        self.muteBtn = QPushButton('M', self)
        self.muteBtn.setMaximumWidth(20)
        self.muteBtn.setCheckable(True)
        self.muteBtn.clicked.connect(self.mute.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.icon)
        layout.addWidget(self.control)
        layout.addWidget(self.title)

        botLayout = QHBoxLayout()
        botLayout.addWidget(self.muteBtn)

        layout.addLayout(botLayout)
        self.setLayout(layout)
        self.control.setMinimum(pulse.VOLUME_MIN)
        self.control.setMaximum(pulse.VOLUME_NORM)

    def setIcon(self, p):
        pix = QPixmap(p)
        pix = pix.scaledToWidth(38)
        self.icon.setPixmap(pix)

    def showEvent(self, event):
        self.shown.emit()

    def volumeMouseDown(self):
        QApplication.processEvents()
        self.volMouseDown = True

    def volumeMouseUp(self):
        QApplication.processEvents()
        self.volMouseDown = False

    def setVolume(self, val):
        if self.volMouseDown == False:
            self.control.setValue(val)

    def setMuted(self, val): self.muteBtn.setChecked(val)
