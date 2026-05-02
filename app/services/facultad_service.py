from app.database.database import get_connection

def obtener_todas_facultades():
    
    #Consulta todas las facultades de la base de datos
    #Retorna: lista de diccionarios con los datos de facultades
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id_facultad, nombre, estado FROM facultad")
        filas = cursor.fetchall()
        
        facultades = []
        for fila in filas:
            facultades.append({
                "id": fila[0],
                "nombre": fila[1],
                "estado": fila[2]
            })
        
        conn.close()
        return facultades
    
    except Exception as e:
        print(f"Error al obtener facultades: {e}")
        return []


def crear_facultad(nombre, estado=1):
    
    #Inserta una nueva facultad en la base de datos
    #Parámetros:
        #- nombre: str - Nombre de la facultad
        #- estado: int - 1=activa, 0=inactiva (default: 1)
    #Retorna: True si se creó, False si falló
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO facultad (nombre, estado) VALUES (?, ?)",
            (nombre, estado)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al crear facultad: {e}")
        return False


def actualizar_facultad(id_facultad, nombre, estado):

    #Actualiza una facultad existente
    #Parámetros:
        #- id_facultad: int - ID de la facultad a editar
        #- nombre: str - Nuevo nombre
        #- estado: int - Nuevo estado (1=activa, 0=inactiva)
    #Retorna: True si se actualizó, False si falló

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE facultad SET nombre = ?, estado = ? WHERE id_facultad = ?",
            (nombre, estado, id_facultad)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al actualizar facultad: {e}")
        return False


def desactivar_facultad(id_facultad):

    #Desactiva una facultad (cambia estado a 0)
    #Parámetros:
        #- id_facultad: int - ID de la facultad a desactivar
    #Retorna: True si se desactivó, False si falló

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE facultad SET estado = 0 WHERE id_facultad = ?",
            (id_facultad,)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al desactivar facultad: {e}")
        return False


def reactivar_facultad(id_facultad):

    #Reactiva una facultad (cambia estado a 1)
    #Parámetros:
        #- id_facultad: int - ID de la facultad a reactivar
    #Retorna: True si se reactivó, False si falló

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE facultad SET estado = 1 WHERE id_facultad = ?",
            (id_facultad,)
        )
        
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        print(f"Error al reactivar facultad: {e}")
        return False


def obtener_facultad_por_id(id_facultad):
    
    #Obtiene los datos de una facultad específica
    #Parámetros:
        #- id_facultad: int - ID de la facultad
    #Retorna: diccionario con los datos, o None si no existe
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id_facultad, nombre, estado FROM facultad WHERE id_facultad = ?",
            (id_facultad,)
        )
        
        fila = cursor.fetchone()
        conn.close()
        
        if fila is None:
            return None
        
        return {
            "id": fila[0],
            "nombre": fila[1],
            "estado": fila[2]
        }
    
    except Exception as e:
        print(f"Error al obtener facultad: {e}")
        return None