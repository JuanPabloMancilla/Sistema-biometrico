import time

from app.recognition.encoding_manager import cargar_encodings, find_best_match

def reconocer_usuario(encoding_actual, threshold=0.6):

    encodings_db, usuarios_db = cargar_encodings()

    inicio = time.time()

    index, distancia = find_best_match(
        encoding_actual,
        encodings_db,
        threshold
    )

    tiempo = time.time() - inicio

    if index is not None:
        usuario = usuarios_db[index]
    else:
        usuario = "Desconocido"

    print("Tiempo reconocimiento:", tiempo)

    return usuario, distancia, tiempo