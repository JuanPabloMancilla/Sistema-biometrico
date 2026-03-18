import customtkinter as ctk

class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color="#F8F9FA") 
        self.on_login_success = on_login_success
        self.password_visible = False 

        # --- BARRA SUPERIOR (SOLO CONTROLES) ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(side="top", fill="x", padx=30, pady=20)

        # Contenedor de botones a la derecha
        self.controls_wrapper = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.controls_wrapper.pack(side="right")

        # Control de Tema
        self.theme_control = ctk.CTkFrame(self.controls_wrapper, fg_color="#E2E8F0", corner_radius=20, width=110, height=38)
        self.theme_control.pack(side="left", padx=10)
        self.theme_control.pack_propagate(False) 
        
        self.theme_icon = ctk.CTkLabel(self.theme_control, text="☀️", font=("Inter", 16), text_color="black")
        self.theme_icon.place(x=22, y=19, anchor="center") 
        
        self.theme_switch = ctk.CTkSwitch(
            self.theme_control, text="", width=45, progress_color="#1D1D1F",
            button_color="#1D1D1F", command=self.actualizar_icono_tema 
        )
        self.theme_switch.place(x=72, y=19, anchor="center")

        # Selector de Idioma
        self.lang_control = ctk.CTkFrame(self.controls_wrapper, fg_color="#E2E8F0", corner_radius=20, height=38)
        self.lang_control.pack(side="left", padx=10)
        ctk.CTkLabel(self.lang_control, text="🌐", font=("Inter", 16), text_color="black").pack(side="left", padx=(12, 5))
        
        self.es_btn = ctk.CTkButton(self.lang_control, text="ES", width=38, height=28, corner_radius=14, 
                                   fg_color="#1D1D1F", text_color="white", font=("Inter", 11, "bold"),
                                   hover_color="#1D1D1F", command=lambda: self.actualizar_idioma("ES"))
        self.es_btn.pack(side="left", padx=2, pady=5)
        
        self.en_btn = ctk.CTkButton(self.lang_control, text="EN", width=38, height=28, corner_radius=14, 
                                   fg_color="transparent", text_color="#4A4A4A", font=("Inter", 11, "bold"),
                                   hover_color="#CBD5E1", command=lambda: self.actualizar_idioma("EN"))
        self.en_btn.pack(side="left", padx=(2, 10), pady=5)

        # --- TARJETA DE LOGIN ---
        self.card = ctk.CTkFrame(
            self, 
            fg_color="white", 
            width=420, 
            height=600, 
            corner_radius=15,
            border_width=1,          
            border_color="#E0E0E0"   
        )
        self.card.place(relx=0.5, rely=0.5, anchor="center")
        self.card.pack_propagate(False) 
        self.create_form()

    # --- LÓGICA INTERACTIVA ---
    def actualizar_icono_tema(self):
        if self.theme_switch.get() == 1:
            self.theme_icon.configure(text="🌙")
            self.theme_control.configure(fg_color="#CBD5E1")
        else:
            self.theme_icon.configure(text="☀️")
            self.theme_control.configure(fg_color="#E2E8F0")
        self.theme_icon.place(x=22, y=19, anchor="center")

    def actualizar_idioma(self, lang):
        if lang == "ES":
            self.es_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#1D1D1F")
            self.en_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")
        else:
            self.en_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#1D1D1F")
            self.es_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")

    def toggle_password_visibility(self):
        if self.password_visible:
            self.pass_entry.configure(show="*")
            self.eye_btn.configure(text="🔒")
            self.password_visible = False
        else:
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="🔓")
            self.password_visible = True

    def create_form(self):
        ctk.CTkLabel(self.card, text="K O D A", font=("Times New Roman", 45, "bold"), text_color="#3C054F").pack(pady=(40, 10))
        ctk.CTkLabel(self.card, text="Sistema de Reconocimiento\nFacial", 
                     font=("Inter", 24, "bold"), text_color="#000000", justify="center").pack(pady=10)
        ctk.CTkLabel(self.card, text="Ingresa tus credenciales para continuar", 
                     font=("Inter", 13), text_color="#8E8E93").pack(pady=(0, 30))

        self.create_input_group("CORREO ELECTRÓNICO", "Escribe tu correo electrónico")
        self.user_entry = self.last_entry
        self.create_input_group("CONTRASEÑA", "Escribe tu contraseña", is_password=True)
        self.pass_entry = self.last_entry

        self.error_label = ctk.CTkLabel(self.card, text="", text_color="#EF4444", font=("Inter", 12))
        self.error_label.pack(pady=(5, 0))

        self.login_btn = ctk.CTkButton(
            self.card, text="→   INICIAR SESIÓN", 
            fg_color="#000000", hover_color="#262626", 
            width=340, height=50, corner_radius=8,
            font=("Inter", 14, "bold"), command=self.validar_login
        )
        self.login_btn.pack(pady=(30, 20))

    def create_input_group(self, label_text, placeholder, is_password=False):
        group_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        group_frame.pack(fill="x", padx=40, pady=8)

        lbl = ctk.CTkLabel(group_frame, text=label_text, font=("Inter", 11, "bold"), text_color="#1D1D1F")
        lbl.pack(side="top", anchor="w")

        input_container = ctk.CTkFrame(group_frame, fg_color="#F1F5F9", height=45, corner_radius=8)
        input_container.pack(fill="x", pady=(5, 0))
        input_container.pack_propagate(False)

        entry = ctk.CTkEntry(
            input_container, placeholder_text=placeholder,
            fg_color="transparent", border_width=0, font=("Inter", 13),
            text_color="black"
        )
        
        if is_password:
            entry.configure(show="*")
            entry.pack(side="left", fill="both", expand=True, padx=(10, 0))
            self.eye_btn = ctk.CTkButton(
                input_container, text="🔒", width=35, height=35, 
                fg_color="transparent", hover_color="#E2E8F0", text_color="black",
                font=("Inter", 14), command=self.toggle_password_visibility
            )
            self.eye_btn.pack(side="right", padx=5)
        else:
            entry.pack(side="left", fill="both", expand=True, padx=10)

        self.last_entry = entry

    def validar_login(self):
        user = self.user_entry.get()
        pw = self.pass_entry.get()
        if user == "1" and pw == "1":
            self.on_login_success()
        else:
            self.error_label.configure(text="Credenciales incorrectas.")