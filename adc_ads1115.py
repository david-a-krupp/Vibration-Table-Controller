# vtc/adc_ads1115.py
import time
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_ads1x15.ads1115 as ADS
import board, busio

class ADSReader:
    def __init__(self, differential=False, pga=1, v_scale=1.0):
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.ads = ADS.ADS1115(self.i2c)
        self.ads.gain = pga
        self.v_scale = v_scale
        if differential:
            self.chan = AnalogIn(self.ads, ADS.P0, ADS.P1)
        else:
            self.chan = AnalogIn(self.ads, ADS.P0)

    def read_v(self):
        return self.chan.voltage * self.v_scale

    def read_samples(self, n=200, dt=0.002):
        data = []
        for _ in range(n):
            data.append(self.read_v())
            time.sleep(dt)
        return data
