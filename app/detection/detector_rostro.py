import cv2
import face_recognition
import numpy as np


from app.recognition.encoding_manager import (
    verificar_dimension,
    guardar_encoding,
    cargar_encodings
)

ultimo_encoding = None

def procesar_frame(frame):
    #Esto convertira el frame de BGR a RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #Este detectara las caras en el frame
    face_locations = face_recognition.face_locations(rgb)

    num_faces = len(face_locations)

    #Politicas de deteccion

    if num_faces == 0:
        return frame, None, "No se detectó ninguna cara"
    
    if num_faces > 1:
        return frame, None, "Se detectaron múltiples caras"
    
    #Puntos clave para la deteccion de rostro
    face_landmarks = face_recognition.face_landmarks(rgb, face_locations)

    landmarks = face_landmarks[0]

    #Dibujar landmarks
    for feature in landmarks.values():
        for (x, y) in feature:
            cv2.circle(frame, (x, y), 1, (255, 0, 255), -1)

    left_eye = landmarks['left_eye']
    right_eye = landmarks['right_eye']

    left_eye_center = np.mean(left_eye, axis=0).astype(int)
    right_eye_center = np.mean(right_eye, axis=0).astype(int)

    cv2.circle(frame, tuple(left_eye_center), 3, (255,0,0), -1)
    cv2.circle(frame, tuple(right_eye_center), 3, (255,0,0), -1)

    #Angulo de rotacion
    dY = right_eye_center[1] - left_eye_center[1]
    dX = right_eye_center[0] - left_eye_center[0]

    angle = np.degrees(np.arctan2(dY, dX))

    #Centro de ojos
    eyes_center = (
        int((left_eye_center[0] + right_eye_center[0]) / 2),
        int((left_eye_center[1] + right_eye_center[1]) / 2)
    )

    #rotar imagen
    M = cv2.getRotationMatrix2D(eyes_center, angle, 1)
    aligned_frame = cv2.warpAffine(frame, M, (frame.shape[1], frame.shape[0]))

    #Detectar rostro nuevamente
    rgb_aligned = cv2.cvtColor(aligned_frame, cv2.COLOR_BGR2RGB)
    face_locations_aligned = face_recognition.face_locations(rgb_aligned)

    if len(face_locations_aligned) == 0:
        return aligned_frame, None, "No se detectó ninguna cara"

    #Vector numérico de la cara
    face_encoding = face_recognition.face_encodings(rgb, face_locations)[0]
    
    if verificar_dimension(face_encoding):

        encodings_guardados, usuarios = cargar_encodings()

        if len(encodings_guardados) > 0:

            distancias = face_recognition.face_distance(
                encodings_guardados,
                face_encoding
            )

            mejor_distancia = min(distancias)

            if mejor_distancia < 0.6:
                print("Este rostro ya está registrado")
            else:
                guardar_encoding(face_encoding)
                print("Nuevo rostro registrado")

        else:
            guardar_encoding(face_encoding)
            print("Primer rostro registrado")

    #Dibujar un rectángulo alrededor de la cara detectada
    top, right, bottom, left = face_locations[0]
    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    #Dibujar puntos clave en la cara
    for (x,y) in face_landmarks[0]['chin']:
        cv2.circle(frame, (x,y), 1, (0, 0, 255), -1)

    return frame, face_encoding, "Cara detectada correctamente"
