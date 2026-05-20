import customtkinter as ctk
import re
from app.views.terminal_view import TerminalView
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.detection.detector_rostro import encodings_db, usuarios_db
from app.recognition.encoding_manager import (
    cargar_encodings,
    eliminar_encoding,
    guardar_encoding,
    find_best_match
)
from app.services.carrera_service import obtener_todas_carreras, obtener_facultades_para_dropdown
from app.services.usuario_service import (
    crear_usuario,
    actualizar_usuario,
    existe_correo,
    existe_cuenta,
    obtener_todos_usuarios,
    obtener_usuario_por_id,
    obtener_id_facultad_por_nombre,
    desactivar_usuario,
    reactivar_usuario
)

TIPOS_USUARIO = {
    1: "Estudiante",
    2: "Docente",
    3: "Trabajador"
}

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color=COLORS["bg"])
        self.controller = controller
        self.usuario_editando_id = None

        self.font_header = ("Inter", 30, "bold")
        self.font_sub    = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small  = ("Inter", 11, "bold")

        self.rol_var             = ctk.StringVar(value="ESTUDIANTE")
        self.carrera_var         = ctk.StringVar()
        self.inputs_obligatorios = {}
        self.inputs_apellidos    = {}

        self.refresh_data()

        self.colors = {
            "DOCENTE":     {"bg": "#F3E8FF", "text": "#A855F7"},
            "ESTUDIANTE":  {"bg": "#DBEAFE", "text": "#3B82F6"},
            "TRABAJADOR":  {"bg": "#D1FAE5", "text": "#10B981"}
        }

        self.filtro_rol_actual = "Todos"
        self.filter_visible    = False
        self.is_compact        = False
        self.bind("<Configure>", self._on_resize)

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)

        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")

        self.main_card = ctk.CTkFrame(
            self.vista_tabla,
            fg_color=COLORS["card"],
            corner_radius=15,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))

        self.render_table_content(self.all_users)

    # ─────────────────────────────────────────────────────────────
    # DATA
    # ─────────────────────────────────────────────────────────────
    def refresh_data(self):
        try:
            data = obtener_todos_usuarios()
            self.all_users = []
            for u in data:
                self.all_users.append({
                    "nombre_solo": u["nombre"],
                    "ap":          u["a_paterno"],
                    "am":          u["a_materno"],
                    "r":           TIPOS_USUARIO.get(u.get("tipo_usuario", 1), "N/A"),
                    "cuenta":      u.get("cuenta", ""),
                    "id":          u["id_usuario"],
                    "correo":      u.get("correo", ""),
                    "estado":      u.get("estado", 1)
                })
            self.all_users.sort(key=lambda u: (u["estado"] == 0, u["nombre_solo"]))
        except Exception as e:
            print("Error usuarios:", e)
            self.all_users = []

    # ─────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────
    def validar_ocho_numeros(self, P):
        if P == "":
            return True
        return P.isdigit() and len(P) <= 8

    def limpiar_texto(self, texto):
        return " ".join(texto.strip().split()).title()

    def validar_texto_real(self, texto):
        texto = texto.strip()
        if len(texto) < 2:
            return False
        return bool(re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", texto))

    # ─────────────────────────────────────────────────────────────
    # RESIZE
    # ─────────────────────────────────────────────────────────────
    def _on_resize(self, event):
        nuevo_compact = event.width < 700
        if nuevo_compact != self.is_compact:
            self.is_compact = nuevo_compact
            if hasattr(self, "vista_tabla") and self.vista_tabla.winfo_exists():
                for w in self.vista_tabla.winfo_children():
                    w.destroy()
                self.create_header(self.vista_tabla)
                self.create_search_bar(self.vista_tabla)
                self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
                self.main_card = ctk.CTkFrame(
                    self.vista_tabla,
                    fg_color=COLORS["card"],
                    corner_radius=15,
                    border_width=1,
                    border_color=COLORS["border"]
                )
                self.main_card.pack(
                    expand=True, fill="both",
                    padx=10 if self.is_compact else 30,
                    pady=(5, 15)
                )
                self.render_table_content(self.all_users)

    # ─────────────────────────────────────────────────────────────
    # TABLA
    # ─────────────────────────────────────────────────────────────
    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=10 if self.is_compact else 20, pady=10)

        if not user_list:
            ctk.CTkLabel(
                scroll,
                text="No hay usuarios registrados",
                font=self.font_normal,
                text_color=COLORS["subtext"]
            ).pack(pady=40)
            return

        # ── VISTA COMPACTA ──────────────────────────────────────
        if self.is_compact:
            for u in user_list:
                es_activo = u.get("estado", 1) == 1

                card = ctk.CTkFrame(
                    scroll, fg_color=COLORS["card"],
                    corner_radius=14, border_width=1, border_color=COLORS["border"]
                )
                card.pack(fill="x", padx=2, pady=8)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=12, pady=(12, 4))

                ctk.CTkLabel(top, text="👤", font=("Inter", 28)).pack(side="left", padx=(0, 8))

                info = ctk.CTkFrame(top, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)

                ctk.CTkLabel(
                    info,
                    text=f"{u['nombre_solo']} {u['ap']} {u['am']}".upper(),
                    font=("Inter", 12, "bold"), text_color=COLORS["text"],
                    anchor="w", wraplength=300, justify="left"
                ).pack(anchor="w", fill="x")

                ctk.CTkLabel(
                    info, text=f"ID: {u['cuenta']}",
                    font=("Inter", 11), text_color=COLORS["subtext"], anchor="w"
                ).pack(anchor="w", fill="x")

                if u["correo"]:
                    ctk.CTkLabel(
                        info, text=u["correo"],
                        font=("Inter", 10), text_color=COLORS["subtext"],
                        anchor="w", wraplength=300, justify="left"
                    ).pack(anchor="w", fill="x")

                badges = ctk.CTkFrame(card, fg_color="transparent")
                badges.pack(fill="x", padx=12, pady=(4, 8))

                col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
                badge_r = ctk.CTkFrame(badges, fg_color=col["bg"], corner_radius=12)
                badge_r.pack(side="left", padx=(0, 6))
                ctk.CTkLabel(badge_r, text=u["r"], font=("Inter", 9, "bold"), text_color=col["text"]).pack(padx=8, pady=3)

                badge_e = ctk.CTkFrame(
                    badges,
                    fg_color="#D1FAE5" if es_activo else "#FEE2E2",
                    corner_radius=12
                )
                badge_e.pack(side="left")
                ctk.CTkLabel(
                    badge_e,
                    text="● ACTIVO" if es_activo else "● INACTIVO",
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activo else "#991B1B"
                ).pack(padx=8, pady=3)

                actions = ctk.CTkFrame(card, fg_color="transparent")
                actions.pack(fill="x", padx=12, pady=(0, 12))

                ctk.CTkButton(
                    actions, text="✏️ Editar", height=34,
                    fg_color=COLORS["hover"], text_color=COLORS["text"],
                    command=lambda d=u: self.abrir_formulario(d)
                ).pack(side="left", expand=True, fill="x", padx=(0, 6))

                if es_activo:
                    ctk.CTkButton(
                        actions, text="🗑️ Desactivar", height=34,
                        fg_color="#FFF1F2", text_color="#E11D48",
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=True)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))
                else:
                    ctk.CTkButton(
                        actions, text="🔄 Activar", height=34,
                        fg_color="#10B981", text_color="white",
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=False)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        # ── VISTA ESCRITORIO ────────────────────────────────────
        else:
            ancho_foto, ancho_info, ancho_estado = 140, 400, 150

            table_head = ctk.CTkFrame(scroll, fg_color="transparent", height=35)
            table_head.pack(fill="x", pady=(0, 5))

            ctk.CTkLabel(table_head, text="👤 " + AppContext.t("FOTOGRAFÍA"), font=self.font_small, text_color=COLORS["subtext"], width=ancho_foto).pack(side="left")
            ctk.CTkLabel(table_head, text="🆔 " + AppContext.t("INFORMACIÓN"), font=self.font_small, text_color=COLORS["subtext"], width=ancho_info, anchor="w").pack(side="left")
            ctk.CTkLabel(table_head, text="⚙️ " + AppContext.t("ESTADO"), font=self.font_small, text_color=COLORS["subtext"], width=ancho_estado).pack(side="left")
            ctk.CTkLabel(table_head, text=AppContext.t("ACCIONES"), font=self.font_small, text_color=COLORS["subtext"]).pack(side="right", padx=60)

            ctk.CTkFrame(scroll, fg_color=COLORS["border"], height=1).pack(fill="x")

            for u in user_list:
                es_activo = u.get("estado", 1) == 1

                row = ctk.CTkFrame(scroll, fg_color="transparent", height=70)
                row.pack(fill="x", side="top", pady=1)
                row.pack_propagate(False)

                # Foto
                f_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_foto)
                f_b.pack(side="left")
                f_b.pack_propagate(False)
                ctk.CTkLabel(f_b, text="👤", font=("Inter", 32)).pack(expand=True)

                # Info
                i_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_info)
                i_b.pack(side="left", fill="y")
                i_b.pack_propagate(False)

                i_in = ctk.CTkFrame(i_b, fg_color="transparent")
                i_in.pack(expand=True, fill="x", anchor="w")

                l_n = ctk.CTkFrame(i_in, fg_color="transparent")
                l_n.pack(anchor="w")

                ctk.CTkLabel(
                    l_n,
                    text=f"{u['nombre_solo']} {u['ap']} {u['am']}".upper(),
                    font=("Inter", 13, "bold"), text_color=COLORS["text"]
                ).pack(side="left")

                col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
                badge_r = ctk.CTkFrame(l_n, fg_color=col["bg"], corner_radius=4)
                badge_r.pack(side="left", padx=8)
                ctk.CTkLabel(badge_r, text=u["r"], font=("Inter", 9, "bold"), text_color=col["text"]).pack(padx=6, pady=1)

                ctk.CTkLabel(
                    i_in,
                    text=f"ID: {u['cuenta']}  •  {u['correo']}",
                    font=("Inter", 11), text_color=COLORS["subtext"]
                ).pack(anchor="w")

                # Estado
                e_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_estado)
                e_b.pack(side="left", fill="y")
                e_b.pack_propagate(False)

                badge_e = ctk.CTkFrame(
                    e_b,
                    fg_color="#D1FAE5" if es_activo else "#FEE2E2",
                    corner_radius=20
                )
                badge_e.pack(expand=True)
                ctk.CTkLabel(
                    badge_e,
                    text="● ACTIVO" if es_activo else "● INACTIVO",
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activo else "#991B1B"
                ).pack(padx=10, pady=3)

                # Acciones
                a_b = ctk.CTkFrame(row, fg_color="transparent")
                a_b.pack(side="right", padx=20)

                ctk.CTkButton(
                    a_b, text="✏️",
                    width=32, height=32,
                    fg_color=COLORS["hover"], text_color=COLORS["text"],
                    command=lambda d=u: self.abrir_formulario(d)
                ).pack(side="left", padx=4)

                if es_activo:
                    ctk.CTkButton(
                        a_b, text="🗑️",
                        width=32, height=32,
                        fg_color="#FFF1F2", text_color="#E11D48",
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=True)
                    ).pack(side="left", padx=2)
                else:
                    ctk.CTkButton(
                        a_b, text="🔄",
                        width=32, height=32,
                        fg_color="#10B981", text_color="white",
                        hover_color="#059669",
                        command=lambda i=u["id"], n=f"{u['nombre_solo']} {u['ap']}": self.confirmar_cambio_estado(i, n, desactivar=False)
                    ).pack(side="left", padx=2)

                ctk.CTkFrame(scroll, fg_color=COLORS["hover"], height=1).pack(fill="x")

    # ─────────────────────────────────────────────────────────────
    # MODAL CAMBIO DE ESTADO
    # ─────────────────────────────────────────────────────────────
    def confirmar_cambio_estado(self, id_usuario, nombre, desactivar=True):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay, fg_color=COLORS["card"], corner_radius=20,
            width=420, height=250, border_width=2, border_color="#CBD5E1"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        if desactivar:
            icono     = "🗑️"
            titulo    = AppContext.t("¿Desactivar este usuario?")
            sub       = AppContext.t("El usuario perderá acceso al sistema.")
            btn_txt   = AppContext.t("Desactivar")
            btn_color = "#EF4444"
            btn_hover = "#DC2626"
        else:
            icono     = "🔄"
            titulo    = AppContext.t("¿Activar este usuario?")
            sub       = AppContext.t("El usuario recuperará acceso al sistema.")
            btn_txt   = AppContext.t("Activar")
            btn_color = "#10B981"
            btn_hover = "#059669"

        ctk.CTkLabel(modal, text=icono, font=("Inter", 45)).pack(pady=(20, 5))
        ctk.CTkLabel(modal, text=titulo, font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(modal, text=nombre.upper(), font=("Inter", 12, "bold"), text_color=COLORS["subtext"]).pack()
        ctk.CTkLabel(modal, text=sub, font=("Inter", 11), text_color=COLORS["subtext"]).pack(pady=(2, 0))

        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=25, padx=30)

        ctk.CTkButton(
            btns, text=AppContext.t("Cancelar"),
            fg_color="#94A3B8", text_color="white", hover_color="#64748B",
            height=40, font=("Inter", 13, "bold"),
            command=self.cerrar_modal
        ).pack(side="left", expand=True, padx=(0, 10))

        ctk.CTkButton(
            btns, text=btn_txt,
            fg_color=btn_color, text_color="white", hover_color=btn_hover,
            height=40, font=("Inter", 13, "bold"),
            command=lambda: self._ejecutar_cambio_estado(id_usuario, desactivar)
        ).pack(side="left", expand=True)

    def _ejecutar_cambio_estado(self, id_usuario, desactivar_flag):
        if desactivar_flag:
            desactivar_usuario(id_usuario)
        else:
            reactivar_usuario(id_usuario)
        self.refresh_data()
        self.render_table_content(self.all_users)
        self.cerrar_modal()

    def cerrar_modal(self):
        if hasattr(self, "overlay"):
            self.overlay.destroy()

    # ─────────────────────────────────────────────────────────────
    # FORMULARIO
    # ─────────────────────────────────────────────────────────────
    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios, self.inputs_apellidos = {}, {}

        if not usuario:
            self.biometria_temp = None

        self.usuario_editando_id = usuario["id"] if usuario else None
        self.rol_var.set(usuario["r"] if usuario else "ESTUDIANTE")

        self.estado_var = ctk.BooleanVar(value=True)
        if usuario:
            self.estado_var.set(usuario.get("estado", 1) == 1)

        self.dict_facultades = obtener_facultades_para_dropdown()
        nombres_f = list(self.dict_facultades.values()) if self.dict_facultades else ["Sin Datos"]
        self.carreras_por_plantel = {}

        for c in obtener_todas_carreras():
            if c.get("estado", 1) != 1:
                continue
            fn = c["facultad_nombre"]
            if fn not in self.carreras_por_plantel:
                self.carreras_por_plantel[fn] = []
            self.carreras_por_plantel[fn].append(c["nombre"])

        self.form_base = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.form_base.pack(fill="both", expand=True)

        padx_form = 12 if self.is_compact else 60
        self.form_container = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=padx_form, pady=10)

        ctk.CTkLabel(
            self.form_container,
            text=("✏️ " + AppContext.t("Editar Registro")) if usuario else ("➕ " + AppContext.t("Nuevo Registro")),
            font=self.font_header, text_color=COLORS["text"]
        ).pack(anchor="w", padx=padx_form, pady=(30, 10))

        # Clasificación
        c_clasi = ctk.CTkFrame(self.form_container, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        c_clasi.pack(fill="x", padx=padx_form, pady=10)
        grid = ctk.CTkFrame(c_clasi, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=20)

        self.rol_menu = ctk.CTkOptionMenu(grid, values=["ESTUDIANTE", "DOCENTE", "TRABAJADOR"], variable=self.rol_var, height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"])
        self.plantel_menu = ctk.CTkOptionMenu(grid, values=nombres_f, command=self.update_carreras_dinamicas, height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"])
        self.carrera_menu = ctk.CTkOptionMenu(grid, variable=self.carrera_var, values=[], height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"])

        if self.is_compact:
            self.rol_menu.pack(fill="x", pady=5)
            self.plantel_menu.pack(fill="x", pady=5)
            self.carrera_menu.pack(fill="x", pady=5)
        else:
            self.rol_menu.pack(side="left", expand=True, fill="x", padx=5)
            self.plantel_menu.pack(side="left", expand=True, fill="x", padx=5)
            self.carrera_menu.pack(side="left", expand=True, fill="x", padx=5)

        if nombres_f:
            self.update_carreras_dinamicas(nombres_f[0])

        self.create_section_card(self.form_container, "👤 Información Personal", [
            ("Nombres",          usuario["nombre_solo"] if usuario else ""),
            ("Apellido Paterno", usuario["ap"]          if usuario else ""),
            ("Apellido Materno", usuario["am"]          if usuario else "")
        ])
        self.create_section_card(self.form_container, "🆔 Identificación", [
            ("cuenta", str(usuario["cuenta"]) if usuario and usuario["cuenta"] else ""),
            ("correo", str(usuario["correo"]) if usuario and usuario["correo"] else "")
        ])

        if usuario:
            estado_card = ctk.CTkFrame(self.form_container, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
            estado_card.pack(fill="x", padx=padx_form, pady=10)
            ctk.CTkLabel(estado_card, text="⚙️ Estado del usuario", font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 5))
            self.switch_estado = ctk.CTkSwitch(estado_card, text="Usuario activo", variable=self.estado_var, onvalue=True, offvalue=False, font=self.font_normal, text_color=COLORS["text"])
            self.switch_estado.pack(anchor="w", padx=20, pady=(5, 20))

        vcmd = (self.register(self.validar_ocho_numeros), "%P")
        entrada = self.inputs_obligatorios.get("cuenta")
        if entrada:
            entrada.configure(validate="key", validatecommand=vcmd)

        self.btn_biometria = ctk.CTkButton(
            self.form_container, text="📷 Registrar Biometría",
            height=50, fg_color="#0EA5E9", text_color="white",
            font=self.font_sub, command=self.abrir_terminal_biometrica
        )
        self.btn_biometria.pack(fill="x", padx=padx_form, pady=(20, 10))

        self.label_estado = ctk.CTkLabel(self.form_container, text="", font=self.font_small, text_color="#EF4444")
        self.label_estado.pack(fill="x", padx=padx_form, pady=(0, 10))

        btns = ctk.CTkFrame(self.form_container, fg_color="transparent")
        btns.pack(fill="x", padx=padx_form, pady=(20, 50))

        self.btn_guardar = ctk.CTkButton(btns, text="💾 Guardar", font=self.font_sub, fg_color="#10B981", text_color="white", hover_color="#059669", height=50, command=self.validar_y_guardar)
        btn_cancelar     = ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color=COLORS["text"], height=50, command=self.cerrar_formulario)

        if self.is_compact:
            btn_cancelar.pack(fill="x", pady=(0, 10))
            self.btn_guardar.pack(fill="x")
        else:
            btn_cancelar.pack(side="left", expand=True, fill="x", padx=(0, 10))
            self.btn_guardar.pack(side="left", expand=True, fill="x", padx=(10, 0))

    def create_section_card(self, master, title, fields):
        padx_form = 12 if self.is_compact else 60
        card = ctk.CTkFrame(master, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", padx=padx_form, pady=10)
        ctk.CTkLabel(card, text=title, font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=(0, 20))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent")
            if self.is_compact:
                f.pack(fill="x", pady=6)
            else:
                f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(f, text=label, font=self.font_small, text_color=COLORS["subtext"]).pack(anchor="w")
            entry = ctk.CTkEntry(f, height=40, font=self.font_normal, fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"])
            entry.insert(0, val)
            entry.pack(fill="x", pady=5)
            if "Apellido" in label:
                self.inputs_apellidos[label] = entry
            else:
                self.inputs_obligatorios[label] = entry

    # ─────────────────────────────────────────────────────────────
    # VALIDACIÓN Y GUARDADO
    # ─────────────────────────────────────────────────────────────
    def _limpiar_errores(self):
        for entry in self.inputs_obligatorios.values():
            entry.configure(border_width=0)
        for entry in self.inputs_apellidos.values():
            entry.configure(border_width=0)
        if hasattr(self, "label_estado"):
            self.label_estado.configure(text="")

    def _mostrar_error(self, campo, mensaje):
        entry = self.inputs_obligatorios.get(campo) or self.inputs_apellidos.get(campo)
        if entry:
            entry.configure(border_width=2, border_color="#EF4444")
        if hasattr(self, "label_estado"):
            self.label_estado.configure(text=f"❌ {mensaje}", text_color="#EF4444")

    def validar_y_guardar(self):
        self._limpiar_errores()

        if not self.usuario_editando_id:
            if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
                print("❌ Debes registrar biometría primero")
                self.btn_biometria.configure(text="❌ Biometría requerida", fg_color="#EF4444", hover_color="#DC2626")
                return

        n   = self.inputs_obligatorios.get("Nombres").get().strip()
        em  = self.inputs_obligatorios.get("correo").get().strip()
        cta = self.inputs_obligatorios.get("cuenta").get().strip()

        hay_error = False

        if not n:
            self._mostrar_error("Nombres", "El nombre es obligatorio")
            hay_error = True

        if not cta:
            self._mostrar_error("cuenta", "La cuenta es obligatoria")
            hay_error = True
        elif not cta.isdigit():
            self._mostrar_error("cuenta", "La cuenta solo debe contener números")
            hay_error = True
        elif len(cta) != 8:
            self._mostrar_error("cuenta", f"La cuenta debe tener 8 dígitos (actualmente tiene {len(cta)})")
            hay_error = True

        if em and "@" not in em:
            self._mostrar_error("correo", "El correo debe contener @")
            hay_error = True

        if hay_error:
            return

        if existe_cuenta(cta, self.usuario_editando_id):
            self._mostrar_error("cuenta", "La cuenta ya está registrada")
            return

        if em and existe_correo(em, self.usuario_editando_id):
            self._mostrar_error("correo", "El correo ya está registrado")
            return

        try:
            id_usuario = self.usuario_editando_id

            if not n or not cta:
                print("❌ Faltan datos:", n, cta, em)
                return

            if em:
                if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", em):
                    self._mostrar_error("correo", "Correo inválido")
                    return

            if not self.usuario_editando_id and len(cta) != 8:
                return

            ap = self.inputs_apellidos["Apellido Paterno"].get().strip()
            am = self.inputs_apellidos["Apellido Materno"].get().strip()

            if not self.validar_texto_real(n):
                self._mostrar_error("Nombres", "Nombre inválido")
                return
            if not self.validar_texto_real(ap):
                self._mostrar_error("Apellido Paterno", "Apellido paterno inválido")
                return
            if am and not self.validar_texto_real(am):
                self._mostrar_error("Apellido Materno", "Apellido materno inválido")
                return

            n  = n.title()
            ap = ap.title()
            am = am.title()

            TIPOS_USUARIO_INV = {"ESTUDIANTE": 1, "DOCENTE": 2, "TRABAJADOR": 3}
            tipo_usuario = TIPOS_USUARIO_INV.get(self.rol_var.get().upper())

            carrera_seleccionada = self.carrera_var.get()
            carreras_validas     = self.carreras_por_plantel.get(self.plantel_menu.get(), [])
            if carrera_seleccionada not in carreras_validas:
                print("❌ Carrera inválida")
                return

            id_fac = obtener_id_facultad_por_nombre(self.plantel_menu.get())
            if not id_fac or not tipo_usuario:
                print("Error: tipo_usuario o id_fac inválido", tipo_usuario, id_fac)
                return

            if self.usuario_editando_id:
                estado_valor = 1 if self.estado_var.get() else 0
                actualizar_usuario(id_usuario, n, ap, am, cta, tipo_usuario, id_fac, em, estado_valor)
                if hasattr(self, "biometria_temp") and self.biometria_temp is not None:
                    print("Reemplazando biometría...")
                    eliminar_encoding(id_usuario)
                    guardar_encoding(id_usuario, self.biometria_temp)
                    encodings_db[:], usuarios_db[:] = cargar_encodings()
                    self.biometria_temp = None

            else:
                if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
                    self.label_estado.configure(text="❌ Debes registrar biometría antes de guardar", text_color="#EF4444")
                    return

                usuario_id = None
                try:
                    usuario_id = crear_usuario(n, ap, am, tipo_usuario, id_fac, None, cta, em)
                    if not usuario_id:
                        self.label_estado.configure(text="❌ No se pudo crear el usuario", text_color="#EF4444")
                        return

                    resultado = guardar_encoding(usuario_id, self.biometria_temp)

                    if not resultado["ok"]:
                        # Revertir usuario creado
                        from app.database.database import get_connection
                        conn = get_connection()
                        conn.cursor().execute("DELETE FROM usuario WHERE id_usuario = ?", (usuario_id,))
                        conn.commit()
                        conn.close()

                        error = resultado.get("error")
                        if error == "rostro_duplicado":
                            dup = resultado.get("usuario_duplicado")
                            self.label_estado.configure(text=f"❌ Este rostro ya pertenece al usuario ID {dup}", text_color="#EF4444")
                        elif error == "usuario_duplicado":
                            self.label_estado.configure(text="❌ Este usuario ya tiene biometría", text_color="#EF4444")
                        else:
                            self.label_estado.configure(text="❌ Error al guardar biometría", text_color="#EF4444")

                        self.refresh_data()
                        self.render_table_content(self.all_users)
                        return

                    encodings_db[:], usuarios_db[:] = cargar_encodings()
                    self.biometria_temp = None
                    print("✔ Usuario y biometría guardados correctamente")

                except Exception as e:
                    print("ERROR al guardar usuario/biometría:", e)
                    if usuario_id:
                        from app.database.database import get_connection
                        conn = get_connection()
                        conn.cursor().execute("DELETE FROM usuario WHERE id_usuario = ?", (usuario_id,))
                        conn.commit()
                        conn.close()
                    self.label_estado.configure(text="❌ Error al guardar. No se registró el usuario.", text_color="#EF4444")
                    return

            self.refresh_data()
            self.render_table_content(self.all_users)
            self.cerrar_formulario()

        except Exception as e:
            print("ERROR AL GUARDAR:", e)

    def cambiar_estado_usuario(self, id_usuario, nuevo_estado):
        try:
            usuario = obtener_usuario_por_id(id_usuario)
            if not usuario:
                print(f"Usuario {id_usuario} no encontrado")
                return
            estado_valor = 1 if nuevo_estado else 0
            actualizar_usuario(id_usuario, usuario["nombre"], usuario["a_paterno"], usuario["a_materno"], "", usuario["tipo_usuario"], usuario["id_facultad"], estado_valor)
            print(f"✔ Estado del usuario {id_usuario} cambiado a: {'ACTIVO' if estado_valor else 'INACTIVO'}")
            self.refresh_data()
            self.render_table_content(self.all_users)
        except Exception as e:
            print(f"❌ Error al cambiar estado: {e}")

    def cerrar_formulario(self):
        if hasattr(self, "form_base"):
            self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content(self.all_users)

    # ─────────────────────────────────────────────────────────────
    # HEADER, BÚSQUEDA Y FILTROS
    # ─────────────────────────────────────────────────────────────
    def create_header(self, master):
        padx_header = 12 if self.is_compact else 30
        h = ctk.CTkFrame(master, fg_color="transparent")
        h.pack(fill="x", padx=padx_header, pady=(20, 10))

        if self.is_compact:
            ctk.CTkLabel(h, text="👥 Gestión de Usuarios", font=("Inter", 30, "bold"), text_color=COLORS["text"]).pack(anchor="center", pady=(0, 12))
            ctk.CTkButton(h, text="➕ Agregar Usuario", font=self.font_sub, fg_color="#000000", height=45, corner_radius=10, command=self.abrir_formulario).pack(fill="x", padx=20)
        else:
            ctk.CTkLabel(h, text="👥 Gestión de Usuarios", font=self.font_header, text_color=COLORS["text"]).pack(side="left")
            ctk.CTkButton(h, text="➕ Agregar Usuario", font=self.font_sub, fg_color="#000000", height=45, corner_radius=10, command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent")
        bar.pack(fill="x", padx=30, pady=10)
        self.entry_busqueda = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar usuario...", height=42, corner_radius=10, fg_color=COLORS["hover"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.btn_filter = ctk.CTkButton(bar, text="⚙️ Filtrar ⌵", width=110, height=42, corner_radius=10, fg_color=COLORS["card"], text_color=COLORS["text"], border_color=COLORS["border"], command=self.toggle_filter)
        self.btn_filter.pack(side="left")

    def toggle_filter(self):
        if not self.filter_visible:
            self.draw_tags()
            self.filter_container.pack(fill="x", padx=30, pady=(0, 15), before=self.main_card)
            self.btn_filter.configure(text="⚙️ Filtrar ︿")
            self.filter_visible = True
        else:
            self.filter_container.pack_forget()
            self.btn_filter.configure(text="⚙️ Filtrar ⌵")
            self.filter_visible = False

    def draw_tags(self):
        for w in self.filter_container.winfo_children():
            w.destroy()
        r1 = ctk.CTkFrame(self.filter_container, fg_color="transparent")
        r1.pack(fill="x", padx=20)
        ctk.CTkLabel(r1, text="👤 Rol:", font=self.font_small, text_color=COLORS["text"], width=80).pack(side="left")
        for t in ["Todos", "ESTUDIANTE", "DOCENTE", "TRABAJADOR"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(
                r1, text=t, height=28, corner_radius=10,
                fg_color=COLORS["hover"] if act else "white",
                text_color=COLORS["text"], border_color=COLORS["border"],
                command=lambda v=t: self.aplicar_filtro_visual(v)
            ).pack(side="left", padx=3)

    def aplicar_filtro_visual(self, v):
        self.filtro_rol_actual = v
        self.draw_tags()
        if v == "Todos":
            self.render_table_content(self.all_users)
            return
        self.render_table_content([u for u in self.all_users if u["r"].upper() == v.upper()])

    def update_carreras_dinamicas(self, fn):
        c = self.carreras_por_plantel.get(fn, ["Sin Carreras"])
        self.carrera_menu.configure(values=c)
        self.carrera_var.set(c[0])

    # ─────────────────────────────────────────────────────────────
    # BIOMETRÍA
    # ─────────────────────────────────────────────────────────────
    def abrir_terminal_biometrica(self):
        self._limpiar_errores()

        nombres = self.limpiar_texto(self.inputs_obligatorios["Nombres"].get())
        cuenta  = self.inputs_obligatorios["cuenta"].get().strip()
        correo  = self.inputs_obligatorios["correo"].get().strip()
        ap      = self.limpiar_texto(self.inputs_apellidos["Apellido Paterno"].get())
        am      = self.limpiar_texto(self.inputs_apellidos["Apellido Materno"].get())

        hay_error = False

        if not self.validar_texto_real(nombres):
            self._mostrar_error("Nombres", "El nombre solo debe contener letras")
            hay_error = True
        if not self.validar_texto_real(ap):
            self._mostrar_error("Apellido Paterno", "Apellido paterno inválido")
            hay_error = True
        if am and not self.validar_texto_real(am):
            self._mostrar_error("Apellido Materno", "Apellido materno inválido")
            hay_error = True
        if not cuenta:
            self._mostrar_error("cuenta", "La cuenta es obligatoria")
            hay_error = True
        elif not cuenta.isdigit():
            self._mostrar_error("cuenta", "La cuenta solo debe contener números")
            hay_error = True
        elif len(cuenta) != 8:
            self._mostrar_error("cuenta", "La cuenta debe tener exactamente 8 números")
            hay_error = True
        if correo and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", correo):
            self._mostrar_error("correo", "Correo electrónico inválido")
            hay_error = True

        if hay_error:
            self.btn_biometria.configure(text="❌ Corrige los datos primero", fg_color="#EF4444", hover_color="#DC2626")
            return

        self.btn_biometria.configure(text="📷 Abriendo cámara...", fg_color="#0EA5E9")
        self.form_base.pack_forget()

        self.terminal_container = ctk.CTkFrame(self, fg_color="black")
        self.terminal_container.pack(fill="both", expand=True)

        self.terminal_view = TerminalView(
            self.terminal_container,
            user_id=None,
            on_back=self.cerrar_terminal_biometrica,
            on_capture=self.recibir_biometria,
            modo="registro"
        )
        self.terminal_view.pack(fill="both", expand=True)

    def cerrar_terminal_biometrica(self):
        if hasattr(self, "terminal_view"):
            try:
                self.terminal_view.on_close()
            except Exception:
                pass
        if hasattr(self, "terminal_container"):
            self.terminal_container.destroy()
            
        self.form_base.pack(fill="both", expand=True)
        
        # 🔥 Restaurar botón si NO se registró biometría
        if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
            self.btn_biometria.configure(
                text="📷 Registrar Biometría",
                fg_color="#0EA5E9",
                hover_color="#0284C7"
            )

    def recibir_biometria(self, encoding):
        print("✔ Captura recibida")
        

        self.biometria_temp = encoding

        if hasattr(self, "btn_biometria"):
            self.btn_biometria.configure(
                text="✔ Biometría registrada",
                fg_color="#10B981",
                hover_color="#059669"
            )

        self.cerrar_terminal_biometrica()