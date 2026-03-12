import json
import numpy as np
import face_recognition

# Cargar encodings
with open("encodings.json", "r") as f:
    datos = json.load(f)

encodings = []
usuarios = []

for d in datos:
    encodings.append(np.array(d["encoding"]))
    usuarios.append(d["usuario"])


# Umbrales a probar
thresholds = [0.4, 0.5, 0.6, 0.7]

for threshold in thresholds:

    falsos_aceptados = 0
    falsos_rechazados = 0
    intentos_genuinos = 0
    intentos_impostores = 0

    for i in range(len(encodings)):
        for j in range(len(encodings)):

            if i == j:
                continue

            distancia = face_recognition.face_distance(
                [encodings[i]],
                encodings[j]
            )[0]

            misma_persona = usuarios[i] == usuarios[j]

            if misma_persona:

                intentos_genuinos += 1

                if distancia > threshold:
                    falsos_rechazados += 1

            else:

                intentos_impostores += 1

                if distancia < threshold:
                    falsos_aceptados += 1

    FAR = falsos_aceptados / intentos_impostores if intentos_impostores > 0 else 0
    FRR = falsos_rechazados / intentos_genuinos if intentos_genuinos > 0 else 0

    print("------------------------")
    print("Threshold:", threshold)
    print("FAR:", FAR)
    print("FRR:", FRR)