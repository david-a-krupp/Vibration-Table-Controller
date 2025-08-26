# vtc/config.py
from dataclasses import dataclass

@dataclass
class Calibration:
    DAC_OFFSET: float = 0.0   # volts
    DAC_SCALE: float  = 1.0   # multiplier after waveform calc
    ADC_SCALE: float  = 1.0   # volts multiplier after divider (V_meas = ADC*ADC_SCALE)
    G_PER_V: float    = 1.0   # g per volt on monitor/accelerometer path

@dataclass
class GPIOPins:
    ESTOP_PIN: int = 17
    MUTE_PIN: int  = 18

@dataclass
class Runtime:
    SAMPLE_HZ: int   = 500    # UI update cadence for reading ADC
    LOG_PATH: str    = "/home/pi/vtc_logs"
