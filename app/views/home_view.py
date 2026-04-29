import customtkinter as ctk
from app.views.app_context import AppContext

class HomeView(ctk.CTkFrame):
    def __init__(self, master, on_logout=None):
        # Fondo azul bebé muy claro
        super().__init__(master, fg_color="#e3f2fd")
        self.on_logout = on_logout
        
        # --- BARRA LATERAL ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#ffffff")
        self.sidebar.pack(side="left", fill="y")
        
        self.title_label = ctk.CTkLabel(self.sidebar, text=AppContext.t("MENÚ"), 
                                        font=("Inter", 18, "bold"), text_color="#4388b9")
        self.title_label.pack(pady=30)

        # Botón de Regreso (Estilo azul suave)
        self.btn_regresar = ctk.CTkButton(
            self.sidebar, 
            text="← " + AppContext.t("CERRAR SESIÓN"), 
            fg_color="transparent", 
            text_color="#e74c3c",
            hover_color="#fdecea",
            font=("Inter", 12, "bold"),
            command=self.ejecutar_regreso
        )
        self.btn_regresar.pack(side="bottom", pady=30, padx=20, fill="x")

        # --- CONTENIDO PRINCIPAL ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", expand=True, fill="both", padx=60, pady=60)

        # Tarjeta Blanca Central
        self.card = ctk.CTkFrame(self.main_content, fg_color="white", corner_radius=20)
        self.card.pack(expand=True, fill="both", padx=20, pady=20)

        self.welcome_label = ctk.CTkLabel(self.card, text=AppContext.t("Panel de Control Biométrico"), 
                                          font=("Inter", 24, "bold"), text_color="black")
        self.welcome_label.pack(pady=(40, 20))

        self.btn_camara = ctk.CTkButton(
            self.card, 
            text=AppContext.t("ACTIVAR CÁMARA"), 
            fg_color="#4388b9", 
            hover_color="#366d94",
            font=("Inter", 14, "bold"), 
            height=45, 
            command=self.abrir_camara
        )
        self.btn_camara.pack(pady=20)

    def ejecutar_regreso(self):
        if self.on_logout:
            self.on_logout()

    def abrir_camara(self):
        print("Cámara activada")