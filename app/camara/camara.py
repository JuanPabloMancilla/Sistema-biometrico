import cv2
import os
import subprocess
import sys
import time
import platform
import threading
import numpy as np

ES_RASPBERRY = platform.system() == "Linux"
PICAMERA2_DISPONIBLE = False
DMA_HEAP_VIDEO = "/dev/dma_heap/vidbuf_cached"
PICAMERA2_BRIDGE_PYTHON = os.environ.get(
    "PICAMERA2_BRIDGE_PYTHON", "/usr/bin/python3"
)

if ES_RASPBERRY:
    try:
        from picamera2 import Picamera2

        PICAMERA2_DISPONIBLE = True
    except ImportError as error:
        Picamera2 = None
        print(f"Picamera2 no disponible en este entorno: {error}")

picam2 = None


class Picamera2BridgeCamera:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.frame_size = width * height * 3
        self.proc = None
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None

    def start(self):
        if os.path.exists(DMA_HEAP_VIDEO) and not os.access(
            DMA_HEAP_VIDEO, os.R_OK | os.W_OK
        ):
            print(
                "Sin permisos para la camara Raspberry: "
                f"{DMA_HEAP_VIDEO}. Agregue el usuario a los grupos video y "
                "render, luego cierre sesion o reinicie la Raspberry."
            )
            return self

        script = os.path.join(os.path.dirname(__file__), "picamera2_bridge.py")
        self.proc = subprocess.Popen(
            [
                PICAMERA2_BRIDGE_PYTHON,
                "-u",
                script,
                str(self.width),
                str(self.height),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

        deadline = time.time() + 3
        while time.time() < deadline:
            if self.proc.poll() is not None:
                err = self._read_stderr()
                if "PERMISSION_ERROR" in err:
                    print(
                        "No hay permisos para usar la camara Raspberry. "
                        "Agregue el usuario a los grupos video y render, "
                        "luego reinicie la sesion o la Raspberry."
                    )
                else:
                    print(f"Bridge picamera2 finalizo al iniciar: {err}")
                return self
            with self.lock:
                if self.frame is not None:
                    return self
            time.sleep(0.05)

        return self

    def _read_stderr(self):
        if not self.proc or not self.proc.stderr:
            return ""
        try:
            return self.proc.stderr.read().decode("utf-8", errors="replace").strip()
        except Exception:
            return ""

    def _read_exact(self, size):
        data = bytearray()
        while self.running and len(data) < size:
            if self.proc is None or self.proc.stdout is None:
                return None
            chunk = self.proc.stdout.read(size - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def _reader(self):
        while self.running and self.proc and self.proc.poll() is None:
            raw = self._read_exact(self.frame_size)
            if raw is None:
                break
            frame = np.frombuffer(raw, dtype=np.uint8).reshape(
                (self.height, self.width, 3)
            )
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            with self.lock:
                self.frame = frame.copy()
        self.running = False

    def isOpened(self):
        return self.proc is not None and self.proc.poll() is None and self.frame is not None

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return True, self.frame.copy()

    def release(self):
        self.running = False
        if self.proc is not None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if self.proc is not None:
            for stream in (self.proc.stdout, self.proc.stderr):
                try:
                    if stream is not None:
                        stream.close()
                except Exception:
                    pass
        self.proc = None
        self.thread = None


class CamaraThreaded:
    def __init__(self, index=0, width=640, height=480, fps=30):
        backend = cv2.CAP_DSHOW if platform.system() == "Windows" else 0
        self.cap = cv2.VideoCapture(index, backend)
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.thread = None

        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    def isOpened(self):
        return self.cap is not None and self.cap.isOpened()

    def start(self):
        if not self.isOpened():
            return self
        self.running = True
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()
        return self

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return True, self.frame.copy()

    def release(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=0.5)
        if self.cap is not None:
            self.cap.release()
            self.cap = None


def iniciar_camara():
    global picam2

    if ES_RASPBERRY and PICAMERA2_DISPONIBLE:
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
            print("Probando bridge picamera2 despues del error")

    if ES_RASPBERRY:
        bridge = Picamera2BridgeCamera().start()
        if bridge.isOpened():
            print("Cámara Raspberry iniciada con bridge picamera2")
            return bridge
        bridge.release()
        print("No se pudo iniciar bridge picamera2, probando OpenCV")

    cap = CamaraThreaded(0).start()

    if not cap.isOpened():
        print("No se pudo abrir la cámara")
        return None

    deadline = time.time() + 2.5
    while time.time() < deadline:
        ret, frame = cap.read()
        if ret and frame is not None:
            print("Cámara OpenCV iniciada")
            return cap
        time.sleep(0.05)

    print("OpenCV abrio la camara, pero no entrego frames")
    cap.release()
    return None


def obtener_frame(cap):
    if cap is None:
        return None

    if ES_RASPBERRY and PICAMERA2_DISPONIBLE and cap is picam2:
        try:
            frame = cap.capture_array()

            if frame is None:
                return None

            frame = cv2.rotate(frame, cv2.ROTATE_180)

            return frame

        except Exception as e:
            print(f"Error capturando frame Raspberry: {e}")
            return None

    ret, frame = cap.read()

    if not ret:
        print("No se pudo leer frame")
        return None

    return frame


def liberar_camara(cap=None):
    global picam2

    if ES_RASPBERRY and PICAMERA2_DISPONIBLE and (cap is picam2 or cap is None):
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

    if cap is not None:
        try:
            cap.release()
        except Exception:
            pass

    cv2.destroyAllWindows()
    print("📷 Cámara liberada")
