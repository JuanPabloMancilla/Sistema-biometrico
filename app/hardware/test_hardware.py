import logging
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import PIN_BUZZER, PIN_PIR, PIN_RELEVADOR, UNLOCK_TIMEOUT
from app.hardware import buzzer
from app.hardware.cerradura import Cerradura
from app.hardware.gpio_backend import get_backend_info


def probar_cerradura():
    print(f"\n[RELÉ] Probando cerradura en GPIO {PIN_RELEVADOR}")
    cerradura = Cerradura()

    try:
        cerradura.desbloquear()
        time.sleep(1)
        cerradura.bloquear()
        print("[RELÉ] OK")
    finally:
        cerradura.cerrar()


def probar_buzzer():
    print(f"\n[BUZZER] Probando buzzer en GPIO {PIN_BUZZER}")
    buzzer.buzz(0.15)
    buzzer.buzz(0.08)
    buzzer.close()
    print("[BUZZER] OK")


def probar_pir(segundos=5):
    print(f"\n[PIR] Probando sensor PIR en GPIO {PIN_PIR} durante {segundos}s")

    if not get_backend_info().get("gpio_ok"):
        print("[PIR] Modo simulación: gpiozero no disponible o SIMULATE_HARDWARE activo")
        return

    try:
        from gpiozero import MotionSensor  # type: ignore
    except Exception as exc:
        print(f"[PIR] No se pudo importar MotionSensor: {exc}")
        return

    sensor = MotionSensor(PIN_PIR)
    fin = time.time() + segundos

    try:
        while time.time() < fin:
            estado = "movimiento" if sensor.motion_detected else "sin movimiento"
            print(f"[PIR] {estado}")
            time.sleep(0.5)
    finally:
        sensor.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    backend = get_backend_info()
    print("Backend GPIO:", backend)
    print("UNLOCK_TIMEOUT:", UNLOCK_TIMEOUT)

    probar_cerradura()
    probar_buzzer()
    probar_pir()

    print("\nPruebas de hardware finalizadas.")


if __name__ == "__main__":
    main()
