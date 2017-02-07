from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QSlider, QButton,
                             QHBoxLayout, QVBoxLayout)

class Slider(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(parent)
        slider = QWidget(Qt.Vertical, self)
        layout = QVBoxLayout()
        self.setLayout(layout)
