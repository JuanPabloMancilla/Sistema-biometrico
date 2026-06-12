import csv
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime

from app.services import reporte_asistencia_service


class ReporteAsistenciaServiceTest(unittest.TestCase):
    def setUp(self):
        descriptor, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        self.original = reporte_asistencia_service.get_connection
        reporte_asistencia_service.get_connection = lambda: sqlite3.connect(self.db_path)
        conn = sqlite3.connect(self.db_path)
        conn.executescript(
            """
            CREATE TABLE usuario (
                id_usuario INTEGER PRIMARY KEY,
                nombre TEXT, a_paterno TEXT, a_materno TEXT, cuenta TEXT
            );
            CREATE TABLE jornada_laboral (
                id_jornada INTEGER PRIMARY KEY,
                id_usuario INTEGER,
                fecha_entrada TEXT,
                fecha_salida TEXT,
                duracion_segundos INTEGER,
                estado TEXT
            );
            CREATE TABLE configuracion_asistencia (
                id_configuracion INTEGER PRIMARY KEY,
                hora_entrada TEXT, tolerancia_minutos INTEGER,
                jornada_objetivo_minutos INTEGER, descanso_minutos INTEGER
            );
            INSERT INTO configuracion_asistencia VALUES (1, '08:00', 10, 480, 0);
            INSERT INTO usuario VALUES (1, 'Ana', 'Lopez', '', 'A-1');
            INSERT INTO jornada_laboral VALUES
                (1, 1, '2026-06-10 08:00:00', '2026-06-10 16:00:00', 28800, 'finalizada'),
                (2, 1, '2026-06-12 08:00:00', NULL, NULL, 'trabajando');
            """
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        reporte_asistencia_service.get_connection = self.original
        os.remove(self.db_path)

    def test_resume_jornadas_cerradas_y_abiertas(self):
        filas = reporte_asistencia_service.obtener_reporte_asistencia(
            "2026-06-01", "2026-06-30", datetime(2026, 6, 12, 12, 0, 0)
        )

        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["jornadas"], 2)
        self.assertEqual(filas[0]["estado"], "Trabajando")
        self.assertEqual(filas[0]["segundos_trabajados"], 43200)
        self.assertEqual(filas[0]["tiempo_trabajado"], "12 h 0 min")
        self.assertEqual(filas[0]["retardo"], "0 s")
        self.assertEqual(filas[0]["horas_extra"], "0 s")

    def test_exporta_csv(self):
        filas = reporte_asistencia_service.obtener_reporte_asistencia(
            "2026-06-01", "2026-06-30", datetime(2026, 6, 12, 12, 0, 0)
        )
        descriptor, ruta = tempfile.mkstemp(suffix=".csv")
        os.close(descriptor)
        try:
            reporte_asistencia_service.exportar_reporte_csv(ruta, filas)
            with open(ruta, encoding="utf-8-sig") as archivo:
                datos = list(csv.DictReader(archivo))
            self.assertEqual(datos[0]["nombre"], "Ana Lopez")
            self.assertEqual(datos[0]["estado"], "Trabajando")
        finally:
            os.remove(ruta)


if __name__ == "__main__":
    unittest.main()
