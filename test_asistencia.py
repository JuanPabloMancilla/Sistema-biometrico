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


if __name__ == "__main__":
    unittest.main()
