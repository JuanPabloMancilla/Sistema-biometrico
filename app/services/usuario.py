import sqlite3 # IMPORTANTE: Se debe importar para manejar los IntegrityError
from app.database.database import get_connection
from datetime import datetime

def obtener_usuarios_formateados():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Seleccionamos explícitamente a_materno
        cursor.execute("""
            SELECT u.nombre, u.a_paterno, u.a_materno, u.cuenta, r.nombre, f.nombre, u.correo
            FROM usuario u
            LEFT JOIN usuario_rol r ON u.id_rol = r.id_rol
            LEFT JOIN facultad f ON u.id_facultad = f.id_facultad
            WHERE u.estado = 1
        """)
        filas = cursor.fetchall()
        return [
            {
                "nombre_solo": f[0], 
                "ap": f[1], 
                "am": f[2] if f[2] else "", # <--- Aquí capturamos el materno
                "c": f[3], 
                "r": f[4], 
                "f": f[5], 
                "m": f[6],
                "n": f"{f[0]} {f[1]} {f[2] if f[2] else ''}".strip() # Para mostrar en la tabla
            } for f in filas
        ]
    finally:
        conn.close()

def obtener_id_facultad_por_nombre(nombre):
    """Busca el ID de la facultad por su nombre exacto"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_facultad FROM facultad WHERE nombre = ?", (nombre,))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()

def obtener_id_rol_por_nombre(nombre):
    """Busca el ID del rol (ESTUDIANTE, DOCENTE, etc)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_rol FROM usuario_rol WHERE UPPER(nombre) = UPPER(?)", (nombre,))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()

def insertar_usuario(nombre, a_paterno, a_materno, id_rol, id_facultad, id_carrera, cuenta, correo):
    """Inserta un nuevo usuario manejando errores de cuenta duplicada"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO usuario (nombre, a_paterno, a_materno, fecha_registro, id_rol, id_facultad, id_carrera, cuenta, correo, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (nombre, a_paterno, a_materno, fecha, id_rol, id_facultad, id_carrera, int(cuenta), correo))
        
        conn.commit()
        return True, "✅ Usuario guardado exitosamente"
    except sqlite3.IntegrityError:
        return False, "⚠️ Error: El número de cuenta ya está registrado."
    except Exception as e:
        return False, f"❌ Error al guardar: {e}"
    finally:
        conn.close()

def actualizar_usuario(cuenta, nombre, a_paterno, a_materno, id_rol, id_facultad, correo):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # IMPORTANTE: Aseguramos que el estado vuelva a 1 al editar
        cursor.execute("""
            UPDATE usuario 
            SET nombre = ?, a_paterno = ?, a_materno = ?, id_rol = ?, 
                id_facultad = ?, correo = ?, fecha_actualizacion = ?, estado = 1
            WHERE cuenta = ?
        """, (nombre, a_paterno, a_materno, id_rol, id_facultad, correo, fecha, cuenta))
        
        conn.commit()
        return cursor.rowcount > 0, "✅ Cambios aplicados"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()

def desactivar_usuario(id_usuario):
    """Realiza un borrado lógico del usuario cambiando su estado a 0"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE usuario SET estado = 0, fecha_actualizacion = ? 
            WHERE id_usuario = ?
        """, (fecha, id_usuario))
        conn.commit()
        return True
    finally:
        conn.close()
        
