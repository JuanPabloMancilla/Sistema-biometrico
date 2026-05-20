from gpiozero import OutputDevice
from time import sleep

relay = OutputDevice(
    17,
    active_high=True,
    initial_value=False
)

print("🔒 Cerradura cerrada")
relay.off()

sleep(5)

print("🔓 Abriendo cerradura")
relay.on()

sleep(3)

print("🔒 Cerrando cerradura")
relay.off()

print("✅ Fin")