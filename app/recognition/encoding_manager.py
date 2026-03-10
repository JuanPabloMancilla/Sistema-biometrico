import face_recognition
import json
import os


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

def obtener_siguiente_usuario(archivo="encodings.json"):

    if not os.path.exists(archivo):
        return "usuario_1"

    with open(archivo, "r") as f:
        datos = json.load(f)

    numero = len(datos) + 1

    return f"usuario_{numero}"

# Guardar encoding en JSON
def guardar_encoding(encoding, archivo="encodings.json"):

    usuario_id = obtener_siguiente_usuario(archivo)

    datos_usuario = {
        "usuario": usuario_id,
        "encoding": encoding.tolist()
    }

    if os.path.exists(archivo):

        with open(archivo, "r") as f:
            datos = json.load(f)

    else:
        datos = []

    datos.append(datos_usuario)

    with open(archivo, "w") as f:
        json.dump(datos, f, indent=4)

    print(f"Encoding guardado como {usuario_id}")


# Comparar distancia entre rostros
def comparar_encodings(encoding_guardado, encoding_actual):

    distancia = face_recognition.face_distance(
        [encoding_guardado],
        encoding_actual
    )[0]

    return distancia