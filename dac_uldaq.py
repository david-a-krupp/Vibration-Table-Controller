# vtc/dac_uldaq.py
from uldaq import (get_daq_device_inventory, DaqDevice, InterfaceType,
                   AOutFlag, Range)

class DacULDAQ:
    def __init__(self, device_hint=None, channel=0, out_range=Range.UNI5VOLTS):
        self.channel = channel
        devices = get_daq_device_inventory(InterfaceType.USB)
        if not devices:
            raise RuntimeError("No MCC USB DAQ devices found.")
        if device_hint:
            matches = [d for d in devices if device_hint in d.product_name]
            dd = matches[0] if matches else devices[0]
        else:
            dd = devices[0]
        self.device = DaqDevice(dd)
        self.ao_device = None
        self.out_range = out_range

    def connect(self):
        self.device.connect()
        self.ao_device = self.device.get_ao_device()
        if self.ao_device is None:
            raise RuntimeError("Device has no AO.")
        self.write(0.0)

    def write(self, volts: float):
        if self.out_range == Range.UNI5VOLTS:
            volts = max(0.0, min(5.0, volts))
        else:
            volts = max(-5.0, min(5.0, volts))
        self.ao_device.a_out(self.channel, self.out_range, AOutFlag.DEFAULT, volts)

    def close(self):
        try:
            self.write(0.0)
        finally:
            self.device.disconnect()
            self.device.release()
