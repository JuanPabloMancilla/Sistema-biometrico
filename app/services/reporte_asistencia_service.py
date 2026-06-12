import csv
from datetime import datetime

from app.database.database import get_connection
from app.services.asistencia_service import (
    calcular_metricas_jornada,
    formatear_duracion,
    obtener_configuracion_asistencia,
)


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
            j.id_jornada,
            j.fecha_entrada,
            j.fecha_salida,
            j.duracion_segundos,
            j.estado
        FROM usuario u
        JOIN jornada_laboral j ON j.id_usuario = u.id_usuario
        WHERE DATE(j.fecha_entrada) BETWEEN ? AND ?
        ORDER BY u.a_paterno, u.a_materno, u.nombre, j.fecha_entrada
        """,
        (fecha_inicio, fecha_fin),
    )
    filas = cursor.fetchall()
    conn.close()

    configuracion = obtener_configuracion_asistencia()
    acumulado = {}
    for fila in filas:
        (
            id_usuario, nombre, ap, am, cuenta, id_jornada, fecha_entrada,
            fecha_salida, duracion_segundos, estado,
        ) = fila
        if estado == "trabajando":
            entrada = datetime.strptime(fecha_entrada, "%Y-%m-%d %H:%M:%S")
            segundos = max(0, int((ahora - entrada).total_seconds()))
        else:
            segundos = int(duracion_segundos or 0)
        metricas = calcular_metricas_jornada(fecha_entrada, segundos, configuracion)

        item = acumulado.setdefault(id_usuario, {
            "id_usuario": id_usuario,
            "nombre": f"{nombre or ''} {ap or ''} {am or ''}".strip(),
            "cuenta": cuenta or "",
            "jornadas": 0,
            "primera_entrada": fecha_entrada,
            "ultima_salida": "",
            "estado": "Fuera",
            "segundos_trabajados": 0,
            "retardo_segundos": 0,
            "extra_segundos": 0,
        })
        item["jornadas"] += 1
        item["primera_entrada"] = min(item["primera_entrada"], fecha_entrada)
        if fecha_salida:
            item["ultima_salida"] = max(item["ultima_salida"], fecha_salida)
        if estado == "trabajando":
            item["estado"] = "Trabajando"
        item["segundos_trabajados"] += metricas["segundos_netos"]
        item["retardo_segundos"] += metricas["retardo_segundos"]
        item["extra_segundos"] += metricas["extra_segundos"]

    reporte = list(acumulado.values())
    for item in reporte:
        item["tiempo_trabajado"] = formatear_duracion(item["segundos_trabajados"])
        item["retardo"] = formatear_duracion(item["retardo_segundos"])
        item["horas_extra"] = formatear_duracion(item["extra_segundos"])

    return reporte


def exportar_reporte_csv(ruta, reporte):
    columnas = [
        "id_usuario", "nombre", "cuenta", "jornadas", "primera_entrada",
        "ultima_salida", "estado", "tiempo_trabajado", "retardo", "horas_extra",
    ]
    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for fila in reporte:
            escritor.writerow({columna: fila[columna] for columna in columnas})
