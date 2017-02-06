import sys
import signal
from py_pulse_tray_mixer import application

signal.signal(signal.SIGINT, signal.SIG_DFL)

def main():
    app = application.Application(sys.argv)
    app.exec()

main()
