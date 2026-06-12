import face_recognition
import json
import os
import numpy as np

def generar_face_encoding(frame_rgb):

    encodings = face_recognition.face_encodings(frame_rgb)

    if len(encodings) == 0:
        return None

    encoding = encodings[0]

    return encoding

def verificar_dimension(encoding):

    if encoding is None:
        return False

    return len(encoding) == 128

def cargar_encodings(archivo="encodings.json"):

    if not os.path.exists(archivo):
        return [], []

    with open(archivo, "r") as f:
        datos = json.load(f)

    encodings = []
    usuarios = []

    for usuario in datos:
        encodings.append(np.array(usuario["encoding"]))
        usuarios.append(usuario["usuario"])

    return encodings, usuarios

def compare_embeddings(embedding1, embedding2):

    distancia = face_recognition.face_distance(
        [embedding1],
        embedding2
    )[0]

    return distancia

def find_best_match(
    encoding_actual,
    encoding_db,
    usuarios_db,
    threshold=0.42
):

    mejor_distancia = float("inf")
    mejor_usuario = None

    for i, encoding_guardado in enumerate(encoding_db):

        distancia = compare_embeddings(
            encoding_guardado,
            encoding_actual
        )

        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_usuario = usuarios_db[i]

    if mejor_distancia < threshold:

        return mejor_usuario, mejor_distancia

    return None, mejor_distancia

def guardar_encoding(
    usuario,
    encoding,
    archivo="encodings.json",
    reemplazar=False
):

    if encoding is None:

        return {
            "ok": False,
            "error": "No hay encoding facial"
        }

    muestras = encoding if isinstance(encoding, (list, tuple)) else [encoding]
    muestras = [np.array(muestra) for muestra in muestras]

    if not muestras or any(len(muestra) != 128 for muestra in muestras):

        return {
            "ok": False,
            "error": "Encoding inválido"
        }

    if os.path.exists(archivo):

        with open(archivo, "r") as f:
            datos = json.load(f)

    else:
        datos = []

    # ============================================
    # VALIDAR USUARIO DUPLICADO
    # ============================================

    for existente in datos:

        mismo_usuario = (
            str(existente["usuario"]) == str(usuario)
        )

        # ? SOLO bloquear si NO estamos reemplazando
        if mismo_usuario and not reemplazar:

            return {
                "ok": False,
                "error": "usuario_duplicado"
            }

    # ============================================
    # VALIDAR ROSTRO DUPLICADO
    # ============================================

    for existente in datos:

        mismo_usuario = (
            str(existente["usuario"]) == str(usuario)
        )

        # ? IGNORAR SU PROPIO ROSTRO
        if mismo_usuario:
            continue

        encoding_existente = np.array(existente["encoding"])
        for muestra in muestras:
            distancia = face_recognition.face_distance([encoding_existente], muestra)[0]
            if distancia < 0.45:
                return {
                    "ok": False,
                    "error": "rostro_duplicado",
                    "usuario_duplicado": existente["usuario"],
                    "distancia": float(distancia)
                }

    # ============================================
    # REEMPLAZAR BIOMETR�A
    # ============================================

    if reemplazar:

        datos = [
            u for u in datos
            if str(u["usuario"]) != str(usuario)
        ]

    datos.extend({
        "usuario": usuario,
        "encoding": muestra.tolist()
    } for muestra in muestras)

    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

    return {
        "ok": True,
        "muestras": len(muestras)
    }

def comparar_encodings(encoding_guardado, encoding_actual):

    distancia = face_recognition.face_distance(
        [encoding_guardado],
        encoding_actual
    )[0]

    return distancia

def eliminar_encoding(usuario_id, archivo="encodings.json"):
    if not os.path.exists(archivo):
        return

    with open(archivo, "r") as f:
        datos = json.load(f)

    datos = [u for u in datos if str(u["usuario"]) != str(usuario_id)]

    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)
