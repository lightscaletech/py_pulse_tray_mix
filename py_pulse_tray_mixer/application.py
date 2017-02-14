from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from py_pulse_tray_mixer import pulse
from py_pulse_tray_mixer.windowMixer import MixerWindow
from py_pulse_tray_mixer.trayicon import TrayIcon

class Application(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)

        self.trayIcon = TrayIcon()
        self.paMl = pulse.PulseMainloop(self)
        self.pa = pulse.Pulse(self.paMl)
        self.mixWin = MixerWindow(self.paMl, self.pa, self.trayIcon)
        self.setQuitOnLastWindowClosed(False)

        self.trayIcon.activated.connect(self.mixWin.toggle)

    def __del__(self):
        self.paMl.stop()
        del self.mixWin
        del self.trayIcon
