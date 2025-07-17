# logging.py
import csv, time

def log_run(filename, timestamps, waveform, readbacks):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time_s','out_V','feedback'])
        for t, out, fb in zip(timestamps, waveform, readbacks):
            writer.writerow([f"{t:.6f}", f"{out:.4f}", f"{fb:.4f}"])
