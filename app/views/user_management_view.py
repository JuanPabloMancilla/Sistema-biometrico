import customtkinter as ctk
from app.services.carrera_service import obtener_todas_carreras, obtener_facultades_para_dropdown
from app.services.usuario import (
    insertar_usuario, 
    actualizar_usuario,
    obtener_usuarios_formateados, 
    obtener_id_facultad_por_nombre, 
    obtener_id_rol_por_nombre,
    desactivar_usuario 
)

class UserManagementView(ctk.CTkFrame):
    def __init__(self, master, controller=None):
        super().__init__(master, fg_color="#F8FAFC")
        self.controller = controller
        self.usuario_editando_id = None 
        
        # --- Configuración de Fuentes ---
        self.font_header = ("Inter", 30, "bold")
        self.font_sub = ("Inter", 16, "bold")
        self.font_normal = ("Inter", 13)
        self.font_small = ("Inter", 11, "bold")
        
        # --- Variables ---
        self.rol_var = ctk.StringVar(value="ESTUDIANTE")
        self.carrera_var = ctk.StringVar()
        self.inputs_obligatorios = {}
        self.inputs_apellidos = {}
        
        self.refresh_data()

        self.colors = {
            "DOCENTE": {"bg": "#F3E8FF", "text": "#A855F7"}, 
            "ESTUDIANTE": {"bg": "#DBEAFE", "text": "#3B82F6"}, 
            "AUXILIAR": {"bg": "#D1FAE5", "text": "#10B981"}
        }
        
        self.filtro_rol_actual = "Todos"
        self.filter_visible = False 

        self.vista_tabla = ctk.CTkFrame(self, fg_color="transparent")
        self.vista_tabla.pack(fill="both", expand=True)

        self.create_header(self.vista_tabla)
        self.create_search_bar(self.vista_tabla)
        
        self.filter_container = ctk.CTkFrame(self.vista_tabla, fg_color="transparent")
        
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color="white", corner_radius=15, border_width=1, border_color="#E2E8F0")
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))
        
        self.render_table_content(self.all_users)

    def refresh_data(self):
        try:
            self.all_users = obtener_usuarios_formateados()
        except:
            self.all_users = []

    def validar_ocho_numeros(self, P):
        """Solo permite números y máximo 8 dígitos en el campo de Cuenta"""
        if P == "": return True
        return P.isdigit() and len(P) <= 8

    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children(): 
            w.destroy()

        ancho_foto, ancho_info, ancho_estado = 140, 400, 150

        table_head = ctk.CTkFrame(self.main_card, fg_color="transparent", height=35)
        table_head.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(table_head, text="👤 FOTOGRAFÍA", font=self.font_small, text_color="#64748B", width=ancho_foto).pack(side="left")
        ctk.CTkLabel(table_head, text="🆔 INFORMACIÓN", font=self.font_small, text_color="#64748B", width=ancho_info, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="⚙️ ESTADO", font=self.font_small, text_color="#64748B", width=ancho_estado).pack(side="left")
        ctk.CTkLabel(table_head, text="ACCIONES", font=self.font_small, text_color="#64748B").pack(side="right", padx=60)

        ctk.CTkFrame(self.main_card, fg_color="#E2E8F0", height=1).pack(fill="x", padx=20)

        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
        
        for u in user_list:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=70)
            row.pack(fill="x", side="top", pady=1)
            row.pack_propagate(False)

            # 1. Foto
            f_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_foto)
            f_b.pack(side="left"); f_b.pack_propagate(False)
            ctk.CTkLabel(f_b, text="👤", font=("Inter", 32)).pack(expand=True)

            # 2. Información
            i_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_info)
            i_b.pack(side="left", fill="y"); i_b.pack_propagate(False)
            i_in = ctk.CTkFrame(i_b, fg_color="transparent"); i_in.pack(expand=True, fill="x", anchor="w")

            l_n = ctk.CTkFrame(i_in, fg_color="transparent"); l_n.pack(anchor="w")
            ctk.CTkLabel(l_n, text=f"{u['nombre_solo']} {u['ap']} {u['am']}".upper(), font=("Inter", 13, "bold"), text_color="#1E293B").pack(side="left")
            
            col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
            badge_r = ctk.CTkFrame(l_n, fg_color=col["bg"], corner_radius=4); badge_r.pack(side="left", padx=8)
            ctk.CTkLabel(badge_r, text=u["r"], font=("Inter", 9, "bold"), text_color=col["text"]).pack(padx=6, pady=1)
            ctk.CTkLabel(i_in, text=f"ID: {u['c']}  •  {u['m']}", font=("Inter", 11), text_color="#64748B").pack(anchor="w")

            # 3. Estado
            e_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_estado)
            e_b.pack(side="left", fill="y"); e_b.pack_propagate(False)
            es_activo = u.get('estado', 1) == 1
            badge_e = ctk.CTkFrame(e_b, fg_color="#D1FAE5" if es_activo else "#FEE2E2", corner_radius=20); badge_e.pack(expand=True)
            ctk.CTkLabel(badge_e, text="● ACTIVO" if es_activo else "● INACTIVO", font=("Inter", 9, "bold"), text_color="#065F46" if es_activo else "#991B1B").pack(padx=10, pady=3)

            # 4. Acciones
            a_b = ctk.CTkFrame(row, fg_color="transparent")
            a_b.pack(side="right", padx=20, fill="y")
            ctk.CTkButton(a_b, text="✏️", width=32, height=32, fg_color="#F1F5F9", text_color="#1E293B", command=lambda d=u: self.abrir_formulario(d)).pack(side="left", padx=4, pady=18)
            ctk.CTkButton(a_b, text="🗑️", width=32, height=32, fg_color="#FFF1F2", text_color="#E11D48", command=lambda i=u['c']: self.ejecutar_eliminacion(i)).pack(side="left", padx=2, pady=18)

            ctk.CTkFrame(scroll, fg_color="#F1F5F9", height=1).pack(fill="x", padx=20, side="top")

    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios, self.inputs_apellidos = {}, {}
        self.usuario_editando_id = usuario["c"] if usuario else None 
        self.rol_var.set(usuario["r"] if usuario else "ESTUDIANTE")
        
        self.dict_facultades = obtener_facultades_para_dropdown()
        nombres_f = list(self.dict_facultades.values()) if self.dict_facultades else ["Sin Datos"]
        self.carreras_por_plantel = {}
        for c in obtener_todas_carreras():
            fn = c['facultad_nombre']
            if fn not in self.carreras_por_plantel: self.carreras_por_plantel[fn] = []
            self.carreras_por_plantel[fn].append(c['nombre'])

        self.form_base = ctk.CTkFrame(self, fg_color="#F8FAFC"); self.form_base.pack(fill="both", expand=True)
        self.form_container = ctk.CTkScrollableFrame(self.form_base, fg_color="transparent"); self.form_container.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(self.form_container, text="✏️ Editar Registro" if usuario else "➕ Nuevo Registro", font=self.font_header, text_color="#000000").pack(anchor="w", padx=60, pady=(30, 10))

        # Card Clasificación
        c_clasi = ctk.CTkFrame(self.form_container, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0"); c_clasi.pack(fill="x", padx=60, pady=10)
        grid = ctk.CTkFrame(c_clasi, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=20)
        ctk.CTkOptionMenu(grid, values=["ESTUDIANTE", "DOCENTE", "AUXILIAR"], variable=self.rol_var, height=40, text_color="black", fg_color="#F1F5F9", button_color="#E2E8F0").pack(side="left", expand=True, fill="x", padx=5)
        self.plantel_menu = ctk.CTkOptionMenu(grid, values=nombres_f, command=self.update_carreras_dinamicas, height=40, text_color="black", fg_color="#F1F5F9", button_color="#E2E8F0"); self.plantel_menu.pack(side="left", expand=True, fill="x", padx=5)
        self.carrera_menu = ctk.CTkOptionMenu(grid, variable=self.carrera_var, values=[], height=40, text_color="black", fg_color="#F1F5F9", button_color="#E2E8F0"); self.carrera_menu.pack(side="left", expand=True, fill="x", padx=5)

        if nombres_f: self.update_carreras_dinamicas(nombres_f[0])

        self.create_section_card(self.form_container, "👤 Información Personal", [("Nombres", usuario["nombre_solo"] if usuario else ""), ("Apellido Paterno", usuario["ap"] if usuario else ""), ("Apellido Materno", usuario["am"] if usuario else "")])
        self.create_section_card(self.form_container, "🆔 Identificación", [("Cuenta", str(usuario["c"]) if usuario else ""), ("Correo", usuario["m"] if usuario else "")])

        # Registro de validación de 8 dígitos para Cuenta
        vcmd = (self.register(self.validar_ocho_numeros), '%P')
        self.inputs_obligatorios["Cuenta"].configure(validate="key", validatecommand=vcmd)
        if usuario: self.inputs_obligatorios["Cuenta"].configure(state="disabled", fg_color="#E2E8F0")

        btns = ctk.CTkFrame(self.form_container, fg_color="transparent"); btns.pack(fill="x", padx=60, pady=(20, 50))
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color="#000000", height=50, command=self.cerrar_formulario).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar", font=self.font_sub, fg_color="#D1FAE5", text_color="#000000", height=50, command=self.validar_y_guardar).pack(side="left", expand=True, fill="x", padx=(10, 0))

    def create_section_card(self, master, title, fields):
        card = ctk.CTkFrame(master, fg_color="white", corner_radius=12, border_width=1, border_color="#E2E8F0"); card.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card, text=title, font=self.font_sub, text_color="#000000").pack(anchor="w", padx=20, pady=(15, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=(0, 20))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(f, text=label, font=self.font_small, text_color="#64748B").pack(anchor="w")
            entry = ctk.CTkEntry(f, height=40, font=self.font_normal, fg_color="#F1F5F9", border_width=0, text_color="black")
            entry.insert(0, val); entry.pack(fill="x", pady=5)
            if "Apellido" in label: self.inputs_apellidos[label] = entry
            else: self.inputs_obligatorios[label] = entry

    def validar_y_guardar(self):
        n = self.inputs_obligatorios.get("Nombres").get().strip()
        em = self.inputs_obligatorios.get("Correo").get().strip()
        cta = self.usuario_editando_id if self.usuario_editando_id else self.inputs_obligatorios.get("Cuenta").get().strip()
        
        if not n or not cta or not em: return
        if "@" not in em: 
            self.inputs_obligatorios["Correo"].configure(border_width=1, border_color="red")
            return
        if not self.usuario_editando_id and len(cta) != 8:
            self.inputs_obligatorios["Cuenta"].configure(border_width=1, border_color="red")
            return

        id_rol = obtener_id_rol_por_nombre(self.rol_var.get())
        id_fac = obtener_id_facultad_por_nombre(self.plantel_menu.get())
        
        if self.usuario_editando_id:
            actualizar_usuario(cta, n, self.inputs_apellidos["Apellido Paterno"].get(), self.inputs_apellidos["Apellido Materno"].get(), id_rol, id_fac, em)
        else:
            insertar_usuario(n, self.inputs_apellidos["Apellido Paterno"].get(), self.inputs_apellidos["Apellido Materno"].get(), id_rol, id_fac, None, cta, em)
        
        self.refresh_data(); self.render_table_content(self.all_users); self.cerrar_formulario()

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent"); h.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(h, text="👥 Gestión de Usuarios", font=self.font_header, text_color="#000000").pack(side="left")
        ctk.CTkButton(h, text="➕ Agregar Usuario", font=self.font_sub, fg_color="#000000", height=45, corner_radius=10, command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=10)
        self.entry_busqueda = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar usuario...", height=42, corner_radius=10, fg_color="#F1F5F9", border_width=1, text_color="black")
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.btn_filter = ctk.CTkButton(bar, text="⚙️ Filtrar ⌵", width=110, height=42, corner_radius=10, fg_color="white", text_color="black", border_width=1, command=self.toggle_filter)
        self.btn_filter.pack(side="left")

    def toggle_filter(self):
        if not self.filter_visible:
            self.draw_tags(); self.filter_container.pack(fill="x", padx=30, pady=(0, 15), before=self.main_card)
            self.btn_filter.configure(text="⚙️ Filtrar ︿"); self.filter_visible = True
        else:
            self.filter_container.pack_forget(); self.btn_filter.configure(text="⚙️ Filtrar ⌵"); self.filter_visible = False

    def draw_tags(self):
        for w in self.filter_container.winfo_children(): w.destroy()
        r1 = ctk.CTkFrame(self.filter_container, fg_color="transparent"); r1.pack(fill="x", padx=20)
        ctk.CTkLabel(r1, text="👤 Rol:", font=self.font_small, text_color="#000000", width=80).pack(side="left")
        for t in ["Todos", "ESTUDIANTE", "DOCENTE", "AUXILIAR"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(r1, text=t, height=28, corner_radius=10, fg_color="#F1F5F9" if act else "white", text_color="black", border_width=1, command=lambda v=t: self.aplicar_filtro_visual(v)).pack(side="left", padx=3)

    def aplicar_filtro_visual(self, v):
        self.filtro_rol_actual = v
        self.draw_tags()
        # Aquí puedes añadir la lógica de filtrado real sobre self.all_users si lo deseas

    def update_carreras_dinamicas(self, fn):
        c = self.carreras_por_plantel.get(fn, ["Sin Carreras"])
        self.carrera_menu.configure(values=c); self.carrera_var.set(c[0])

    def ejecutar_eliminacion(self, id_cuenta):
        self.overlay = ctk.CTkFrame(self, fg_color="#262626"); self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        modal = ctk.CTkFrame(self.overlay, fg_color="white", corner_radius=15, width=360, height=200)
        modal.place(relx=0.5, rely=0.5, anchor="center"); modal.pack_propagate(False)
        ctk.CTkLabel(modal, text="¿Eliminar usuario?", font=self.font_sub, text_color="#E11D48").pack(pady=30)
        btns = ctk.CTkFrame(modal, fg_color="transparent"); btns.pack(fill="x", side="bottom", pady=20, padx=20)
        ctk.CTkButton(btns, text="Cancelar", command=self.cerrar_modal).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btns, text="Eliminar", fg_color="#E11D48", command=lambda: self.confirmar_borrado(id_cuenta)).pack(side="left", expand=True, padx=5)

    def cerrar_modal(self):
        if hasattr(self, 'overlay'): self.overlay.destroy()

    def confirmar_borrado(self, id_cuenta):
        if desactivar_usuario(id_cuenta): self.refresh_data(); self.render_table_content(self.all_users)
        self.cerrar_modal()

    def cerrar_formulario(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content(self.all_users)