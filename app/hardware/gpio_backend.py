import logging
from app.config import SIMULATE_HARDWARE

SIMULATE = SIMULATE_HARDWARE
BACKEND_ERROR = None

try:
    if not SIMULATE:
        from gpiozero import Device, OutputDevice, Buzzer as GpioBuzzer  # type: ignore

        Device.ensure_pin_factory()
        GPIO_OK = True
    else:
        raise Exception("SIMULATE_HARDWARE enabled")
except Exception as e:
    BACKEND_ERROR = str(e)
    logging.debug("gpiozero not available or simulation enabled: %s", e)
    GPIO_OK = False


class MockOutputDevice:
    def __init__(self, pin, active_high=True, initial_value=False):
        self.pin = pin
        self.active_high = active_high
        self.value = initial_value
        logging.info("MockOutputDevice initialized on pin %s (initial=%s)", pin, initial_value)

    def on(self):
        self.value = True
        logging.info("MockOutputDevice pin %s ON", self.pin)

    def off(self):
        self.value = False
        logging.info("MockOutputDevice pin %s OFF", self.pin)

    def close(self):
        logging.info("MockOutputDevice pin %s closed", self.pin)


class MockBuzzer:
    def __init__(self, pin):
        self.pin = pin
        self.value = False
        logging.info("MockBuzzer initialized on pin %s", pin)

    def on(self):
        self.value = True
        logging.info("MockBuzzer pin %s ON", self.pin)

    def off(self):
        self.value = False
        logging.info("MockBuzzer pin %s OFF", self.pin)

    def beep(self, on_time=0.1, off_time=0.1, n=1):
        for i in range(n):
            logging.info("MockBuzzer beep #%s on pin %s", i + 1, self.pin)

    def close(self):
        self.off()
        logging.info("MockBuzzer pin %s closed", self.pin)


# Expose API
if GPIO_OK:
    Buzzer = GpioBuzzer
    BackendOutputDevice = OutputDevice
else:
    Buzzer = MockBuzzer
    BackendOutputDevice = MockOutputDevice


def get_backend_info():
    return {"gpio_ok": GPIO_OK, "simulate": SIMULATE, "error": BACKEND_ERROR}
