from app.database.database import get_connection
from datetime import datetime

def insertar_facultad(nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO facultad (nombre) VALUES (?)", (nombre,))
    conn.commit()
    conn.close()

def obtener_facultades():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM facultad")
    datos = cursor.fetchall()
    conn.close()
    return datos

def actualizar_facultad(id_facultad, nombre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE facultad SET nombre = ? WHERE id_facultad = ?", (nombre, id_facultad))
    conn.commit()
    conn.close()

def desactivar_facultad(id_facultad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE facultad SET estado = 0 WHERE id_facultad = ?", (id_facultad,))
    conn.commit()
    conn.close()