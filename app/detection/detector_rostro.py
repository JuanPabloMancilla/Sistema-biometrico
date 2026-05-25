import cv2
import face_recognition
import numpy as np
import time
from datetime import datetime
import json
import os
from app.services.usuario_service import obtener_nombre_usuario_por_id
from app.recognition.encoding_manager import (
    verificar_dimension,
    guardar_encoding,
    cargar_encodings
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGS_PATH = os.path.join(BASE_DIR, "logs_accesos.json")

def guardar_logs():
    with open(LOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(logs_accesos, f, ensure_ascii=False, indent=2)

def cargar_logs():
    global logs_accesos

    if not os.path.exists(LOGS_PATH) or os.path.getsize(LOGS_PATH) == 0:
        logs_accesos = []
        guardar_logs()
        return

    try:
        with open(LOGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        logs_accesos = data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        logs_accesos = []
        guardar_logs()

# --- CACHÃ‰ DE DATOS ---
encodings_db, usuarios_db = cargar_encodings()
ultimo_resultado = (None, "ESCANEANDO...")
ultimo_encoding = None
ultimo_usuario_id = None
frame_count = 0

logs_accesos = []
cargar_logs()

ultimo_registro = 0
TIEMPO_ESPERA = 10  # segundos

def registrar_acceso():
    global ultimo_registro

    ahora = time.time()

    if ahora - ultimo_registro < TIEMPO_ESPERA:
        return

    ultimo_registro = ahora

    logs_accesos.append({
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H")
    })

    guardar_logs()

def _centro_puntos(puntos):
    arr = np.array(puntos, dtype=np.float32)
    return float(np.mean(arr[:, 0])), float(np.mean(arr[:, 1]))

def _validar_postura(rgb_small, face_location, frame_shape):
    top, right, bottom, left = face_location
    alto_small, ancho_small = rgb_small.shape[:2]
    alto_frame, ancho_frame = frame_shape[:2]

    fw = right - left
    fh = bottom - top
    if fw <= 0 or fh <= 0:
        return False, "ROSTRO NO VALIDO"

    centro_x = (left + right) / 2
    centro_y = (top + bottom) / 2
    desviacion_x = abs(centro_x - (ancho_small / 2)) / max(ancho_small, 1)
    desviacion_y = abs(centro_y - (alto_small / 2)) / max(alto_small, 1)

    area_relativa = ((fw * 4) * (fh * 4)) / max(alto_frame * ancho_frame, 1)
    if area_relativa < 0.045:
        return False, "ACERQUESE A LA CAMARA"
    if area_relativa > 0.55:
        return False, "ALEJESE UN POCO"
    if desviacion_x > 0.22 or desviacion_y > 0.20:
        return False, "CENTRE SU ROSTRO"

    gris = cv2.cvtColor(rgb_small, cv2.COLOR_RGB2GRAY)
    roi = gris[max(0, top):min(alto_small, bottom), max(0, left):min(ancho_small, right)]
    if roi.size and float(np.mean(roi)) < 45:
        return False, "MEJORE LA ILUMINACION"

    try:
        landmarks = face_recognition.face_landmarks(rgb_small, [face_location])
    except Exception:
        landmarks = []

    if not landmarks:
        return False, "MIRE AL FRENTE"

    puntos = landmarks[0]
    if "left_eye" not in puntos or "right_eye" not in puntos or "nose_tip" not in puntos:
        return False, "MIRE AL FRENTE"

    ojo_izq = _centro_puntos(puntos["left_eye"])
    ojo_der = _centro_puntos(puntos["right_eye"])
    nariz = _centro_puntos(puntos["nose_tip"])

    distancia_ojos = max(abs(ojo_der[0] - ojo_izq[0]), 1.0)
    inclinacion = abs(ojo_der[1] - ojo_izq[1]) / distancia_ojos
    if inclinacion > 0.18:
        return False, "ENDERECE SU ROSTRO"

    centro_ojos_x = (ojo_izq[0] + ojo_der[0]) / 2
    giro = abs(nariz[0] - centro_ojos_x) / distancia_ojos
    if giro > 0.23:
        return False, "MIRE AL FRENTE"

    return True, "ROSTRO LISTO"

def procesar_frame(frame):
    global encodings_db, usuarios_db, ultimo_resultado, ultimo_encoding, ultimo_usuario_id, frame_count
    
    frame_count += 1
    # OPTIMIZACIÃ“N: Solo procesar reconocimiento cada 3 frames para evitar lag
    if frame_count % 3 != 0 and ultimo_resultado[0] is not None:
        top, right, bottom, left = ultimo_resultado[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (10, 185, 129), 2)
        return frame, ultimo_encoding, ultimo_resultado[1], ultimo_usuario_id

    # 1. Reducir imagen para detecciÃ³n rÃ¡pida (Escala 1/4)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 2. DetecciÃ³n con modelo HOG (el mÃ¡s rÃ¡pido en CPU)
    face_locations = face_recognition.face_locations(rgb_small, model="hog")
    
    if not face_locations:
        ultimo_resultado = (None, "No se detectÃ³ ninguna cara")
        ultimo_encoding = None
        ultimo_usuario_id = None
        return frame, None, "No se detectÃ³ ninguna cara", None

    if len(face_locations) > 1:
        ultimo_encoding = None
        ultimo_usuario_id = None
        return frame, None, "Se detectaron mÃºltiples caras", None

    postura_ok, mensaje_postura = _validar_postura(rgb_small, face_locations[0], frame.shape)

    # 3. Reescalar coordenadas al tamaÃ±o original
    top, right, bottom, left = [v * 4 for v in face_locations[0]]

    if not postura_ok:
        ultimo_resultado = ((top, right, bottom, left), mensaje_postura)
        ultimo_encoding = None
        ultimo_usuario_id = None
        cv2.rectangle(frame, (left, top), (right, bottom), (217, 119, 6), 2)
        return frame, None, mensaje_postura, None
    
    # 4. Extraer encoding (esta es la parte pesada, se hace sobre el frame original)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])
    if not encodings:
        ultimo_resultado = ((top, right, bottom, left), "MIRE AL FRENTE")
        ultimo_encoding = None
        ultimo_usuario_id = None
        cv2.rectangle(frame, (left, top), (right, bottom), (217, 119, 6), 2)
        return frame, None, "MIRE AL FRENTE", None

    face_encoding = encodings[0]
    
    nombre_detectado = "DESCONOCIDO"
    usuario_id = None
    if verificar_dimension(face_encoding) and len(encodings_db) > 0:
        distancias = face_recognition.face_distance(encodings_db, face_encoding)
        mejor_distancia = min(distancias)

        if mejor_distancia < 0.6:
            idx = np.argmin(distancias)

            usuario_id = usuarios_db[idx]  # ðŸ”¥ este es el ID
            nombre_detectado = obtener_nombre_usuario_por_id(usuario_id)  # ðŸ”¥ aquÃ­ lo conviertes a nombre

            registrar_acceso()

    # Guardar resultado para frames intermedios
    ultimo_resultado = ((top, right, bottom, left), nombre_detectado)
    ultimo_encoding = face_encoding
    ultimo_usuario_id = usuario_id

    # 5. Dibujo limpio (Solo el rectÃ¡ngulo)
    color = (16, 185, 129) if nombre_detectado != "DESCONOCIDO" else (239, 68, 68)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    return frame, face_encoding, nombre_detectado, usuario_id
    
def find_best_match(face_encoding, known_encodings, known_ids, threshold=0.45):
    import numpy as np

    if face_encoding is None:
        return None, None

    if known_encodings is None or len(known_encodings) == 0:
        return None, None

    if known_ids is None or len(known_ids) == 0:
        return None, None

    face_encoding = np.array(face_encoding, dtype=np.float64)

    distancias = []

    for enc in known_encodings:
        enc = np.array(enc, dtype=np.float64)

        # Asegurar que sea vector plano
        enc = enc.flatten()
        face_encoding_flat = face_encoding.flatten()

        distancia = np.linalg.norm(enc - face_encoding_flat)
        distancias.append(float(distancia))

    mejor_indice = int(np.argmin(distancias))
    mejor_distancia = float(distancias[mejor_indice])

    if mejor_distancia < threshold:
        return known_ids[mejor_indice], mejor_distancia

    return None, mejor_distancia
   
