# waveform.py
import numpy as np

def sine(freq, amp, duration, fs=20000):
    t = np.arange(0, duration, 1/fs)
    return t, amp * np.sin(2*np.pi*freq*t)

def sweep(f0, f1, amp, duration, fs=20000):
    t = np.arange(0, duration, 1/fs)
    freqs = np.logspace(np.log10(f0), np.log10(f1), t.size)
    phase = 2*np.pi * np.cumsum(freqs)/fs
    return t, amp * np.sin(phase)
