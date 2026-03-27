from app.database.database import get_connection

def obtener_registros_acceso():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_registro, id_usuario, fecha_hora, resultado
            FROM registro_acceso
            ORDER BY fecha_hora DESC
        """)

        filas = cursor.fetchall()

        registros = []
        for fila in filas:
            registros.append({
                "id": fila[0],
                "id_usuario": fila[1],
                "fecha_hora": fila[2],
                "resultado": fila[3]
            })

        return registros

    except Exception as e:
        print(f"Error al obtener registros: {e}")
        return []

    finally:
        conn.close()