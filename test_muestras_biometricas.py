import json
import os
import tempfile
import unittest

import numpy as np

from app.recognition.encoding_manager import cargar_encodings, guardar_encoding


class MuestrasBiometricasTest(unittest.TestCase):
    def setUp(self):
        descriptor, self.ruta = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        os.remove(self.ruta)

    def tearDown(self):
        if os.path.exists(self.ruta):
            os.remove(self.ruta)

    def test_guarda_tres_muestras_del_mismo_usuario(self):
        muestras = [np.full(128, valor) for valor in (0.01, 0.02, 0.03)]
        resultado = guardar_encoding(7, muestras, archivo=self.ruta)

        self.assertTrue(resultado["ok"])
        self.assertEqual(resultado["muestras"], 3)
        encodings, usuarios = cargar_encodings(self.ruta)
        self.assertEqual(len(encodings), 3)
        self.assertEqual(usuarios, [7, 7, 7])

    def test_reemplazo_elimina_muestras_anteriores(self):
        guardar_encoding(7, [np.full(128, 0.01), np.full(128, 0.02)], archivo=self.ruta)
        guardar_encoding(7, [np.full(128, 0.04), np.full(128, 0.05)], archivo=self.ruta, reemplazar=True)

        with open(self.ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        self.assertEqual(len(datos), 2)
        self.assertTrue(all(fila["usuario"] == 7 for fila in datos))


if __name__ == "__main__":
    unittest.main()
