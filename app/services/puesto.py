from app.database.database import get_connection

def insertar_carrera(nombre, id_facultad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carrera (nombre, id_facultad) VALUES (?, ?)", (nombre, id_facultad))
    conn.commit()
    conn.close()

def obtener_carreras():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM carrera")
    datos = cursor.fetchall()
    conn.close()
    return datos

def actualizar_carrera(id_carrera, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE carrera SET nombre = ? WHERE id_carrera = ?", (nombre, id_carrera))
    conn.commit()
    conn.close()

def desactivar_carrera(id_carrera):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE carrera SET estado = 0 WHERE id_carrera = ?", (id_carrera,))
    conn.commit()
    conn.close()