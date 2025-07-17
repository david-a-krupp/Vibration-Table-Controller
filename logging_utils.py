import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

class DataLogger:
    def __init__(self):
        self.data = []

    def start_new_log(self):
        self.data.clear()

    def log_data(self, timestamp, cmd_v, acc, mode, event):
        self.data.append([timestamp, cmd_v, acc, mode, event])

    def finalize_log(self):
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = f"vibration_test_{self.timestamp}.csv"
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
        fft_filename = f"fft_{self.timestamp}.csv"
        with open(fft_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Frequency (Hz)", "Magnitude"])
            for freq, val in zip(freqs, np.abs(acc_fft)):
                writer.writerow([freq, val])

        # Save FFT Plot
        plt.figure(figsize=(10, 5))
        plt.plot(freqs[:len(freqs)//2], np.abs(acc_fft)[:len(acc_fft)//2])
        plt.title("FFT of Acceleration Signal")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"fft_plot_{self.timestamp}.png")
        plt.close()