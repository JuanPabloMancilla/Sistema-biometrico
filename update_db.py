import sqlite3

conn = sqlite3.connect("tu_base_de_datos.db")  # ← pon aquí el nombre real
cursor = conn.cursor()

# Agregar columnas
cursor.execute("ALTER TABLE usuario ADD COLUMN cuenta TEXT;")
cursor.execute("ALTER TABLE usuario ADD COLUMN correo TEXT;")

conn.commit()
conn.close()

print("✅ Columnas agregadas correctamente")