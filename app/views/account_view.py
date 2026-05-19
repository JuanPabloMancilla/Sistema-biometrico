import json
import os
import shutil
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.services.usuario_service import actualizar_usuario, obtener_usuario_por_cuenta

# ─── Ruta del archivo de persistencia ───────────────────────────────────────
_DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
_DATA_FILE = os.path.join(_DATA_DIR, "perfil_usuario.json")
_FOTO_DIR  = os.path.join(_DATA_DIR, "fotos")

_DEFAULTS = {
    "nombre":   "ADMINISTRADOR DEL SISTEMA",
    "correo":   "admin@universidad.edu.mx",
    "tel":      "5512345678",
    "facultad": "ADMINISTRACIÓN CENTRAL",
    "foto":     None,
}


def _cargar_datos() -> dict:
    """Lee el JSON de perfil; si no existe devuelve los valores por defecto."""
    if os.path.exists(_DATA_FILE):
        try:
            with open(_DATA_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
            for k, v in _DEFAULTS.items():
                datos.setdefault(k, v)
            return datos
        except Exception:
            pass
    return dict(_DEFAULTS)


def _guardar_datos(datos: dict) -> None:
    """Escribe el JSON de perfil en disco."""
    os.makedirs(_DATA_DIR, exist_ok=True)
    with open(_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


class AccountView(ctk.CTkFrame):
    def __init__(self, master, on_logout):
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_logout = on_logout

        self.is_compact = False
        self.current_view = "read"

        self.font_header = ("Inter", 30, "bold")
        self.font_sub    = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small  = ("Inter", 11, "bold")

        self.datos = _cargar_datos()
        self._ctk_foto = None

        self.bind("<Configure>", self._on_resize)
        self.crear_vista_lectura()

    # ─────────────────────────────────────────────────────────────────────
    # RESPONSIVE
    # ─────────────────────────────────────────────────────────────────────

    def _on_resize(self, event=None):
        ancho = self.winfo_width()
        nuevo_compact = ancho <= 620

        if nuevo_compact != self.is_compact:
            self.is_compact = nuevo_compact
            self._actualizar_fuentes()
            if self.current_view == "edit":
                self.abrir_formulario_edicion()
            else:
                self.crear_vista_lectura()

    def _actualizar_fuentes(self):
        if self.is_compact:
            self.font_header = ("Inter", 20, "bold")
            self.font_sub    = ("Inter", 13, "bold")
            self.font_normal = ("Inter", 11)
            self.font_small  = ("Inter", 10, "bold")
        else:
            self.font_header = ("Inter", 30, "bold")
            self.font_sub    = ("Inter", 16, "bold")
            self.font_normal = ("Inter", 13)
            self.font_small  = ("Inter", 11, "bold")

    def _layout(self):
        if self.is_compact:
            return {
                "page_pad": 12,
                "content_pad": 8,
                "header_y": (18, 10),
                "card_pad": 6,
                "banner_h": 138,
                "avatar": 70,
                "field_h": 62,
                "btn_h": 44,
            }
        return {
            "page_pad": 40,
            "content_pad": 30,
            "header_y": (40, 20),
            "card_pad": 30,
            "banner_h": 160,
            "avatar": 90,
            "field_h": 70,
            "btn_h": 50,
        }

    def _pack_header(self, parent, title, subtitle, button_text=None, button_command=None):
        l = self._layout()
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=l["page_pad"], pady=l["header_y"])

        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(fill="x", side="top" if self.is_compact else "left")

        ctk.CTkLabel(
            title_cont,
            text=title,
            font=self.font_header,
            text_color=COLORS["text"],
            wraplength=430 if self.is_compact else 900,
            justify="left",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_cont,
            text=subtitle,
            font=self.font_normal,
            text_color=COLORS["subtext"],
            wraplength=430 if self.is_compact else 900,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        if button_text and button_command:
            btn = ctk.CTkButton(
                header,
                text=button_text,
                fg_color=COLORS["card"],
                text_color=COLORS["text"],
                border_width=1,
                border_color=COLORS["border"],
                hover_color=COLORS["hover"],
                width=150 if not self.is_compact else 120,
                height=40 if not self.is_compact else 36,
                font=self.font_small,
                command=button_command,
            )
            if self.is_compact:
                btn.pack(anchor="e", pady=(10, 0))
            else:
                btn.pack(side="right", anchor="n")

    # ─────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _cargar_ctk_image(self, size=(90, 90)):
        ruta = self.datos.get("foto")
        if ruta and os.path.exists(ruta):
            try:
                img = Image.open(ruta).convert("RGBA")
                lado = min(img.size)
                left = (img.width - lado) // 2
                top = (img.height - lado) // 2
                img = img.crop((left, top, left + lado, top + lado))
                img = img.resize(size, Image.LANCZOS)

                mask_size = (size[0] * 2, size[1] * 2)
                mask = Image.new("L", mask_size, 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
                mask = mask.resize(size, Image.LANCZOS)
                img.putalpha(mask)

                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception:
                pass
        return None

    def _seleccionar_foto(self):
        ruta_origen = filedialog.askopenfilename(
            title="Seleccionar foto de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
        )
        if not ruta_origen:
            return

        os.makedirs(_FOTO_DIR, exist_ok=True)
        ext = os.path.splitext(ruta_origen)[1]
        ruta_dest = os.path.join(_FOTO_DIR, f"avatar{ext}")
        shutil.copy2(ruta_origen, ruta_dest)

        self.datos["foto"] = ruta_dest
        _guardar_datos(self.datos)
        self.abrir_formulario_edicion()

    # ─────────────────────────────────────────────────────────────────────
    # VISTA LECTURA
    # ─────────────────────────────────────────────────────────────────────

    def crear_vista_lectura(self):
        self.current_view = "read"
        self._actualizar_fuentes()
        self.limpiar_pantalla()
        l = self._layout()

        self._pack_header(
            self,
            AppContext.t("⚙️ Configuración Cuenta") if self.is_compact else AppContext.t("⚙️   Configuración Cuenta"),
            AppContext.t("Configura tu perfil y preferencias"),
            "📝 " + AppContext.t("Editar" if self.is_compact else "Editar Perfil"),
            self.abrir_formulario_edicion,
        )

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=l["page_pad"])

        self.create_profile_banner(is_editing=False)
        self.create_customization_card()

        ctk.CTkLabel(
            self.container,
            text="📋 " + AppContext.t("Detalles de la Cuenta"),
            font=self.font_sub,
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=l["card_pad"], pady=(14, 8))

        self.create_read_only_field(AppContext.t("Nombres"),  self.datos["nombre"],   "👤")
        self.create_read_only_field(AppContext.t("Correo"),   self.datos["correo"],   "📧")
        self.create_read_only_field(AppContext.t("Teléfono"), self.datos["tel"],      "📞")
        self.create_read_only_field(AppContext.t("Facultad"), self.datos["facultad"], "🏛️")

        ctk.CTkButton(
            self.container,
            text="🚪 " + AppContext.t("Cerrar Sesión"),
            fg_color="#FFF1F2",
            text_color="#E11D48",
            hover_color="#FEE2E2",
            height=l["btn_h"],
            corner_radius=12,
            font=self.font_sub,
            command=self.on_logout,
        ).pack(fill="x", pady=(24, 45), padx=l["card_pad"])

    # ─────────────────────────────────────────────────────────────────────
    # COMPONENTES COMPARTIDOS
    # ─────────────────────────────────────────────────────────────────────

    def create_profile_banner(self, is_editing=False):
        l = self._layout()
        avatar_size = l["avatar"]
        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["primary"],
            corner_radius=18,
            height=l["banner_h"],
        )
        card.pack(fill="x", pady=8, padx=l["card_pad"])
        card.pack_propagate(False)

        if self.is_compact:
            avatar_x = 18
            text_x = avatar_x + avatar_size + 14
            title_font = ("Inter", 14, "bold")
            role_font = ("Inter", 9, "bold")
            wrap = 240
        else:
            avatar_x = 40
            text_x = 150
            title_font = ("Inter", 20, "bold")
            role_font = self.font_small
            wrap = 700

        ctk_img = self._cargar_ctk_image(size=(avatar_size, avatar_size))
        if ctk_img:
            self._ctk_foto = ctk_img
            avatar_frame = ctk.CTkFrame(card, width=avatar_size, height=avatar_size, corner_radius=0, fg_color="transparent")
            avatar_frame.place(x=avatar_x, rely=0.5, anchor="w")
            avatar_frame.pack_propagate(False)
            ctk.CTkLabel(avatar_frame, image=ctk_img, text="", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        else:
            avatar_frame = ctk.CTkFrame(card, width=avatar_size, height=avatar_size, corner_radius=avatar_size // 2, fg_color=COLORS["hover"])
            avatar_frame.place(x=avatar_x, rely=0.5, anchor="w")
            avatar_frame.pack_propagate(False)
            ctk.CTkLabel(avatar_frame, text="👤", font=("Inter", 32 if self.is_compact else 40)).place(relx=0.5, rely=0.5, anchor="center")

        if is_editing:
            ctk.CTkLabel(
                card,
                text=AppContext.t("Editar Registro..."),
                font=title_font,
                text_color="#FFFFFF",
                wraplength=wrap,
                justify="left",
            ).place(x=text_x, rely=0.35, anchor="w")

            ctk.CTkButton(
                card,
                text="📸 " + AppContext.t("Actualizar Foto"),
                font=("Inter", 9 if self.is_compact else 10, "bold"),
                fg_color="#38BDF8",
                text_color="#082736",
                height=28,
                width=126 if self.is_compact else 140,
                command=self._seleccionar_foto,
            ).place(x=text_x, rely=0.65, anchor="w")
        else:
            ctk.CTkLabel(
                card,
                text=self.datos["nombre"],
                font=title_font,
                text_color="#FFFFFF",
                wraplength=wrap,
                justify="left",
            ).place(x=text_x, rely=0.42, anchor="w")
            ctk.CTkLabel(
                card,
                text=AppContext.t("ADMINISTRADOR DEL SISTEMA"),
                font=role_font,
                text_color="#38BDF8",
            ).place(x=text_x, rely=0.62, anchor="w")

    def create_customization_card(self):
        l = self._layout()
        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.pack(fill="x", pady=8, padx=l["card_pad"])

        ctk.CTkLabel(
            card,
            text="🎨 " + AppContext.t("Personalización"),
            font=self.font_sub,
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=16, pady=(14, 8))

        f2 = ctk.CTkFrame(card, fg_color="transparent")
        f2.pack(fill="x", padx=16, pady=(4, 16))

        ctk.CTkLabel(
            f2,
            text="🌐 " + AppContext.t("Idioma del Sistema"),
            font=self.font_normal,
            text_color=COLORS["text"],
        ).pack(side="left", anchor="w")

        lang_group = ctk.CTkFrame(f2, fg_color=COLORS["hover"], corner_radius=10)
        lang_group.pack(side="right", anchor="e")

        color_es = "#1D1D1F" if AppContext.idioma_actual == "es" else "transparent"
        txt_es = "white" if AppContext.idioma_actual == "es" else COLORS["text"]
        ctk.CTkButton(
            lang_group,
            text="ES",
            width=36 if self.is_compact else 40,
            height=28 if self.is_compact else 30,
            fg_color=color_es,
            text_color=txt_es,
            corner_radius=8,
            font=self.font_small,
            command=lambda: self.cambiar_idioma_local("es"),
        ).pack(side="left", padx=2, pady=2)

        color_en = "#1D1D1F" if AppContext.idioma_actual == "en" else "transparent"
        txt_en = "white" if AppContext.idioma_actual == "en" else COLORS["text"]
        ctk.CTkButton(
            lang_group,
            text="EN",
            width=36 if self.is_compact else 40,
            height=28 if self.is_compact else 30,
            fg_color=color_en,
            text_color=txt_en,
            corner_radius=8,
            font=self.font_small,
            hover_color="#CBD5E1",
            command=lambda: self.cambiar_idioma_local("en"),
        ).pack(side="left", padx=2, pady=2)

    def cambiar_idioma_local(self, nuevo_idioma):
        if AppContext.idioma_actual == nuevo_idioma:
            return
        AppContext.set_idioma(nuevo_idioma)
        ptr, main_app = self, None
        while ptr is not None:
            if hasattr(ptr, "refrescar_idioma_completo"):
                main_app = ptr
                break
            ptr = ptr.master
        if main_app:
            main_app.refrescar_idioma_completo()
        else:
            self.crear_vista_lectura()

    def create_read_only_field(self, label, value, icon):
        l = self._layout()
        f = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["card"],
            height=l["field_h"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        f.pack(fill="x", pady=5, padx=l["card_pad"])
        f.pack_propagate(False)

        x_icon = 14 if self.is_compact else 20
        x_text = 45 if self.is_compact else 55
        ctk.CTkLabel(f, text=icon, font=("Inter", 16 if self.is_compact else 18)).place(x=x_icon, rely=0.5, anchor="w")
        ctk.CTkLabel(f, text=label, font=("Inter", 9 if self.is_compact else 10, "bold"), text_color=COLORS["subtext"]).place(x=x_text, y=10)
        ctk.CTkLabel(
            f,
            text=value,
            font=self.font_sub,
            text_color=COLORS["text"],
            wraplength=330 if self.is_compact else 900,
            justify="left",
        ).place(x=x_text, y=30)

    def create_edit_field(self, parent, label, icon, placeholder, textvariable, padx=None):
        l = self._layout()
        if padx is None:
            padx = l["card_pad"]

        f = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        f.pack(fill="x", pady=5, padx=padx)

        header_row = ctk.CTkFrame(f, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(header_row, text=icon, font=("Inter", 13 if self.is_compact else 14)).pack(side="left")
        ctk.CTkLabel(header_row, text=f"  {label}", font=("Inter", 9 if self.is_compact else 10, "bold"), text_color=COLORS["subtext"]).pack(side="left")

        entry = ctk.CTkEntry(
            f,
            textvariable=textvariable,
            placeholder_text=placeholder,
            font=self.font_sub,
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text"],
            height=32 if self.is_compact else 35,
        )
        entry.pack(fill="x", padx=12, pady=(0, 10))
        return entry

    def create_edit_field_grid(self, parent, label, icon, placeholder, textvariable, row=0, col=0):
        pad_left = (0, 4) if col == 0 else (4, 0)
        f = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        f.grid(row=row, column=col, sticky="nsew", pady=5, padx=pad_left)

        header_row = ctk.CTkFrame(f, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 2))
        ctk.CTkLabel(header_row, text=icon, font=("Inter", 14)).pack(side="left")
        ctk.CTkLabel(header_row, text=f"  {label}", font=("Inter", 10, "bold"), text_color=COLORS["subtext"]).pack(side="left")

        entry = ctk.CTkEntry(
            f,
            textvariable=textvariable,
            placeholder_text=placeholder,
            font=self.font_sub,
            fg_color="transparent",
            border_width=0,
            text_color=COLORS["text"],
            height=35,
        )
        entry.pack(fill="x", padx=12, pady=(0, 10))
        return entry

    # ─────────────────────────────────────────────────────────────────────
    # FORMULARIO DE EDICIÓN
    # ─────────────────────────────────────────────────────────────────────

    def abrir_formulario_edicion(self):
        self.current_view = "edit"
        self._actualizar_fuentes()
        self.limpiar_pantalla()
        l = self._layout()

        self._pack_header(
            self,
            AppContext.t("✏️ Editar Registro") if self.is_compact else AppContext.t("✏️   Editar Registro"),
            AppContext.t("Modifica tu información personal"),
        )

        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.pack(expand=True, fill="both", padx=l["page_pad"])
        self.container = form_scroll

        self.create_profile_banner(is_editing=True)

        self.var_nombre = ctk.StringVar(value=self.datos["nombre"])
        self.var_correo = ctk.StringVar(value=self.datos["correo"])
        self.var_tel = ctk.StringVar(value=self.datos["tel"])
        self.var_facultad = ctk.StringVar(value=self.datos["facultad"])

        ctk.CTkLabel(
            form_scroll,
            text="📋 " + AppContext.t("Información Personal"),
            font=self.font_sub,
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=l["card_pad"], pady=(14, 8))

        self.create_edit_field(form_scroll, AppContext.t("Nombres"), "👤", "Nombre completo", self.var_nombre)

        if self.is_compact:
            # En 480x800 se apilan para que no se aplasten.
            self.create_edit_field(form_scroll, AppContext.t("Correo"), "📧", "correo@dominio.com", self.var_correo)
            self.create_edit_field(form_scroll, AppContext.t("Teléfono"), "📞", "10 dígitos", self.var_tel)
        else:
            row2 = ctk.CTkFrame(form_scroll, fg_color="transparent")
            row2.pack(fill="x", padx=l["card_pad"], pady=0)
            row2.columnconfigure(0, weight=1)
            row2.columnconfigure(1, weight=1)
            self.create_edit_field_grid(row2, AppContext.t("Correo"), "📧", "correo@dominio.com", self.var_correo, col=0)
            self.create_edit_field_grid(row2, AppContext.t("Teléfono"), "📞", "10 dígitos", self.var_tel, col=1)

        self.create_edit_field(form_scroll, AppContext.t("Facultad"), "🏛️", "Nombre de la facultad", self.var_facultad)

        btn_row = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=l["card_pad"], pady=(16, 40))

        if self.is_compact:
            ctk.CTkButton(
                btn_row,
                text="💾 " + AppContext.t("Guardar Cambios"),
                fg_color=COLORS["primary"],
                text_color="#FFFFFF",
                hover_color=COLORS.get("primary_hover", COLORS["primary"]),
                height=l["btn_h"],
                corner_radius=12,
                font=self.font_sub,
                command=self.guardar_cambios,
            ).pack(fill="x", pady=(0, 8))

            ctk.CTkButton(
                btn_row,
                text=AppContext.t("Cancelar"),
                fg_color=COLORS["card"],
                text_color=COLORS["text"],
                border_width=1,
                border_color=COLORS["border"],
                hover_color=COLORS["hover"],
                height=l["btn_h"],
                corner_radius=12,
                font=self.font_sub,
                command=self.crear_vista_lectura,
            ).pack(fill="x")
        else:
            ctk.CTkButton(
                btn_row,
                text="💾 " + AppContext.t("Guardar Cambios"),
                fg_color=COLORS["primary"],
                text_color="#FFFFFF",
                hover_color=COLORS.get("primary_hover", COLORS["primary"]),
                height=l["btn_h"],
                corner_radius=12,
                font=self.font_sub,
                command=self.guardar_cambios,
            ).pack(side="left", expand=True, fill="x", padx=(0, 8))

            ctk.CTkButton(
                btn_row,
                text=AppContext.t("Cancelar"),
                fg_color=COLORS["card"],
                text_color=COLORS["text"],
                border_width=1,
                border_color=COLORS["border"],
                hover_color=COLORS["hover"],
                height=l["btn_h"],
                corner_radius=12,
                font=self.font_sub,
                command=self.crear_vista_lectura,
            ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    # ─────────────────────────────────────────────────────────────────────
    # GUARDAR
    # ─────────────────────────────────────────────────────────────────────

    def guardar_cambios(self):
        nombre = self.var_nombre.get().strip()
        correo = self.var_correo.get().strip()
        tel = self.var_tel.get().strip()
        facultad = self.var_facultad.get().strip()

        if not nombre or not correo:
            self._mostrar_toast(AppContext.t("El nombre y correo son obligatorios."), error=True)
            return

        self.datos["nombre"] = nombre
        self.datos["correo"] = correo
        self.datos["tel"] = tel
        self.datos["facultad"] = facultad

        _guardar_datos(self.datos)

        # actualizar_usuario(cuenta_id, nombre, correo, tel, facultad)  # BD real

        self._mostrar_toast(AppContext.t("Cambios guardados correctamente."), error=False)
        self.crear_vista_lectura()

    # ─────────────────────────────────────────────────────────────────────
    # TOAST
    # ─────────────────────────────────────────────────────────────────────

    def _mostrar_toast(self, mensaje, error=False):
        color_bg = "#FEE2E2" if error else "#D1FAE5"
        color_text = "#B91C1C" if error else "#065F46"
        toast = ctk.CTkLabel(
            self,
            text=mensaje,
            fg_color=color_bg,
            text_color=color_text,
            corner_radius=10,
            font=self.font_small,
            padx=14,
            pady=8,
            wraplength=360 if self.is_compact else 700,
        )
        toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(3000, toast.destroy)
