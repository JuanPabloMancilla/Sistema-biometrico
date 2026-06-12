import customtkinter as ctk
import re
from app.services.theme import COLORS
from app.views.app_context import AppContext
from app.services.area_service import (
    obtener_todas_facultades,
    crear_facultad,
    actualizar_facultad,
    desactivar_facultad,
    reactivar_facultad,
    obtener_facultad_por_id
)

class AreaManagementView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])

        self.modo_edicion       = False
        self.facultad_actual_id = None

        self.font_header = ("Inter", 24, "bold")
        self.font_sub    = ("Inter", 14, "bold")
        self.font_normal = ("Inter", 12)
        self.font_small  = ("Inter", 12, "bold")

        self.is_compact = False
        self.bind("<Configure>", self._on_resize)

        self.crear_vista_tabla()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # RESIZE
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _on_resize(self, event):
        nuevo_compact = event.width < 1040
        if nuevo_compact != self.is_compact:
            self.is_compact = nuevo_compact
            if hasattr(self, "vista_tabla") and self.vista_tabla.winfo_exists():
                self.vista_tabla.destroy()
            self.crear_vista_tabla()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # VISTA TABLA
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def crear_vista_tabla(self):
        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        padx_main = 8 if self.is_compact else 40
        pady_top  = 6 if self.is_compact else 40

        # â”€â”€ Header â”€â”€
        header = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
        header.pack(fill="x", padx=padx_main, pady=(pady_top, 10))

        title_cont = ctk.CTkFrame(header, fg_color="transparent")

        if self.is_compact:
            title_cont.pack(fill="x")
            ctk.CTkLabel(
                title_cont,
                text=AppContext.t("Áreas"),
                font=("Inter", 20, "bold"),
                text_color=COLORS["text"]
            ).pack(anchor="center", pady=(0, 6))
            ctk.CTkLabel(
                title_cont,
                text=AppContext.t("Administra las unidades acadÃ©micas"),
                font=("Inter", 12),
                text_color=COLORS["subtext"]
            ).pack(anchor="center", pady=(0, 10))
            ctk.CTkButton(
                header,
                text=AppContext.t("Nueva área"),
                fg_color=COLORS["primary"],
                font=self.font_sub,
                height=36, corner_radius=8,
                command=self.abrir_formulario
            ).pack(fill="x", padx=4)
        else:
            title_cont.pack(side="left")
            ctk.CTkLabel(
                title_cont,
                text=AppContext.t("Áreas"),
                font=self.font_header, text_color=COLORS["text"]
            ).pack(anchor="w")
            ctk.CTkLabel(
                title_cont,
                text=AppContext.t("Administra las unidades acadÃ©micas del sistema"),
                font=self.font_normal, text_color=COLORS["subtext"]
            ).pack(anchor="w")
            ctk.CTkButton(
                header,
                text=AppContext.t("Nueva área"),
                fg_color=COLORS["text"], hover_color=COLORS["hover"],
                text_color=COLORS["bg"], font=self.font_sub,
                height=40, corner_radius=8,
                command=self.abrir_formulario
            ).pack(side="right", anchor="n")

        # â”€â”€ Barra de bÃºsqueda â”€â”€
        bar = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
        bar.pack(fill="x", padx=padx_main, pady=(0, 10))
        self.entry_busqueda = ctk.CTkEntry(
            bar,
            placeholder_text=AppContext.t("Buscar facultad por nombre..."),
            height=36 if self.is_compact else 40, corner_radius=8,
            fg_color=COLORS["hover"], border_width=1,
            border_color=COLORS["border"], text_color=COLORS["text"]
        )
        self.entry_busqueda.pack(fill="x", expand=True)
        self.entry_busqueda.bind("<KeyRelease>", self._on_search)

        # â”€â”€ Card principal â”€â”€
        self.main_card = ctk.CTkFrame(
            self.vista_tabla, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        self.main_card.pack(fill="both", expand=True, padx=padx_main, pady=(0, pady_top))

        self.render_table_content()

    def _on_search(self, event=None):
        self.render_table_content()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # TABLA
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def render_table_content(self):
        for w in self.main_card.winfo_children():
            w.destroy()

        todas = obtener_todas_facultades()
        todas.sort(key=lambda f: (f.get("estado", 1) == 0, f["nombre"]))

        query = self.entry_busqueda.get().strip().lower() if hasattr(self, "entry_busqueda") else ""
        facultades = (
            [f for f in todas if query in f["nombre"].lower()]
            if query else todas
        )

        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both", padx=8 if self.is_compact else 16, pady=8 if self.is_compact else 12)

        if not facultades:
            msg = f"No se encontraron facultades para '{query}'" if query else "No hay facultades registradas"
            ctk.CTkLabel(
                scroll, text=AppContext.t(msg),
                font=self.font_normal, text_color=COLORS["subtext"]
            ).pack(pady=40)
            return

        # â”€â”€ VISTA COMPACTA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if self.is_compact:
            for f in facultades:
                es_activa = f.get("estado", 1) == 1

                card = ctk.CTkFrame(
                    scroll, fg_color=COLORS["card"],
                    corner_radius=8, border_width=1, border_color=COLORS["border"]
                )
                card.pack(fill="x", padx=2, pady=5)

                top = ctk.CTkFrame(card, fg_color="transparent")
                top.pack(fill="x", padx=10, pady=(8, 5))

                ctk.CTkLabel(top, text="", font=("Inter", 26)).pack(side="left", padx=(0, 10))

                info = ctk.CTkFrame(top, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)

                ctk.CTkLabel(
                    info, text=f["nombre"].upper(),
                    font=("Inter", 13, "bold"), text_color=COLORS["text"],
                    anchor="w", wraplength=260, justify="left"
                ).pack(anchor="w", fill="x")
                ctk.CTkLabel(
                    info, text=f"ID {AppContext.t('Facultad')}: {f['id']}",
                    font=("Inter", 10), text_color=COLORS["subtext"]
                ).pack(anchor="w")

                badge_wrap = ctk.CTkFrame(card, fg_color="transparent")
                badge_wrap.pack(fill="x", padx=14, pady=(0, 10))
                badge_est = ctk.CTkFrame(
                    badge_wrap,
                    fg_color="#D1FAE5" if es_activa else "#FEE2E2",
                    corner_radius=8
                )
                badge_est.pack(side="left")
                ctk.CTkLabel(
                    badge_est,
                    text=AppContext.t("ACTIVA") if es_activa else AppContext.t("INACTIVA"),
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activa else "#991B1B"
                ).pack(padx=10, pady=4)

                actions = ctk.CTkFrame(card, fg_color="transparent")
                actions.pack(fill="x", padx=10, pady=(0, 8))

                ctk.CTkButton(
                    actions, text="✎", height=30,
                    fg_color=COLORS["hover"], text_color=COLORS["text"],
                    font=("Segoe UI Symbol", 14, "bold"),
                    command=lambda id_f=f["id"]: self.abrir_formulario(id_f)
                ).pack(side="left", expand=True, fill="x", padx=(0, 6))

                if es_activa:
                    ctk.CTkButton(
                        actions, text="⊘", height=30,
                        fg_color="#FFF1F2", text_color="#E11D48",
                        font=("Segoe UI Symbol", 14, "bold"),
                        command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_cambio_estado(id_f, n, desactivar=True)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))
                else:
                    ctk.CTkButton(
                        actions, text="✓", height=30,
                        fg_color="#10B981", text_color="white",
                        font=("Segoe UI Symbol", 14, "bold"),
                        command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_cambio_estado(id_f, n, desactivar=False)
                    ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        # â”€â”€ VISTA ESCRITORIO â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        else:
            tabla = ctk.CTkFrame(scroll, fg_color="transparent")
            tabla.pack(fill="both", expand=True)

            tabla.columnconfigure(0, weight=5)
            tabla.columnconfigure(1, weight=1)
            tabla.columnconfigure(2, weight=1)

            HEADERS = [
                (AppContext.t("NOMBRE DE LA FACULTAD"), "w"),
                (AppContext.t("ESTADO"),                 "center"),
                (AppContext.t("ACCIONES"),                        "center"),
            ]
            for col, (text, anchor) in enumerate(HEADERS):
                ctk.CTkLabel(
                    tabla, text=text, font=self.font_small,
                    text_color=COLORS["subtext"], anchor=anchor
                ).grid(row=0, column=col, sticky="ew", padx=8, pady=(6, 4))

            ctk.CTkFrame(tabla, fg_color=COLORS["border"], height=1).grid(
                row=1, column=0, columnspan=3, sticky="ew"
            )

            for idx, f in enumerate(facultades):
                es_activa = f.get("estado", 1) == 1
                data_row  = 2 + idx * 2
                sep_row   = data_row + 1

                ctk.CTkLabel(
                    tabla, text=f["nombre"].upper(),
                    font=("Inter", 12, "bold"), text_color=COLORS["text"], anchor="w"
                ).grid(row=data_row, column=0, sticky="ew", padx=8, pady=10)

                badge_outer = ctk.CTkFrame(tabla, fg_color="transparent")
                badge_outer.grid(row=data_row, column=1, sticky="nsew", padx=4, pady=6)
                badge_outer.columnconfigure(0, weight=1)
                badge_outer.rowconfigure(0, weight=1)
                badge = ctk.CTkFrame(
                    badge_outer,
                    fg_color="#D1FAE5" if es_activa else "#FEE2E2",
                    corner_radius=8
                )
                badge.grid(row=0, column=0)
                ctk.CTkLabel(
                    badge,
                    text="" + (AppContext.t("ACTIVA") if es_activa else AppContext.t("INACTIVA")),
                    font=("Inter", 9, "bold"),
                    text_color="#065F46" if es_activa else "#991B1B"
                ).pack(padx=12, pady=4)

                act_outer = ctk.CTkFrame(tabla, fg_color="transparent")
                act_outer.grid(row=data_row, column=2, sticky="nsew", padx=4, pady=6)
                act_outer.columnconfigure(0, weight=1)
                act_outer.rowconfigure(0, weight=1)

                btns = ctk.CTkFrame(act_outer, fg_color="transparent")
                btns.grid(row=0, column=0)

                ctk.CTkButton(
                    btns, text="✎", width=34, height=34,
                    font=("Segoe UI Symbol", 14, "bold"), fg_color=COLORS["hover"],
                    hover_color=COLORS["border"], text_color=COLORS["text"],
                    command=lambda id_f=f["id"]: self.abrir_formulario(id_f)
                ).pack(side="left", padx=3)

                if es_activa:
                    ctk.CTkButton(
                        btns, text="⊘", width=34, height=34,
                        font=("Segoe UI Symbol", 14, "bold"), fg_color="#FFF1F2",
                        hover_color="#FEE2E2", text_color="#E11D48",
                        command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_cambio_estado(id_f, n, desactivar=True)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkButton(
                        btns, text="✓", width=34, height=34,
                        font=("Segoe UI Symbol", 14, "bold"), fg_color="#10B981",
                        hover_color="#059669", text_color="white",
                        command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_cambio_estado(id_f, n, desactivar=False)
                    ).pack(side="left", padx=3)

                ctk.CTkFrame(tabla, fg_color=COLORS["hover"], height=1).grid(
                    row=sep_row, column=0, columnspan=3, sticky="ew"
                )

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # MODAL UNIFICADO ACTIVAR / DESACTIVAR
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def confirmar_cambio_estado(self, id_facultad, nombre, desactivar=True):
        self.overlay = ctk.CTkFrame(self, fg_color="transparent")
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        modal = ctk.CTkFrame(
            self.overlay, fg_color=COLORS["card"], corner_radius=8,
            width=340 if self.is_compact else 420,
            height=220 if self.is_compact else 250,
            border_width=2, border_color="#CBD5E1"
        )
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        if desactivar:
            icono     = ""
            titulo    = AppContext.t("Â¿Desactivar esta facultad?")
            sub       = AppContext.t("La facultad dejarÃ¡ de estar disponible.")
            btn_txt   = AppContext.t("Desactivar")
            btn_color = "#EF4444"
            btn_hover = "#DC2626"
        else:
            icono     = ""
            titulo    = AppContext.t("Â¿Activar esta facultad?")
            sub       = AppContext.t("La facultad volverÃ¡ a estar disponible.")
            btn_txt   = AppContext.t("Activar")
            btn_color = "#10B981"
            btn_hover = "#059669"

        ctk.CTkLabel(modal, text=icono, font=("Inter", 32 if self.is_compact else 45)).pack(pady=(12 if self.is_compact else 20, 5))
        ctk.CTkLabel(modal, text=titulo, font=("Inter", 14 if self.is_compact else 16, "bold"), text_color=COLORS["text"]).pack()
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
            command=lambda: self._ejecutar_cambio_estado(id_facultad, desactivar)
        ).pack(side="left", expand=True)

    def _ejecutar_cambio_estado(self, id_facultad, desactivar_flag):
        if desactivar_flag:
            desactivar_facultad(id_facultad)
        else:
            reactivar_facultad(id_facultad)
        self.render_table_content()
        self.cerrar_modal()

    def cerrar_modal(self):
        if hasattr(self, "overlay"):
            self.overlay.destroy()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # FORMULARIO
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def abrir_formulario(self, id_facultad=None):
        self.vista_tabla.pack_forget()

        if id_facultad:
            self.modo_edicion       = True
            self.facultad_actual_id = id_facultad
            facultad   = obtener_facultad_por_id(id_facultad)
            titulo     = AppContext.t("Editar Facultad")
            nombre_ini = facultad["nombre"] if facultad else ""
            estado_ini = AppContext.t("Activa") if facultad and facultad["estado"] == 1 else AppContext.t("Inactiva")
        else:
            self.modo_edicion = False
            titulo     = AppContext.t("Crear Nueva Facultad")
            nombre_ini = ""
            estado_ini = AppContext.t("Activa")

        self.form_base = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.form_base.pack(fill="both", expand=True)
        padx_form = 12 if self.is_compact else 60
        form_scroll = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            form_scroll, text=titulo,
            font=self.font_header, text_color=COLORS["text"]
        ).pack(anchor="w", padx=padx_form, pady=(8 if self.is_compact else 24, 10))

        form_card = ctk.CTkFrame(
            form_scroll, fg_color=COLORS["card"],
            corner_radius=8, border_width=1, border_color=COLORS["border"]
        )
        form_card.pack(fill="x", padx=padx_form, pady=6)

        ctk.CTkLabel(
            form_card, text=AppContext.t("Nombre de la Facultad"),
            font=self.font_small, text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=14 if self.is_compact else 20, pady=(10, 3))
        self.input_nombre = ctk.CTkEntry(
            form_card, height=36 if self.is_compact else 40, font=self.font_normal,
            fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"]
        )
        self.input_nombre.insert(0, nombre_ini)
        self.input_nombre.pack(fill="x", padx=14 if self.is_compact else 20, pady=(0, 10))

        ctk.CTkLabel(
            form_card, text=AppContext.t("Estado"),
            font=self.font_small, text_color=COLORS["subtext"]
        ).pack(anchor="w", padx=14 if self.is_compact else 20, pady=(0, 3))
        self.combo_estado = ctk.CTkOptionMenu(
            form_card,
            values=[AppContext.t("Activa"), AppContext.t("Inactiva")],
            height=36 if self.is_compact else 40, font=self.font_normal,
            fg_color=COLORS["hover"], button_color=COLORS["border"],
            text_color=COLORS["text"]
        )
        self.combo_estado.set(estado_ini)
        self.combo_estado.pack(fill="x", padx=14 if self.is_compact else 20, pady=(0, 14))

        btns = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btns.pack(fill="x", padx=padx_form, pady=12)

        btn_cancelar = ctk.CTkButton(
            btns, text=AppContext.t("Cancelar"),
            font=self.font_sub, fg_color="#FEE2E2", text_color="#991B1B",
            height=38 if self.is_compact else 42, command=self.volver_a_tabla
        )
        btn_guardar = ctk.CTkButton(
            btns, text=AppContext.t("Guardar Facultad"),
            font=self.font_sub, fg_color="#10B981", text_color="white",
            height=38 if self.is_compact else 42, command=self.guardar_facultad
        )

        if self.is_compact:
            btn_cancelar.pack(fill="x", pady=(0, 10))
            btn_guardar.pack(fill="x")
        else:
            btn_cancelar.pack(side="left", expand=True, fill="x", padx=(0, 10))
            btn_guardar.pack(side="left", expand=True, fill="x", padx=(10, 0))

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # HELPERS
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def facultad_existe(self, nombre):
        todas = obtener_todas_facultades()
        return any(
            f["nombre"].strip().lower() == nombre.strip().lower()
            for f in todas
        )

    def guardar_facultad(self):
        nombre = self.input_nombre.get().strip()
        estado = 1 if self.combo_estado.get() == AppContext.t("Activa") else 0

        if not nombre:
            return
        if not re.match(r"^[A-Za-zÃÃ‰ÃÃ“ÃšÃ¡Ã©Ã­Ã³ÃºÃ‘Ã±\s]+$", nombre):
            print("Error: Nombre de facultad invÃ¡lido")
            return
        if len(nombre) < 5:
            print("Error: Facultad demasiado corta")
            return
        if self.facultad_existe(nombre) and not self.modo_edicion:
            print("Error: Facultad duplicada")
            return

        if self.modo_edicion:
            actualizar_facultad(self.facultad_actual_id, nombre, estado)
        else:
            crear_facultad(nombre, estado)
        self.volver_a_tabla()

    def volver_a_tabla(self):
        if hasattr(self, "form_base"):
            self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content()
