# vtc/dac_uldaq.py
from uldaq import (
    get_daq_device_inventory, DaqDevice, InterfaceType,
    AOutFlag, AInFlag, Range
)

class DacULDAQ:
    """
    Simple wrapper around an MCC USB-1208FS-Plus:
    - AO: single channel for drive (0–5 V typical)
    - AI: single channel for feedback (BIP10VOLTS from ADAM-3017)
    """
    def __init__(
        self,
        device_hint=None,
        ao_channel=0,
        ai_channel=0,
        ao_range=Range.UNI5VOLTS,
        ai_range=Range.BIP10VOLTS,
    ):
        self.ao_channel = ao_channel
        self.ai_channel = ai_channel
        self.ao_range = ao_range
        self.ai_range = ai_range

        devices = get_daq_device_inventory(InterfaceType.USB)
        if not devices:
            raise RuntimeError("MCC DAQ not found")

        if device_hint:
            matches = [d for d in devices if device_hint in d.product_name]
            dd = matches[0] if matches else devices[0]
        else:
            dd = devices[0]

        self.device = DaqDevice(dd)
        self.ao_device = None
        self.ai_device = None

    def connect(self):
        self.device.connect()
        self.ao_device = self.device.get_ao_device()
        self.ai_device = self.device.get_ai_device()
        if self.ao_device is None:
            raise RuntimeError("Device has no AO.")
        if self.ai_device is None:
            raise RuntimeError("Device has no AI.")
        # Start with 0 V output
        self.write(0.0)

    # --- AO ---

    def write(self, volts: float):
        # Clamp to selected AO range
        if self.ao_range == Range.UNI5VOLTS:
            volts = max(0.0, min(5.0, volts))
        else:
            volts = max(-5.0, min(5.0, volts))
        self.ao_device.a_out(self.ao_channel, self.ao_range, AOutFlag.DEFAULT, volts)

    # --- AI ---

    def read(self) -> float:
        """
        Returns AI voltage on ai_channel in volts.
        Assumes ADAM-3017 output is wired to that channel.
        """
        return float(self.ai_device.a_in(self.ai_channel, self.ai_range, AInFlag.DEFAULT))

    def close(self):
        try:
            self.write(0.0)
        finally:
            self.device.disconnect()
            self.device.release()

