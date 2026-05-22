from app.database import get_connection

conn = get_connection()
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuario ADD COLUMN cuenta TEXT;")
    cursor.execute("ALTER TABLE usuario ADD COLUMN correo TEXT;")
    conn.commit()
    print("Columnas agregadas correctamente")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()