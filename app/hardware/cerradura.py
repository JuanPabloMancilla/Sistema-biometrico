from threading import Thread
from time import sleep

try:
    from gpiozero import OutputDevice
    GPIO_OK = True
except Exception as e:
    GPIO_OK = False
    print("GPIO no disponible:", e)

PIN_RELEVADOR = 22


class Cerradura:

    def __init__(self):

        self.rele = None

        if GPIO_OK:

            self.rele = OutputDevice(
                PIN_RELEVADOR,
                active_high=True,
                initial_value=False
            )

            self.bloquear()

            print("?? Cerradura lista")

    def desbloquear(self):

        if self.rele:
            self.rele.on()

        print("?? LED ENCENDIDO")

    def bloquear(self):

        if self.rele:
            self.rele.off()

        print("? LED APAGADO")

    def desbloquear_temporal(self, segundos=2):

        def tarea():

            self.desbloquear()

            sleep(segundos)

            self.bloquear()

        Thread(target=tarea, daemon=True).start()