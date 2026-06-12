class DetectorParpadeo:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.vio_abiertos = False
        self.vio_cerrados = False
        self.parpadeo_confirmado = False

    def actualizar(self, ojos_cerrados):
        if ojos_cerrados is None or self.parpadeo_confirmado:
            return self.parpadeo_confirmado

        if not ojos_cerrados:
            if self.vio_cerrados:
                self.parpadeo_confirmado = True
            else:
                self.vio_abiertos = True
        elif self.vio_abiertos:
            self.vio_cerrados = True

        return self.parpadeo_confirmado
