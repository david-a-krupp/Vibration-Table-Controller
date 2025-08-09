# app.py - entry point (sets touch-friendly attributes and launches UI)
from PyQt5 import QtWidgets, QtCore
from vtc.ui import VTCApp
import sys

if __name__ == "__main__":
    # Touch-friendly scaling on Pi 7" display
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = VTCApp()
    app.run()
