# vtc/ui.py
import sys, time, os
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
from .config import Calibration, GPIOPins, Runtime
from .dac_uldaq import DacULDAQ
from .adc_ads1115 import ADSReader
from .safety_gpio import SafetyController
from . import waveform as wf
from .logging_utils import CSVLogger
from .export_utils import list_usb_mounts, export_files

class VTCApp:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # Touch font scaling for 7" display
        f = self.app.font()
        f.setPointSize(12)
        self.app.setFont(f)

        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle("Vibration Table Controller")
        self.win.resize(1200, 720)

        self.cal = Calibration()
        self.gpio = GPIOPins()
        self.rt  = Runtime()

        # Core devices
        self.safety = SafetyController(estop_pin=self.gpio.ESTOP_PIN, mute_pin=self.gpio.MUTE_PIN)
        self.dac = DacULDAQ()
        self.dac.connect()
        self.adc = ADSReader(differential=False, pga=1, v_scale=self.cal.ADC_SCALE)

        # State
        self.mode = "Manual"
        self.t0 = time.time()
        self.logger = CSVLogger(folder=self.rt.LOG_PATH)

        # UI
        central = QtWidgets.QWidget()
        self.win.setCentralWidget(central)
        layout = QtWidgets.QGridLayout(central)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        # Controls
        self.modeBox = QtWidgets.QComboBox()
        self.modeBox.addItems(["Manual", "Sine", "SineSweep", "Random", "SoR", "Dwell", "Shock"])
        self.armBtn = QtWidgets.QPushButton("ARM")
        self.muteBtn = QtWidgets.QPushButton("MUTE")
        self.exportBtn = QtWidgets.QPushButton("Export")
        self.fullscreenChk = QtWidgets.QCheckBox("Full-screen")

        for btn in (self.armBtn, self.muteBtn, self.exportBtn):
            btn.setMinimumHeight(40)

        self.cmdSpin = QtWidgets.QDoubleSpinBox(); self.cmdSpin.setRange(-5.0, 5.0); self.cmdSpin.setSingleStep(0.1); self.cmdSpin.setValue(0.0)
        self.ampSpin = QtWidgets.QDoubleSpinBox(); self.ampSpin.setRange(0.0, 2.5); self.ampSpin.setValue(1.0)
        self.freqSpin = QtWidgets.QDoubleSpinBox(); self.freqSpin.setRange(0.01, 200.0); self.freqSpin.setValue(1.0)
        self.statusLbl = QtWidgets.QLabel("Status: MUTED")

        layout.addWidget(QtWidgets.QLabel("Mode"), 0,0); layout.addWidget(self.modeBox,0,1)
        layout.addWidget(self.armBtn,0,2); layout.addWidget(self.muteBtn,0,3)
        layout.addWidget(self.exportBtn,0,4); layout.addWidget(self.fullscreenChk,0,5)
        layout.addWidget(QtWidgets.QLabel("Manual Cmd / Amp"),1,0); layout.addWidget(self.cmdSpin,1,1); layout.addWidget(self.ampSpin,1,2)
        layout.addWidget(QtWidgets.QLabel("Frequency (Hz)"),2,0); layout.addWidget(self.freqSpin,2,1)
        layout.addWidget(self.statusLbl,2,2,1,4)

        # Plot
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x=True, y=True)
        self.curve_cmd = self.plot.plot(pen=pg.mkPen(width=2))
        self.curve_meas = self.plot.plot(pen=pg.mkPen(style=QtCore.Qt.DashLine))
        layout.addWidget(self.plot,3,0,1,6)

        # Signals
        self.modeBox.currentTextChanged.connect(self._set_mode)
        self.armBtn.clicked.connect(self._arm)
        self.muteBtn.clicked.connect(self._mute)
        self.exportBtn.clicked.connect(self._export_dialog)
        self.fullscreenChk.stateChanged.connect(self._toggle_fullscreen)

        # Timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(int(1000 / 60))  # 60 Hz UI

        self.xdata = []
        self.ycmd  = []
        self.ymeas = []
        self.win.show()

    def _toggle_fullscreen(self, state):
        if state == QtCore.Qt.Checked:
            self.win.showFullScreen()
        else:
            self.win.showNormal()

    def _set_mode(self, m):
        self.mode = m

    def _arm(self):
        res = self.safety.arm()
        self.statusLbl.setText(f"Status: {res}")

    def _mute(self):
        res = self.safety.mute()
        self.statusLbl.setText(f"Status: {res}")

    def _compute_cmd(self, t):
        if self.mode == "Manual":
            return wf.manual(self.cmdSpin.value())
        if self.mode == "Sine":
            return wf.sine(t, amp=self.ampSpin.value(), freq_hz=self.freqSpin.value(), dc=2.5) - 2.5
        if self.mode == "SineSweep":
            return wf.sine_sweep(t, amp=self.ampSpin.value(), f_start=0.5, f_end=50.0, dur=10.0, dc=2.5) - 2.5
        if self.mode == "Random":
            return wf.random_noise(dc=0.0, std=self.ampSpin.value()*0.1)
        if self.mode == "SoR":
            return wf.sine_on_random(t, amp_sine=self.ampSpin.value(), freq_hz=self.freqSpin.value(), dc=0.0, rand_std=0.05)
        if self.mode == "Dwell":
            return wf.resonance_dwell(t, amp=self.ampSpin.value(), freq_hz=self.freqSpin.value(), dc=0.0)
        if self.mode == "Shock":
            return wf.shock(t, t0=1.0, peak=self.ampSpin.value()*2.0, dc=0.0, tau=0.05)
        return 0.0

    def _snapshot_png(self, path):
        # Export current plot to PNG
        exporter = pg.exporters.ImageExporter(self.plot.plotItem)
        exporter.parameters()['width'] = 1200
        exporter.export(path)

    def _export_dialog(self):
        mounts = list_usb_mounts()
        if not mounts:
            QtWidgets.QMessageBox.warning(self.win, "USB Export", "No USB mount detected. Plug in a drive and try again.")
            return
        dest, ok = QtWidgets.QInputDialog.getItem(self.win, "USB Export", "Choose destination mount:", mounts, 0, False)
        if not ok or not dest:
            return
        # Prep files: current CSV and a SS
        png_path = os.path.splitext(self.logger.path)[0] + ".png"
        try:
            # Lazy import to avoid hard dependency until needed
            import pyqtgraph.exporters
            self._snapshot_png(png_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self.win, "Export", f"Plot snapshot failed: {e}")

        files = [self.logger.path]
        if os.path.isfile(png_path):
            files.append(png_path)
        copied = export_files(dest, files)
        QtWidgets.QMessageBox.information(self.win, "Export", f"Exported:
" + "\n".join(copied))

    def _update(self):
        t = time.time() - self.t0

        # Safety
        if self.safety.is_fault():
            self.safety.mute()
            self.statusLbl.setText("Status: FAULT → MUTED")

        # Command
        if self.safety.armed:
            cmd_v = float(self._compute_cmd(t))
            cmd_v = max(-2.5, min(2.5, cmd_v))
            dac_out = 2.5 + cmd_v  # 0–5 V
        else:
            cmd_v = 0.0
            dac_out = 0.0

        # Output
        try:
            self.dac.write(dac_out)
        except Exception as e:
            self.statusLbl.setText(f"Status: DAC ERR {e}")
            self.safety.mute()

        # Measure
        meas_v = 0.0
        try:
            meas_v = self.adc.read_v()
        except Exception:
            pass

        # Log
        try:
            self.logger.write(t, dac_out, meas_v)
        except Exception:
            pass

        # Plot
        self._update_plot(t, dac_out, meas_v)

    def _update_plot(self, t, cmd, meas):
        self.xdata.append(t); self.ycmd.append(cmd); self.ymeas.append(meas)
        if len(self.xdata) > 3000:
            self.xdata = self.xdata[-3000:]
            self.ycmd  = self.ycmd[-3000:]
            self.ymeas = self.ymeas[-3000:]
        self.curve_cmd.setData(self.xdata, self.ycmd)
        self.curve_meas.setData(self.xdata, self.ymeas)

    def run(self):
        try:
            self.win.show()
            self.app.exec_()
        finally:
            try: self.dac.close()
            except Exception: pass
            try: self.logger.close()
            except Exception: pass
