from gpiozero import OutputDevice
from time import sleep

relay = OutputDevice(17, active_high=False)

print("Activando relevador...")
relay.on()

sleep(3)

relay.off()
print("Apagado")