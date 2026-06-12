import os
import sqlite3
import tempfile
import unittest
from datetime import datetime

from app.services import asistencia_service


class AsistenciaServiceTest(unittest.TestCase):
    def setUp(self):
        descriptor, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(descriptor)
        self.get_connection_original = asistencia_service.get_connection
        asistencia_service.get_connection = lambda: sqlite3.connect(self.db_path)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE jornada_laboral (
                id_jornada INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                fecha_entrada TEXT NOT NULL,
                fecha_salida TEXT,
                duracion_segundos INTEGER,
                estado TEXT NOT NULL DEFAULT 'trabajando'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE configuracion_asistencia (
                id_configuracion INTEGER PRIMARY KEY,
                hora_entrada TEXT, tolerancia_minutos INTEGER,
                jornada_objetivo_minutos INTEGER, descanso_minutos INTEGER
            )
            """
        )
        conn.execute("INSERT INTO configuracion_asistencia VALUES (1, '08:00', 10, 480, 30)")
        conn.commit()
        conn.close()

    def tearDown(self):
        asistencia_service.get_connection = self.get_connection_original
        os.remove(self.db_path)

    def test_entrada_y_salida_calculan_tiempo_trabajado(self):
        entrada = asistencia_service.registrar_marcaje(
            7, datetime(2026, 6, 12, 8, 0, 0)
        )
        salida = asistencia_service.registrar_marcaje(
            7, datetime(2026, 6, 12, 16, 31, 5)
        )

        self.assertEqual(entrada["tipo"], "entrada")
        self.assertEqual(entrada["estado"], "Trabajando")
        self.assertEqual(salida["tipo"], "salida")
        self.assertEqual(salida["duracion_segundos"], 30665)
        self.assertEqual(salida["duracion_texto"], "8 h 31 min")

    def test_calcula_retardo_extra_y_descanso(self):
        config = asistencia_service.obtener_configuracion_asistencia()
        metricas = asistencia_service.calcular_metricas_jornada(
            "2026-06-12 08:25:00", 9 * 3600, config
        )
        self.assertEqual(metricas["retardo_segundos"], 15 * 60)
        self.assertEqual(metricas["segundos_netos"], 8 * 3600 + 30 * 60)
        self.assertEqual(metricas["extra_segundos"], 30 * 60)

    def test_corrige_jornada(self):
        asistencia_service.registrar_marcaje(7, datetime(2026, 6, 12, 8, 0, 0))
        jornada = asistencia_service.obtener_ultima_jornada_usuario(7, "2026-06-01", "2026-06-30")
        asistencia_service.corregir_jornada(
            jornada[0], "2026-06-12 08:15:00", "2026-06-12 16:15:00"
        )
        corregida = asistencia_service.obtener_ultima_jornada_usuario(7, "2026-06-01", "2026-06-30")
        self.assertEqual(corregida[1], "2026-06-12 08:15:00")
        self.assertEqual(corregida[2], "2026-06-12 16:15:00")
        self.assertEqual(corregida[3], "finalizada")


if __name__ == "__main__":
    unittest.main()
