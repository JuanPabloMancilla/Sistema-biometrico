import time

from app.recognition.encoding_manager import cargar_encodings, find_best_match

def reconocer_usuario(encoding_actual, threshold=0.42):

    encodings_db, usuarios_db = cargar_encodings()

    inicio = time.time()

    usuario_id, distancia = find_best_match(
        encoding_actual,
        encodings_db,
        usuarios_db,
        threshold
    )

    tiempo = time.time() - inicio

    usuario = usuario_id if usuario_id is not None else "Desconocido"

    print("Tiempo reconocimiento:", tiempo)

    return usuario, distancia, tiempo
