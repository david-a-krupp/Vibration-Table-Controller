# vtc/safety_gpio.py
from gpiozero import Button, OutputDevice
import time

class SafetyController:
    def __init__(self, estop_pin=17, mute_pin=27, debounce_s=0.02):
        # E-stop: NC -> GND with internal pull-up; open = fault
        self.estop = Button(estop_pin, pull_up=True, bounce_time=debounce_s)
        # Mute relay: LOW=mute, HIGH=armed
        self.relay = OutputDevice(mute_pin, active_high=True, initial_value=False)
        self.armed = False
        self.last_fault_time = None
        self.estop.when_pressed = self._on_change
        self.estop.when_released = self._on_change
        self.mute()

    def _on_change(self):
        if self.is_fault():
            self.mute()
            self.armed = False
            self.last_fault_time = time.time()

    def is_fault(self):
        return not self.estop.is_pressed  # open = fault

    def mute(self):
        self.relay.off()
        return "MUTED"

    def arm(self):
        if self.is_fault():
            return "CANNOT_ARM_FAULT_ACTIVE"
        self.relay.on()
        self.armed = True
        return "ARMED"
