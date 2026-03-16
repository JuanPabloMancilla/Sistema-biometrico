from app.database.database import get_connection
from datetime import datetime

# --- FUNCIÓN PARA BUSCAR EL ID DEL ROL ---
def obtener_id_rol_por_nombre(nombre_rol):
    """Busca el ID numérico del rol basado en su nombre (ej. 'ESTUDIANTE')"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Usamos UPPER para asegurar que coincida con lo que insertaste en SQL
        cursor.execute("SELECT id_rol FROM usuario_rol WHERE UPPER(nombre) = UPPER(?)", (nombre_rol.strip(),))
        res = cursor.fetchone()
        return res[0] if res else None
    finally:
        conn.close() # Importante para evitar el error "database is locked"

# --- TU FUNCIÓN DE INSERCIÓN ACTUAL ---
def insertar_usuario(nombre, a_paterno, a_materno, id_rol, id_facultad, id_carrera):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO usuario (nombre, a_paterno, a_materno, fecha_registro, id_rol, id_facultad, id_carrera)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, a_paterno, a_materno, fecha, id_rol, id_facultad, id_carrera))
        
        conn.commit() 
        print("✅ Usuario guardado exitosamente en la base de datos")
        return True
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False
    finally:
        conn.close() # Libera la base de datos para que no aparezca vacía en DB Browser