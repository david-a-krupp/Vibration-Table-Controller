# vtc/waveform.py
import numpy as np

def manual(value_v: float):
    return float(value_v)

def sine(t, amp=2.0, freq_hz=1.0, dc=2.5):
    return float(dc + amp * np.sin(2*np.pi*freq_hz*t))

def sine_sweep(t, amp=2.0, f_start=0.5, f_end=50.0, dur=10.0, dc=2.5):
    k = (f_end - f_start) / max(dur, 1e-6)
    f = f_start + k * np.clip(t, 0, dur)
    return float(dc + amp*np.sin(2*np.pi*f*t))

def random_noise(dc=2.5, std=0.2):
    return float(np.random.normal(loc=dc, scale=std))

def sine_on_random(t, amp_sine=1.0, freq_hz=5.0, dc=2.5, rand_std=0.1):
    return float(dc + amp_sine*np.sin(2*np.pi*freq_hz*t) + np.random.normal(0, rand_std))

def resonance_dwell(t, amp=2.0, freq_hz=10.0, dc=2.5):
    return float(dc + amp*np.sin(2*np.pi*freq_hz*t))

def shock(t, t0=1.0, peak=4.5, dc=2.5, tau=0.02):
    if t < t0: 
        return float(dc)
    return float(dc + peak*np.exp(-(t - t0)/tau))
