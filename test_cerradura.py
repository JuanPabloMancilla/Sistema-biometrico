from gpiozero import OutputDevice
from time import sleep

# GPIO17 = pin físico 11
relay = OutputDevice(
    17,
    active_high=False,
    initial_value=False
)

print("🔒 Estado inicial")

sleep(5)

print("🔓 Activando relevador...")
relay.on()

sleep(3)

print("🔒 Apagando relevador...")
relay.off()

sleep(5)

print("✅ Fin de prueba")