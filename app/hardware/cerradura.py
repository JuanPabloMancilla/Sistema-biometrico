from threading import Thread
from time import sleep
import logging

from .gpio_backend import BackendOutputDevice, get_backend_info
from app.config import PIN_RELEVADOR, UNLOCK_TIMEOUT


logger = logging.getLogger(__name__)


class Cerradura:

    def __init__(self):

        self.rele = None
        self._desbloqueo_id = 0

        info = get_backend_info()
        try:
            self.rele = BackendOutputDevice(
                PIN_RELEVADOR,
                active_high=True,
                initial_value=False,
            )
            self.bloquear()

            modo = "GPIO real" if info.get("gpio_ok") else "simulación/mock"
            logger.info("Cerradura lista (%s) en pin %s", modo, PIN_RELEVADOR)
        except Exception:
            logger.exception("Error iniciando dispositivo para cerradura")

    def desbloquear(self):

        if self.rele:
            try:
                self.rele.on()
            except Exception:
                logger.exception("Error al activar rele")

        logger.info("Cerradura: desbloqueada")

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

        if segundos is None:
            self.desbloquear()
            logger.warning("Cerradura desbloqueada sin temporizador")
            return

        def tarea():

            self.desbloquear()

            sleep(segundos)

            if desbloqueo_id == self._desbloqueo_id:
                self.bloquear()

        Thread(target=tarea, daemon=True).start()

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
