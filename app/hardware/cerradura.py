from threading import Thread
from time import sleep

try:
    from gpiozero import OutputDevice
    GPIO_OK = True
except Exception as e:
    GPIO_OK = False
    print("⚠️ GPIO no disponible:", e)


PIN_RELEVADOR = 17


class Cerradura:

    def __init__(self):

        self.rele = None

        if GPIO_OK:

            # IMPORTANTE:
            # active_high=False para relevador activo LOW
            self.rele = OutputDevice(
                PIN_RELEVADOR,
                active_high=False,
                initial_value=False
            )

            print("🔐 Cerradura lista en GPIO17")

        else:
            print("⚠️ Cerradura en modo simulación")


    def abrir(self, segundos=3):

        def tarea():

            print("🔓 ABRIENDO")

            self.rele.on()

            sleep(segundos)

            self.rele.off()

            print("🔒 CERRADA")

        Thread(target=tarea, daemon=True).start()


    def cerrar(self):

        if self.rele:
            self.rele.off()

        print("🔒 APAGADA")