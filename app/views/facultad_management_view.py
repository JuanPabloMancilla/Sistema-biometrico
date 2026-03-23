import customtkinter as ctk
from app.services.facultad_service import (
    obtener_todas_facultades,
    crear_facultad,
    actualizar_facultad,
    eliminar_facultad,
    obtener_facultad_por_id
)

class FacultadManagementView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")
        
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
        ctk.CTkLabel(title_cont, text="🏫 Gestión de Facultades", font=self.font_header, text_color="#000000").pack(anchor="w")
        ctk.CTkLabel(title_cont, text="Administra las unidades académicas del sistema", font=self.font_normal, text_color="#64748B").pack(anchor="w")
        
        ctk.CTkButton(header, text="➕ Agregar Facultad", fg_color="#000000", hover_color="#262626",
                     font=self.font_sub, height=50, corner_radius=12, command=self.abrir_formulario).pack(side="right", anchor="n")
        
        # 2. Card Principal
        self.main_card = ctk.CTkFrame(self, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.render_table_content()

    def render_table_content(self):
        """Renderiza la tabla de facultades con 4 columnas e iconos"""
        for w in self.main_card.winfo_children(): 
            w.destroy()

        # --- CONFIGURACIÓN DE ANCHOS ---
        ancho_id = 100
        ancho_nombre = 450
        ancho_estado = 150

        # --- ENCABEZADO FIJO ---
        table_head = ctk.CTkFrame(self.main_card, fg_color="transparent", height=35)
        table_head.pack(fill="x", padx=20, pady=(10, 5))

        # Títulos en NEGRO
        ctk.CTkLabel(table_head, text="🆔 ID", font=self.font_small, text_color="#000000", width=ancho_id, anchor="center").pack(side="left")
        ctk.CTkLabel(table_head, text="🏛️ NOMBRE DE FACULTAD", font=self.font_small, text_color="#000000", width=ancho_nombre, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="⚙️ ESTADO", font=self.font_small, text_color="#000000", width=ancho_estado, anchor="center").pack(side="left")
        ctk.CTkLabel(table_head, text="ACCIONES", font=self.font_small, text_color="#000000").pack(side="right", padx=60)

        ctk.CTkFrame(self.main_card, fg_color="#E2E8F0", height=1).pack(fill="x", padx=20)

        # --- CUERPO SCROLLABLE ---
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

            # 1. ID
            id_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_id)
            id_block.pack(side="left")
            id_block.pack_propagate(False)
            ctk.CTkLabel(id_block, text=f"#{f['id']}", font=self.font_normal, text_color="#000000").pack(expand=True)

            # 2. NOMBRE
            info_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_nombre)
            info_block.pack(side="left", fill="y")
            info_block.pack_propagate(False)
            ctk.CTkLabel(info_block, text=f["nombre"].upper(), font=("Inter", 12, "bold"), 
                         text_color="#000000", anchor="w").pack(expand=True, fill="x")

            # 3. ESTADO
            estado_block = ctk.CTkFrame(row, fg_color="transparent", width=ancho_estado)
            estado_block.pack(side="left", fill="y")
            estado_block.pack_propagate(False)

            es_activa = f.get('estado', 1) == 1
            est_bg = "#D1FAE5" if es_activa else "#FEE2E2"
            est_txt = "#065F46" if es_activa else "#991B1B"
            
            badge_est = ctk.CTkFrame(estado_block, fg_color=est_bg, corner_radius=20)
            badge_est.pack(expand=True)
            ctk.CTkLabel(badge_est, text="● ACTIVA" if es_activa else "● INACTIVA", 
                         font=("Inter", 9, "bold"), text_color=est_txt).pack(padx=10, pady=3)

            # 4. ACCIONES
            act_block = ctk.CTkFrame(row, fg_color="transparent")
            act_block.pack(side="right", padx=20, fill="y")
            
            ctk.CTkButton(act_block, text="✏️", width=32, height=32, font=("Inter", 14), 
                         fg_color="#F1F5F9", hover_color="#E2E8F0", text_color="#000000", 
                         command=lambda id_f=f["id"]: self.abrir_formulario(id_f)).pack(side="left", padx=4, pady=16)
            
            ctk.CTkButton(act_block, text="🗑️", width=32, height=32, font=("Inter", 14), 
                         fg_color="#FFF1F2", hover_color="#FEE2E2", text_color="#E11D48", 
                         command=lambda id_f=f["id"], n=f["nombre"]: self.confirmar_eliminar(id_f, n)).pack(side="left", padx=2, pady=16)

            ctk.CTkFrame(scroll, fg_color="#F1F5F9", height=1).pack(fill="x", padx=20, side="top")

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

        self.form_base = ctk.CTkFrame(self, fg_color="#F8FAFC")
        self.form_base.pack(fill="both", expand=True)
        
        # Título Formulario en NEGRO
        ctk.CTkLabel(self.form_base, text=titulo, font=self.font_header, text_color="#000000").pack(anchor="w", padx=60, pady=(40, 20))

        form_card = ctk.CTkFrame(self.form_base, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        form_card.pack(fill="x", padx=60, pady=10)

        # Campos con letras en NEGRO (#000000)
        ctk.CTkLabel(form_card, text="🏛️ Nombre de la Facultad", font=self.font_small, text_color="#000000").pack(anchor="w", padx=25, pady=(25, 5))
        self.input_nombre = ctk.CTkEntry(form_card, height=45, font=self.font_normal, fg_color="#F1F5F9", border_width=0, text_color="#000000")
        self.input_nombre.insert(0, nombre_ini)
        self.input_nombre.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(form_card, text="⚙️ Estado", font=self.font_small, text_color="#000000").pack(anchor="w", padx=25, pady=(0, 5))
        self.combo_estado = ctk.CTkOptionMenu(form_card, values=["Activa", "Inactiva"], height=45, font=self.font_normal, fg_color="#F1F5F9", button_color="#E2E8F0", text_color="#000000")
        self.combo_estado.set(estado_ini)
        self.combo_estado.pack(fill="x", padx=25, pady=(0, 30))

        # Botones
        btns = ctk.CTkFrame(self.form_base, fg_color="transparent")
        btns.pack(fill="x", padx=60, pady=30)
        
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color="#000000", height=55, command=self.volver_a_tabla).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar Facultad", font=self.font_sub, fg_color="#D1FAE5", text_color="#000000", height=55, command=self.guardar_facultad).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def guardar_facultad(self):
        nombre = self.input_nombre.get().strip()
        estado = 1 if self.combo_estado.get() == "Activa" else 0
        if not nombre: return

        if self.modo_edicion:
            actualizar_facultad(self.facultad_actual_id, nombre, estado)
        else:
            crear_facultad(nombre, estado)
        
        self.volver_a_tabla()

    def confirmar_eliminar(self, id_facultad, nombre):
        if eliminar_facultad(id_facultad):
            self.render_table_content()

    def volver_a_tabla(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.main_card.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        self.render_table_content()