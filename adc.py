# adc.py
import Adafruit_ADS1x15

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

def read_channel(ch):
    return adc.read_adc(ch, gain=GAIN)
