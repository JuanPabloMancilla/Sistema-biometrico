import os


def _env_bool(name, default=False):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on", "si", "sí")


def _env_optional_float(name, default):
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default

    valor = raw.strip().lower()
    if valor in ("none", "null", "off", "false"):
        return None

    return float(raw)


# Hardware pins (default values)
PIN_RELEVADOR = int(os.getenv("PIN_RELEVADOR", "22"))
PIN_BUZZER = int(os.getenv("PIN_BUZZER", "18"))
PIN_PIR = int(os.getenv("PIN_PIR", "17"))

# Simulation flag: set SIMULATE_HARDWARE=1 to force mock backends
SIMULATE_HARDWARE = _env_bool("SIMULATE_HARDWARE", False)

# Unlock timeout in seconds. Set UNLOCK_TIMEOUT=none to keep the lock open.
UNLOCK_TIMEOUT = _env_optional_float("UNLOCK_TIMEOUT", 2.0)
