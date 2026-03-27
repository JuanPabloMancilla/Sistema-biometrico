import sqlite3
from app.database.database import get_connection
from datetime import datetime

# -------------------------------
# CREAR USUARIO
# -------------------------------
def insertar_usuario(nombre, a_paterno, a_materno, id_rol, id_facultad=None, id_carrera=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO usuario (
                nombre, a_paterno, a_materno,
                estado, fecha_registro,
                id_rol, id_facultad, id_carrera
            )
            VALUES (?, ?, ?, 1, ?, ?, ?, ?)
        """, (nombre, a_paterno, a_materno, fecha, id_rol, id_facultad, id_carrera))

        conn.commit()
        return True, "✅ Usuario guardado"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        conn.close()



def crear_usuario(*args, **kwargs):
    return insertar_usuario(*args, **kwargs)


# -------------------------------
# OBTENER USUARIOS (RAW)
# -------------------------------
def obtener_usuarios():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario")
        return cursor.fetchall()
    finally:
        conn.close()


# -------------------------------
# OBTENER USUARIOS FORMATEADOS
# -------------------------------
def obtener_usuarios_formateados():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                u.id_usuario,
                u.nombre,
                u.a_paterno,
                u.a_materno,
                r.nombre,
                f.nombre
            FROM usuario u
            LEFT JOIN usuario_rol r ON u.id_rol = r.id_rol
            LEFT JOIN facultad f ON u.id_facultad = f.id_facultad
            WHERE u.estado = 1
        """)

        filas = cursor.fetchall()

        return [
            {
                "id": f[0],
                "nombre": f"{f[1]} {f[2]} {f[3] if f[3] else ''}".strip(),
                "rol": f[4],
                "facultad": f[5]
            }
            for f in filas
        ]
    finally:
        conn.close()


# -------------------------------
# OBTENER ID POR NOMBRE
# -------------------------------
def obtener_id_facultad_por_nombre(nombre):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_facultad FROM facultad WHERE nombre = ?", (nombre,))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()


def obtener_id_rol_por_nombre(nombre):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_rol FROM usuario_rol WHERE UPPER(nombre) = UPPER(?)",
            (nombre,)
        )
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()


# -------------------------------
# ACTUALIZAR USUARIO
# -------------------------------
def actualizar_usuario(id_usuario, nombre=None, a_paterno=None, a_materno=None, id_rol=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        campos = []
        params = []

        if nombre:
            campos.append("nombre = ?")
            params.append(nombre)
        if a_paterno:
            campos.append("a_paterno = ?")
            params.append(a_paterno)
        if a_materno:
            campos.append("a_materno = ?")
            params.append(a_materno)
        if id_rol:
            campos.append("id_rol = ?")
            params.append(id_rol)

        campos.append("fecha_actualizacion = ?")
        params.append(fecha)

        query = "UPDATE usuario SET " + ", ".join(campos) + " WHERE id_usuario = ?"
        params.append(id_usuario)

        cursor.execute(query, tuple(params))
        conn.commit()

        return True
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# -------------------------------
# DESACTIVAR USUARIO (BORRADO LÓGICO)
# -------------------------------
def desactivar_usuario(id_usuario):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            UPDATE usuario 
            SET estado = 0, fecha_actualizacion = ?
            WHERE id_usuario = ?
        """, (fecha, id_usuario))

        conn.commit()
        return True
    except Exception as e:
        print(f"Error al desactivar: {e}")
        return False
    finally:
        conn.close()