import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import datetime
from adc import read_acceleration
from dac import output_voltage
from logging_utils import DataLogger
from usb_export import export_to_usb
from waveform import generate_waveform

class VibrationControllerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibration Table Controller")
        self.root.attributes("-fullscreen", True)

        self.running = False
        self.mode = tk.StringVar(value="Sine")
        self.logger = DataLogger()
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Vibration Table Controller", font=("Arial", 24, "bold")).pack(pady=10)
        mode_frame = tk.Frame(self.root)
        mode_frame.pack()
        for mode in ["Sine", "Sweep", "Random", "Stop"]:
            ttk.Radiobutton(mode_frame, text=mode, variable=self.mode, value=mode).pack(side=tk.LEFT, padx=10)

        self.param_frame = tk.Frame(self.root)
        self.param_frame.pack(pady=10)
        self.freq_entry = self.create_labeled_entry(self.param_frame, "Frequency (Hz):")
        self.amp_entry = self.create_labeled_entry(self.param_frame, "Amplitude (V):")

        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=20)
        ttk.Button(control_frame, text="Start", command=self.start_test).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Stop", command=self.stop_test).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Export to USB", command=self.export_data).pack(side=tk.LEFT, padx=10)
        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=10)

        self.status_text = tk.Text(self.root, height=10, width=100)
        self.status_text.pack(pady=10)

    def create_labeled_entry(self, parent, label_text):
        frame = tk.Frame(parent)
        frame.pack()
        tk.Label(frame, text=label_text).pack(side=tk.LEFT)
        entry = tk.Entry(frame)
        entry.pack(side=tk.LEFT)
        return entry

    def log(self, message):
        timestamp = datetime.datetime.now().isoformat()
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)

    def start_test(self):
        if self.running:
            return
        self.running = True
        self.logger.start_new_log()
        self.start_time = time.time()
        self.log(f"Test started in mode: {self.mode.get()}")
        threading.Thread(target=self.run_test, daemon=True).start()

    def stop_test(self):
        self.running = False
        self.log("Test stopped.")
        self.logger.finalize_log()
        self.logger.compute_fft()
        self.log("Data saved and FFT computed.")

    def run_test(self):
        while self.running:
            elapsed = time.time() - self.start_time
            freq = float(self.freq_entry.get() or 1)
            amp = float(self.amp_entry.get() or 1)
            cmd_v = generate_waveform(self.mode.get(), elapsed, freq, amp)
            acc = read_acceleration()
            output_voltage(cmd_v)
            self.logger.log_data(elapsed, cmd_v, acc, self.mode.get(), "")
            time.sleep(0.01)

    def export_data(self):
        result = export_to_usb()
        self.log(result)
        messagebox.showinfo("Export", result)