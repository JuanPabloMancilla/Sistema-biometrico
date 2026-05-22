from app.database.database import get_connection
import json

conn = get_connection()
cursor = conn.cursor()

# Desactivar restricciones
cursor.execute("PRAGMA foreign_keys = OFF")

# Borrar accesos
cursor.execute("DELETE FROM registro_acceso")

# Borrar biometrías
cursor.execute("DELETE FROM biometria")

# Borrar usuarios
cursor.execute("DELETE FROM usuario")

# Reactivar restricciones
cursor.execute("PRAGMA foreign_keys = ON")

conn.commit()
conn.close()

# Limpiar encodings
with open("encodings.json", "w") as f:
    json.dump([], f)

print("✅ Sistema limpio")