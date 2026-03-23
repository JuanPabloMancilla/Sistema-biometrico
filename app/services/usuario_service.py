from app.database.database import get_connection
from datetime import datetime

# --- FUNCIÓN PARA BUSCAR EL ID DEL ROL ---
def obtener_id_rol_por_nombre(nombre_rol):
    """Busca el ID numérico del rol basado en su nombre (ej. 'ESTUDIANTE')"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id_rol FROM usuario_rol WHERE UPPER(nombre) = UPPER(?)", (nombre_rol.strip(),))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close()

# --- FUNCIÓN DE INSERCIÓN ACTUALIZADA (AHORA CON 8 PARÁMETROS) ---
def insertar_usuario(nombre, a_paterno, a_materno, id_rol, id_facultad, id_carrera, cuenta, correo):
    """
    Guarda un usuario incluyendo cuenta y correo.
    Validado para recibir los 8 parámetros desde la View.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Agregamos 'cuenta' y 'correo' tanto en las columnas como en los VALUES
        # También forzamos estado = 1 (Activo) por defecto
        cursor.execute("""
            INSERT INTO usuario (
                nombre, 
                a_paterno, 
                a_materno, 
                cuenta, 
                correo, 
                fecha_registro, 
                id_rol, 
                id_facultad, 
                id_carrera, 
                estado
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (nombre, a_paterno, a_materno, str(cuenta), correo, fecha, id_rol, id_facultad, id_carrera))
        
        conn.commit() 
        print(f"✅ Usuario {nombre} con cuenta {cuenta} guardado exitosamente.")
        return True
    except Exception as e:
        print(f"❌ Error al guardar en usuario_service: {e}")
        return False
    finally:
        conn.close()

# --- FUNCIÓN DE ACTUALIZACIÓN ---
def actualizar_usuario(cuenta, nombre, a_paterno, a_materno, id_rol, id_facultad, correo):
    """Actualiza los datos de un usuario existente basado en su número de cuenta"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE usuario 
            SET nombre = ?, a_paterno = ?, a_materno = ?, id_rol = ?, 
                id_facultad = ?, correo = ?, fecha_actualizacion = ?
            WHERE cuenta = ?
        """, (nombre, a_paterno, a_materno, id_rol, id_facultad, correo, fecha, str(cuenta)))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ Error al actualizar: {e}")
        return False
    finally:
        conn.close()