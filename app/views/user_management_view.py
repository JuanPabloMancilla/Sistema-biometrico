import customtkinter as ctk
from app.recognition.encoding_manager import cargar_encodings, eliminar_encoding, guardar_encoding
from app.views.terminal_view import TerminalView
from app.services.theme import COLORS
from app.detection.detector_rostro import encodings_db, usuarios_db
from app.recognition.encoding_manager import cargar_encodings
from app.services.carrera_service import obtener_todas_carreras, obtener_facultades_para_dropdown
from app.services.usuario_service import (
    crear_usuario, 
    actualizar_usuario,
    obtener_todos_usuarios, 
    obtener_id_facultad_por_nombre, 
    desactivar_usuario 
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
        
        self.main_card = ctk.CTkFrame(self.vista_tabla, fg_color=COLORS["card"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.main_card.pack(expand=True, fill="both", padx=30, pady=(5, 15))
        
        self.render_table_content(self.all_users)

    def refresh_data(self):
        try:
            data = obtener_todos_usuarios()

            self.all_users = []
            for u in data:
                self.all_users.append({
                    "nombre_solo": u["nombre"],
                    "ap": u["a_paterno"],
                    "am": u["a_materno"],
                    "r": TIPOS_USUARIO.get(u.get("tipo_usuario", 1), "N/A"),
                    "cuenta": u.get("cuenta", ""),
                    "id": u["id_usuario"],
                    "correo": u.get("correo", ""), # no tienes correo en tu query
                    "estado": u.get("estado", 1)
            })

        except Exception as e:
            print("Error usuarios:", e)
            self.all_users = []

    def validar_ocho_numeros(self, P):
        if P == "": return True
        return P.isdigit() and len(P) <= 8

    def render_table_content(self, user_list):
        for w in self.main_card.winfo_children(): 
            w.destroy()

        ancho_foto, ancho_info, ancho_estado = 140, 400, 150
        table_head = ctk.CTkFrame(self.main_card, fg_color="transparent", height=35)
        table_head.pack(fill="x", padx=20, pady=(10, 5))

        ctk.CTkLabel(table_head, text="👤 FOTOGRAFÍA", font=self.font_small, text_color=COLORS["subtext"], width=ancho_foto).pack(side="left")
        ctk.CTkLabel(table_head, text="🆔 INFORMACIÓN", font=self.font_small, text_color=COLORS["subtext"], width=ancho_info, anchor="w").pack(side="left")
        ctk.CTkLabel(table_head, text="⚙️ ESTADO", font=self.font_small, text_color=COLORS["subtext"], width=ancho_estado).pack(side="left")
        ctk.CTkLabel(table_head, text="ACCIONES", font=self.font_small, text_color=COLORS["subtext"]).pack(side="right", padx=60)

        ctk.CTkFrame(self.main_card, fg_color=COLORS["border"], height=1).pack(fill="x", padx=20)
        scroll = ctk.CTkScrollableFrame(self.main_card, fg_color="transparent")
        scroll.pack(expand=True, fill="both")
        
        for u in user_list:
            row = ctk.CTkFrame(scroll, fg_color="transparent", height=70); row.pack(fill="x", side="top", pady=1); row.pack_propagate(False)
            f_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_foto); f_b.pack(side="left"); f_b.pack_propagate(False)
            ctk.CTkLabel(f_b, text="👤", font=("Inter", 32)).pack(expand=True)

            i_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_info); i_b.pack(side="left", fill="y"); i_b.pack_propagate(False)
            i_in = ctk.CTkFrame(i_b, fg_color="transparent"); i_in.pack(expand=True, fill="x", anchor="w")
            l_n = ctk.CTkFrame(i_in, fg_color="transparent"); l_n.pack(anchor="w")
            ctk.CTkLabel(l_n, text=f"{u['nombre_solo']} {u['ap']} {u['am']}".upper(), font=("Inter", 13, "bold"), text_color=COLORS["text"]).pack(side="left")
            
            col = self.colors.get(u["r"].upper(), {"bg": "#E2E8F0", "text": "#475569"})
            badge_r = ctk.CTkFrame(l_n, fg_color=col["bg"], corner_radius=4); badge_r.pack(side="left", padx=8)
            ctk.CTkLabel(badge_r, text=u["r"], font=("Inter", 9, "bold"), text_color=col["text"]).pack(padx=6, pady=1)
            ctk.CTkLabel(i_in, text=f"ID: {u['cuenta']}  •  {u['correo']}", font=("Inter", 11), text_color=COLORS["subtext"]).pack(anchor="w")

            e_b = ctk.CTkFrame(row, fg_color="transparent", width=ancho_estado); e_b.pack(side="left", fill="y"); e_b.pack_propagate(False)
            es_activo = u.get('estado', 1) == 1
            badge_e = ctk.CTkFrame(e_b, fg_color="#D1FAE5" if es_activo else "#FEE2E2", corner_radius=20); badge_e.pack(expand=True)
            ctk.CTkLabel(badge_e, text="● ACTIVO" if es_activo else "● INACTIVO", font=("Inter", 9, "bold"), text_color="#065F46" if es_activo else "#991B1B").pack(padx=10, pady=3)

            a_b = ctk.CTkFrame(row, fg_color="transparent"); a_b.pack(side="right", padx=20)
            ctk.CTkButton(a_b, text="✏️", width=32, height=32, fg_color=COLORS["hover"]
, text_color=COLORS["text"], command=lambda d=u: self.abrir_formulario(d)).pack(side="left", padx=4)
            ctk.CTkButton(a_b, text="🗑️", width=32, height=32, fg_color="#FFF1F2", text_color="#E11D48", command=lambda i=u['id']: self.ejecutar_eliminacion(i)).pack(side="left", padx=2)
            ctk.CTkFrame(scroll, fg_color=COLORS["hover"]
, height=1).pack(fill="x", padx=20, side="top")

    def abrir_formulario(self, usuario=None):
        self.vista_tabla.pack_forget()
        self.inputs_obligatorios, self.inputs_apellidos = {}, {}
        self.usuario_editando_id = usuario["id"] if usuario else None 
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

        ctk.CTkLabel(self.form_container, text="✏️ Editar Registro" if usuario else "➕ Nuevo Registro", font=self.font_header, text_color=COLORS["text"]).pack(anchor="w", padx=60, pady=(30, 10))

        c_clasi = ctk.CTkFrame(self.form_container, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=COLORS["border"]); c_clasi.pack(fill="x", padx=60, pady=10)
        grid = ctk.CTkFrame(c_clasi, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=20)
        ctk.CTkOptionMenu(grid, values=["ESTUDIANTE", "DOCENTE", "TRABAJADOR"], variable=self.rol_var, height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"]).pack(side="left", expand=True, fill="x", padx=5)
        self.plantel_menu = ctk.CTkOptionMenu(grid, values=nombres_f, command=self.update_carreras_dinamicas, height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"]); self.plantel_menu.pack(side="left", expand=True, fill="x", padx=5)
        self.carrera_menu = ctk.CTkOptionMenu(grid, variable=self.carrera_var, values=[], height=40, text_color=COLORS["text"], fg_color=COLORS["hover"], button_color=COLORS["border"]); self.carrera_menu.pack(side="left", expand=True, fill="x", padx=5)

        if nombres_f: self.update_carreras_dinamicas(nombres_f[0])

        self.create_section_card(self.form_container, "👤 Información Personal", [("Nombres", usuario["nombre_solo"] if usuario else ""), ("Apellido Paterno", usuario["ap"] if usuario else ""), ("Apellido Materno", usuario["am"] if usuario else "")])
        self.create_section_card(self.form_container, "🆔 Identificación", [("cuenta", str(usuario["cuenta"]) if usuario and usuario["cuenta"] else ""), ("correo", str(usuario["correo"]) if usuario and usuario["correo"] else "")])

        vcmd = (self.register(self.validar_ocho_numeros), '%P')
        entrada = self.inputs_obligatorios.get("cuenta") 
        if entrada: 
                entrada.configure(validate="key", validatecommand=vcmd)
        # Botón biométrico
        self.btn_biometria = ctk.CTkButton(self.form_container, text="📷 Registrar Biometría", height=50, fg_color="#0EA5E9", text_color="white", font=self.font_sub, command=self.abrir_terminal_biometrica) 
        self.btn_biometria.pack(fill="x", padx=60, pady=(20, 10))
        btns = ctk.CTkFrame(self.form_container, fg_color="transparent"); btns.pack(fill="x", padx=60, pady=(20, 50))
        ctk.CTkButton(btns, text="❌ Cancelar", font=self.font_sub, fg_color="#FEE2E2", text_color=COLORS["text"], height=50, command=self.cerrar_formulario).pack(side="left", expand=True, fill="x", padx=(0, 10))
        ctk.CTkButton(btns, text="💾 Guardar", font=self.font_sub, fg_color="#D1FAE5", text_color=COLORS["text"], height=50, command=self.validar_y_guardar).pack(side="left", expand=True, fill="x", padx=(10, 0))
        

    def create_section_card(self, master, title, fields):
        card = ctk.CTkFrame(master, fg_color=COLORS["card"], corner_radius=12, border_width=1, border_color=COLORS["border"]); card.pack(fill="x", padx=60, pady=10)
        ctk.CTkLabel(card, text=title, font=self.font_sub, text_color=COLORS["text"]).pack(anchor="w", padx=20, pady=(15, 5))
        grid = ctk.CTkFrame(card, fg_color="transparent"); grid.pack(fill="x", padx=20, pady=(0, 20))
        for label, val in fields:
            f = ctk.CTkFrame(grid, fg_color="transparent"); f.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(f, text=label, font=self.font_small, text_color=COLORS["subtext"]).pack(anchor="w")
            entry = ctk.CTkEntry(f, height=40, font=self.font_normal, fg_color=COLORS["hover"]
, border_width=0, text_color=COLORS["text"])
            entry.insert(0, val); entry.pack(fill="x", pady=5)
            if "Apellido" in label: self.inputs_apellidos[label] = entry
            else: self.inputs_obligatorios[label] = entry

    def validar_y_guardar(self):
        if not self.usuario_editando_id:
            if not hasattr(self, "biometria_temp") or self.biometria_temp is None:
                print("❌ Debes registrar biometría primero")

                self.btn_biometria.configure(
                    text="❌ Biometría requerida",
                    fg_color="#EF4444",
                    hover_color="#DC2626"
                )
                return

        try:
            n = self.inputs_obligatorios.get("Nombres").get().strip()
            em = self.inputs_obligatorios.get("correo").get().strip()
            id_usuario = self.usuario_editando_id
            cta = self.inputs_obligatorios.get("cuenta").get().strip()
            if not n or not cta:
                print("❌ Faltan datos:", n, cta, em)
                return

            if em and "@" not in em: 
                self.inputs_obligatorios["correo"].configure(border_color=COLORS["border"])
                print("❌ Correo inválido:", em)
                return

            if not self.usuario_editando_id and len(cta) != 8:
                self.inputs_obligatorios["cuenta"].configure(border_color=COLORS["border"])
                return

            ap = self.inputs_apellidos["Apellido Paterno"].get().strip()
            am = self.inputs_apellidos["Apellido Materno"].get().strip()

            # 🔥 AQUÍ ESTABA EL ERROR
            tipo_texto = self.rol_var.get()

            TIPOS_USUARIO_INV = {
            "ESTUDIANTE": 1,
            "DOCENTE": 2,
            "TRABAJADOR": 3
            }

            tipo_usuario = TIPOS_USUARIO_INV.get(tipo_texto.upper())

            id_fac = obtener_id_facultad_por_nombre(self.plantel_menu.get())

            if not tipo_usuario or not id_fac:
                print("Error: tipo_usuario o id_fac inválido", tipo_usuario, id_fac)
                return

            if self.usuario_editando_id:

               actualizar_usuario(id_usuario, n, ap, am, cta, tipo_usuario, id_fac, em)

             # 🔥 SI TOMÓ NUEVA BIOMETRÍA → reemplazar
               if hasattr(self, "biometria_temp") and self.biometria_temp is not None:

                  print("♻️ Reemplazando biometría...")

                  eliminar_encoding(id_usuario)  # borrar viejo
                  guardar_encoding(id_usuario, self.biometria_temp)  # guardar nuevo

                  encodings_db[:], usuarios_db[:] = cargar_encodings()

                  self.biometria_temp = None
                  
            else:
                usuario_id = crear_usuario(n, ap, am, tipo_usuario, id_fac, None, cta, em)

                print("DEBUG usuario_id:", usuario_id)
                print("DEBUG biometria:", self.biometria_temp)

                try:
                    guardado = guardar_encoding(usuario_id, encoding=self.biometria_temp)

                    if not guardado:
                        print("❌ No se guardó porque es duplicado")
                        return

                    print("✔ Encoding guardado en BD")
                
                except Exception as e:
                    print("ERROR al guardar encoding:", e)

                encodings_db[:], usuarios_db[:] = cargar_encodings()

                self.biometria_temp = None

            self.refresh_data()
            self.render_table_content(self.all_users)
            self.cerrar_formulario()

        except Exception as e:
            print("ERROR AL GUARDAR:", e)

    def create_header(self, master):
        h = ctk.CTkFrame(master, fg_color="transparent"); h.pack(fill="x", padx=30, pady=(20, 10))
        ctk.CTkLabel(h, text="👥 Gestión de Usuarios", font=self.font_header, text_color=COLORS["text"]).pack(side="left")
        ctk.CTkButton(h, text="➕ Agregar Usuario", font=self.font_sub, fg_color="#000000", height=45, corner_radius=10, command=self.abrir_formulario).pack(side="right")

    def create_search_bar(self, master):
        bar = ctk.CTkFrame(master, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=10)
        self.entry_busqueda = ctk.CTkEntry(bar, placeholder_text="🔍 Buscar usuario...", height=42, corner_radius=10, fg_color=COLORS["hover"]
, border_color=COLORS["border"], text_color=COLORS["text"])
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.btn_filter = ctk.CTkButton(bar, text="⚙️ Filtrar ⌵", width=110, height=42, corner_radius=10, fg_color=COLORS["card"], text_color=COLORS["text"], border_color=COLORS["border"], command=self.toggle_filter)
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
        ctk.CTkLabel(r1, text="👤 Rol:", font=self.font_small, text_color=COLORS["text"], width=80).pack(side="left")
        for t in ["Todos", "ESTUDIANTE", "DOCENTE", "AUXILIAR"]:
            act = self.filtro_rol_actual == t
            ctk.CTkButton(r1, text=t, height=28, corner_radius=10, fg_color=COLORS["hover"]
        if act else "white", text_color=COLORS["text"], border_color=COLORS["border"], command=lambda v=t: self.aplicar_filtro_visual(v)).pack(side="left", padx=3)

    def aplicar_filtro_visual(self, v):
        self.filtro_rol_actual = v
        self.draw_tags()

    def update_carreras_dinamicas(self, fn):
        c = self.carreras_por_plantel.get(fn, ["Sin Carreras"])
        self.carrera_menu.configure(values=c); self.carrera_var.set(c[0])

    def ejecutar_eliminacion(self, id_cuenta):
        # 1. Overlay Transparente (eliminamos el color azul oscuro)
        self.overlay = ctk.CTkFrame(self, fg_color="transparent") 
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 2. Caja del Modal (la ventanita blanca)
        # Añadimos borde más fuerte para que resalte sobre el fondo blanco
        modal = ctk.CTkFrame(self.overlay, fg_color=COLORS["card"], corner_radius=20, width=420, height=240, border_width=2, border_color="#CBD5E1")
        modal.place(relx=0.5, rely=0.5, anchor="center")
        modal.pack_propagate(False)

        ctk.CTkLabel(modal, text="🗑️", font=("Inter", 45)).pack(pady=(25, 5))
        ctk.CTkLabel(modal, text="¿Está seguro de eliminar al usuario?", font=("Inter", 16, "bold"), text_color=COLORS["text"]).pack()
        ctk.CTkLabel(modal, text="Esta acción desactivará al usuario permanentemente.", font=("Inter", 12), text_color=COLORS["subtext"]).pack(pady=5)
        
        # 3. Botones (Verde para confirmar, Rojo para cancelar)
        btns = ctk.CTkFrame(modal, fg_color="transparent")
        btns.pack(fill="x", side="bottom", pady=25, padx=30)
        
        # CANCELAR - Rojo
        ctk.CTkButton(btns, text="Cancelar", fg_color="#EF4444", text_color="white", hover_color="#DC2626", height=40, font=("Inter", 13, "bold"), command=self.cerrar_modal).pack(side="left", expand=True, padx=(0, 10))
        
        # CONFIRMAR - Verde
        ctk.CTkButton(btns, text="Confirmar y Borrar", fg_color="#10B981", text_color="white", hover_color="#059669", height=40, font=("Inter", 13, "bold"), command=lambda: self.confirmar_borrado(id_cuenta)).pack(side="left", expand=True)

    def cerrar_modal(self):
        if hasattr(self, 'overlay'): self.overlay.destroy()

    def confirmar_borrado(self, id_cuenta):
        if desactivar_usuario(id_cuenta): 
            self.refresh_data()
            self.render_table_content(self.all_users)
        self.cerrar_modal()

    def cerrar_formulario(self):
        if hasattr(self, 'form_base'): self.form_base.destroy()
        self.vista_tabla.pack(fill="both", expand=True)
        self.render_table_content(self.all_users)

    def abrir_terminal_biometrica(self):
    # NO validar ID aquí ❌

        self.form_base.pack_forget()

        self.terminal_container = ctk.CTkFrame(self, fg_color="black")
        self.terminal_container.pack(fill="both", expand=True)

        self.terminal_view = TerminalView(
        self.terminal_container,
        user_id=None,  # 🔥 aún no existe
        on_back=self.cerrar_terminal_biometrica,
        on_capture=self.recibir_biometria,
        modo="registro"   # 👈 ESTO ES CLAVE
        )
    
        self.terminal_view.pack(fill="both", expand=True)


    def cerrar_terminal_biometrica(self):
        if hasattr(self, "terminal_view"):
            try:
                self.terminal_view.on_close()
            except:
                pass

            if hasattr(self, "terminal_container"):
                self.terminal_container.destroy()
               
            self.form_base.pack(fill="both", expand=True)

    def recibir_biometria(self, encoding):
    
        print("✔ Captura recibida")

        self.biometria_temp = encoding

    # 🔥 CAMBIO VISUAL DEL BOTÓN
        if hasattr(self, "btn_biometria"):
            self.btn_biometria.configure(
                text="✔ Biometría registrada",
                fg_color="#10B981",   # verde
                hover_color="#059669"
            )
        self.cerrar_terminal_biometrica()