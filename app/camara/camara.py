import cv2
import time
import platform

ES_RASPBERRY = platform.system() == "Linux"

if ES_RASPBERRY:
    from picamera2 import Picamera2

picam2 = None


def iniciar_camara():
    global picam2

    if ES_RASPBERRY:
        try:
            # Si ya había una cámara abierta, cerrarla primero
            if picam2 is not None:
                try:
                    picam2.stop()
                    picam2.close()
                except Exception:
                    pass
                picam2 = None
                time.sleep(0.5)

            picam2 = Picamera2()

            config = picam2.create_preview_configuration(
                main={
                    "size": (640, 480),
                    "format": "RGB888"
                }
            )

            picam2.configure(config)
            picam2.start()

            time.sleep(1)

            print("Cámara Raspberry iniciada")
            return picam2

        except Exception as e:
            print(f"Error iniciando cámara Raspberry: {e}")

            try:
                if picam2 is not None:
                    picam2.stop()
                    picam2.close()
            except Exception:
                pass

            picam2 = None
            return None

    else:
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return None

        print("Cámara PC iniciada")
        return cap


def obtener_frame(cap):
    if cap is None:
        return None

    if ES_RASPBERRY:
        try:
            frame = cap.capture_array()

            if frame is None:
                return None

            frame = cv2.rotate(frame, cv2.ROTATE_180)

            return frame

        except Exception as e:
            print(f"Error capturando frame Raspberry: {e}")
            return None

    else:
        ret, frame = cap.read()

        if not ret:
            print("No se pudo leer frame")
            return None

        return frame


def liberar_camara(cap=None):
    global picam2

    if ES_RASPBERRY:
        cam = cap if cap is not None else picam2

        if cam is not None:
            try:
                cam.stop()
            except Exception:
                pass

            try:
                cam.close()
            except Exception:
                pass

        picam2 = None
        time.sleep(0.5)

        print("📷 Cámara liberada")

    else:
        if cap is not None:
            try:
                cap.release()
            except Exception:
                pass

        cv2.destroyAllWindows()
        print("📷 Cámara liberada")