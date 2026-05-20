import time
from gpiozero import OutputDevice

relay = OutputDevice(
    17,
    active_high=True,
    initial_value=True  # Arranca ABIERTA
)

def ejecutar_cerradura(segundos=2):
    print("🔓 ABIERTA")
    relay.on()
    time.sleep(3)

    print("🔒 CERRADA")
    relay.off()
    time.sleep(segundos)

    print("🔓 ABIERTA")
    relay.on()

# ─── Aquí va tu sistema de reconocimiento ───────────────────
def reconocimiento():
    # sea RFID, facial, PIN, lo que sea...
    resultado = tu_modulo_de_reconocimiento()

    if resultado == "admitido":
        ejecutar_cerradura(segundos=2)  # ← se dispara aquí
    else:
        print("❌ Acceso denegado")