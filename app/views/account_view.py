import customtkinter as ctk
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.services.usuario_service import actualizar_usuario, obtener_usuario_por_cuenta

class AccountView(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_logout = on_logout
        
        # --- Configuración de Fuentes ---
        self.font_header = ("Inter", 30, "bold")
        self.font_sub = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small = ("Inter", 11, "bold")
        
        # Datos simulados (puedes conectarlos a tu BD después)
        self.datos = {
            "nombre": "ADMINISTRADOR DEL SISTEMA",
            "correo": "admin@universidad.edu.mx",
            "tel": "5512345678",
            "facultad": "ADMINISTRACIÓN CENTRAL"
        }

        self.crear_vista_lectura()

    def limpiar_pantalla(self):
        """Limpia todos los widgets para redibujar la vista"""
        for widget in self.winfo_children():
            widget.destroy()

    def crear_vista_lectura(self):
        """Dibuja la interfaz de perfil en modo lectura"""
        self.limpiar_pantalla()
        
        # --- HEADER ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text=AppContext.t("⚙️   Configuración Cuenta"), font=self.font_header, text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_cont, text=AppContext.t("Configura tu perfil y preferencias"), font=self.font_normal, text_color=COLORS["subtext"]).pack(anchor="w")

        ctk.CTkButton(header, text="📝 " + AppContext.t("Editar Perfil"), fg_color=COLORS["card"], text_color=COLORS["text"], 
                     border_width=1, border_color=COLORS["border"], hover_color=COLORS["hover"], 
                     width=150, height=40, font=self.font_small,
                     command=self.abrir_formulario_edicion).pack(side="right", anchor="n")

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40)

        # 1. Banner de Perfil
        self.create_profile_banner(is_editing=False)

        # 2. Card de Personalización (IDIOIMA)
        self.create_customization_card()

        # 3. Detalles de la Cuenta
        ctk.CTkLabel(self.container, text="📋 " + AppContext.t("Detalles de la Cuenta"), font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=100, pady=(20, 10))
        self.create_read_only_field(AppContext.t("Nombres"), self.datos["nombre"], "👤")
        self.create_read_only_field(AppContext.t("correo"), self.datos["correo"], "📧")
        self.create_read_only_field(AppContext.t("Teléfono"), self.datos["tel"], "📞")
        self.create_read_only_field(AppContext.t("Facultad"), self.datos["facultad"], "🏛️")

        # Botón Cerrar Sesión
        ctk.CTkButton(self.container, text="🚪 " + AppContext.t("Cerrar Sesión"), fg_color="#FFF1F2", text_color="#E11D48", 
                     hover_color="#FEE2E2", height=50, corner_radius=12, font=self.font_sub, 
                     command=self.on_logout).pack(fill="x", pady=(40, 60), padx=100)

    def create_customization_card(self):
        """Crea la sección de cambio de idioma con botones funcionales"""
        card = ctk.CTkFrame(self.container, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=10, padx=100)
        
        ctk.CTkLabel(card, text="🎨 " + AppContext.t("Personalización"), font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Fila Idioma
        f2 = ctk.CTkFrame(card, fg_color="transparent", height=40)
        f2.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(f2, text="🌐 " + AppContext.t("Idioma del Sistema"), font=self.font_normal, text_color=COLORS["text"]).pack(side="left")
        
        lang_group = ctk.CTkFrame(f2, fg_color=COLORS["hover"], corner_radius=10)
        lang_group.pack(side="right")
        
        # Botón ES
        color_es = "#1D1D1F" if AppContext.idioma_actual == "es" else "transparent"
        txt_es = "white" if AppContext.idioma_actual == "es" else COLORS["text"]
        ctk.CTkButton(lang_group, text="ES", width=40, height=30, fg_color=color_es, text_color=txt_es, 
                     corner_radius=8, font=self.font_small, 
                     command=lambda: self.cambiar_idioma_local("es")).pack(side="left", padx=2, pady=2)
        
        # Botón EN
        color_en = "#1D1D1F" if AppContext.idioma_actual == "en" else "transparent"
        txt_en = "white" if AppContext.idioma_actual == "en" else COLORS["text"]
        ctk.CTkButton(lang_group, text="EN", width=40, height=30, fg_color=color_en, text_color=txt_en, 
                     corner_radius=8, font=self.font_small, hover_color="#CBD5E1",
                     command=lambda: self.cambiar_idioma_local("en")).pack(side="left", padx=2, pady=2)

    def cambiar_idioma_local(self, nuevo_idioma):
        """Cambia el idioma y fuerza el refresco de toda la aplicación"""
        if AppContext.idioma_actual == nuevo_idioma:
            return

        AppContext.set_idioma(nuevo_idioma)
        
        # BUSCADOR DEL MAIN: Sube por la jerarquía de componentes hasta hallar AppPrincipal
        ptr = self
        main_app = None
        while ptr is not None:
            if hasattr(ptr, 'refrescar_idioma_completo'):
                main_app = ptr
                break
            ptr = ptr.master # Sube un nivel al padre
            
        if main_app:
            main_app.refrescar_idioma_completo()
        else:
            # Fallback: si falla la comunicación, al menos refresca esta vista
            self.crear_vista_lectura()

    def create_read_only_field(self, label, value, icon):
        f = ctk.CTkFrame(self.container, fg_color=COLORS["card"], height=70, corner_radius=12, border_width=1, border_color=COLORS["border"])
        f.pack(fill="x", pady=5, padx=100)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=icon, font=("Inter", 18)).place(x=20, rely=0.5, anchor="w")
        ctk.CTkLabel(f, text=label, font=("Inter", 10, "bold"), text_color=COLORS["subtext"]).place(x=55, y=12)
        ctk.CTkLabel(f, text=value, font=self.font_sub, text_color=COLORS["text"]).place(x=55, y=32)

    def create_profile_banner(self, is_editing=False):
        card = ctk.CTkFrame(self.container, fg_color=COLORS["primary"], corner_radius=20, height=160)
        card.pack(fill="x", pady=10, padx=100)
        card.pack_propagate(False)

        avatar = ctk.CTkFrame(card, width=90, height=90, corner_radius=45, fg_color=COLORS["hover"])
        avatar.place(x=40, rely=0.5, anchor="w")
        ctk.CTkLabel(avatar, text="👤", font=("Inter", 40)).place(relx=0.5, rely=0.5, anchor="center")
        
        if is_editing:
            ctk.CTkButton(card, text="📸 " + AppContext.t("Actualizar Foto"), font=("Inter", 10, "bold"), 
                         fg_color="#38BDF8", text_color="#082736", height=28, width=120,
                         command=lambda: print("Foto")).place(x=150, rely=0.7, anchor="w")
            ctk.CTkLabel(card, text=AppContext.t("Editar Registro..."), font=("Inter", 18, "bold"), text_color="#FFFFFF").place(x=150, rely=0.4, anchor="w")
        else:
            ctk.CTkLabel(card, text=self.datos["nombre"], font=("Inter", 20, "bold"), text_color="#FFFFFF").place(x=150, rely=0.45, anchor="w")
            ctk.CTkLabel(card, text=AppContext.t("ADMINISTRADOR DEL SISTEMA"), font=self.font_small, text_color="#38BDF8").place(x=150, rely=0.58, anchor="w")

    def abrir_formulario_edicion(self):
        self.limpiar_pantalla()
        ctk.CTkLabel(self, text="✏️ " + AppContext.t("Editar Registro"), font=self.font_header, text_color=COLORS["text"]).pack(anchor="w", padx=60, pady=(40, 20))
        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.pack(expand=True, fill="both", padx=60)
        self.container = form_scroll 
        self.create_profile_banner(is_editing=True)
        # Formulario... (puedes seguir agregando los campos aquí)
        ctk.CTkButton(form_scroll, text=AppContext.t("Cancelar"), command=self.crear_vista_lectura).pack(pady=20)