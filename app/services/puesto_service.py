from app.database.database import get_connection

def obtener_todas_carreras():
    
    #Consulta todas las carreras de la base de datos con info de facultad
    #Retorna: lista de diccionarios con los datos de carreras
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # JOIN con facultad para obtener el nombre de la facultad
        cursor.execute("""
            SELECT c.id_carrera, c.nombre, c.id_facultad, f.nombre as facultad_nombre, c.estado 
            FROM carrera c
            LEFT JOIN facultad f ON c.id_facultad = f.id_facultad
        """)
        filas = cursor.fetchall()
        
        carreras = []
        for fila in filas:
            carreras.append({
                "id": fila[0],
                "nombre": fila[1],
                "id_facultad": fila[2],
                "facultad_nombre": fila[3],
                "estado": fila[4]
            })
        
        conn.close()
        return carreras
    
    except Exception as e:
        print(f"Error al obtener carreras: {e}")
        return []


def crear_carrera(nombre, id_facultad, estado=1):
    
    #Inserta una nueva carrera en la base de datos
    #ParÃ¡metros:
        #- nombre: str - Nombre de la carrera
        #- id_facultad: int - ID de la facultad a la que pertenece
        #- estado: int - 1=activa, 0=inactiva (default: 1)
    #Retorna: True si se creÃ³, False si fallÃ³
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO carrera (nombre, id_facultad, estado) VALUES (?, ?, ?)",
            (nombre, id_facultad, estado)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al crear carrera: {e}")
        return False


def actualizar_carrera(id_carrera, nombre, id_facultad, estado):
    
    #Actualiza una carrera existente
    #ParÃ¡metros:
        #- id_carrera: int - ID de la carrera a editar
        #- nombre: str - Nuevo nombre
        #- id_facultad: int - Nueva facultad
        #- estado: int - Nuevo estado (1=activa, 0=inactiva)
    #Retorna: True si se actualizÃ³, False si fallÃ³
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE carrera SET nombre = ?, id_facultad = ?, estado = ? WHERE id_carrera = ?",
            (nombre, id_facultad, estado, id_carrera)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al actualizar carrera: {e}")
        return False

def desactivar_carrera(id_carrera):
    """Desactiva una carrera sin eliminarla fÃ­sicamente"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE carrera SET estado = 0 WHERE id_carrera = ?",
            (id_carrera,)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al desactivar carrera: {e}")
        return False

def reactivar_carrera(id_carrera):
    """Reactiva una carrera inactiva"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE carrera SET estado = 1 WHERE id_carrera = ?",
            (id_carrera,)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al reactivar carrera: {e}")
        return False


def obtener_carrera_por_id(id_carrera):
    
    #Obtiene los datos de una carrera especÃ­fica
    #ParÃ¡metros:
        #- id_carrera: int - ID de la carrera
    #Retorna: diccionario con los datos, o None si no existe
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id_carrera, nombre, id_facultad, estado FROM carrera WHERE id_carrera = ?",
            (id_carrera,)
        )
        
        fila = cursor.fetchone()
        conn.close()
        
        if fila is None:
            return None
        
        return {
            "id": fila[0],
            "nombre": fila[1],
            "id_facultad": fila[2],
            "estado": fila[3]
        }
    
    except Exception as e:
        print(f"Error al obtener carrera: {e}")
        return None


def obtener_facultades_para_dropdown():
    
    #Obtiene lista de facultades para el dropdown
    #Retorna: diccionario {id_facultad: nombre_facultad}
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_facultad, nombre FROM facultad WHERE estado = 1")
        filas = cursor.fetchall()
        
        facultades = {}
        for fila in filas:
            facultades[fila[0]] = fila[1]
        
        conn.close()
        return facultades
    
    except Exception as e:
        print(f"Error al obtener facultades: {e}")
        return {}
    
def obtener_id_carrera_por_nombre(nombre):
    from app.database.database import get_connection

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_carrera
        FROM carrera
        WHERE nombre = ?
    """, (nombre,))

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None