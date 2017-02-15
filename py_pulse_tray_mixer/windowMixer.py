import sip
from PyQt5 import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QSizePolicy, QHBoxLayout,
                             QDesktopWidget)
from py_pulse_tray_mixer import slider
from py_pulse_tray_mixer import icon
from py_pulse_tray_mixer.trayicon import TrayIcon


class MixerWindow(QWidget):

    sinks = {}
    inputs = {}

    def __init__(self, ml, pa, trayicon, parent=None):
        QWidget.__init__(self, parent, Qt.Qt.Dialog | Qt.Qt.FramelessWindowHint)
        self.trayicon = trayicon
        self.ml = ml
        self.pa = pa
        self.setWindowTitle("Mixer")
        self.icoFinder = icon.IconFinder([icon.CONTEXT_APPLICATION,
                                          icon.CONTEXT_DEVICE])
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,
                                       QSizePolicy.Expanding))

        contype = Qt.Qt.BlockingQueuedConnection
        pa.input_manager.added.connect(self.input_new, type=contype)
        pa.input_manager.changed.connect(self.input_update, type=contype)
        pa.input_manager.removed.connect(self.input_removed, type=contype)

        pa.sink_manager.added.connect(self.sink_new, type=contype)
        pa.sink_manager.changed.connect(self.sink_update, type=contype)
        pa.sink_manager.removed.connect(self.sink_removed, type=contype)

        self.sinkLayout = QHBoxLayout()
        self.inputLayout = QHBoxLayout()

        layout = QHBoxLayout()
        layout.addLayout(self.inputLayout)
        layout.addLayout(self.sinkLayout)

        self.setLayout(layout)

        self.redoGeom()

    def redoGeom(self):
        self.widg_resize()
        self.reposition()

    def widg_resize(self):
        self.setMaximumHeight(300)
        self.setMinimumHeight(300)
        QApplication.processEvents()
        self.resize(0,0)
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

    @staticmethod
    def mk_slider_change_slot(index, cb):
        return lambda value, func=cb: cb(index, value)

    def new_item(self, container, layout, item, iconCtx):
        s = slider.Slider(self)
        s.shown.connect(self.redoGeom)
        s.title.setText(item.title)
        s.setVolume(item.volume)
        s.setMuted(item.mute)

        icoPath = self.icoFinder.find_icon(iconCtx, item.icon)
        if icoPath is None:
            icoPath = self.icoFinder.find_icon(icon.CONTEXT_DEVICE, 'audio-card')
        s.setIcon(icoPath)
        container[item.index] = s
        layout.addWidget(s)
        return s

    def remove_item(self, container, layout, index):
        inp = container[index]
        res = self.inputLayout.removeWidget(inp)
        sip.delete(inp)
        del container[index]
        self.redoGeom()

    def update_item(self, container, item):
        container[item.index].setVolume(item.volume)
        container[item.index].setMuted(item.mute)

    def sink_new(self, item):
        index = item.index
        s = self.new_item(self.sinks, self.sinkLayout, item,
                          icon.CONTEXT_DEVICE)

        s.mute.connect(
            self.mk_slider_change_slot(index, self.pa.setSinkMute))
        s.volumeChange.connect(
            self.mk_slider_change_slot(index, self.pa.setSinkVolume))

    def sink_update(self, item): self.update_item(self.sinks, item)

    def sink_removed(self, id):
        self.remove_item(self.sinks, self.sinkLayout, index)

    def input_new(self, item):
        index = item.index
        s = self.new_item(self.inputs, self.inputLayout, item,
                          icon.CONTEXT_APPLICATION)

        s.mute.connect(
            self.mk_slider_change_slot(index, self.pa.setInputMute))
        s.volumeChange.connect(
            self.mk_slider_change_slot(index, self.pa.setInputVolume))

    def input_update(self, item):
        self.update_item(self.inputs, item)

    def input_removed(self, index):
        self.remove_item(self.inputs, self.inputLayout, index)
