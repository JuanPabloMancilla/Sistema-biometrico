from threading import Thread
from time import sleep
import logging

from .gpio_backend import BackendOutputDevice, get_backend_info
from app.config import PIN_RELEVADOR, RELE_ACTIVE_HIGH, UNLOCK_TIMEOUT


logger = logging.getLogger(__name__)


class Cerradura:

    def __init__(self):

        self.rele = None
        self._desbloqueo_id = 0

        info = get_backend_info()
        try:
            self.rele = BackendOutputDevice(
                PIN_RELEVADOR,
                active_high=RELE_ACTIVE_HIGH,
                initial_value=False,
            )
            self.bloquear()

            modo = "GPIO real" if info.get("gpio_ok") else "simulación/mock"
            logger.info(
                "Cerradura lista (%s) en pin %s, active_high=%s",
                modo,
                PIN_RELEVADOR,
                RELE_ACTIVE_HIGH,
            )
            if not info.get("gpio_ok"):
                logger.warning(
                    "La cerradura no enviara señal fisica. Backend GPIO: %s",
                    info.get("error") or "no disponible",
                )
        except Exception:
            logger.exception("Error iniciando dispositivo para cerradura")

    def desbloquear(self):

        if not self.rele:
            logger.error("No se puede abrir: rele GPIO no disponible")
            print("ERROR CERRADURA: rele GPIO no disponible")
            return False

        try:
            self.rele.on()
            logger.info("Cerradura: desbloqueada")
            print(f"CERRADURA: señal de apertura enviada a GPIO {PIN_RELEVADOR}")
            return True
        except Exception:
            logger.exception("Error al activar rele")
            print(f"ERROR CERRADURA: no se pudo activar GPIO {PIN_RELEVADOR}")
            return False

    def bloquear(self):

        if self.rele:
            try:
                self.rele.off()
            except Exception:
                logger.exception("Error al desactivar rele")

        logger.info("Cerradura: bloqueada")

    def desbloquear_temporal(self, segundos=UNLOCK_TIMEOUT):
        self._desbloqueo_id += 1
        desbloqueo_id = self._desbloqueo_id

        if not self.desbloquear():
            return False

        if segundos is None:
            logger.warning("Cerradura desbloqueada sin temporizador")
            return True

        def tarea():
            sleep(segundos)

            if desbloqueo_id == self._desbloqueo_id:
                self.bloquear()

        Thread(target=tarea, daemon=True).start()
        return True

    def cerrar(self):
        if not self.rele:
            return

        try:
            self.bloquear()
            if hasattr(self.rele, "close"):
                self.rele.close()
        except Exception:
            logger.exception("Error cerrando dispositivo de cerradura")
        finally:
            self.rele = None
