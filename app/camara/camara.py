import cv2
import time
import platform

# Detectar si estamos en Raspberry Pi/Linux
ES_RASPBERRY = platform.system() == "Linux"

if ES_RASPBERRY:
    from picamera2 import Picamera2

picam2 = None


def iniciar_camara():
    global picam2

    # ===== RASPBERRY PI =====
    if ES_RASPBERRY:
        try:
            picam2 = Picamera2()

            config = picam2.create_preview_configuration(
                main={
                    "size": (640, 480),
                    "format": "RGB888"
                }
            )

            picam2.configure(config)
            picam2.start()

            time.sleep(2)

            print("Cámara Raspberry iniciada")

            return picam2

        except Exception as e:
            print(f"Error iniciando cámara Raspberry: {e}")
            return None

    # ===== WINDOWS / PC =====
    else:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return None

        print("Cámara PC iniciada")

        return cap


def obtener_frame(cap):

    # ===== RASPBERRY =====
    if ES_RASPBERRY:
        try:
            frame = cap.capture_array()

            if frame is None:
                return None

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            return frame

        except Exception as e:
            print(f"Error capturando frame Raspberry: {e}")
            return None

    # ===== WINDOWS =====
    else:
        ret, frame = cap.read()

        if not ret:
            print("No se pudo leer frame")
            return None

        return frame


def liberar_camara(cap):

    if ES_RASPBERRY:
        if cap is not None:
            cap.stop()

    else:
        if cap is not None:
            cap.release()