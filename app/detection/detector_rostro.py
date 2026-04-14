import cv2
import face_recognition
import numpy as np
from app.recognition.encoding_manager import (
    verificar_dimension,
    guardar_encoding,
    cargar_encodings
)

# --- CACHÉ DE DATOS ---
encodings_db, usuarios_db = cargar_encodings()
ultimo_resultado = (None, "ESCANEANDO...")
frame_count = 0

def procesar_frame(frame):
    global encodings_db, usuarios_db, ultimo_resultado, frame_count
    
    frame_count += 1
    # OPTIMIZACIÓN: Solo procesar reconocimiento cada 3 frames para evitar lag
    if frame_count % 3 != 0 and ultimo_resultado[0] is not None:
        top, right, bottom, left = ultimo_resultado[0]
        cv2.rectangle(frame, (left, top), (right, bottom), (10, 185, 129), 2)
        return frame, None, ultimo_resultado[1]

    # 1. Reducir imagen para detección rápida (Escala 1/4)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # 2. Detección con modelo HOG (el más rápido en CPU)
    face_locations = face_recognition.face_locations(rgb_small, model="hog")
    
    if not face_locations:
        ultimo_resultado = (None, "No se detectó ninguna cara")
        return frame, None, "No se detectó ninguna cara"

    if len(face_locations) > 1:
        return frame, None, "Se detectaron múltiples caras"

    # 3. Reescalar coordenadas al tamaño original
    top, right, bottom, left = [v * 4 for v in face_locations[0]]
    
    # 4. Extraer encoding (esta es la parte pesada, se hace sobre el frame original)
    face_encoding = face_recognition.face_encodings(frame, [(top, right, bottom, left)])[0]
    
    nombre_detectado = "DESCONOCIDO"
    if verificar_dimension(face_encoding) and len(encodings_db) > 0:
        distancias = face_recognition.face_distance(encodings_db, face_encoding)
        mejor_distancia = min(distancias)

        if mejor_distancia < 0.6:
            idx = np.argmin(distancias)
            nombre_detectado = usuarios_db[idx]
        
    # Guardar resultado para frames intermedios
    ultimo_resultado = ((top, right, bottom, left), nombre_detectado)

    # 5. Dibujo limpio (Solo el rectángulo)
    color = (16, 185, 129) if nombre_detectado != "DESCONOCIDO" else (239, 68, 68)
    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

    return frame, face_encoding, nombre_detectado