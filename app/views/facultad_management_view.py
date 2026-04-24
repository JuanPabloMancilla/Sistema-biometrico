import customtkinter as ctk
from app.services.theme import COLORS
from app.services.facultad_service import (
    obtener_todas_facultades,
    crear_facultad,
    actualizar_facultad,
    eliminar_facultad,
    obtener_facultad_por_id
)

class FacultadManagementView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["bg"])
        
        self.modo_edicion = False
        self.facultad_actual_id = None
        
        # --- Configuración de Fuentes ---
        self.font_header = ("Inter", 30, "bold")
        self.font_sub = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small = ("Inter", 11, "bold")
        
        self.crear_vista_tabla()
    
    def crear_vista_tabla(self):
        # 1. Header de la vista
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40, 20))
        
        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")
        ctk.CTkLabel(title_cont, text="🏫 Gestión de Facultades", font=self.font_header, text_color=COLORS["text"]).pack(anchor="w")
        ctk.CTkLabel(title_cont, text="Administra las unidades académicas del sistema", font=self.font_normal, text_color=COLORS["subtext"]).pack(anchor="w")
        
        ctk.CTkButton(header, text="➕ Agregar Facultad", fg_color=COLORS["text"], hover_color=COLORS["hover"], text_color=COLORS["bg"],
                     font=self.font_sub, height=50, corner_radius=12, command=self.abrir_formulario).pack(side="right", anchor="n")
        
        # 2. Card Principal
        self.main_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.render_table_content()

    def render_table_content(self):
        """Renderiza la tabla de facultades"""
        for w in self.main_card.winfo_children(): 
            w.destroy()

        ancho_id = 100
        ancho_nombre = 450
        ancho_estado = 150

        table_head = ctk.CTkFrame(self.main_card, fg_color="transparent", height=35)
        table_head.pack(fill="x", padx=20, pady=(10, 5))

        
        ctk.CTkLabel(table_head, text="🏛️ NOMBRE DE FACULTAD", font=self.font_small, text_color=COLORS["text"], width=ancho_nombre, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="⚙️ ESTADO", font=self.font_small, text_color=COLORS["text"], width=ancho_estado, anchor="center").pack(side="left")
        ctk.CTkLabel(table_head, text="ACCIONES", font=self.font_small, text_color=COLORS["text"]).pack(side="right", padx=60)

        ctk.CTkFrame(self.main_card, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20)

        facultades = obtener_todas_facultades()
        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both")

        if not facultades:
            ctk.CTkLabel(scroll, text="No hay facultades registradas", font=self.font_normal, text_color="#94A3B8").pack(pady=40)
            return

        for f in facultades:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=65)
            row.pack(fill="x", side="top", pady=1)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=f"#{f['id']}", font=self.font_normal, text_color=COLORS["text"], width=ancho_id).pack(side="left")
            ctk.CTkLabel(row, text=f["nombre"].upper(), font=("Inter", 12, "bold"), text_color=COLORS["text"], width=ancho_nombre, anchor="w").pack(side="left")

            es_activa = f.get('estado', 1) == 1
            badge_est = ctk.CTkFrame(row, fg_color="#D1FAE5" if es_activa else "#FEE2E2", corner_radius=20, width=110, height=26)
            badge_est.pack(side="left", padx=(20,0))
            badge_est.pack_propagate(False)
            ctk.CTkLabel(badge_est, text="● ACTIVA" if es_activa else "● INACTIVA", font=("Inter", 9, "bold"), text_color="#065F46" if es_activa else "#991B1B").pack(expand=True)

            act_block = ctk.CTkFrame(row, fg_color="transparent")
            act_block.pack(side="right", padx=20)
            ctk.CTkButton(act_block, text="✏️", width=32, height=32, fg_color=COLORS["hover"], text_color=COLORS["text"], command=lambda id_f=f["id"]: self.abrir_formulario(id_f)).pack(side="left", padx=4)
            ctk.CTkButton(act_block, text="🗑️", width=32, height=32, fg_color="#FFF1F2", text_color="#E11D48", command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_eliminar_modal(id_f, n)).pack(side="left", padx=2)

            ctk.CTkFrame(scroll, fg_color=COLORS["hover"], height=1).pack(fill="x", padx=20)

    def abrir_formulario(self, id_facultad=None):
        self.main_card.pack_forget()
        
        if id_facultad:
            self.modo_edicion = True
            self.facultad_actual_id = id_facultad
            facultad = obtener_facultad_por_id(id_facultad)
            titulo = "✏️ Editar Facultad"
            nombre_ini = facultad["nombre"] if facultad else ""
            estado_ini = "Activa" if facultad and facultad["estado"] == 1 else "Inactiva"
        else:
            self.modo_edicion = False
            titulo = "➕ Crear Nueva Facultad"
            nombre_ini = ""
            estado_ini = "Activa"

        self.form_base = ctk.CTkFrame(self, fg_color=COLORS["bg"])
        self.form_base.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.form_base, text=titulo, font=self.font_header, text_color=COLORS["text"]).pack(anchor="w", padx=60, pady=(40, 20))

        form_card = ctk.CTkFrame(self.form_base, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        form_card.pack(fill="x", padx=60, pady=10)

        ctk.CTkLabel(form_card, text="🏛️ Nombre de la Facultad", font=self.font_small, text_color=COLORS["text"]).pack(anchor="w", padx=25, pady=(25, 5))
        self.input_nombre = ctk.CTkEntry(form_card, height=45, font=self.font_normal, fg_color=COLORS["hover"], border_width=0, text_color=COLORS["text"])
        self.input_nombre.insert(0, nombre_ini)
        self.input_nombre.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(form_card, text="⚙️ Estado", font=self.font_small, text_color=COLORS["text"]).pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_estado = ctk.CTkOptionMenu(form_card, values=["Activa", "Inactiva"], height=45, font=self.font_normal, fg_color=COLORS["hover"], button_color=COLORS["border"], text_color=COLORS["text"])
        self.combo_estado.set(estado_ini)
        self.combo_estado.pack(fill="x", padx=25, pady=(0, 30))

        btns = ctk.CTkFrame(self.form_base, fg_color="transparent")
        btns.pack(fill="x", padx=60, pady=30)
        
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color=COLORS["text"], height=55, command=self.volver_a_tabla).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar Facultad", font=self.font_sub, fg_color="#D1FAE5", text_color=COLORS["text"], height=55, command=self.guardar_facultad).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def guardar_facultad(self):
        nombre = self.input_nombre.get().strip()
        estado = 1 if self.combo_estado.get() == "Activa" else 0
        if not nombre: return
        if self.modo_edicion: actualizar_facultad(self.facultad_actual_id, nombre, estado)
        else: crear_facultad(nombre, estado)
        self.volver_a_tabla()

    def confirmar_eliminar_modal(self, id_facultad, nombre):
        # 1. Overlay Transparente
        self.overlay = ctk.CTkFrame(self, fg_color="transparent") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 2. Ventana Modal
        modal = ctk.CTkFrame(self.overlay, fg_color=COLORS["card"], corner_radius=20, width=420, height=240, border_width=2, border_color=COLORS["border"])
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(modal, text="🏛️", font=("Inter", 45)).pack(pady=(25, 5))
        ctk.CTkLabel(modal, text="¿Está seguro de eliminar esta facultad?", font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(modal, text=f"Se eliminará: {nombre.upper()}", font=("Inter", 12), text_color=COLORS["subtext"]).pack(pady=5)
        
        # 3. Botones (Verde Confirmar / Rojo Cancelar)
        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=25, padx=30)
        
        ctk.CTkButton(btns, text="Cancelar", fg_color="#EF4444", text_color="white", hover_color="#DC2626", 
                     height=40, font=("Inter", 13, "bold"), command=self.cerrar_modal).pack(side="left", expand=True, padx=(0, 10))
        
        ctk.CTkButton(btns, text="Confirmar y Borrar", fg_color="#10B981", text_color="white", hover_color="#059669", 
                     height=40, font=("Inter", 13, "bold"), command=lambda: self.borrar_facultad_y_cerrar(id_facultad)).pack(side="left", expand=True)

    def cerrar_modal(self):
        if hasattr(self, 'overlay'): self.overlay.destroy()

    def borrar_facultad_y_cerrar(self, id_facultad):
        if eliminar_facultad(id_facultad):
            self.render_table_content()
        self.cerrar_modal()

    def volver_a_tabla(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        self.render_table_content()