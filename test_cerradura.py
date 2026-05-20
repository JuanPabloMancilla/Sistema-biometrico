import time
from gpiozero import OutputDevice


# GPIO17 = pin físico 11
relay = OutputDevice(
    17,
    active_high=True,
    initial_value=True
)


def ejecutar_cerradura(segundos=2):

    # =====================================================
    # ESTADO NORMAL
    # ABIERTA
    # =====================================================

    print("🔓 ABIERTA")

    relay.on()

    time.sleep(3)

    # =====================================================
    # CERRAR
    # =====================================================

    print("🔒 CERRADA")

    relay.off()

    time.sleep(segundos)

    # =====================================================
    # VOLVER A ABRIR
    # =====================================================

    print("🔓 ABIERTA")

    relay.on()

    time.sleep(3)


def ciclo_prueba():

    while True:
        ejecutar_cerradura(segundos=2)


if __name__ == "__main__":
    ciclo_prueba()