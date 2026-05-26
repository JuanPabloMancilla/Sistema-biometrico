import json
import os
import shutil
import customtkinter as ctk
from PIL import Image, ImageDraw
from tkinter import filedialog
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.services.usuario_service import actualizar_usuario, obtener_usuario_por_cuenta

# --- Ruta del archivo de persistencia ---------------------------------------
_DATA_DIR  = os.path.join(os.path.dirname(__file__), "..", "data")
_DATA_FILE = os.path.join(_DATA_DIR, "perfil_usuario.json")
_FOTO_DIR  = os.path.join(_DATA_DIR, "fotos")

_DEFAULTS = {
    "nombre":   "ADMINISTRADOR EMPRESARIAL",
    "correo":   "admin@empresa.com",
    "tel":      "5512345678",
    "facultad": "DIRECCIÓN OPERATIVA",
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
    def __init__(self, master, on_logout, on_profile_updated=None):  # ? NUEVO parometro
        super().__init__(master, fg_color=COLORS["bg"])
        self.on_logout = on_logout
        self.on_profile_updated = on_profile_updated  # ? NUEVO

        self.is_compact = False
        self.is_medium = False
        self.current_view = "read"

        self.font_header = ("Inter", 28, "bold")
        self.font_sub    = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small  = ("Inter", 11, "bold")

        self.datos = _cargar_datos()
        self._ctk_foto = None

        self.bind("<Configure>", self._on_resize)
        self.crear_vista_lectura()

    def _on_resize(self, event=None):
        ancho = getattr(event, "width", None) or self.winfo_width()
        nuevo_compact = ancho <= 760
        nuevo_medium = 760 < ancho <= 1120

        if nuevo_compact != self.is_compact or nuevo_medium != self.is_medium:
            self.is_compact = nuevo_compact
            self.is_medium = nuevo_medium
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
        elif self.is_medium:
            self.font_header = ("Inter", 24, "bold")
            self.font_sub    = ("Inter", 14, "bold")
            self.font_normal = ("Inter", 12)
            self.font_small  = ("Inter", 10, "bold")
        else:
            self.font_header = ("Inter", 28, "bold")
            self.font_sub    = ("Inter", 16, "bold")
            self.font_normal = ("Inter", 13)
            self.font_small  = ("Inter", 11, "bold")

    def _layout(self):
        if self.is_compact:
            return {
                "page_pad": 10,
                "content_pad": 6,
                "header_y": (16, 8),
                "card_pad": 4,
                "banner_h": 180,
                "avatar": 64,
                "field_h": 78,
                "btn_h": 42,
            }
        if self.is_medium:
            return {
                "page_pad": 20,
                "content_pad": 14,
                "header_y": (22, 12),
                "card_pad": 0,
                "banner_h": 250,
                "avatar": 78,
                "field_h": 102,
                "btn_h": 44,
            }
        return {
            "page_pad": 28,
            "content_pad": 24,
            "header_y": (28, 16),
            "card_pad": 0,
            "banner_h": 260,
            "avatar": 94,
            "field_h": 112,
            "btn_h": 48,
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
            wraplength=560 if self.is_compact else 900,
            justify="left",
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_cont,
            text=subtitle,
            font=self.font_normal,
            text_color=COLORS["subtext"],
            wraplength=560 if self.is_compact else 900,
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
                width=150 if not self.is_compact else 110,
                height=40 if not self.is_compact else 34,
                font=self.font_small,
                command=button_command,
            )
            if self.is_compact:
                btn.pack(anchor="e", pady=(10, 0))
            else:
                btn.pack(side="right", anchor="n")

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
            filetypes=[("ImÃ¡genes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
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

    def crear_vista_lectura(self):
        self.current_view = "read"
        self._actualizar_fuentes()
        self.limpiar_pantalla()
        l = self._layout()

        self._pack_header(
            self,
            AppContext.t("Identidad administrativa"),
            AppContext.t("Perfil, contacto y sesion del operador"),
        )

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=l["page_pad"])

        top_grid = ctk.CTkFrame(self.container, fg_color="transparent")
        top_grid.pack(fill="x", padx=l["card_pad"], pady=(2, 14))

        if self.is_compact:
            self.create_profile_banner(is_editing=False)
        else:
            top_grid.columnconfigure(0, weight=1 if self.is_medium else 4, uniform="profile_top")
            top_grid.columnconfigure(1, weight=1 if self.is_medium else 3, uniform="profile_top")
            profile_host = ctk.CTkFrame(top_grid, fg_color="transparent")
            profile_host.grid(row=0, column=0, sticky="nsew", padx=(0, 10 if self.is_medium else 14))
            action_host = ctk.CTkFrame(top_grid, fg_color="transparent")
            action_host.grid(row=0, column=1, sticky="nsew")
            old_container = self.container
            self.container = profile_host
            self.create_profile_banner(is_editing=False)
            self.container = old_container
            self.create_session_panel(action_host)

        data_grid = ctk.CTkFrame(self.container, fg_color="transparent")
        data_grid.pack(fill="x", padx=l["card_pad"], pady=(0, 16))
        if not self.is_compact:
            data_grid.columnconfigure(0, weight=1)
            data_grid.columnconfigure(1, weight=1)

        fields = [
            (AppContext.t("Correo corporativo"), self.datos["correo"], COLORS["info"]),
            (AppContext.t("Telefono"), self.datos["tel"], COLORS["primary"]),
            (AppContext.t("Area operativa"), self.datos["facultad"], COLORS["accent"]),
            (AppContext.t("Rol del sistema"), AppContext.t("ADMINISTRADOR DEL SISTEMA"), COLORS["success"]),
        ]
        for idx, (label, value, color) in enumerate(fields):
            if self.is_compact:
                self.create_read_only_field(label, value, "", color=color, parent=data_grid)
            else:
                tile = self.create_read_only_field(label, value, "", color=color, parent=data_grid, pack_it=False)
                tile.grid(row=idx // 2, column=idx % 2, sticky="nsew", padx=(0 if idx % 2 == 0 else 8, 8 if idx % 2 == 0 else 0), pady=6)

        if self.is_compact:
            self.create_session_panel(self.container)

        ctk.CTkButton(
            self.container,
            text=AppContext.t("Cerrar SesiÃ³n"),
            fg_color="#33131B",
            text_color="#FCA5A5",
            hover_color="#4C1624",
            height=l["btn_h"],
            corner_radius=8,
            font=self.font_sub,
            command=self.on_logout,
        ).pack(fill="x", pady=(8, 45), padx=l["card_pad"])

    def create_profile_banner(self, is_editing=False):
        l = self._layout()
        avatar_size = l["avatar"]
        card = ctk.CTkFrame(
            self.container,
            fg_color=COLORS["sidebar"] if not is_editing else COLORS["card"],
            corner_radius=8,
            height=l["banner_h"],
            border_width=1,
            border_color=COLORS["border"] if is_editing else "#22304A",
        )
        card.pack(fill="x", pady=8, padx=l["card_pad"])
        card.pack_propagate(False)

        if self.is_compact:
            avatar_x = 12
            text_x = avatar_x + avatar_size + 10
            title_font = ("Inter", 12, "bold")
            role_font = ("Inter", 9, "bold")
            wrap = 460
        elif self.is_medium:
            avatar_x = 30
            text_x = avatar_x + avatar_size + 18
            title_font = ("Inter", 20, "bold")
            role_font = ("Inter", 10, "bold")
            wrap = 220
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
            ctk.CTkLabel(
                avatar_frame,
                text=self.datos.get("nombre", "A")[:1].upper(),
                font=("Inter", 32 if self.is_compact else 40, "bold"),
                text_color=COLORS["accent"],
            ).place(relx=0.5, rely=0.5, anchor="center")

        if is_editing:
            ctk.CTkLabel(
                card,
                text=AppContext.t("Editar identidad"),
                font=title_font,
                text_color=COLORS["text"],
                wraplength=wrap,
                justify="left",
            ).place(x=text_x, rely=0.35, anchor="w")

            ctk.CTkButton(
                card,
                text=AppContext.t("Actualizar Foto"),
                font=("Inter", 9 if self.is_compact else 10, "bold"),
                fg_color="#38BDF8",
                text_color="#082736",
                height=28,
                width=112 if self.is_compact else 140,
                command=self._seleccionar_foto,
            ).place(x=text_x, rely=0.65, anchor="w")
        else:
            ctk.CTkLabel(
                card,
                text=self.datos["nombre"],
                font=("Inter", 17 if self.is_compact else 20 if self.is_medium else 26, "bold"),
                text_color="#FFFFFF",
                wraplength=wrap,
                justify="left",
            ).place(x=text_x, rely=0.38, anchor="w")
            ctk.CTkLabel(
                card,
                text=AppContext.t("ADMINISTRADOR DEL SISTEMA"),
                font=role_font,
                text_color=COLORS["accent"],
            ).place(x=text_x, rely=0.58, anchor="w")
            ctk.CTkLabel(
                card,
                text=AppContext.t("Operador con permisos de gestion y auditoria"),
                font=("Inter", 9 if self.is_medium else 10 if self.is_compact else 12),
                text_color=COLORS["sidebar_muted"],
                wraplength=wrap,
                justify="left",
            ).place(x=text_x, rely=0.76, anchor="w")

    def create_session_panel(self, parent):
        l = self._layout()
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.pack(fill="both", expand=True, padx=l["card_pad"], pady=8)

        ctk.CTkFrame(card, fg_color=COLORS["accent"], height=4, corner_radius=0).pack(fill="x")
        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=18)

        ctk.CTkLabel(
            body,
            text=AppContext.t("Sesion administrativa").upper(),
            font=("Inter", 10, "bold"),
            text_color=COLORS["subtext"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            body,
            text=AppContext.t("Activa"),
            font=("Inter", 28 if not self.is_compact else 22, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", pady=(8, 0))
        ctk.CTkLabel(
            body,
            text=AppContext.t("Los cambios de perfil se reflejan en la barra superior del sistema."),
            font=("Inter", 12),
            text_color=COLORS["subtext"],
            wraplength=260 if self.is_medium else 280,
            justify="left",
        ).pack(anchor="w", pady=(6, 16))

        ctk.CTkButton(
            body,
            text=AppContext.t("Editar perfil"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#FFFFFF",
            height=38,
            corner_radius=8,
            font=self.font_small,
            command=self.abrir_formulario_edicion,
        ).pack(fill="x", pady=(0, 8))

    def create_read_only_field(self, label, value, icon, color=None, parent=None, pack_it=True):
        l = self._layout()
        parent = parent or self.container
        color = color or COLORS["primary"]
        f = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            height=l["field_h"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        if pack_it:
            f.pack(fill="x", pady=5, padx=l["card_pad"])
        f.pack_propagate(False)

        ctk.CTkFrame(f, fg_color=color, width=4, corner_radius=0).pack(side="left", fill="y")
        x_text = 18 if self.is_compact else 22
        ctk.CTkLabel(
            f,
            text=label.upper(),
            font=("Inter", 9 if self.is_compact else 10, "bold"),
            text_color=COLORS["subtext"],
        ).place(x=x_text, y=18)
        ctk.CTkLabel(
            f,
            text=value,
            font=self.font_sub,
            text_color=COLORS["text"],
            wraplength=300 if self.is_medium else 280 if not self.is_compact else 520,
            justify="left",
        ).place(x=x_text, y=44)
        return f

    def create_edit_field(self, parent, label, icon, placeholder, textvariable, padx=None):
        l = self._layout()
        if padx is None:
            padx = l["card_pad"]

        f = ctk.CTkFrame(
            parent,
            fg_color=COLORS["card"],
            corner_radius=8,
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
            corner_radius=8,
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

    def abrir_formulario_edicion(self):
        self.current_view = "edit"
        self._actualizar_fuentes()
        self.limpiar_pantalla()
        l = self._layout()

        self._pack_header(
            self,
            AppContext.t("Editar identidad"),
            AppContext.t("Actualiza los datos visibles del operador"),
        )

        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.pack(expand=True, fill="both", padx=l["page_pad"])
        self.container = form_scroll

        self.var_nombre = ctk.StringVar(value=self.datos["nombre"])
        self.var_correo = ctk.StringVar(value=self.datos["correo"])
        self.var_tel = ctk.StringVar(value=self.datos["tel"])
        self.var_facultad = ctk.StringVar(value=self.datos["facultad"])

        edit_shell = ctk.CTkFrame(form_scroll, fg_color="transparent")
        edit_shell.pack(fill="both", expand=True, padx=l["card_pad"], pady=(0, 24))
        if not self.is_compact:
            edit_shell.columnconfigure(0, weight=1)
            edit_shell.columnconfigure(1, weight=2)

        identity_card = ctk.CTkFrame(
            edit_shell,
            fg_color=COLORS["sidebar"],
            corner_radius=8,
            border_width=1,
            border_color="#22304A",
            height=280,
        )
        if self.is_compact:
            identity_card.pack(fill="x", pady=(0, 12))
        else:
            identity_card.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        identity_card.pack_propagate(False)

        avatar_size = 84 if not self.is_compact else 64
        ctk_img = self._cargar_ctk_image(size=(avatar_size, avatar_size))
        avatar = ctk.CTkFrame(identity_card, width=avatar_size, height=avatar_size, corner_radius=avatar_size // 2, fg_color="#111C31")
        avatar.pack(anchor="w", padx=22, pady=(24, 10))
        avatar.pack_propagate(False)
        if ctk_img:
            self._ctk_foto = ctk_img
            ctk.CTkLabel(avatar, image=ctk_img, text="", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(avatar, text=self.datos["nombre"][:1].upper(), font=("Inter", 30, "bold"), text_color=COLORS["accent"]).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            identity_card,
            text=AppContext.t("Foto y perfil"),
            font=("Inter", 22 if not self.is_compact else 18, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w", padx=22)
        ctk.CTkLabel(
            identity_card,
            text=AppContext.t("La imagen se usara en la consola administrativa."),
            font=("Inter", 12),
            text_color=COLORS["sidebar_muted"],
            wraplength=230,
            justify="left",
        ).pack(anchor="w", padx=22, pady=(4, 16))
        ctk.CTkButton(
            identity_card,
            text=AppContext.t("Actualizar Foto"),
            font=self.font_small,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color="#111827",
            height=38,
            corner_radius=8,
            command=self._seleccionar_foto,
        ).pack(anchor="w", padx=22, fill="x")

        form_card = ctk.CTkFrame(
            edit_shell,
            fg_color=COLORS["card"],
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"],
        )
        if self.is_compact:
            form_card.pack(fill="x")
        else:
            form_card.grid(row=0, column=1, sticky="nsew")

        ctk.CTkLabel(
            form_card,
            text=AppContext.t("Datos del operador"),
            font=("Inter", 18, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w", padx=18, pady=(18, 6))

        self.create_edit_field(form_card, AppContext.t("Nombres"), "", AppContext.t("Nombre completo"), self.var_nombre, padx=18)
        self.create_edit_field(form_card, AppContext.t("Correo"), "", "correo@dominio.com", self.var_correo, padx=18)
        self.create_edit_field(form_card, AppContext.t("Telefono"), "", AppContext.t("10 digitos"), self.var_tel, padx=18)
        self.create_edit_field(form_card, AppContext.t("Area operativa"), "", AppContext.t("Nombre del area"), self.var_facultad, padx=18)

        btn_row = ctk.CTkFrame(form_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=18, pady=(10, 18))

        if self.is_compact:
            ctk.CTkButton(
                btn_row,
                text=AppContext.t("Guardar Cambios"),
                fg_color=COLORS["primary"],
                text_color="#FFFFFF",
                hover_color=COLORS.get("primary_hover", COLORS["primary"]),
                height=l["btn_h"],
                corner_radius=8,
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
                corner_radius=8,
                font=self.font_sub,
                command=self.crear_vista_lectura,
            ).pack(fill="x")
        else:
            ctk.CTkButton(
                btn_row,
                text=AppContext.t("Guardar Cambios"),
                fg_color=COLORS["primary"],
                text_color="#FFFFFF",
                hover_color=COLORS.get("primary_hover", COLORS["primary"]),
                height=l["btn_h"],
                corner_radius=8,
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
                corner_radius=8,
                font=self.font_sub,
                command=self.crear_vista_lectura,
            ).pack(side="left", expand=True, fill="x", padx=(8, 0))

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

        # ? NUEVO: notificar al dashboard para que refresque el sidebar
        if self.on_profile_updated:
            self.on_profile_updated()

        self._mostrar_toast(AppContext.t("Cambios guardados correctamente."), error=False)
        self.crear_vista_lectura()

    # ---------------------------------------------------------------------
    # TOAST
    # ---------------------------------------------------------------------

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
