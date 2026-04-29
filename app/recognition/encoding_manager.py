import face_recognition
import json
import os
import numpy as np


# Generar encoding facial
def generar_face_encoding(frame_rgb):

    encodings = face_recognition.face_encodings(frame_rgb)

    if len(encodings) == 0:
        return None

    encoding = encodings[0]

    return encoding


# Verificar que tenga dimensión 128
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

def find_best_match(encoding_actual, encoding_db, threshold=0.6):

    mejor_distancia = float("inf")
    mejor_index = None

    for i, encoding_guardado in enumerate(encoding_db):

        distancia = compare_embeddings(
            encoding_guardado,
            encoding_actual
        )
        if distancia < mejor_distancia:
            mejor_distancia = distancia
            mejor_index = i

    if mejor_distancia < threshold:
        return mejor_index, mejor_distancia
    else:
        return None, mejor_distancia

# Guardar encoding en JSON
def guardar_encoding(usuario, encoding, archivo="encodings.json"):

    datos_usuario = {
        "usuario": usuario,
        "encoding": encoding.tolist()
    }

    if os.path.exists(archivo):

        with open(archivo, "r") as f:
            datos = json.load(f)

    else:
        datos = []

    for existente in datos:
        encoding_existente = np.array(existente["encoding"])

        distancia = face_recognition.face_distance(
            [encoding_existente],
            encoding
        )[0]

        if distancia < 0.6:  # mismo rostro
            print("❌ Este rostro ya está registrado")
            return False

    datos.append(datos_usuario)

    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

    print(f"Encoding guardado como {usuario}")
    return True


# Comparar distancia entre rostros
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