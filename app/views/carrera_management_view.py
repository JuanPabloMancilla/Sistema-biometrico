import customtkinter as ctk
import re
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.services.carrera_service import (
    obtener_todas_carreras,
    crear_carrera,
    actualizar_carrera,
    desactivar_carrera,
    reactivar_carrera,
    obtener_carrera_por_id,
    obtener_facultades_para_dropdown
)

class CarreraManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color=COLORS["bg"])
        self.controller = controller
        self.usuario_editando_id = None

        self.font_header = ("Inter", 30, "bold")
        self.font_sub    = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small  = ("Inter", 11, "bold")

        self.modo_edicion      = False
        self.carrera_actual_id = None
        self.is_compact        = False
        self.bind("<Configure>", self._on_resize)

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)

        self.main_card = ctk.CTkFrame(
            self.vista_tabla, fg_color=COLORS["card"],
            corner_radius=15, border_width=1, border_color=COLORS["border"]
        )
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        self.render_table_content()

    # ─────────────────────────────────────────────────────────────
    # RESIZE
    # ─────────────────────────────────────────────────────────────
    def _on_resize(self, event):
        nuevo_compact = event.width < 700
        if nuevo_compact != self.is_compact:
            self.is_compact = nuevo_compact

            if hasattr(self, "vista_tabla") and self.vista_tabla.winfo_exists():
                self.vista_tabla.destroy()

            self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
            self.vista_tabla.pack(fill="both", expand=True)

            self.create_header(self.vista_tabla)
            self.create_search_bar(self.vista_tabla)

            self.main_card = ctk.CTkFrame(
                self.vista_tabla, fg_color=COLORS["card"],
                corner_radius=15, border_width=1, border_color=COLORS["border"]
            )
            self.main_card.pack(
                fill="both", expand=True,
                padx=10 if self.is_compact else 40,
                pady=(0, 20 if self.is_compact else 40)
            )

            self.render_table_content()

    # ─────────────────────────────────────────────────────────────
    # TABLA
    # ─────────────────────────────────────────────────────────────
    def render_table_content(self):
        for w in self.main_card.winfo_children():
            w.destroy()

        todas = obtener_todas_carreras()
        todas.sort(key=lambda c: (c.get("estado", 1) == 0, c["nombre"]))

        query = self.entry_busqueda.get().strip().lower() if hasattr(self, "entry_busqueda") else ""
        carreras = (
            [c for c in todas
             if query in c["nombre"].lower()
             or query in (c.get("facultad_nombre") or "").lower()]
            if query else todas
        )

        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=16, pady=12)

        if not carreras:
            msg = f"No se encontraron carreras para \"{query}\"" if query else "No hay carreras registradas"
            ctk.CTkLabel(
                scroll, text=AppContext.t(msg),
                font=self.font_normal, text_color=COLORS["subtext"]
            ).pack(pady=40)
            return

        # ── VISTA COMPACTA ──────────────────────────────────────
        if self.is_compact:
            for c in carreras:
                es_activa = c.get("estado", 1) == 1
                fac_txt   = c["facultad_nombre"] if c.get("facultad_nombre") else "Sin facultad"

                card = ctk.CTkFrame(
                    scroll, fg_color=COLORS["card"],
                    corner_radius=14, border_width=1, border_color=COLORS["border"]
                )
                card.pack(fill="x", padx=2, pady=8)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=14, pady=(14, 8))

                ctk.CTkLabel(top, text="🎓", font=("Inter", 26)).pack(side="left", padx=(0, 10))

                info = ctk.CTkFrame(top, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)

                ctk.CTkLabel(
                    info, text=c["nombre"].upper(),
                    font=("Inter", 13, "bold"), text_color=COLORS["text"],
                    anchor="w", wraplength=280, justify="left"
                ).pack(anchor="w", fill="x")
                ctk.CTkLabel(
                    info, text=f"Facultad: {fac_txt}",
                    font=("Inter", 10), text_color=COLORS["subtext"],
                    anchor="w", wraplength=280, justify="left"
                ).pack(anchor="w", fill="x")

                badge_wrap = ctk.CTkFrame(card, fg_color="transparent")
                badge_wrap.pack(fill="x", padx=14, pady=(0, 10))
                badge = ctk.CTkFrame(
                    badge_wrap,
                    fg_color="#D1FAE5" if es_activa else "#FEE2E2",
                    corner_radius=20
                )
                badge.pack(side="left")
                ctk.CTkLabel(
                    badge,
                    text="● ACTIVA" if es_activa else "● INACTIVA",
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activa else "#991B1B"
                ).pack(padx=10, pady=4)

                actions = ctk.CTkFrame(card, fg_color="transparent")
                actions.pack(fill="x", padx=14, pady=(0, 14))

                ctk.CTkButton(
                    actions, text="✏️ Editar", height=36,
                    fg_color=COLORS["hover"], text_color=COLORS["text"],
                    command=lambda cid=c["id"]: self.abrir_formulario(cid)
                ).pack(side="left", expand=True, fill="x", padx=(0, 6))

                if es_activa:
                    ctk.CTkButton(
                        actions, text="🗑️ Desactivar", height=36,
                        fg_color="#FFF1F2", text_color="#E11D48",
                        command=lambda cid=c["id"], n=c["nombre"]: self.confirmar_cambio_estado(cid, n, desactivar=True)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))
                else:
                    ctk.CTkButton(
                        actions, text="🔄 Activar", height=36,
                        fg_color="#10B981", text_color="white",
                        command=lambda cid=c["id"], n=c["nombre"]: self.confirmar_cambio_estado(cid, n, desactivar=False)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        # ── VISTA ESCRITORIO ────────────────────────────────────
        else:
            tabla = ctk.CTkFrame(scroll, fg_color="transparent")
            tabla.pack(fill="both", expand=True)

            tabla.columnconfigure(0, weight=3)
            tabla.columnconfigure(1, weight=3)
            tabla.columnconfigure(2, weight=1)
            tabla.columnconfigure(3, weight=1)

            HEADERS = [
                ("📖 " + AppContext.t("NOMBRE").upper(),   "w"),
                ("🏫 " + AppContext.t("FACULTAD").upper(), "w"),
                ("⚙️ " + AppContext.t("ESTADO").upper(),   "center"),
                (AppContext.t("ACCIONES"),                  "center"),
            ]
            for col, (text, anchor) in enumerate(HEADERS):
                ctk.CTkLabel(
                    tabla, text=text, font=self.font_small,
                    text_color=COLORS["subtext"], anchor=anchor
                ).grid(row=0, column=col, sticky="ew", padx=8, pady=(6, 4))

            ctk.CTkFrame(tabla, fg_color=COLORS["border"], height=1).grid(
                row=1, column=0, columnspan=4, sticky="ew"
            )

            for idx, c in enumerate(carreras):
                es_activa = c.get("estado", 1) == 1
                data_row  = 2 + idx * 2
                sep_row   = data_row + 1

                ctk.CTkLabel(
                    tabla, text=c["nombre"].upper(),
                    font=("Inter", 12, "bold"), text_color=COLORS["text"], anchor="w"
                ).grid(row=data_row, column=0, sticky="ew", padx=8, pady=10)

                fac_txt = c["facultad_nombre"] if c.get("facultad_nombre") else "Sin Facultad"
                ctk.CTkLabel(
                    tabla, text=fac_txt,
                    font=self.font_normal, text_color=COLORS["subtext"], anchor="w"
                ).grid(row=data_row, column=1, sticky="ew", padx=8, pady=10)

                badge_outer = ctk.CTkFrame(tabla, fg_color="transparent")
                badge_outer.grid(row=data_row, column=2, sticky="nsew", padx=4, pady=6)
                badge_outer.columnconfigure(0, weight=1)
                badge_outer.rowconfigure(0, weight=1)
                badge = ctk.CTkFrame(
                    badge_outer,
                    fg_color="#D1FAE5" if es_activa else "#FEE2E2",
                    corner_radius=20
                )
                badge.grid(row=0, column=0)
                ctk.CTkLabel(
                    badge,
                    text="● " + (AppContext.t("ACTIVA") if es_activa else AppContext.t("INACTIVA")),
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activa else "#991B1B"
                ).pack(padx=12, pady=4)

                act_outer = ctk.CTkFrame(tabla, fg_color="transparent")
                act_outer.grid(row=data_row, column=3, sticky="nsew", padx=4, pady=6)
                act_outer.columnconfigure(0, weight=1)
                act_outer.rowconfigure(0, weight=1)

                btns = ctk.CTkFrame(act_outer, fg_color="transparent")
                btns.grid(row=0, column=0)

                ctk.CTkButton(
                    btns, text="✏️", width=34, height=34,
                    font=("Inter", 14), fg_color=COLORS["hover"],
                    hover_color=COLORS["border"], text_color=COLORS["text"],
                    command=lambda cid=c["id"]: self.abrir_formulario(cid)
                ).pack(side="left", padx=3)

                if es_activa:
                    ctk.CTkButton(
                        btns, text="🗑️", width=34, height=34,
                        font=("Inter", 14), fg_color="#FFF1F2",
                        hover_color="#FEE2E2", text_color="#E11D48",
                        command=lambda cid=c["id"], n=c["nombre"]: self.confirmar_cambio_estado(cid, n, desactivar=True)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkButton(
                        btns, text="🔄", width=34, height=34,
                        font=("Inter", 11, "bold"), fg_color="#10B981",
                        hover_color="#059669", text_color="white",
                        command=lambda cid=c["id"], n=c["nombre"]: self.confirmar_cambio_estado(cid, n, desactivar=False)
                    ).pack(side="left", padx=3)

                ctk.CTkFrame(tabla, fg_color=COLORS["hover"], height=1).grid(
                    row=sep_row, column=0, columnspan=4, sticky="ew"
                )

    # ─────────────────────────────────────────────────────────────
    # MODAL UNIFICADO ACTIVAR / DESACTIVAR
    # ─────────────────────────────────────────────────────────────
    def confirmar_cambio_estado(self, id_carrera, nombre, desactivar=True):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay, fg_color="white", corner_radius=20,
            width=420, height=250, border_width=2, border_color="#CBD5E1"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        if desactivar:
            icono     = "🎓"
            titulo    = AppContext.t("¿Desactivar esta carrera?")
            sub       = AppContext.t("La carrera dejará de estar disponible.")
            btn_txt   = AppContext.t("Desactivar")
            btn_color = "#EF4444"
            btn_hover = "#DC2626"
        else:
            icono     = "🔄"
            titulo    = AppContext.t("¿Activar esta carrera?")
            sub       = AppContext.t("La carrera volverá a estar disponible.")
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
            command=lambda: self._ejecutar_cambio_estado(id_carrera, desactivar)
        ).pack(side="left", expand=True)

    def _ejecutar_cambio_estado(self, id_carrera, desactivar_flag):
        if desactivar_flag:
            desactivar_carrera(id_carrera)
        else:
            reactivar_carrera(id_carrera)
        self.render_table_content()
        self.cerrar_modal()

    def cerrar_modal(self):
        if hasattr(self, "overlay"):
            self.overlay.destroy()

    # ─────────────────────────────────────────────────────────────
    # FORMULARIO
    # ─────────────────────────────────────────────────────────────
    def abrir_formulario(self, id_carrera=None):
        self.vista_tabla.pack_forget()
        self.facultades_dict = obtener_facultades_para_dropdown()
        facultades_lista     = list(self.facultades_dict.values())

        if id_carrera:
            self.modo_edicion      = True
            self.carrera_actual_id = id_carrera
            c = obtener_carrera_por_id(id_carrera)
            titulo         = "✏️ " + AppContext.t("Editar Carrera")
            nombre_ini     = c["nombre"] if c else ""
            estado_ini     = AppContext.t("Activa") if c and c["estado"] == 1 else AppContext.t("Inactiva")
            fac_id         = c["id_facultad"] if c else None
            fac_nombre_ini = self.facultades_dict.get(fac_id, AppContext.t("Seleccionar facultad"))
        else:
            self.modo_edicion      = False
            titulo         = "➕ " + AppContext.t("Nueva Carrera")
            nombre_ini     = ""
            estado_ini     = "Activa"
            fac_nombre_ini = facultades_lista[0] if facultades_lista else "Seleccionar facultad"

        self.form_base = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.form_base.pack(fill="both", expand=True)
        padx_form = 12 if self.is_compact else 60

        ctk.CTkLabel(
            self.form_base, text=titulo,
            font=self.font_header, text_color=COLORS["text"]
        ).pack(anchor="w", padx=padx_form, pady=(40, 20))

        form_card = ctk.CTkFrame(
            self.form_base, fg_color=COLORS["card"],
            corner_radius=15, border_width=1, border_color=COLORS["border"]
        )
        form_card.pack(fill="x", padx=padx_form, pady=10)

        ctk.CTkLabel(
            form_card, text="📖 " + AppContext.t("Nombre de la Carrera"),
            font=self.font_small, text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=25, pady=(25, 5))
        self.input_nombre = ctk.CTkEntry(
            form_card, height=45, font=self.font_normal,
            fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"]
        )
        self.input_nombre.insert(0, nombre_ini)
        self.input_nombre.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(
            form_card, text="🏫 " + AppContext.t("Facultad"),
            font=self.font_small, text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_facultad = ctk.CTkOptionMenu(
            form_card, values=facultades_lista, height=45,
            font=self.font_normal, fg_color=COLORS["hover"],
            button_color=COLORS["border"], text_color=COLORS["text"]
        )
        self.combo_facultad.set(fac_nombre_ini)
        self.combo_facultad.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(
            form_card, text="⚙️ " + AppContext.t("Estado"),
            font=self.font_small, text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_estado = ctk.CTkOptionMenu(
            form_card,
            values=[AppContext.t("Activa"), AppContext.t("Inactiva")],
            height=45, font=self.font_normal,
            fg_color=COLORS["hover"], button_color=COLORS["border"],
            text_color=COLORS["text"]
        )
        self.combo_estado.set(estado_ini)
        self.combo_estado.pack(fill="x", padx=25, pady=(0, 30))

        btns = ctk.CTkFrame(self.form_base, fg_color="transparent")
        btns.pack(fill="x", padx=padx_form, pady=30)
        ctk.CTkButton(
            btns, text="❌ " + AppContext.t("Cancelar"),
            font=self.font_sub, fg_color="#FEE2E2", text_color="#991B1B",
            height=55, command=self.volver_a_tabla
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(
            btns, text="💾 " + AppContext.t("Guardar Carrera"),
            font=self.font_sub, fg_color="#D1FAE5", text_color="#065F46",
            height=55, command=self.guardar_carrera
        ).pack(side="left", expand=True, fill="x", padx=(10, 0))

    # ─────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────
    def carrera_existe(self, nombre):
        todas = obtener_todas_carreras()
        return any(
            c["nombre"].strip().lower() == nombre.strip().lower()
            for c in todas
        )

    def guardar_carrera(self):
        nombre      = self.input_nombre.get().strip()
        estado      = 1 if self.combo_estado.get() == AppContext.t("Activa") else 0
        fac_nombre  = self.combo_facultad.get()
        id_facultad = next(
            (id for id, n in self.facultades_dict.items() if n == fac_nombre), None
        )

        if not nombre or not id_facultad:
            return
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$", nombre):
            print("❌ Carrera inválida")
            return
        if len(nombre) < 4:
            print("❌ Nombre de carrera demasiado corto")
            return
        if self.carrera_existe(nombre) and not self.modo_edicion:
            print("❌ Carrera duplicada")
            return

        if self.modo_edicion:
            actualizar_carrera(self.carrera_actual_id, nombre, id_facultad, estado)
        else:
            crear_carrera(nombre, id_facultad, estado)
        self.volver_a_tabla()

    def volver_a_tabla(self):
        if hasattr(self, "form_base"):
            self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content()

    # ─────────────────────────────────────────────────────────────
    # HEADER & SEARCH
    # ─────────────────────────────────────────────────────────────
    def create_header(self, master):
        padx_header = 12 if self.is_compact else 30
        h = ctk.CTkFrame(master, fg_color="transparent")
        h.pack(fill="x", padx=padx_header, pady=(15, 10))

        if self.is_compact:
            ctk.CTkLabel(
                h, text=AppContext.t("🎓 Gestión de Carreras"),
                font=("Inter", 26, "bold"), text_color=COLORS["text"]
            ).pack(anchor="center", pady=(0, 10))
            ctk.CTkButton(
                h, text="➕ " + AppContext.t("Agregar Carrera"),
                font=self.font_sub, fg_color="#000000",
                height=45, corner_radius=12,
                command=self.abrir_formulario
            ).pack(fill="x", padx=10)
        else:
            ctk.CTkLabel(
                h, text=AppContext.t("🎓   Gestión de Carreras"),
                font=self.font_header, text_color=COLORS["text"]
            ).pack(side="left")
            ctk.CTkButton(
                h, text="➕ " + AppContext.t("Agregar Carrera"),
                font=self.font_sub, fg_color="#000000",
                height=50, corner_radius=12,
                command=self.abrir_formulario
            ).pack(side="right")

    def create_search_bar(self, master):
        padx_bar = 12 if self.is_compact else 30
        bar = ctk.CTkFrame(master, fg_color="transparent")
        bar.pack(fill="x", padx=padx_bar, pady=10)
        self.entry_busqueda = ctk.CTkEntry(
            bar,
            placeholder_text="🔍 " + AppContext.t("Buscar carrera por nombre..."),
            height=42, corner_radius=10,
            fg_color=COLORS["hover"], border_width=1,
            text_color=COLORS["text"]
        )
        self.entry_busqueda.pack(fill="x", expand=True)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.render_table_content())