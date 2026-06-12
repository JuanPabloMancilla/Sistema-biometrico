from datetime import datetime

from app.database.database import get_connection


def formatear_duracion(segundos):
    segundos = max(0, int(segundos or 0))
    horas, resto = divmod(segundos, 3600)
    minutos, segundos = divmod(resto, 60)

    if horas:
        return f"{horas} h {minutos} min"
    if minutos:
        return f"{minutos} min {segundos} s"
    return f"{segundos} s"


def registrar_marcaje(id_usuario, fecha_hora=None):
    ahora = fecha_hora or datetime.now()
    fecha_texto = ahora.strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute(
            """
            SELECT id_jornada, fecha_entrada
            FROM jornada_laboral
            WHERE id_usuario = ? AND estado = 'trabajando'
            ORDER BY fecha_entrada DESC
            LIMIT 1
            """,
            (id_usuario,),
        )
        jornada_abierta = cursor.fetchone()

        if jornada_abierta is None:
            cursor.execute(
                """
                INSERT INTO jornada_laboral
                    (id_usuario, fecha_entrada, estado)
                VALUES (?, ?, 'trabajando')
                """,
                (id_usuario, fecha_texto),
            )
            conn.commit()
            return {
                "tipo": "entrada",
                "estado": "Trabajando",
                "fecha_entrada": fecha_texto,
            }

        id_jornada, fecha_entrada = jornada_abierta
        entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d %H:%M:%S")
        duracion_segundos = max(0, int((ahora - entrada).total_seconds()))
        cursor.execute(
            """
            UPDATE jornada_laboral
            SET fecha_salida = ?, duracion_segundos = ?, estado = 'finalizada'
            WHERE id_jornada = ?
            """,
            (fecha_texto, duracion_segundos, id_jornada),
        )
        conn.commit()
        return {
            "tipo": "salida",
            "estado": "Finalizada",
            "fecha_entrada": fecha_entrada,
            "fecha_salida": fecha_texto,
            "duracion_segundos": duracion_segundos,
            "duracion_texto": formatear_duracion(duracion_segundos),
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
