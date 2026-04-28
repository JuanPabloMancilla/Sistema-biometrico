import customtkinter as ctk
from app.services.theme import COLORS
from app.services.carrera_service import (
    obtener_todas_carreras,
    crear_carrera,
    actualizar_carrera,
    eliminar_carrera,
    obtener_carrera_por_id,
    obtener_facultades_para_dropdown
)

class CarreraManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color=COLORS["bg"])
        self.controller = controller
        self.usuario_editando_id = None 
        
        # --- Configuración de Fuentes ---
        self.font_header = ("Inter", 30, "bold")
        self.font_sub = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small = ("Inter", 11, "bold")
        
        self.modo_edicion = False
        self.carrera_actual_id = None
        
        # Vista de tabla principal
        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)
        
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.render_table_content()

    def render_table_content(self):
        """Renderiza la tabla compacta con 5 columnas e iconos"""
        for w in self.main_card.winfo_children(): 
            w.destroy()

        # --- CONFIGURACIÓN DE ANCHOS ---
        ancho_id = 100
        ancho_nombre = 300
        ancho_facultad = 150
        ancho_estado = 150

        # --- ENCABEZADO FIJO ---
        table_head = ctk.CTkFrame(self.main_card, fg_color="transparent", height=35)
        table_head.pack(fill="x", padx=20, pady=(10, 5))

        
        ctk.CTkLabel(table_head, text="📖 NOMBRE", font=self.font_small, text_color=COLORS["subtext"], width=ancho_nombre, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="🏫 FACULTAD", font=self.font_small, text_color=COLORS["subtext"], width=ancho_facultad, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="⚙️ ESTADO", font=self.font_small, text_color=COLORS["subtext"], width=ancho_estado, anchor="center").pack(side="left")
        ctk.CTkLabel(table_head, text="ACCIONES", font=self.font_small, text_color=COLORS["subtext"]).pack(side="right", padx=50)

        ctk.CTkFrame(self.main_card, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20)

        # --- CUERPO SCROLLABLE ---
        todas = obtener_todas_carreras()
        query = self.entry_busqueda.get().strip().lower() if hasattr(self, "entry_busqueda") else ""
        carreras = [c for c in todas if query in c["nombre"].lower() or query in (c.get("facultad_nombre") or "").lower()] if query else todas
        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
        
        if not carreras:
            msg = f"No se encontraron carreras para \"{query}\"" if query else "No hay carreras registradas"
            ctk.CTkLabel(scroll, text=msg, font=self.font_normal, text_color=COLORS["subtext"]).pack(pady=40)
            return

        for c in carreras:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=60)
            row.pack(fill="x", side="top", pady=1)
            row.pack_propagate(False)

            # 1. ID
            id_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_id)
            id_block.pack(side="left")
            ctk.CTkLabel(id_block, text=f"#{c['id']}", font=self.font_normal, text_color=COLORS["subtext"]).pack(expand=True)
            id_block.pack_propagate(False)


            # 2. NOMBRE
            nombre_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_nombre)
            nombre_block.pack(side="left", fill="y")
            ctk.CTkLabel(nombre_block, text=c["nombre"].upper(), font=("Inter", 12, "bold"), 
            text_color=COLORS["text"], anchor="w").pack(expand=True, fill="x", padx=5)
            nombre_block.pack_propagate(False)

            # 3. FACULTAD
            fac_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_facultad)
            fac_block.pack(side="left", fill="y")

            fac_txt = c["facultad_nombre"] if c["facultad_nombre"] else "S/F"

            # 🔥 generar abreviatura
            #abreviar la facultad en el catalogo 
            fac_abrev = "".join([p[0] for p in fac_txt.split() if p[0].isalpha()]).upper()

            ctk.CTkLabel(
            fac_block,
            text=fac_abrev,   # 👈 SOLO UNO
            font=self.font_normal,
            text_color=COLORS["text"],
            anchor="w"
            ).pack(expand=True, fill="x", padx=5)

            fac_block.pack_propagate(False)

            # 4. ESTADO
            estado_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_estado)
            estado_block.pack(side="left", fill="y")
            estado_block.pack_propagate(False)

            es_activa = c.get('estado', 1) == 1
            est_bg = "#D1FAE5" if es_activa else "#FEE2E2"
            est_txt = "#065F46" if es_activa else "#991B1B"
            badge = ctk.CTkFrame(estado_block, fg_color=est_bg, corner_radius=20)
            badge.pack(expand=True)
            ctk.CTkLabel(badge, text="● ACTIVA" if es_activa else "● INACTIVA", 
                         font=("Inter", 9, "bold"), text_color=est_txt).pack(padx=10, pady=3)

            # 5. ACCIONES
            act_block = ctk.CTkFrame(row, fg_color="transparent")
            act_block.pack(side="right", padx=20)
            ctk.CTkButton(act_block, text="✏️", width=32, height=32, font=("Inter", 14), 
                         fg_color=COLORS["hover"], hover_color=COLORS["border"], text_color=COLORS["text"], 
                         command=lambda cid=c["id"]: self.abrir_formulario(cid)).pack(side="left", padx=4, pady=14)
            ctk.CTkButton(act_block, text="🗑️", width=32, height=32, font=("Inter", 14), 
                         fg_color="#FFF1F2", hover_color="#FEE2E2", text_color="#E11D48", 
                         command=lambda cid=c["id"], n=c["nombre"]: self.confirmar_eliminar_modal(cid, n)).pack(side="left", padx=2, pady=14)

            ctk.CTkFrame(scroll, fg_color=COLORS["hover"], height=1).pack(fill="x", padx=20, side="top")

    def abrir_formulario(self, id_carrera=None):
        self.vista_tabla.pack_forget()
        self.facultades_dict = obtener_facultades_para_dropdown()
        facultades_lista = list(self.facultades_dict.values())
        
        if id_carrera:
            self.modo_edicion = True
            self.carrera_actual_id = id_carrera
            c = obtener_carrera_por_id(id_carrera)
            titulo = "✏️ Editar Carrera"
            nombre_ini = c["nombre"] if c else ""
            estado_ini = "Activa" if c and c["estado"] == 1 else "Inactiva"
            fac_id = c["id_facultad"] if c else None
            fac_nombre_ini = self.facultades_dict.get(fac_id, "Seleccionar facultad")
        else:
            self.modo_edicion = False
            titulo = "➕ Nueva Carrera"
            nombre_ini = ""
            estado_ini = "Activa"
            fac_nombre_ini = facultades_lista[0] if facultades_lista else "Seleccionar facultad"

        self.form_base = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.form_base.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.form_base, text=titulo, font=self.font_header, text_color=COLORS["text"]).pack(anchor="w", padx=60, pady=(40, 20))

        form_card = ctk.CTkFrame(self.form_base, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        form_card.pack(fill="x", padx=60, pady=10)

        # Inputs con letras negras (#000000)
        ctk.CTkLabel(form_card, text="📖 Nombre de la Carrera", font=self.font_small, text_color=COLORS["subtext"]).pack(anchor="w", padx=25, pady=(25, 5))
        self.input_nombre = ctk.CTkEntry(form_card, height=45, font=self.font_normal, fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"])
        self.input_nombre.insert(0, nombre_ini)
        self.input_nombre.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(form_card, text="🏫 Facultad", font=self.font_small, text_color=COLORS["subtext"]).pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_facultad = ctk.CTkOptionMenu(form_card, values=facultades_lista, height=45, font=self.font_normal, fg_color=COLORS["hover"], button_color=COLORS["border"], text_color=COLORS["text"])
        self.combo_facultad.set(fac_nombre_ini)
        self.combo_facultad.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(form_card, text="⚙️ Estado", font=self.font_small, text_color=COLORS["subtext"]).pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_estado = ctk.CTkOptionMenu(form_card, values=["Activa", "Inactiva"], height=45, font=self.font_normal, fg_color=COLORS["hover"], button_color=COLORS["border"], text_color=COLORS["text"])
        self.combo_estado.set(estado_ini)
        self.combo_estado.pack(fill="x", padx=25, pady=(0, 30))

        btns = ctk.CTkFrame(self.form_base, fg_color="transparent")
        btns.pack(fill="x", padx=60, pady=30)
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color="#991B1B", height=55, command=self.volver_a_tabla).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar Carrera", font=self.font_sub, fg_color="#D1FAE5", text_color="#065F46", height=55, command=self.guardar_carrera).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def confirmar_eliminar_modal(self, id_carrera, nombre):
        """Modal flotante transparente con botones verde/rojo"""
        self.overlay = ctk.CTkFrame(self, fg_color="transparent") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        modal = ctk.CTkFrame(self.overlay, fg_color="white", corner_radius=20, width=420, height=240, border_width=2, border_color="#CBD5E1")
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(modal, text="🗑️", font=("Inter", 45)).pack(pady=(25, 5))
        ctk.CTkLabel(modal, text="¿Está seguro que desea borrar la carrera?", font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(modal, text=f"Se eliminará: {nombre.upper()}", font=("Inter", 12), text_color=COLORS["subtext"]).pack(pady=5)
        
        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=25, padx=30)
        
        # Cancelar en ROJO
        ctk.CTkButton(btns, text="Cancelar", fg_color="#EF4444", text_color="white", hover_color="#DC2626", height=40, font=("Inter", 13, "bold"), command=self.cerrar_modal).pack(side="left", expand=True, padx=(0, 10))
        
        # Confirmar en VERDE
        ctk.CTkButton(btns, text="Confirmar y Borrar", fg_color="#10B981", text_color="white", hover_color="#059669", height=40, font=("Inter", 13, "bold"), command=lambda: self.borrar_carrera_y_cerrar(id_carrera)).pack(side="left", expand=True)

    def cerrar_modal(self):
        if hasattr(self, 'overlay'): self.overlay.destroy()

    def borrar_carrera_y_cerrar(self, id_carrera):
        if eliminar_carrera(id_carrera):
            self.render_table_content()
        self.cerrar_modal()

    def guardar_carrera(self):
        nombre = self.input_nombre.get().strip()
        estado = 1 if self.combo_estado.get() == "Activa" else 0
        fac_nombre = self.combo_facultad.get()
        id_facultad = next((id for id, n in self.facultades_dict.items() if n == fac_nombre), None)
        if not nombre or not id_facultad: return
        if self.modo_edicion: actualizar_carrera(self.carrera_actual_id, nombre, id_facultad, estado)
        else: crear_carrera(nombre, id_facultad, estado)
        self.volver_a_tabla()

    def volver_a_tabla(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content()

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent")
        h.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(h, text="🎓 Gestión de Carreras", font=self.font_header, text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(h, text="➕ Agregar Carrera", font=self.font_sub, fg_color="#000000", height=50, corner_radius=12, command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent")
        bar.pack(fill="x", padx=30, pady=10)
        self.entry_busqueda = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar carrera por nombre...", height=42, corner_radius=10, fg_color=COLORS["hover"], border_width=1, text_color=COLORS["text"])
        self.entry_busqueda.pack(side="left", fill="x", expand=True)
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self.render_table_content())

    