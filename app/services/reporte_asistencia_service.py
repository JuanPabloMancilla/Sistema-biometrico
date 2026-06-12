import csv
from datetime import datetime

from app.database.database import get_connection
from app.services.asistencia_service import formatear_duracion


def obtener_reporte_asistencia(fecha_inicio, fecha_fin, ahora=None):
    ahora = ahora or datetime.now()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            u.id_usuario,
            u.nombre,
            u.a_paterno,
            u.a_materno,
            u.cuenta,
            COUNT(j.id_jornada) AS jornadas,
            MIN(j.fecha_entrada) AS primera_entrada,
            MAX(j.fecha_salida) AS ultima_salida,
            SUM(CASE WHEN j.estado = 'trabajando' THEN 1 ELSE 0 END) AS abiertas,
            SUM(COALESCE(j.duracion_segundos, 0)) AS segundos_cerrados,
            MIN(CASE WHEN j.estado = 'trabajando' THEN j.fecha_entrada END) AS entrada_abierta
        FROM usuario u
        JOIN jornada_laboral j ON j.id_usuario = u.id_usuario
        WHERE DATE(j.fecha_entrada) BETWEEN ? AND ?
        GROUP BY u.id_usuario, u.nombre, u.a_paterno, u.a_materno, u.cuenta
        ORDER BY u.a_paterno, u.a_materno, u.nombre
        """,
        (fecha_inicio, fecha_fin),
    )
    filas = cursor.fetchall()
    conn.close()

    reporte = []
    for fila in filas:
        (
            id_usuario, nombre, ap, am, cuenta, jornadas, primera_entrada,
            ultima_salida, abiertas, segundos_cerrados, entrada_abierta,
        ) = fila
        segundos = int(segundos_cerrados or 0)
        if entrada_abierta:
            entrada = datetime.strptime(entrada_abierta, "%Y-%m-%d %H:%M:%S")
            segundos += max(0, int((ahora - entrada).total_seconds()))

        reporte.append({
            "id_usuario": id_usuario,
            "nombre": f"{nombre or ''} {ap or ''} {am or ''}".strip(),
            "cuenta": cuenta or "",
            "jornadas": int(jornadas or 0),
            "primera_entrada": primera_entrada or "",
            "ultima_salida": ultima_salida or "",
            "estado": "Trabajando" if int(abiertas or 0) > 0 else "Fuera",
            "segundos_trabajados": segundos,
            "tiempo_trabajado": formatear_duracion(segundos),
        })

    return reporte


def exportar_reporte_csv(ruta, reporte):
    columnas = [
        "id_usuario", "nombre", "cuenta", "jornadas", "primera_entrada",
        "ultima_salida", "estado", "tiempo_trabajado",
    ]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for fila in reporte:
            escritor.writerow({columna: fila[columna] for columna in columnas})
