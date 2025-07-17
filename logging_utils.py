import csv
import datetime
import numpy as np
from scipy.fft import fft, fftfreq

class DataLogger:
    def __init__(self):
        self.data = []

    def start_new_log(self):
        self.data.clear()

    def log_data(self, timestamp, cmd_v, acc, mode, event):
        self.data.append([timestamp, cmd_v, acc, mode, event])

    def finalize_log(self):
        self.filename = f"vibration_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(self.filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "command_voltage (V)", "acceleration (g)", "mode", "event"])
            writer.writerows(self.data)

    def compute_fft(self):
        if not self.data:
            return
        times = [row[0] for row in self.data]
        accs = [row[2] for row in self.data]
        if len(times) < 2:
            return
        dt = np.mean(np.diff(times))
        acc_fft = fft(accs)
        freqs = fftfreq(len(accs), dt)
        fft_filename = f"fft_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(fft_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Frequency (Hz)", "Magnitude"])
            for freq, val in zip(freqs, np.abs(acc_fft)):
                writer.writerow([freq, val])