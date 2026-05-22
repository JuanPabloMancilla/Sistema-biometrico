import customtkinter as ctk
from app.views.login_view import LoginView
from app.views.dashboard_view import DashboardView
from app.views.terminal_view import TerminalView
from app.database.database import inicializar_bd

class AppPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SISTEMA BIOMÉTRICO")
        self.geometry("1100x800")
        self.configure(fg_color="white")

        # Inicializar base de datos al arrancar
        inicializar_bd()

        self.contenedor_vista = None
        
        # --- NUEVO: Control de estado ---
        # Guardamos qué vista está activa para poder refrescarla
        self.vista_actual = "terminal" 
        
        # Iniciar directamente en la Terminal
        self.mostrar_terminal()

    def limpiar_pantalla(self):
        """Elimina la vista actual para liberar memoria y espacio"""
        if self.contenedor_vista is not None:
            self.contenedor_vista.destroy()
            self.contenedor_vista = None

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
        # Pasamos self como controller para que la vista pueda pedir refrescos si es necesario
        self.contenedor_vista = TerminalView(self, on_back=self.mostrar_login)
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_login(self):
        """Muestra la pantalla de acceso"""
        self.vista_actual = "login"
        self.limpiar_pantalla()
        self.contenedor_vista = LoginView(self, on_login_success=self.mostrar_dashboard)
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_dashboard(self):
        self.vista_actual = "dashboard"
        self.limpiar_pantalla()
        self.contenedor_vista = DashboardView(self, on_back=self.mostrar_terminal)
        self.contenedor_vista.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()