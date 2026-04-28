# app/context.py
from app.services.traductor import TraductorOffline

class AppContext:
    # Estado global del idioma
    idioma_actual = "es"
    
    # Instancia única del traductor para toda la app (Singleton)
    traductor = TraductorOffline()

    @classmethod
    def t(cls, texto):
        """
        Función estática para traducir. 
        Uso: AppContext.t("Hola")
        """
        return cls.traductor.procesar_texto(texto, cls.idioma_actual)
    
    @classmethod
    def set_idioma(cls, nuevo_idioma):
        """
        Cambia el idioma global. 
        Uso: AppContext.set_idioma("en")
        """
        cls.idioma_actual = nuevo_idioma