from app.database.database import get_connection
from datetime import datetime

# ─────────────────────────────────────────────
#  CONSULTAS
# ─────────────────────────────────────────────

def obtener_todos_usuarios():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.a_paterno, u.a_materno, u.estado,
                   u.fecha_registro, u.fecha_actualizacion,
                   u.tipo_usuario,
                   u.cuenta,
                   u.correo,
                   f.nombre,
                   c.nombre
            FROM usuario u
            LEFT JOIN facultad f ON u.id_facultad = f.id_facultad
            LEFT JOIN carrera c ON u.id_carrera = c.id_carrera
        """)

        filas = cursor.fetchall()

        return [{
            "id_usuario": f[0],
            "nombre": f[1],
            "a_paterno": f[2],
            "a_materno": f[3],
            "estado": f[4],
            "fecha_registro": f[5],
            "fecha_actualizacion": f[6],
            "tipo_usuario": f[7],
            "cuenta": f[8],
            "correo": f[9],
            "facultad_nombre": f[10],
            "carrera_nombre": f[11],
        } for f in filas]

    except Exception as e:
        print(f"❌ Error: {e}")
        return []
    finally:
        conn.close()

def usuario_activo(id_usuario):
    if id_usuario is None:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT estado
        FROM usuario
        WHERE id_usuario = ?
    """, (id_usuario,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return False
    
    return int(row[0]) == 1


def obtener_usuario_por_id(id_usuario):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_usuario, nombre, a_paterno, a_materno,
                   tipo_usuario, id_facultad, id_carrera, cuenta, correo
            FROM usuario
            WHERE id_usuario = ?
        """, (id_usuario,))

        f = cursor.fetchone()

        if not f:
            return None

        return {
            "id": f[0],
            "nombre": f[1],
            "a_paterno": f[2],
            "a_materno": f[3],
            "tipo_usuario": f[4],
            "id_facultad": f[5],
            "id_carrera": f[6],
            "cuenta": f[7],
            "correo": f[8],
        }

    finally:
        conn.close()


# ─────────────────────────────────────────────
#  CRUD
# ─────────────────────────────────────────────

def crear_usuario(nombre, a_paterno, a_materno, tipo_usuario, id_facultad, id_carrera, cuenta, correo):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO usuario (
                nombre, a_paterno, a_materno,
                cuenta, correo,
                tipo_usuario,
                fecha_registro,
                id_facultad, id_carrera,
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (nombre, a_paterno, a_materno, str(cuenta), correo, tipo_usuario, fecha, id_facultad, id_carrera))

        conn.commit()

        # 🔥 ESTO ES LO IMPORTANTE
        return cursor.lastrowid

    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")
        return None
    finally:
        conn.close()

def actualizar_usuario(id_usuario, nombre, ap, am, cuenta, tipo_usuario, id_facultad, id_carrera, correo, estado=1):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuario
            SET nombre = ?, 
                a_paterno = ?, 
                a_materno = ?,
                cuenta = ?,
                tipo_usuario = ?, 
                id_facultad = ?, 
                id_carrera = ?,
                correo = ?,
                estado = ?,
                fecha_actualizacion = datetime('now')
            WHERE id_usuario = ?
        """, (nombre, ap, am, cuenta, tipo_usuario, id_facultad, id_carrera, correo, estado, id_usuario))

        conn.commit()
        return cursor.rowcount > 0

    except Exception as e:
        print("❌ Error al actualizar:", e)
        return False
    finally:
        conn.close()
        
def eliminar_usuario(id_usuario):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id_usuario = ?", (id_usuario,))
        conn.commit()
        return True
    finally:
        conn.close()

def desactivar_usuario(id_usuario):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuario
            SET estado = 0
            WHERE id_usuario = ?
        """, (id_usuario,))
        conn.commit()
        return True
    finally:
        conn.close()

def reactivar_usuario(id_usuario):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuario
            SET estado = 1
            WHERE id_usuario = ?
        """, (id_usuario,))
        conn.commit()
        return True
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────

def obtener_facultades_para_dropdown():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_facultad, nombre FROM facultad WHERE estado=1")
        return {f[0]: f[1] for f in cursor.fetchall()}
    finally:
        conn.close()


def obtener_carreras_por_facultad(id_facultad):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_carrera, nombre FROM carrera WHERE id_facultad=? AND estado=1", (id_facultad,))
        return {f[0]: f[1] for f in cursor.fetchall()}
    finally:
        conn.close()

from app.database.database import get_connection

def existe_cuenta(cuenta, excluir_id=None):
    conn = get_connection()
    cursor = conn.cursor()

    if excluir_id:
        cursor.execute("""
            SELECT id_usuario
            FROM usuario
            WHERE cuenta = ? AND id_usuario != ?
        """, (cuenta, excluir_id))
    else:
        cursor.execute("""
            SELECT id_usuario
            FROM usuario
            WHERE cuenta = ?
        """, (cuenta,))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None


def existe_correo(correo, excluir_id=None):

    if not correo:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    if excluir_id:
        cursor.execute("""
            SELECT id_usuario
            FROM usuario
            WHERE correo = ? AND id_usuario != ?
        """, (correo, excluir_id))
    else:
        cursor.execute("""
            SELECT id_usuario
            FROM usuario
            WHERE correo = ?
        """, (correo,))

    resultado = cursor.fetchone()

    conn.close()

    return resultado is not None

def obtener_usuario_por_cuenta(cuenta):
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id_usuario, nombre, a_paterno, a_materno,
                correo, id_rol, id_facultad
            FROM usuario
            WHERE cuenta = ?
        """, (str(cuenta),))

        f = cursor.fetchone()

        if not f:
            return None

        return {
            "id": f[0],
            "nombre": f[1],
            "a_paterno": f[2],
            "a_materno": f[3],
            "correo": f[4],
            "id_rol": f[5],
            "id_facultad": f[6],
        }

    finally:
        conn.close()

def obtener_id_facultad_por_nombre(nombre):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id_facultad FROM facultad WHERE nombre = ?", (nombre,))
        resultado = cursor.fetchone()

        conn.close()

        return resultado[0] if resultado else None

def obtener_nombre_usuario_por_id(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, a_paterno, a_materno
        FROM usuario
        WHERE id_usuario = ?
    """, (usuario_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return f"{result[0]} {result[1]} {result[2]}"
    return "DESCONOCIDO"