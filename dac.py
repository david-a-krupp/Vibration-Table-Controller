from mcculw import ul
from mcculw.enums import ULRange

BOARD_NUM = 0  # Usually 0 by default
AO_CHANNEL = 0  # AO0 on USB-1208FS-Plus
VOLTAGE_RANGE = ULRange.BIP10VOLTS  # ±10V output
RESOLUTION = 4096  # 12-bit DAC

def voltage_to_dac_value(voltage):
    # Clamp voltage to ±10V range
    voltage = max(-10.0, min(10.0, voltage))
    return int((voltage + 10) / 20 * (RESOLUTION - 1))

def output_waveform(board_num, channel, data, fs):
    import time
    for v in data:
        scaled_val = voltage_to_dac_value(v)
        ul.a_out(board_num, channel, VOLTAGE_RANGE, scaled_val)
        time.sleep(1.0 / fs)
