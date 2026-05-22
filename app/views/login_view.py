import customtkinter as ctk
import os
from app.services.theme import COLORS
from app.views.app_context import AppContext
from PIL import Image, ImageOps, ImageDraw


class LoginView(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=COLORS["bg"])
        self.master = master
        self.on_login_success = on_login_success
        self.password_visible = False

        # --- BARRA SUPERIOR ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent", height=80)
        self.top_bar.place(relx=0, rely=0, relwidth=1)

        # K O D A - Esquina superior izquierda
        self.koda_label_top = ctk.CTkLabel(
            self.top_bar, text="K O D A",
            font=("Times New Roman", 42, "bold"), text_color=COLORS["text"]
        )
        self.koda_label_top.pack(side="left", padx=15, pady=15)

        # Contenedor de Controles - Esquina superior derecha
        self.controls_wrapper = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.controls_wrapper.pack(side="right", padx=15, pady=15)

        # 1. Control de Tema
        self.theme_control = ctk.CTkFrame(self.controls_wrapper, fg_color="#E2E8F0", corner_radius=20, width=110, height=38)
        self.theme_control.pack(side="left", padx=8)
        self.theme_control.pack_propagate(False)
        self.theme_icon = ctk.CTkLabel(self.theme_control, text="??", font=("Inter", 16), text_color="black")
        self.theme_icon.place(x=22, y=19, anchor="center")
        self.theme_switch = ctk.CTkSwitch(
            self.theme_control, text="", width=45,
            progress_color="#1D1D1F", button_color="#1D1D1F",
            command=self.actualizar_icono_tema
        )
        self.theme_switch.place(x=72, y=19, anchor="center")

        # 2. Selector de Idioma
        self.lang_control = ctk.CTkFrame(self.controls_wrapper, fg_color="#E2E8F0", corner_radius=20, height=38)
        self.lang_control.pack(side="left", padx=8)
        ctk.CTkLabel(self.lang_control, text="??", font=("Inter", 16), text_color="black").pack(side="left", padx=(12, 5))

        # Ambos botones se crean neutros; _sincronizar_botones_idioma pinta el correcto
        self.es_btn = ctk.CTkButton(
            self.lang_control, text="ES", width=38, height=28, corner_radius=14,
            fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1",
            command=lambda: self.actualizar_idioma("ES")
        )
        self.es_btn.pack(side="left", padx=2, pady=5)

        self.en_btn = ctk.CTkButton(
            self.lang_control, text="EN", width=38, height=28, corner_radius=14,
            fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1",
            command=lambda: self.actualizar_idioma("EN")
        )
        self.en_btn.pack(side="left", padx=(2, 10), pady=5)

        # Leer idioma guardado y pintar el bot�n correcto
        self._sincronizar_botones_idioma()

        # 3. Bot�n de C�mara
        self.btn_regresar_terminal = ctk.CTkButton(
            self.controls_wrapper, text="??", width=45, height=38, corner_radius=15,
            fg_color="white", text_color="#1D1D1F", hover_color="#CBD5E1",
            border_width=1, border_color="#E2E8F0", font=("Inter", 18),
            command=self.regresar_a_terminal
        )
        self.btn_regresar_terminal.pack(side="left", padx=8)

        # --- TARJETA DE LOGIN CENTRAL ---
        self.card = ctk.CTkFrame(
            self, fg_color=COLORS["card"], width=440, height=640,
            corner_radius=25, border_width=1, border_color=COLORS["border"]
        )
        self.card.place(relx=0.5, rely=0.55, anchor="center")
        self.card.pack_propagate(False)
        self.create_form()

    def hacer_imagen_circular(self, pil_image, size=(120, 120)):
        pil_image = ImageOps.fit(pil_image, size, Image.Resampling.LANCZOS)
        mascara = Image.new('L', size, 0)
        dibujo = ImageDraw.Draw(mascara)
        dibujo.ellipse((0, 0, size[0], size[1]), fill=255)
        pil_image = pil_image.convert("RGBA")
        imagen_circular = pil_image.copy()
        imagen_circular.putalpha(mascara)
        return imagen_circular

    # --------------------------------------------------------------
    # Formulario
    # --------------------------------------------------------------

    def create_form(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        assets_path = os.path.join(base_path, "app", "views", "assets", "imgg.png")

        print(f"DEBUG: Buscando logo circular en: {assets_path}")

        if os.path.exists(assets_path):
            try:
                pil_image_original = Image.open(assets_path)
                tamanio_logo = (120, 120)
                pil_image_circular = self.hacer_imagen_circular(pil_image_original, tamanio_logo)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image_circular,
                    dark_image=pil_image_circular,
                    size=tamanio_logo
                )
                self.logo_label = ctk.CTkLabel(self.card, text="", image=self.logo_image)
                self.logo_label.pack(pady=(30, 0))
                print("DEBUG: Imagen cargada con exito!")
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            print("ERROR: No se encontro la imagen.")

        ctk.CTkLabel(
            self.card,
            text=AppContext.t("Sistema de Reconocimiento\nFacial"),
            font=("Inter", 26, "bold"), text_color=COLORS["text"], justify="center"
        ).pack(pady=(15, 10))

        ctk.CTkLabel(
            self.card,
            text=AppContext.t("Ingresa tus credenciales para continuar"),
            font=("Inter", 14), text_color="#8E8E93"
        ).pack(pady=(0, 25))

        self.create_input_group(AppContext.t("CORREO ELECTRÓNICO"), AppContext.t("Escribe tu correo"))
        self.user_entry = self.last_entry
        self.create_input_group(AppContext.t("CONTRASEÑA"), AppContext.t("Escribe tu contraseña"), is_password=True)
        self.pass_entry = self.last_entry

        self.error_label = ctk.CTkLabel(self.card, text="", text_color="#EF4444", font=("Inter", 13))
        self.error_label.pack(pady=(5, 0))

        self.login_btn = ctk.CTkButton(
            self.card,
            text="?   " + AppContext.t("INICIAR SESIÓN"),
            fg_color="#000000", hover_color="#262626",
            width=350, height=55, corner_radius=12,
            font=("Inter", 15, "bold"), command=self.validar_login
        )
        self.login_btn.pack(pady=(25, 20))

    def _sincronizar_botones_idioma(self):
        """Pinta el botón activo según AppContext.idioma_actual."""
        if AppContext.idioma_actual == "es":
            self.es_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#3E3E3F")
            self.en_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")
        else:
            self.en_btn.configure(fg_color="#1D1D1F", text_color="white", hover_color="#3E3E3F")
            self.es_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")

    def actualizar_idioma(self, lang):
        AppContext.set_idioma("es" if lang == "ES" else "en")
        self._sincronizar_botones_idioma()
        self.recargar_vista()

    def actualizar_icono_tema(self):
        if self.theme_switch.get() == 1:
            self.theme_icon.configure(text="??")
            ctk.set_appearance_mode("dark")
        else:
            self.theme_icon.configure(text="??")
            ctk.set_appearance_mode("light")
        self.recargar_vista()

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------

    def toggle_password_visibility(self):
        if self.pass_entry.cget("show") == "*":
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="??")
        else:
            self.pass_entry.configure(show="*")
            self.eye_btn.configure(text="??")

    def create_input_group(self, label_text, placeholder, is_password=False):
        group_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        group_frame.pack(fill="x", padx=45, pady=10)
        lbl = ctk.CTkLabel(group_frame, text=label_text, font=("Inter", 12, "bold"), text_color=COLORS["text"])
        lbl.pack(side="top", anchor="w")
        input_container = ctk.CTkFrame(group_frame, fg_color=COLORS["hover"], height=50, corner_radius=10)
        input_container.pack(fill="x", pady=(5, 0))
        input_container.pack_propagate(False)
        entry = ctk.CTkEntry(
            input_container, placeholder_text=placeholder,
            fg_color="transparent", border_width=0,
            font=("Inter", 14), text_color=("black", "white")
        )
        if is_password:
            entry.configure(show="*")
            entry.pack(side="left", fill="both", expand=True, padx=(15, 0))
            self.eye_btn = ctk.CTkButton(
                input_container, text="??", width=35, height=35,
                fg_color="transparent", text_color="black", hover_color="#CBD5E1",
                command=self.toggle_password_visibility
            )
            self.eye_btn.pack(side="right", padx=5)
        else:
            entry.pack(side="left", fill="both", expand=True, padx=15)
        self.last_entry = entry

    def validar_login(self):
        if self.user_entry.get() == "1" and self.pass_entry.get() == "1":
            self.on_login_success()
        else:
            self.error_label.configure(text=AppContext.t("Credenciales incorrectas."))

    def recargar_vista(self):
        for widget in self.card.winfo_children():
            widget.destroy()
        self.create_form()

    def regresar_a_terminal(self):
        self.master.mostrar_terminal()