from threading import Thread
from time import sleep

try:
    from gpiozero import OutputDevice
    GPIO_OK = True
except Exception as e:
    GPIO_OK = False
    print("⚠️ GPIO no disponible:", e)


PIN_RELEVADOR = 17  # GPIO17 = pin físico 11


class Cerradura:
    def __init__(self):
        self.rele = None

        if GPIO_OK:
            self.rele = OutputDevice(
                PIN_RELEVADOR,
                active_high=True,
                initial_value=False
            )

            # Estado normal: ABIERTA
            self.abrir_normal()

            print("🔐 Cerradura lista en GPIO17")
        else:
            print("⚠️ Cerradura en modo simulación")

    def abrir_normal(self):
        # En tu conexión: OFF = abierta
        if self.rele:
            self.rele.off()
        print("🔓 Cerradura ABIERTA / estado normal")

    def cerrar_temporal(self, segundos=2):
        def tarea():
            # En tu conexión: ON = cerrada/bloqueada
            print("🔒 Cerrando cerradura")
            if self.rele:
                self.rele.on()

            sleep(segundos)

            print("🔓 Volviendo a abrir")
            if self.rele:
                self.rele.off()

        Thread(target=tarea, daemon=True).start()

    def cerrar(self):
        if self.rele:
            self.rele.on()
        print("🔒 Cerradura cerrada")