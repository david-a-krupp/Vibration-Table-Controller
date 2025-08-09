# vtc/logging_utils.py
import csv, os, time
from datetime import datetime

class CSVLogger:
    def __init__(self, folder, filename_prefix="vtc_run"):
        os.makedirs(folder, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(folder, f"{filename_prefix}_{ts}.csv")
        self.f = open(self.path, "w", newline="")
        self.w = csv.writer(self.f)
        self.w.writerow(["t_s", "cmd_v", "meas_v"])
        self.last_flush = time.time()

    def write(self, t, cmd_v, meas_v, flush_interval_s=1.0):
        self.w.writerow([f"{t:.6f}", f"{cmd_v:.6f}", f"{meas_v:.6f}"])
        now = time.time()
        if now - self.last_flush > flush_interval_s:
            self.f.flush()
            os.fsync(self.f.fileno())
            self.last_flush = now

    def close(self):
        try:
            self.f.flush()
            os.fsync(self.f.fileno())
        finally:
            self.f.close()
