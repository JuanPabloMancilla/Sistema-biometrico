import json
import numpy as np
import face_recognition

#Cargar encodings guardados
with open("encodings.json", "r") as f:
    data = json.load(f)

#Tomar dos encodings del archivo
encoding1 = np.array(data[0]["encoding"])
encoding2 = np.array(data[1]["encoding"])

#Calcular distancia
distancia = face_recognition.face_distance([encoding1], encoding2)

print("Distancia entre encodings:", distancia[0])