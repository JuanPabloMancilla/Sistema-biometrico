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

def obtener_configuracion_asistencia():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT hora_entrada, tolerancia_minutos,
               jornada_objetivo_minutos, descanso_minutos
        FROM configuracion_asistencia
        WHERE id_configuracion = 1
        """
    )
    fila = cursor.fetchone()
    conn.close()
    if not fila:
        return {
            "hora_entrada": "09:00",
            "tolerancia_minutos": 10,
            "jornada_objetivo_minutos": 480,
            "descanso_minutos": 0,
        }
    return {
        "hora_entrada": fila[0],
        "tolerancia_minutos": int(fila[1]),
        "jornada_objetivo_minutos": int(fila[2]),
        "descanso_minutos": int(fila[3]),
    }


def guardar_configuracion_asistencia(
    hora_entrada, tolerancia_minutos, jornada_objetivo_minutos, descanso_minutos
):
    datetime.strptime(hora_entrada, "%H:%M")
    valores = [
        int(tolerancia_minutos),
        int(jornada_objetivo_minutos),
        int(descanso_minutos),
    ]
    if any(valor < 0 for valor in valores) or valores[1] == 0:
        raise ValueError("La configuracion de asistencia no es valida")

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO configuracion_asistencia
            (id_configuracion, hora_entrada, tolerancia_minutos,
             jornada_objetivo_minutos, descanso_minutos)
        VALUES (1, ?, ?, ?, ?)
        ON CONFLICT(id_configuracion) DO UPDATE SET
            hora_entrada = excluded.hora_entrada,
            tolerancia_minutos = excluded.tolerancia_minutos,
            jornada_objetivo_minutos = excluded.jornada_objetivo_minutos,
            descanso_minutos = excluded.descanso_minutos
        """,
        (hora_entrada, *valores),
    )
    conn.commit()
    conn.close()


def calcular_metricas_jornada(fecha_entrada, segundos_trabajados, configuracion):
    entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d %H:%M:%S")
    hora, minuto = [int(valor) for valor in configuracion["hora_entrada"].split(":")]
    limite = entrada.replace(hour=hora, minute=minuto, second=0)
    limite = limite.timestamp() + configuracion["tolerancia_minutos"] * 60
    retardo_segundos = max(0, int(entrada.timestamp() - limite))

    descanso = configuracion["descanso_minutos"] * 60
    segundos_netos = max(0, int(segundos_trabajados) - descanso)
    objetivo = configuracion["jornada_objetivo_minutos"] * 60
    extra_segundos = max(0, segundos_netos - objetivo)
    return {
        "retardo_segundos": retardo_segundos,
        "extra_segundos": extra_segundos,
        "segundos_netos": segundos_netos,
    }


def obtener_ultima_jornada_usuario(id_usuario, fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id_jornada, fecha_entrada, fecha_salida, estado
        FROM jornada_laboral
        WHERE id_usuario = ? AND DATE(fecha_entrada) BETWEEN ? AND ?
        ORDER BY fecha_entrada DESC
        LIMIT 1
        """,
        (id_usuario, fecha_inicio, fecha_fin),
    )
    fila = cursor.fetchone()
    conn.close()
    return fila


def corregir_jornada(id_jornada, fecha_entrada, fecha_salida=None):
    entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d %H:%M:%S")
    salida = datetime.strptime(fecha_salida, "%Y-%m-%d %H:%M:%S") if fecha_salida else None
    if salida and salida < entrada:
        raise ValueError("La salida no puede ser anterior a la entrada")

    duracion = int((salida - entrada).total_seconds()) if salida else None
    estado = "finalizada" if salida else "trabajando"
    conn = get_connection()
    conn.execute(
        """
        UPDATE jornada_laboral
        SET fecha_entrada = ?, fecha_salida = ?, duracion_segundos = ?, estado = ?
        WHERE id_jornada = ?
        """,
        (fecha_entrada, fecha_salida, duracion, estado, id_jornada),
    )
    conn.commit()
    conn.close()


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
