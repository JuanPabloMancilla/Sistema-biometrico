
from threading import Thread
from time import sleep

try:
    from gpiozero import OutputDevice
    GPIO_OK = True
except Exception as e:
    GPIO_OK = False
    print("⚠️ GPIO no disponible:", e)


PIN_RELEVADOR = 17  # Pin físico 11 = GPIO17

# Si tu relevador funciona al revés, cambia a True
ACTIVE_HIGH = True


class Cerradura:
    def __init__(self):
        self.rele = None

        if GPIO_OK:
            self.rele = OutputDevice(
                PIN_RELEVADOR,
                active_high=ACTIVE_HIGH,
                initial_value=True
            )
            
            self.rele.off()
            print("🔐 Cerradura lista en GPIO17")
        else:
            print("⚠️ Cerradura en modo simulación")

    def abrir(self, segundos=3):
        def tarea():
            print("🔓 Cerradura abierta")
            if self.rele:
                self.rele.on()

            sleep(segundos)

            if self.rele:
                self.rele.off()
            print("🔒 Cerradura cerrada")

        Thread(target=tarea, daemon=True).start()

    def cerrar(self):
        if self.rele:
            self.rele.off()
        print("🔒 Cerradura cerrada / apagada")