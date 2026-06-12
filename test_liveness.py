import unittest

from app.services.liveness_service import DetectorParpadeo


class DetectorParpadeoTest(unittest.TestCase):
    def test_confirma_secuencia_abierto_cerrado_abierto(self):
        detector = DetectorParpadeo()

        self.assertFalse(detector.actualizar(False))
        self.assertFalse(detector.actualizar(True))
        self.assertTrue(detector.actualizar(False))

    def test_foto_con_ojos_abiertos_no_supera_prueba(self):
        detector = DetectorParpadeo()

        for _ in range(10):
            self.assertFalse(detector.actualizar(False))

    def test_no_confirma_si_inicia_con_ojos_cerrados(self):
        detector = DetectorParpadeo()

        self.assertFalse(detector.actualizar(True))
        self.assertFalse(detector.actualizar(False))


if __name__ == "__main__":
    unittest.main()
