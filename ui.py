# vtc/ui.py
import sys
import time
import os

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

from config import Calibration, GPIOPins, Runtime
from dac_uldaq import DacULDAQ
from safety_gpio import SafetyController
import waveform as wf
from logging_utils import CSVLogger
from export_utils import list_usb_mounts, export_files


class VTCApp:
    """
    Main Qt application for the Vibration Table Controller.

    Responsibilities:
    - Connect to the MCC USB-1208FS-Plus (AO for drive, AI for feedback)
    - Provide waveform selection and parameter controls
    - Implement a simple safety state machine (MUTED / ARMED / RUNNING)
    - Plot command vs measured voltage in real time
    - Log data to CSV and export CSV + plot PNG to a USB drive
    """

    def __init__(self):
        # One QApplication for the whole program
        self.app = QtWidgets.QApplication(sys.argv)

        # Config / calibration
        self.cal = Calibration()
        self.gpio = GPIOPins()
        self.rt = Runtime()

        # Hardware interfaces
        # Assumes dac_uldaq.DacULDAQ has AO + AI (with .write() and .read())
        self.dac = DacULDAQ()  # uses defaults: AO0 / AI0
        self.dac.connect()

        # Safety controller (may be GPIO-based, or a software stub)
        self.safety = SafetyController(
            estop_pin=self.gpio.ESTOP_PIN,
            mute_pin=self.gpio.MUTE_PIN,
        )

        # Logging
        self.logger = CSVLogger(self.rt.LOG_PATH)

        # Timebase
        self.sample_hz = int(self.rt.SAMPLE_HZ)
        self.dt = 1.0 / max(self.sample_hz, 1)
        self.t0 = None

        # State
        self.running = False
        self.last_t = 0.0

        # Data buffers for plot
        self.xdata = []
        self.ycmd = []
        self.ymeas = []
        self.max_points = 3000

        # Build UI
        self._build_ui()

        # Timer for real-time updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(int(1000 * self.dt))

    # UI layout

    def _build_ui(self):
        self.win = QtWidgets.QMainWindow()
        self.win.setWindowTitle("Vibration Table Controller")
        self.win.resize(1024, 600)

        central = QtWidgets.QWidget()
        self.win.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)

        # Top bar: safety and status
        top_bar = QtWidgets.QHBoxLayout()

        self.lbl_status = QtWidgets.QLabel("Status: INIT")
        self.lbl_status.setMinimumWidth(180)
        self.lbl_status.setStyleSheet("font-weight: bold;")

        self.btn_arm = QtWidgets.QPushButton("ARM")
        self.btn_mute = QtWidgets.QPushButton("MUTE")
        self.btn_arm.setMinimumHeight(40)
        self.btn_mute.setMinimumHeight(40)

        self.btn_arm.clicked.connect(self._on_arm)
        self.btn_mute.clicked.connect(self._on_mute)

        self.lbl_fault = QtWidgets.QLabel("Fault: --")
        self.lbl_fault.setMinimumWidth(140)

        top_bar.addWidget(self.lbl_status)
        top_bar.addWidget(self.btn_arm)
        top_bar.addWidget(self.btn_mute)
        top_bar.addWidget(self.lbl_fault)
        top_bar.addStretch(1)

        layout.addLayout(top_bar)

        # Waveform controls
        controls = QtWidgets.QGridLayout()

        row = 0

        # Mode
        controls.addWidget(QtWidgets.QLabel("Mode:"), row, 0)
        self.cmb_mode = QtWidgets.QComboBox()
        self.cmb_mode.addItems([
            "Manual",
            "Sine",
            "Sine Sweep",
            "Random Noise",
            "Sine on Random",
            "Resonance Dwell",
            "Shock",
        ])
        controls.addWidget(self.cmb_mode, row, 1, 1, 2)
        row += 1

        # Manual value
        self.lbl_manual = QtWidgets.QLabel("Manual V:")
        self.spin_manual = QtWidgets.QDoubleSpinBox()
        self.spin_manual.setRange(0.0, 5.0)
        self.spin_manual.setSingleStep(0.1)
        self.spin_manual.setValue(2.5)
        controls.addWidget(self.lbl_manual, row, 0)
        controls.addWidget(self.spin_manual, row, 1)
        row += 1

        # Common sine parameters
        self.lbl_amp = QtWidgets.QLabel("Amplitude (V):")
        self.spin_amp = QtWidgets.QDoubleSpinBox()
        self.spin_amp.setRange(0.0, 5.0)
        self.spin_amp.setSingleStep(0.1)
        self.spin_amp.setValue(2.0)

        self.lbl_freq = QtWidgets.QLabel("Frequency (Hz):")
        self.spin_freq = QtWidgets.QDoubleSpinBox()
        self.spin_freq.setRange(0.01, 200.0)
        self.spin_freq.setSingleStep(0.1)
        self.spin_freq.setValue(10.0)

        self.lbl_dc = QtWidgets.QLabel("DC Offset (V):")
        self.spin_dc = QtWidgets.QDoubleSpinBox()
        self.spin_dc.setRange(0.0, 5.0)
        self.spin_dc.setSingleStep(0.1)
        self.spin_dc.setValue(2.5)

        controls.addWidget(self.lbl_amp, row, 0)
        controls.addWidget(self.spin_amp, row, 1)
        controls.addWidget(self.lbl_freq, row, 2)
        controls.addWidget(self.spin_freq, row, 3)
        row += 1

        controls.addWidget(self.lbl_dc, row, 0)
        controls.addWidget(self.spin_dc, row, 1)
        row += 1

        # Sweep-specific
        self.lbl_fstart = QtWidgets.QLabel("Sweep f_start (Hz):")
        self.spin_fstart = QtWidgets.QDoubleSpinBox()
        self.spin_fstart.setRange(0.01, 200.0)
        self.spin_fstart.setSingleStep(0.1)
        self.spin_fstart.setValue(0.5)

        self.lbl_fend = QtWidgets.QLabel("Sweep f_end (Hz):")
        self.spin_fend = QtWidgets.QDoubleSpinBox()
        self.spin_fend.setRange(0.01, 200.0)
        self.spin_fend.setSingleStep(0.1)
        self.spin_fend.setValue(50.0)

        self.lbl_dur = QtWidgets.QLabel("Sweep duration (s):")
        self.spin_dur = QtWidgets.QDoubleSpinBox()
        self.spin_dur.setRange(0.1, 300.0)
        self.spin_dur.setSingleStep(0.5)
        self.spin_dur.setValue(10.0)

        controls.addWidget(self.lbl_fstart, row, 0)
        controls.addWidget(self.spin_fstart, row, 1)
        controls.addWidget(self.lbl_fend, row, 2)
        controls.addWidget(self.spin_fend, row, 3)
        row += 1

        controls.addWidget(self.lbl_dur, row, 0)
        controls.addWidget(self.spin_dur, row, 1)
        row += 1

        # Noise / shock params
        self.lbl_noise = QtWidgets.QLabel("Noise std (V):")
        self.spin_noise = QtWidgets.QDoubleSpinBox()
        self.spin_noise.setRange(0.0, 2.0)
        self.spin_noise.setSingleStep(0.05)
        self.spin_noise.setValue(0.2)

        self.lbl_t0 = QtWidgets.QLabel("Shock t0 (s):")
        self.spin_t0 = QtWidgets.QDoubleSpinBox()
        self.spin_t0.setRange(0.0, 30.0)
        self.spin_t0.setSingleStep(0.1)
        self.spin_t0.setValue(1.0)

        self.lbl_peak = QtWidgets.QLabel("Shock peak (V):")
        self.spin_peak = QtWidgets.QDoubleSpinBox()
        self.spin_peak.setRange(0.0, 5.0)
        self.spin_peak.setSingleStep(0.1)
        self.spin_peak.setValue(4.5)

        self.lbl_tau = QtWidgets.QLabel("Shock tau (s):")
        self.spin_tau = QtWidgets.QDoubleSpinBox()
        self.spin_tau.setRange(0.001, 5.0)
        self.spin_tau.setSingleStep(0.01)
        self.spin_tau.setValue(0.02)

        controls.addWidget(self.lbl_noise, row, 0)
        controls.addWidget(self.spin_noise, row, 1)
        controls.addWidget(self.lbl_t0, row, 2)
        controls.addWidget(self.spin_t0, row, 3)
        row += 1

        controls.addWidget(self.lbl_peak, row, 0)
        controls.addWidget(self.spin_peak, row, 1)
        controls.addWidget(self.lbl_tau, row, 2)
        controls.addWidget(self.spin_tau, row, 3)
        row += 1

        layout.addLayout(controls)

        # Start/stop and export buttons
        btn_row = QtWidgets.QHBoxLayout()

        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")
        self.btn_export = QtWidgets.QPushButton("Export to USB")

        self.btn_start.setMinimumHeight(40)
        self.btn_stop.setMinimumHeight(40)
        self.btn_export.setMinimumHeight(40)

        self.btn_start.clicked.connect(self._on_start)
        self.btn_stop.clicked.connect(self._on_stop)
        self.btn_export.clicked.connect(self._on_export)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addWidget(self.btn_export)
        btn_row.addStretch(1)

        layout.addLayout(btn_row)

        # Plot area
        self.plot = pg.PlotWidget()
        self.plot.setLabel("bottom", "Time", units="s")
        self.plot.setLabel("left", "Voltage", units="V")
        self.plot.showGrid(x=True, y=True, alpha=0.3)

        # Two curves: command and measured
        self.curve_cmd = self.plot.plot(pen=pg.mkPen(width=2))
        self.curve_meas = self.plot.plot(
            pen=pg.mkPen(style=QtCore.Qt.DashLine, width=2)
        )

        legend = self.plot.addLegend(offset=(10, 10))
        legend.addItem(self.curve_cmd, "Command (V)")
        legend.addItem(self.curve_meas, "Measured (V)")

        layout.addWidget(self.plot, stretch=1)

        # Measurements label
        self.lbl_meas = QtWidgets.QLabel("Meas: 0.000 V, 0.000 g")
        layout.addWidget(self.lbl_meas)

        # Initialize state labels
        self._update_status_labels()

    # Event handlers

    def _on_arm(self):
        status = self.safety.arm()
        if status == "ARMED":
            self._set_status("ARMED")
        else:
            # Could not arm, probably because of external fault
            self._set_status("FAULT")
        self._update_status_labels()

    def _on_mute(self):
        self.safety.mute()
        self.running = False
        self._set_status("MUTED")
        self._update_status_labels()

    def _on_start(self):
        # Only allow if armed and no fault
        if self.safety.is_fault():
            self._set_status("FAULT")
        else:
            self.running = True
            self.t0 = time.time()
            self._set_status("RUNNING")
        self._update_status_labels()

    def _on_stop(self):
        self.running = False
        self.dac.write(0.0)
        if getattr(self.safety, "armed", False):
            self._set_status("ARMED")
        else:
            self._set_status("MUTED")
        self._update_status_labels()

    def _on_export(self):
        """
        Export current CSV log and a PNG screenshot of the plot
        to a selected USB mount.
        """
        mounts = list_usb_mounts()
        if not mounts:
            QtWidgets.QMessageBox.warning(
                self.win,
                "Export",
                "No USB mount points found. Is a drive plugged in?",
            )
            return

        item, ok = QtWidgets.QInputDialog.getItem(
            self.win, "Select USB mount", "Mount point:", mounts, 0, False
        )
        if not ok or not item:
            return

        dest = item

        # Save a PNG screenshot of the plot to the log folder
        png_path = os.path.splitext(self.logger.path)[0] + ".png"
        pixmap = self.plot.grab()
        pixmap.save(png_path)

        exported = export_files(dest, [self.logger.path, png_path])

        QtWidgets.QMessageBox.information(
            self.win, "Export", f"Exported {len(exported)} file(s) to {dest}"
        )

    # Core update loop

    def _update(self):
        # Safety fault check
        fault = self.safety.is_fault()
        self.lbl_fault.setText(f"Fault: {'YES' if fault else 'NO'}")

        if fault:
            # Hard mute if fault occurs
            self.running = False
            self.dac.write(0.0)
            self._set_status("FAULT")
            self._update_status_labels()
            return

        if not self.running:
            # Ensure output is muted when not running
            self.dac.write(0.0)
            return

        if self.t0 is None:
            self.t0 = time.time()

        t = time.time() - self.t0
        self.last_t = t

        # Determine command voltage from selected waveform
        mode = self.cmb_mode.currentText()
        cmd_v = self._compute_cmd_voltage(mode, t)

        # Apply DAC calibration
        out_v = self.cal.DAC_OFFSET + self.cal.DAC_SCALE * cmd_v

        # Clamp in software to 0–5 V (MCC UNI5VOLTS)
        out_v = max(0.0, min(5.0, out_v))

        # Send to hardware
        try:
            self.dac.write(out_v)
        except Exception:
            # If something goes wrong, stop output
            self.running = False
            self._set_status("ERROR")
            self._update_status_labels()
            return

        # Read measurement from MCC AI through ADAM-3017
        meas_v = 0.0
        try:
            raw_v = self.dac.read()
            meas_v = raw_v * self.cal.ADC_SCALE
        except Exception:
            pass

        meas_g = meas_v * self.cal.G_PER_V

        # Append to buffers
        self.xdata.append(t)
        self.ycmd.append(out_v)
        self.ymeas.append(meas_v)

        if len(self.xdata) > self.max_points:
            self.xdata = self.xdata[-self.max_points:]
            self.ycmd = self.ycmd[-self.max_points:]
            self.ymeas = self.ymeas[-self.max_points:]

        # Update plot
        self.curve_cmd.setData(self.xdata, self.ycmd)
        self.curve_meas.setData(self.xdata, self.ymeas)

        # Update measurement label
        self.lbl_meas.setText(f"Meas: {meas_v:.3f} V, {meas_g:.3f} g")

        # Log
        self.logger.write(t, out_v, meas_v)

    # Helpers

    def _compute_cmd_voltage(self, mode: str, t: float) -> float:
        """Return uncalibrated command voltage based on mode and time."""
        dc = self.spin_dc.value()
        amp = self.spin_amp.value()
        freq = self.spin_freq.value()

        if mode == "Manual":
            return wf.manual(self.spin_manual.value())

        if mode == "Sine":
            return wf.sine(t, amp=amp, freq_hz=freq, dc=dc)

        if mode == "Sine Sweep":
            return wf.sine_sweep(
                t,
                amp=amp,
                f_start=self.spin_fstart.value(),
                f_end=self.spin_fend.value(),
                dur=self.spin_dur.value(),
                dc=dc,
            )

        if mode == "Random Noise":
            return wf.random_noise(dc=dc, std=self.spin_noise.value())

        if mode == "Sine on Random":
            return wf.sine_on_random(
                t,
                amp_sine=amp,
                freq_hz=freq,
                dc=dc,
                rand_std=self.spin_noise.value(),
            )

        if mode == "Resonance Dwell":
            return wf.resonance_dwell(t, amp=amp, freq_hz=freq, dc=dc)

        if mode == "Shock":
            return wf.shock(
                t,
                t0=self.spin_t0.value(),
                peak=self.spin_peak.value(),
                dc=dc,
                tau=self.spin_tau.value(),
            )

        # Fallback
        return wf.manual(dc)

    def _set_status(self, status: str):
        self._status = status

    def _update_status_labels(self):
        status = getattr(self, "_status", "INIT")
        self.lbl_status.setText(f"Status: {status}")

    # Main entry point

    def run(self):
        try:
            self.win.show()
            self.app.exec_()
        finally:
            try:
                self.dac.write(0.0)
            except Exception:
                pass
            try:
                self.dac.close()
            except Exception:
                pass
            try:
                self.logger.close()
            except Exception:
                pass


if __name__ == "__main__":
    app = VTCApp()
    app.run()
