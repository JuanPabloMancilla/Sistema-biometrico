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
                initial_value=True
            )

            # ESTADO NORMAL = ABIERTA
            self.abrir_normal()

            print("Cerradura lista")

    def abrir_normal(self):

        if self.rele:
            self.rele.on()

        print("ABIERTA")

    def cerrar_temporal(self, segundos=2):

        def tarea():

            print("CERRANDO")

            if self.rele:
                self.rele.off()

            sleep(segundos)

            print("ABRIENDO")

            if self.rele:
                self.rele.on()

        Thread(target=tarea, daemon=True).start()