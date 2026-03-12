import customtkinter as ctk
from app.services.registro_acceso_service import obtener_registros_acceso


class RegistroAccesoManagementView(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="#F8FAFC")

        self.crear_vista_tabla()


    def crear_vista_tabla(self):

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=(40,20))

        title_cont = ctk.CTkFrame(header, fg_color="transparent")
        title_cont.pack(side="left")

        ctk.CTkLabel(
            title_cont,
            text="Registro de Accesos",
            font=("Inter",28,"bold"),
            text_color="#1E293B"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_cont,
            text="Historial de accesos al sistema biométrico",
            font=("Inter",15),
            text_color="#64748B"
        ).pack(anchor="w")


        self.tabla_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=15,
            border_width=1,
            border_color="#E2E8F0"
        )
        self.tabla_frame.pack(fill="both", expand=True, padx=40, pady=(0,40))

        self.actualizar_tabla()


    def actualizar_tabla(self):

        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        registros = obtener_registros_acceso()

        header_frame = ctk.CTkFrame(self.tabla_frame, fg_color="#F1F5F9")
        header_frame.pack(fill="x", padx=20, pady=(20,10))

        ctk.CTkLabel(header_frame,text="ID",width=50).pack(side="left", padx=5)
        ctk.CTkLabel(header_frame,text="Usuario").pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(header_frame,text="Fecha / Hora").pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(header_frame,text="Resultado",width=100).pack(side="left")

        if not registros:
            ctk.CTkLabel(
                self.tabla_frame,
                text="No hay registros de acceso",
                font=("Inter",14)
            ).pack(pady=40)
            return

        for registro in registros:

            fila = ctk.CTkFrame(
                self.tabla_frame,
                fg_color="white",
                border_width=1,
                border_color="#E2E8F0",
                corner_radius=8
            )
            fila.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(fila,text=str(registro["id"]),width=50).pack(side="left", padx=5)
            ctk.CTkLabel(fila,text=str(registro["id_usuario"])).pack(side="left", expand=True, fill="x")
            ctk.CTkLabel(fila,text=str(registro["fecha_hora"])).pack(side="left", expand=True, fill="x")

            resultado = "Permitido" if registro["resultado"] == 1 else "Denegado"
            color = "#10B981" if registro["resultado"] == 1 else "#EF4444"

            ctk.CTkLabel(
                fila,
                text=resultado,
                text_color=color
            ).pack(side="left", padx=5)