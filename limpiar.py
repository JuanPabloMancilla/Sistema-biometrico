from app.database.database import get_connection
import json

conn = get_connection()
cursor = conn.cursor()

cursor.execute("DELETE FROM usuario")
cursor.execute("DELETE FROM registro_acceso")
cursor.execute("DELETE FROM biometria")

conn.commit()
conn.close()

with open("encodings.json", "w") as f:
    json.dump([], f, indent=4)

print("Usuarios y encodings eliminados correctamente")