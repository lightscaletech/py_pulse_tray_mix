from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QSlider,
                             QHBoxLayout, QVBoxLayout)

class Slider(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        slider = QSlider(Qt.Vertical, self)
        layout = QVBoxLayout()
        layout.addWidget(slider)
        self.setLayout(layout)
