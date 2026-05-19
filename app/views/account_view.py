import json
import os
import shutil
import customtkinter as ctk
from PIL import Image, ImageTk
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

        self.font_header = ("Inter", 30, "bold")
        self.font_sub    = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small  = ("Inter", 11, "bold")

        # Cargar datos persistidos desde disco
        self.datos = _cargar_datos()

        # Referencia para evitar que el GC destruya la imagen
        self._ctk_foto = None

        self.crear_vista_lectura()

    # ─────────────────────────────────────────────────────────────────────────
    #  UTILIDADES
    # ─────────────────────────────────────────────────────────────────────────

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _cargar_ctk_image(self, size=(90, 90)):
        ruta = self.datos.get("foto")
        if ruta and os.path.exists(ruta):
            try:
                # 1. Abrir y recortar al centro en cuadrado
                img = Image.open(ruta).convert("RGBA")
                lado = min(img.size)
                left  = (img.width  - lado) // 2
                top   = (img.height - lado) // 2
                img   = img.crop((left, top, left + lado, top + lado))
                img   = img.resize(size, Image.LANCZOS)

                # 2. Máscara circular con antialiasing (escala 2×)
                mask_size = (size[0] * 2, size[1] * 2)
                mask = Image.new("L", mask_size, 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size[0], mask_size[1]), fill=255)
                mask = mask.resize(size, Image.LANCZOS)

                # 3. Aplicar máscara al canal alpha
                img.putalpha(mask)

                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
            except Exception:
                pass
        return None

    def _seleccionar_foto(self):
        """Abre el explorador, copia la imagen elegida y refresca el formulario."""
        ruta_origen = filedialog.askopenfilename(
            title="Seleccionar foto de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp *.bmp *.gif")]
        )
        if not ruta_origen:
            return

        os.makedirs(_FOTO_DIR, exist_ok=True)
        ext       = os.path.splitext(ruta_origen)[1]
        ruta_dest = os.path.join(_FOTO_DIR, f"avatar{ext}")
        shutil.copy2(ruta_origen, ruta_dest)

        self.datos["foto"] = ruta_dest
        _guardar_datos(self.datos)          # guarda la ruta de la foto de inmediato
        self.abrir_formulario_edicion()     # refresca para mostrar la nueva foto

    # ─────────────────────────────────────────────────────────────────────────
    #  VISTA LECTURA
    # ─────────────────────────────────────────────────────────────────────────

    def crear_vista_lectura(self):
        self.limpiar_pantalla()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))

        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text=AppContext.t("⚙️   Configuración Cuenta"),
                     font=self.font_header, text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_cont, text=AppContext.t("Configura tu perfil y preferencias"),
                     font=self.font_normal, text_color=COLORS["subtext"]).pack(anchor="w")

        ctk.CTkButton(header, text="📝 " + AppContext.t("Editar Perfil"),
                      fg_color=COLORS["card"], text_color=COLORS["text"],
                      border_width=1, border_color=COLORS["border"], hover_color=COLORS["hover"],
                      width=150, height=40, font=self.font_small,
                      command=self.abrir_formulario_edicion).pack(side="right", anchor="n")

        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(expand=True, fill="both", padx=40)

        self.create_profile_banner(is_editing=False)
        self.create_customization_card()

        ctk.CTkLabel(self.container, text="📋 " + AppContext.t("Detalles de la Cuenta"),
                     font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=(20, 10))
        self.create_read_only_field(AppContext.t("Nombres"),  self.datos["nombre"],   "👤")
        self.create_read_only_field(AppContext.t("Correo"),   self.datos["correo"],   "📧")
        self.create_read_only_field(AppContext.t("Teléfono"), self.datos["tel"],      "📞")
        self.create_read_only_field(AppContext.t("Facultad"), self.datos["facultad"], "🏛️")

        ctk.CTkButton(self.container, text="🚪 " + AppContext.t("Cerrar Sesión"),
                      fg_color="#FFF1F2", text_color="#E11D48", hover_color="#FEE2E2",
                      height=50, corner_radius=12, font=self.font_sub,
                      command=self.on_logout).pack(fill="x", pady=(40, 60), padx=30)

    # ─────────────────────────────────────────────────────────────────────────
    #  COMPONENTES COMPARTIDOS
    # ─────────────────────────────────────────────────────────────────────────

    def create_profile_banner(self, is_editing=False):
        card = ctk.CTkFrame(self.container, fg_color=COLORS["primary"], corner_radius=20, height=160)
        card.pack(fill="x", pady=10, padx=30)
        card.pack_propagate(False)

        # Avatar
        ctk_img = self._cargar_ctk_image(size=(90, 90))
        if ctk_img:
            # Con foto: frame transparente, la máscara circular de la imagen hace el círculo
            self._ctk_foto = ctk_img
            avatar_frame = ctk.CTkFrame(card, width=90, height=90, corner_radius=0, fg_color="transparent")
            avatar_frame.place(x=40, rely=0.5, anchor="w")
            avatar_frame.pack_propagate(False)
            ctk.CTkLabel(avatar_frame, image=ctk_img, text="", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        else:
            # Sin foto: frame con color de fondo y emoji
            avatar_frame = ctk.CTkFrame(card, width=90, height=90, corner_radius=45, fg_color=COLORS["hover"])
            avatar_frame.place(x=40, rely=0.5, anchor="w")
            avatar_frame.pack_propagate(False)
            ctk.CTkLabel(avatar_frame, text="👤", font=("Inter", 40)).place(relx=0.5, rely=0.5, anchor="center")

        if is_editing:
            ctk.CTkLabel(card, text=AppContext.t("Editar Registro..."),
                         font=("Inter", 18, "bold"), text_color="#FFFFFF").place(x=150, rely=0.35, anchor="w")
            ctk.CTkButton(card, text="📸 " + AppContext.t("Actualizar Foto"),
                          font=("Inter", 10, "bold"), fg_color="#38BDF8", text_color="#082736",
                          height=28, width=140, command=self._seleccionar_foto
                          ).place(x=150, rely=0.65, anchor="w")
        else:
            ctk.CTkLabel(card, text=self.datos["nombre"],
                         font=("Inter", 20, "bold"), text_color="#FFFFFF").place(x=150, rely=0.45, anchor="w")
            ctk.CTkLabel(card, text=AppContext.t("ADMINISTRADOR DEL SISTEMA"),
                         font=self.font_small, text_color="#38BDF8").place(x=150, rely=0.58, anchor="w")

    def create_customization_card(self):
        card = ctk.CTkFrame(self.container, fg_color=COLORS["card"], corner_radius=15,
                            border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=10, padx=30)

        ctk.CTkLabel(card, text="🎨 " + AppContext.t("Personalización"),
                     font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 10))

        f2 = ctk.CTkFrame(card, fg_color="transparent", height=40)
        f2.pack(fill="x", padx=20, pady=(5, 20))
        ctk.CTkLabel(f2, text="🌐 " + AppContext.t("Idioma del Sistema"),
                     font=self.font_normal, text_color=COLORS["text"]).pack(side="left")

        lang_group = ctk.CTkFrame(f2, fg_color=COLORS["hover"], corner_radius=10)
        lang_group.pack(side="right")

        color_es = "#1D1D1F" if AppContext.idioma_actual == "es" else "transparent"
        txt_es   = "white"   if AppContext.idioma_actual == "es" else COLORS["text"]
        ctk.CTkButton(lang_group, text="ES", width=40, height=30, fg_color=color_es, text_color=txt_es,
                      corner_radius=8, font=self.font_small,
                      command=lambda: self.cambiar_idioma_local("es")).pack(side="left", padx=2, pady=2)

        color_en = "#1D1D1F" if AppContext.idioma_actual == "en" else "transparent"
        txt_en   = "white"   if AppContext.idioma_actual == "en" else COLORS["text"]
        ctk.CTkButton(lang_group, text="EN", width=40, height=30, fg_color=color_en, text_color=txt_en,
                      corner_radius=8, font=self.font_small, hover_color="#CBD5E1",
                      command=lambda: self.cambiar_idioma_local("en")).pack(side="left", padx=2, pady=2)

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
        f = ctk.CTkFrame(self.container, fg_color=COLORS["card"], height=70, corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        f.pack(fill="x", pady=5, padx=30)
        f.pack_propagate(False)
        ctk.CTkLabel(f, text=icon,  font=("Inter", 18)).place(x=20, rely=0.5, anchor="w")
        ctk.CTkLabel(f, text=label, font=("Inter", 10, "bold"), text_color=COLORS["subtext"]).place(x=55, y=12)
        ctk.CTkLabel(f, text=value, font=self.font_sub, text_color=COLORS["text"]).place(x=55, y=32)

    def create_edit_field(self, parent, label, icon, placeholder, textvariable, padx=30):
        f = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        f.pack(fill="x", pady=5, padx=padx)

        header_row = ctk.CTkFrame(f, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(12, 2))
        ctk.CTkLabel(header_row, text=icon, font=("Inter", 14)).pack(side="left")
        ctk.CTkLabel(header_row, text=f"  {label}",
                     font=("Inter", 10, "bold"), text_color=COLORS["subtext"]).pack(side="left")

        entry = ctk.CTkEntry(f, textvariable=textvariable, placeholder_text=placeholder,
                             font=self.font_sub, fg_color="transparent", border_width=0,
                             text_color=COLORS["text"], height=35)
        entry.pack(fill="x", padx=15, pady=(0, 12))
        return entry

    def create_edit_field_grid(self, parent, label, icon, placeholder, textvariable, col=0):
        """Versión para layout de 2 columnas usando grid."""
        pad_left = (0, 4) if col == 0 else (4, 0)
        f = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=12,
                         border_width=1, border_color=COLORS["border"])
        f.grid(row=0, column=col, sticky="nsew", pady=5, padx=pad_left)

        header_row = ctk.CTkFrame(f, fg_color="transparent")
        header_row.pack(fill="x", padx=15, pady=(12, 2))
        ctk.CTkLabel(header_row, text=icon, font=("Inter", 14)).pack(side="left")
        ctk.CTkLabel(header_row, text=f"  {label}",
                     font=("Inter", 10, "bold"), text_color=COLORS["subtext"]).pack(side="left")

        entry = ctk.CTkEntry(f, textvariable=textvariable, placeholder_text=placeholder,
                             font=self.font_sub, fg_color="transparent", border_width=0,
                             text_color=COLORS["text"], height=35)
        entry.pack(fill="x", padx=15, pady=(0, 12))
        return entry

    # ─────────────────────────────────────────────────────────────────────────
    #  FORMULARIO DE EDICIÓN
    # ─────────────────────────────────────────────────────────────────────────

    def abrir_formulario_edicion(self):
        self.limpiar_pantalla()

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))

        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text=AppContext.t("✏️   Editar Registro"),
                     font=self.font_header, text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_cont, text=AppContext.t("Modifica tu información personal"),
                     font=self.font_normal, text_color=COLORS["subtext"]).pack(anchor="w")

        form_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        form_scroll.pack(expand=True, fill="both", padx=40)
        self.container = form_scroll

        self.create_profile_banner(is_editing=True)

        self.var_nombre   = ctk.StringVar(value=self.datos["nombre"])
        self.var_correo   = ctk.StringVar(value=self.datos["correo"])
        self.var_tel      = ctk.StringVar(value=self.datos["tel"])
        self.var_facultad = ctk.StringVar(value=self.datos["facultad"])

        ctk.CTkLabel(form_scroll, text="📋 " + AppContext.t("Información Personal"),
                     font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=30, pady=(20, 10))

        # Nombre — ancho completo
        self.create_edit_field(form_scroll, AppContext.t("Nombres"), "👤", "Nombre completo", self.var_nombre, padx=30)

        # Correo + Teléfono — 2 columnas
        row2 = ctk.CTkFrame(form_scroll, fg_color="transparent")
        row2.pack(fill="x", padx=30, pady=0)
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)
        self.create_edit_field_grid(row2, AppContext.t("Correo"),   "📧", "correo@dominio.com", self.var_correo, col=0)
        self.create_edit_field_grid(row2, AppContext.t("Teléfono"), "📞", "10 dígitos",         self.var_tel,    col=1)

        # Facultad — ancho completo
        self.create_edit_field(form_scroll, AppContext.t("Facultad"), "🏛️", "Nombre de la facultad", self.var_facultad, padx=30)

        btn_row = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=(20, 40))

        ctk.CTkButton(btn_row, text="💾 " + AppContext.t("Guardar Cambios"),
                      fg_color=COLORS["primary"], text_color="#FFFFFF",
                      hover_color=COLORS.get("primary_hover", COLORS["primary"]),
                      height=50, corner_radius=12, font=self.font_sub,
                      command=self.guardar_cambios
                      ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(btn_row, text=AppContext.t("Cancelar"),
                      fg_color=COLORS["card"], text_color=COLORS["text"],
                      border_width=1, border_color=COLORS["border"], hover_color=COLORS["hover"],
                      height=50, corner_radius=12, font=self.font_sub,
                      command=self.crear_vista_lectura
                      ).pack(side="left", expand=True, fill="x", padx=(8, 0))

    # ─────────────────────────────────────────────────────────────────────────
    #  GUARDAR
    # ─────────────────────────────────────────────────────────────────────────

    def guardar_cambios(self):
        nombre   = self.var_nombre.get().strip()
        correo   = self.var_correo.get().strip()
        tel      = self.var_tel.get().strip()
        facultad = self.var_facultad.get().strip()

        if not nombre or not correo:
            self._mostrar_toast(AppContext.t("El nombre y correo son obligatorios."), error=True)
            return

        self.datos["nombre"]   = nombre
        self.datos["correo"]   = correo
        self.datos["tel"]      = tel
        self.datos["facultad"] = facultad

        _guardar_datos(self.datos)   # <-- escribe en disco

        # actualizar_usuario(cuenta_id, nombre, correo, tel, facultad)  # BD real

        self._mostrar_toast(AppContext.t("Cambios guardados correctamente."), error=False)
        self.crear_vista_lectura()

    # ─────────────────────────────────────────────────────────────────────────
    #  TOAST
    # ─────────────────────────────────────────────────────────────────────────

    def _mostrar_toast(self, mensaje, error=False):
        color_bg   = "#FEE2E2" if error else "#D1FAE5"
        color_text = "#B91C1C" if error else "#065F46"
        toast = ctk.CTkLabel(self, text=mensaje, fg_color=color_bg, text_color=color_text,
                             corner_radius=10, font=self.font_small, padx=16, pady=10)
        toast.place(relx=0.5, rely=0.95, anchor="center")
        self.after(3000, toast.destroy)