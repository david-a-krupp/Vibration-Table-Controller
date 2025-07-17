# gui.py
from PyQt5 import QtWidgets, QtCore
from waveform import sine, sweep

class MainWindow(QtWidgets.QWidget):
    run_signal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        # ... interface with freq, amp, duration, run button
        # on run: self.run_signal.emit({'mode':'sine', 'f':..., 'amp':..., ...})
