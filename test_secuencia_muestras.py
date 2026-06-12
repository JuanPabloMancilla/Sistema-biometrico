import unittest


def accion_despues_de_muestra(cantidad, objetivo=3):
    return "continuar" if cantidad < objetivo else "finalizar"


class SecuenciaMuestrasTest(unittest.TestCase):
    def test_primeras_dos_muestras_continuan(self):
        self.assertEqual(accion_despues_de_muestra(1), "continuar")
        self.assertEqual(accion_despues_de_muestra(2), "continuar")

    def test_tercera_muestra_finaliza(self):
        self.assertEqual(accion_despues_de_muestra(3), "finalizar")


if __name__ == "__main__":
    unittest.main()
