from mcculw.ul import ao_win_buf_write, ao_out
from mcculw.enums import BoardInfo, AnalogOutputRange
from mcculw.ul import get_config, set_config, ConfigItem

# Set board number (usually 0 for first MCC device)
BOARD_NUM = 0
CHANNEL = 0
RANGE = AnalogOutputRange.BIP10VOLTS  # +/-10V range

def output_voltage(voltage):
    # Convert -10V to +10V range into 0–4095 (12-bit)
    value = int((voltage + 10) / 20 * 4095)
    value = max(0, min(4095, value))  # Clamp
    ao_out(BOARD_NUM, CHANNEL, RANGE, value)