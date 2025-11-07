# vtc/safety_gpio.py

class SafetyController:
    """
    Software-only safety controller.

    In this configuration the amplifier's own E-stop handles hardware safety.
    This class simply tracks an 'armed' state so the UI can gate when it is
    allowed to send non-zero drive voltages. No GPIO is used.
    """

    def __init__(self, estop_pin=17, mute_pin=18, debounce_s=0.02):
        # Parameters are kept for API compatibility but unused.
        self.armed = False
        self.last_fault_time = None

    def is_fault(self) -> bool:
        """
        Return False to indicate no Pi-side fault detection.

        All hard safety is handled by the HPA-K amplifier E-stop,
        so from the controller's perspective there is never a fault.
        """
        return False

    def mute(self) -> str:
        """
        Software mute: mark the system as not armed.
        The UI will respond by holding the drive output at 0 V.
        """
        self.armed = False
        return "MUTED"

    def arm(self) -> str:
        """
        Software arm: allow the UI to start sending waveforms.
        """
        self.armed = True
        return "ARMED"
