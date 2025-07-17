import numpy as np
import random

def generate_waveform(mode, t, freq, amp):
    if mode == "Sine":
        return amp * np.sin(2 * np.pi * freq * t)
    elif mode == "Random":
        return random.uniform(-amp, amp)
    elif mode == "Sweep":
        sweep_freq = freq + (t * 0.1)
        return amp * np.sin(2 * np.pi * sweep_freq * t)
    else:
        return 0