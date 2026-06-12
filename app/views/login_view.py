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
        self.is_compact = (
            self.winfo_screenwidth() < 900 or self.winfo_screenheight() < 650
        )

        # --- BARRA SUPERIOR ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent", height=58)
        self.top_bar.place(relx=0, rely=0, relwidth=1)

        # Marca empresarial - Esquina superior izquierda
        self.koda_label_top = ctk.CTkLabel(
            self.top_bar, text="SECUREWORK",
            font=("Inter", 18, "bold"), text_color=COLORS["primary"]
        )
        self.koda_label_top.pack(side="left", padx=10, pady=10)

        # Contenedor de Controles - Esquina superior derecha
        self.controls_wrapper = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.controls_wrapper.pack(side="right", padx=8, pady=8)

        # 1. Control de Tema
        self.theme_control = ctk.CTkFrame(self.controls_wrapper, fg_color=COLORS["card"], corner_radius=8, width=82, height=34, border_width=1, border_color=COLORS["border"])
        self.theme_control.pack(side="left", padx=4)
        self.theme_control.pack_propagate(False)
        self.theme_icon = ctk.CTkLabel(self.theme_control, text="", font=("Inter", 16), text_color="black")
        self.theme_icon.place(x=22, y=19, anchor="center")
        self.theme_switch = ctk.CTkSwitch(
            self.theme_control, text="", width=45,
            progress_color="#1D1D1F", button_color="#1D1D1F",
            command=self.actualizar_icono_tema
        )
        self.theme_switch.place(x=55, y=17, anchor="center")

        # 2. Selector de Idioma
        self.lang_control = ctk.CTkFrame(self.controls_wrapper, fg_color=COLORS["card"], corner_radius=8, height=34, border_width=1, border_color=COLORS["border"])
        self.lang_control.pack(side="left", padx=4)
        ctk.CTkLabel(self.lang_control, text="", font=("Inter", 16), text_color="black").pack(side="left", padx=(12, 5))

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

        # Leer idioma guardado y pintar el botï¿½n correcto
        self._sincronizar_botones_idioma()

        # 3. Botï¿½n de Cï¿½mara
        self.btn_regresar_terminal = ctk.CTkButton(
            self.controls_wrapper, text="Cam", width=48, height=34, corner_radius=8,
            fg_color=COLORS["card"], text_color=COLORS["primary"], hover_color=COLORS["hover"],
            border_width=1, border_color=COLORS["border"], font=("Inter", 12, "bold"),
            command=self.regresar_a_terminal
        )
        self.btn_regresar_terminal.pack(side="left", padx=4)

        # --- TARJETA DE LOGIN CENTRAL ---
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            width=min(390, self.winfo_screenwidth() - 24),
            height=390 if self.is_compact else 440,
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        self.card.place(relx=0.5, rely=0.56 if self.is_compact else 0.55, anchor="center")
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
                tamanio_logo = (44, 44) if self.is_compact else (60, 60)
                pil_image_circular = self.hacer_imagen_circular(pil_image_original, tamanio_logo)
                self.logo_image = ctk.CTkImage(
                    light_image=pil_image_circular,
                    dark_image=pil_image_circular,
                    size=tamanio_logo
                )
                self.logo_label = ctk.CTkLabel(self.card, text="", image=self.logo_image)
                self.logo_label.pack(pady=(6 if self.is_compact else 12, 0))
                print("DEBUG: Imagen cargada con exito!")
            except Exception as e:
                print(f"ERROR: {e}")
        else:
            print("ERROR: No se encontro la imagen.")

        ctk.CTkLabel(
            self.card,
            text=AppContext.t("Acceso administrativo"),
            font=("Inter", 19 if self.is_compact else 22, "bold"),
            text_color=COLORS["text"], justify="center"
        ).pack(pady=(4 if self.is_compact else 6, 3))

        ctk.CTkLabel(
            self.card,
            text=AppContext.t("Verifica tu identidad para continuar"),
            font=("Inter", 11), text_color="#8E8E93"
        ).pack(pady=(0, 8 if self.is_compact else 14))

        self.create_input_group(AppContext.t("CORREO CORPORATIVO"), AppContext.t("Escribe tu correo"))
        self.user_entry = self.last_entry
        self.create_input_group(AppContext.t("CONTRASENA"), AppContext.t("Escribe tu contrasena"), is_password=True)
        self.pass_entry = self.last_entry

        self.error_label = ctk.CTkLabel(self.card, text="", text_color="#EF4444", font=("Inter", 13))
        self.error_label.pack(pady=(5, 0))

        self.login_btn = ctk.CTkButton(
            self.card,
            text=AppContext.t("INICIAR SESION"),
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            width=292, height=42, corner_radius=8,
            font=("Inter", 13, "bold"), command=self.validar_login
        )
        self.login_btn.pack(pady=(5 if self.is_compact else 8, 8))

    def _sincronizar_botones_idioma(self):
        """Pinta el botÃ³n activo segÃºn AppContext.idioma_actual."""
        if AppContext.idioma_actual == "es":
            self.es_btn.configure(fg_color=COLORS["primary"], text_color="white", hover_color=COLORS["primary_hover"])
            self.en_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")
        else:
            self.en_btn.configure(fg_color=COLORS["primary"], text_color="white", hover_color=COLORS["primary_hover"])
            self.es_btn.configure(fg_color="transparent", text_color="#4A4A4A", hover_color="#CBD5E1")

    def actualizar_idioma(self, lang):
        AppContext.set_idioma("es" if lang == "ES" else "en")
        self._sincronizar_botones_idioma()
        self.recargar_vista()

    def actualizar_icono_tema(self):
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        self.recargar_vista()

    # --------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------

    def toggle_password_visibility(self):
        if self.pass_entry.cget("show") == "*":
            self.pass_entry.configure(show="")
            self.eye_btn.configure(text="")
        else:
            self.pass_entry.configure(show="*")
            self.eye_btn.configure(text="")

    def create_input_group(self, label_text, placeholder, is_password=False):
        group_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        group_frame.pack(fill="x", padx=24 if self.is_compact else 34, pady=3 if self.is_compact else 4)
        lbl = ctk.CTkLabel(group_frame, text=label_text, font=("Inter", 10, "bold"), text_color=COLORS["text"])
        lbl.pack(side="top", anchor="w")
        input_container = ctk.CTkFrame(group_frame, fg_color=COLORS["card_alt"], height=40, corner_radius=8, border_width=1, border_color=COLORS["border"])
        input_container.pack(fill="x", pady=(4, 0))
        input_container.pack_propagate(False)
        entry = ctk.CTkEntry(
            input_container, placeholder_text=placeholder,
            fg_color="transparent", border_width=0,
            font=("Inter", 12), text_color=("black", "white")
        )
        if is_password:
            entry.configure(show="*")
            entry.pack(side="left", fill="both", expand=True, padx=(15, 0))
            self.eye_btn = ctk.CTkButton(
                input_container, text="", width=35, height=35,
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
