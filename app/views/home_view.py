import customtkinter as ctk
from app.views.app_context import AppContext
from app.services.theme import COLORS

class HomeView(ctk.CTkFrame):
    def __init__(self, master, on_logout=None):
        # Fondo azul bebé muy claro
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_logout = on_logout
        
        # --- BARRA LATERAL ---
        self.sidebar = ctk.CTkFrame(self, width=196, corner_radius=0, fg_color=COLORS["sidebar"])
        self.sidebar.pack(side="left", fill="y")
        
        self.title_label = ctk.CTkLabel(self.sidebar, text=AppContext.t("MENÚ"), 
                                        font=("Inter", 18, "bold"), text_color=COLORS["sidebar_text"])
        self.title_label.pack(pady=18)
        ctk.CTkFrame(self.sidebar, fg_color=COLORS["accent"], height=3).pack(fill="x", padx=24)

        # Botón de Regreso (Estilo azul suave)
        self.btn_regresar = ctk.CTkButton(
            self.sidebar, 
            text="← " + AppContext.t("CERRAR SESIÓN"), 
            fg_color="transparent", 
            text_color=COLORS["danger"],
            hover_color="#33131B",
            font=("Inter", 12, "bold"),
            command=self.ejecutar_regreso
        )
        self.btn_regresar.pack(side="bottom", pady=18, padx=10, fill="x")

        # --- CONTENIDO PRINCIPAL ---
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", expand=True, fill="both", padx=12, pady=12)

        # Tarjeta Blanca Central
        self.card = ctk.CTkFrame(self.main_content, fg_color=COLORS["card"], corner_radius=8, border_width=1, border_color=COLORS["border"])
        self.card.pack(expand=True, fill="both", padx=8, pady=8)

        self.welcome_label = ctk.CTkLabel(self.card, text=AppContext.t("Panel de Control Biométrico"), 
                                          font=("Inter", 24, "bold"), text_color=COLORS["text"])
        self.welcome_label.pack(pady=(24, 16))

        self.btn_camara = ctk.CTkButton(
            self.card, 
            text=AppContext.t("ACTIVAR CÁMARA"), 
            fg_color=COLORS["primary"], 
            hover_color=COLORS["primary_hover"],
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
