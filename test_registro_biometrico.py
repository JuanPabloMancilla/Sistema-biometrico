import unittest


def rostro_de_otro_usuario(match_id, distancia, usuario_editando, umbral=0.42):
    return (
        match_id is not None
        and distancia < umbral
        and str(match_id) != str(usuario_editando)
    )


class RegistroBiometricoTest(unittest.TestCase):
    def test_permite_actualizar_el_propio_rostro(self):
        self.assertFalse(rostro_de_otro_usuario(7, 0.20, 7))
        self.assertFalse(rostro_de_otro_usuario("7", 0.20, 7))

    def test_bloquea_rostro_de_otro_usuario(self):
        self.assertTrue(rostro_de_otro_usuario(8, 0.20, 7))

    def test_nuevo_usuario_bloquea_cualquier_rostro_existente(self):
        self.assertTrue(rostro_de_otro_usuario(7, 0.20, None))


if __name__ == "__main__":
    unittest.main()
