# app/context.py

# from app.services.traductor import TraductorOffline

class AppContext:
    # Estado global del idioma
    idioma_actual = "es"

    # Desactivado temporalmente en Raspberry
    traductor = None

    @classmethod
    def t(cls, texto):
        """
        Función de traducción temporal.
        """
        return texto

    @classmethod
    def set_idioma(cls, nuevo_idioma):
        """
        Cambia el idioma global.
        """
        cls.idioma_actual = nuevo_idioma