import logging
import time
import atexit
from threading import Lock, Thread

from .gpio_backend import Buzzer as _Buzzer
from app.config import PIN_BUZZER


logger = logging.getLogger(__name__)
_lock = Lock()
_play_lock = Lock()
_device = None
_device_pin = None


def _get_device(pin):
    global _device, _device_pin

    with _lock:
        if _device is None or _device_pin != pin:
            _close_unlocked()
            _device = _Buzzer(pin)
            _device_pin = pin

        return _device


def _close_unlocked():
    global _device, _device_pin

    device = _device
    _device = None
    _device_pin = None

    if not device:
        return

    try:
        if hasattr(device, "off"):
            device.off()
        if hasattr(device, "close"):
            device.close()
    except Exception:
        logger.exception("Error cerrando buzzer")


def buzz(duration: float = 0.15, pin: int | None = None):
    """Play a short buzz without recreating the GPIO device each time."""
    buzzer_pin = pin or PIN_BUZZER
    duration = max(float(duration), 0.0)

    with _play_lock:
        try:
            b = _get_device(buzzer_pin)

            if hasattr(b, "on") and hasattr(b, "off"):
                b.on()
                time.sleep(duration)
                b.off()
            elif hasattr(b, "beep"):
                b.beep(on_time=duration, off_time=0, n=1)
            else:
                logger.info("Buzzer backend has no on/off or beep; skipping")
        except Exception:
            logger.exception("Error using buzzer backend")
        finally:
            try:
                if "b" in locals() and hasattr(b, "off"):
                    b.off()
            except Exception:
                logger.exception("Error apagando buzzer")


def buzz_async(duration: float = 0.15, pin: int | None = None):
    Thread(target=buzz, args=(duration, pin), daemon=True).start()


def close():
    with _play_lock:
        with _lock:
            _close_unlocked()


atexit.register(close)
