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

        inicializar_bd()

        self.contenedor_vista = None
        
        # Iniciar directamente en la Terminal
        self.mostrar_terminal()

    def limpiar_pantalla(self):
        if self.contenedor_vista is not None:
            self.contenedor_vista.destroy()
            self.contenedor_vista = None

    def mostrar_terminal(self):
        """Muestra la terminal. Al 'regresar' o 'cerrar', manda al Login"""
        self.limpiar_pantalla()
        # --- CAMBIO CLAVE ---
        # Ahora, cuando se active el callback de la terminal, vamos al Login
        self.contenedor_vista = TerminalView(self, on_back=self.mostrar_login)
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_login(self):
        self.limpiar_pantalla()
        # CAMBIO AQUÍ: Antes decía self.mostrar_landing, ahora directo a dashboard
        self.contenedor_vista = LoginView(self, on_login_success=self.mostrar_dashboard)
        self.contenedor_vista.pack(expand=True, fill="both")

    def mostrar_dashboard(self):
        self.limpiar_pantalla()
        # Al darle "Atrás" en el Dashboard, regresa a la cámara
        self.contenedor_vista = DashboardView(self, on_back=self.mostrar_terminal)
        self.contenedor_vista.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = AppPrincipal()
    app.mainloop()