import os
import sys

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
os.environ.setdefault("GLOG_minloglevel", "3")
os.environ.setdefault("ABSL_LOGGING_MIN_LOG_LEVEL", "3")

import customtkinter as ctk
from app.database.database import inicializar_bd
from app.tk_compat import apply_customtkinter_compatibility

ctk.set_appearance_mode("light")
apply_customtkinter_compatibility()


class ErrorView(ctk.CTkFrame):
    def __init__(self, master, titulo, detalle, on_back=None):
        super().__init__(master, fg_color="white")
        self.on_back = on_back

        card = ctk.CTkFrame(
            self,
            width=560,
            height=320,
            fg_color="#F8FAFC",
            border_width=1,
            border_color="#CBD5E1",
            corner_radius=8,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Inter", 24, "bold"),
            text_color="#0F172A",
        ).pack(pady=(34, 12), padx=28)

        ctk.CTkLabel(
            card,
            text=detalle,
            font=("Inter", 14),
            text_color="#334155",
            wraplength=480,
            justify="center",
        ).pack(pady=(0, 24), padx=28)

        if self.on_back is not None:
            ctk.CTkButton(
                card,
                text="Ir al login",
                width=180,
                height=42,
                corner_radius=8,
                command=self.on_back,
            ).pack()


def _detalle_dependencia(error):
    modulo = getattr(error, "name", None) or str(error)
    version = ".".join(str(part) for part in sys.version_info[:3])
    if modulo == "picamera2":
        return (
            f"No se pudo cargar el modulo necesario: {modulo}.\n\n"
            "En Raspberry Pi, picamera2 normalmente se instala como paquete "
            "del sistema. El entorno virtual debe crearse con acceso a paquetes "
            "del sistema para poder verlo.\n\n"
            f"Python actual: {version}.\n"
            "Voy a recrear el entorno con Python 3.10 y --system-site-packages."
        )

    return (
        f"No se pudo cargar un modulo necesario: {error}.\n\n"
        f"Este proyecto esta preparado para Python 3.10. Python actual: {version}.\n\n"
        "Para el modo biometrico completo crea el entorno con Python 3.10 y "
        "ejecuta: pip install -r requirements.txt"
    )

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._closing = False

        self.title("SECUREWORK")
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1100, screen_width)
        window_height = min(800, screen_height)
        self.geometry(f"{window_width}x{window_height}+0+0")
        self.minsize(min(640, screen_width), min(420, screen_height))
        if sys.platform.startswith("linux"):
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass
        self.configure(fg_color="white")

        # Inicializar base de datos al arrancar
        inicializar_bd()

        self.contenedor_vista = None
        
        # --- NUEVO: Control de estado ---
        # Guardamos qué vista está activa para poder refrescarla
        self.vista_actual = "terminal" 
        
        # Iniciar en terminal biometrica si el entorno esta completo.
        self.mostrar_terminal()

    def limpiar_pantalla(self):
        """Elimina la vista actual para liberar memoria y espacio"""
        if self.contenedor_vista is not None:
            self._cerrar_recursos(self.contenedor_vista)
            try:
                self.contenedor_vista.destroy()
            except Exception as error:
                print(f"Error destruyendo vista: {error}")
            self.contenedor_vista = None

    def _cerrar_recursos(self, widget):
        try:
            children = list(widget.winfo_children())
        except Exception:
            children = []

        for child in children:
            self._cerrar_recursos(child)

        close_method = getattr(widget, "on_close", None)
        if callable(close_method):
            try:
                close_method()
            except Exception as error:
                print(f"Error cerrando recursos: {error}")

    def cerrar_aplicacion(self):
        if self._closing:
            return
        self._closing = True

        if self.contenedor_vista is not None:
            self._cerrar_recursos(self.contenedor_vista)
            self.contenedor_vista = None

        try:
            from app.camara.camara import liberar_camara

            liberar_camara()
        except Exception as error:
            print(f"Error en limpieza final de camara: {error}")

        try:
            self.quit()
        finally:
            try:
                super().destroy()
            except Exception as error:
                print(f"Error cerrando interfaz: {error}")
                os._exit(0)

    # --- MÉTODO CLAVE: REFRESCAR TODO EL SISTEMA ---
    def refrescar_idioma_completo(self):
        """
        Este método destruye y vuelve a crear la vista activa.
        Al reconstruirse, las llamadas a AppContext.t() obtendrán el nuevo idioma.
        """
        if self.vista_actual == "terminal":
            self.mostrar_terminal()
        elif self.vista_actual == "login":
            self.mostrar_login()
        elif self.vista_actual == "dashboard":
            self.mostrar_dashboard()

    def mostrar_terminal(self):
        """Muestra la terminal de reconocimiento facial"""
        self.vista_actual = "terminal"
        self.limpiar_pantalla()
        try:
            from app.views.terminal_view import TerminalView

            self.contenedor_vista = TerminalView(self, on_back=self.mostrar_login)
        except ModuleNotFoundError as error:
            self.contenedor_vista = ErrorView(
                self,
                "Entorno biometrico incompleto",
                _detalle_dependencia(error),
                on_back=self.mostrar_login,
            )
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_login(self):
        """Muestra la pantalla de acceso"""
        self.vista_actual = "login"
        self.limpiar_pantalla()
        from app.views.login_view import LoginView

        self.contenedor_vista = LoginView(self, on_login_success=self.mostrar_dashboard)
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_dashboard(self):
        self.vista_actual = "dashboard"
        self.limpiar_pantalla()
        try:
            from app.views.dashboard_view import DashboardView

            self.contenedor_vista = DashboardView(self, on_back=self.mostrar_terminal)
        except ModuleNotFoundError as error:
            self.contenedor_vista = ErrorView(
                self,
                "Dashboard incompleto",
                _detalle_dependencia(error),
                on_back=self.mostrar_login,
            )
        self.contenedor_vista.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AppPrincipal()
    try:
        app.mainloop()
    finally:
        if not app._closing:
            app.cerrar_aplicacion()
