import os
from PyQt5 import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QSystemTrayIcon,
                             QDesktopWidget, QHBoxLayout)
from py_pulse_tray_mixer import slider
from py_pulse_tray_mixer import pulse
from py_pulse_tray_mixer import icon

class Application(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)

        self.trayIcon = TrayIcon()
        self.paMl = pulse.PulseMainloop(self)
        self.pa = pulse.Pulse(self.paMl)
        self.mixWin = MixerWindow(self.paMl, self.pa, self.trayIcon)

        self.trayIcon.activated.connect(self.mixWin.toggle)

    def __del__(self):
        self.paMl.stop()
        del self.mixWin
        del self.trayIcon


class MixerWindow(QWidget):

    sinks = {}
    inputs = {}

    def __init__(self, ml, pa, trayicon, parent=None):
        QWidget.__init__(self, parent, Qt.Qt.Dialog | Qt.Qt.FramelessWindowHint)
        self.trayicon = trayicon
        self.ml = ml
        self.setWindowTitle("Mixer")
        self.icoFinder = icon.IconFinder([icon.CONTEXT_APPLICATION,
                                          icon.CONTEXT_DEVICE])

        pa.input_manager.added.connect(self.input_new)
        pa.input_manager.changed.connect(self.input_update)
        pa.input_manager.removed.connect(self.input_removed)

        pa.sink_manager.added.connect(self.sink_new)
        pa.sink_manager.changed.connect(self.sink_update)
        pa.sink_manager.removed.connect(self.sink_removed)

        self.sinkLayout = QHBoxLayout()
        self.inputLayout = QHBoxLayout()

        layout = QHBoxLayout()
        layout.addLayout(self.inputLayout)
        layout.addLayout(self.sinkLayout)

        self.setLayout(layout)

        self.redoGeom()

    def redoGeom(self):
        self.resize()
        self.reposition()

    def resize(self):
        self.setMaximumHeight(300)
        self.setMinimumHeight(300)
        self.updateGeometry()

    def reposition(self):
        pos = self.trayicon.getPos()
        iconRect = self.trayicon.geometry()
        screenRect = QApplication.desktop().screenGeometry()
        rect = self.rect()
        if (pos & TrayIcon.Possition.RIGHT) > 0:
            rect.setX(screenRect.width() - rect.right() - 5)
        if (pos & TrayIcon.Possition.LEFT) > 0:
            rect.setX(screenRect.left())

        if (pos & TrayIcon.Possition.TOP) > 0:
            rect.setY(screenRect.top() + iconRect.bottom())
        if (pos & TrayIcon.Possition.BOTTOM) > 0:
            rect.setY(screenRect.bottom() - iconRect.height() - rect.height() - 10)

        self.move(rect.topLeft())

    def toggle(self):
        if self.isVisible():
            self.hide()
            self.ml.stop()
        else:
            self.ml.start()
            self.show()
            self.redoGeom()

    def sink_new(self, item):
        s = slider.Slider(self)
        s.shown.connect(self.redoGeom)
        icoPath = self.icoFinder.find_icon(icon.CONTEXT_DEVICE, item.icon)
        print(icoPath)
        if icoPath is None:
            icoPath = self.icoFinder.find_icon(icon.CONTEXT_DEVICE, 'audio-card')
        s.setIcon(icoPath)
        s.title.setText(item.title)
        self.sinks[item.index] = s
        self.sinkLayout.addWidget(s)

    def sink_update(self, item):
        pass

    def sink_removed(self, id):
        del self.sinks[id]

    def input_new(self, item):
        s = slider.Slider(self)
        s.title.setText(item.name)
        icoPath = self.icoFinder.find_icon(icon.CONTEXT_APPLICATION, item.icon)
        if icoPath is None:
            icoPath = self.icoFinder.find_icon(icon.CONTEXT_DEVICE, 'audio-card')
        s.setIcon(icoPath)
        self.inputs[item.index] = s
        self.inputLayout.addWidget(s)
        self.redoGeom()

    def input_update(self, item):
        pass

    def input_removed(self, id):
        del self.inputs[id]

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
