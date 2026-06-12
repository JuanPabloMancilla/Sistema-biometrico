import customtkinter as ctk
from datetime import date
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry

from app.services.asistencia_service import (
    corregir_jornada,
    guardar_configuracion_asistencia,
    obtener_configuracion_asistencia,
    obtener_ultima_jornada_usuario,
)
from app.services.reporte_asistencia_service import (
    exportar_reporte_csv,
    obtener_reporte_asistencia,
)
from app.services.theme import COLORS
from app.views.app_context import AppContext


class AttendanceReportView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.reporte = []
        self._construir()
        self.actualizar_reporte()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(14, 8))
        ctk.CTkLabel(
            header, text=AppContext.t("Reportes de asistencia"),
            font=("Inter", 26, "bold"), text_color=COLORS["text"],
        ).pack(side="left")

        filtros = ctk.CTkFrame(
            self, fg_color=COLORS["card"], corner_radius=8,
            border_width=1, border_color=COLORS["border"],
        )
        filtros.pack(fill="x", padx=18, pady=(0, 10))

        hoy = date.today()
        ctk.CTkLabel(filtros, text=AppContext.t("Desde"), text_color=COLORS["subtext"]).pack(side="left", padx=(14, 5), pady=12)
        self.fecha_inicio = DateEntry(filtros, date_pattern="yyyy-mm-dd", year=hoy.year, month=hoy.month, day=1)
        self.fecha_inicio.pack(side="left", padx=5, pady=12)
        ctk.CTkLabel(filtros, text=AppContext.t("Hasta"), text_color=COLORS["subtext"]).pack(side="left", padx=(12, 5), pady=12)
        self.fecha_fin = DateEntry(filtros, date_pattern="yyyy-mm-dd")
        self.fecha_fin.pack(side="left", padx=5, pady=12)

        ctk.CTkButton(
            filtros, text=AppContext.t("Consultar"), command=self.actualizar_reporte,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"], width=105,
        ).pack(side="left", padx=12, pady=10)
        ctk.CTkButton(
            filtros, text=AppContext.t("Exportar CSV"), command=self.exportar_csv,
            fg_color=COLORS["info"], hover_color="#1D4ED8", width=120,
        ).pack(side="right", padx=14, pady=10)
        ctk.CTkButton(
            filtros, text=AppContext.t("Configurar horario"), command=self.configurar_horario,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#111827", width=135,
        ).pack(side="right", padx=4, pady=10)

        self.resumen = ctk.CTkLabel(self, text="", font=("Inter", 13, "bold"), text_color=COLORS["subtext"])
        self.resumen.pack(anchor="w", padx=20, pady=(0, 6))
        self.contenedor = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.contenedor.pack(fill="both", expand=True, padx=18, pady=(0, 18))

    def actualizar_reporte(self):
        inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
        fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
        self.reporte = obtener_reporte_asistencia(inicio, fin)
        self._renderizar()

    def _renderizar(self):
        for widget in self.contenedor.winfo_children():
            widget.destroy()

        total_segundos = sum(fila["segundos_trabajados"] for fila in self.reporte)
        trabajando = sum(1 for fila in self.reporte if fila["estado"] == "Trabajando")
        self.resumen.configure(text=f"{len(self.reporte)} trabajadores  |  {total_segundos / 3600:.1f} horas netas  |  {trabajando} trabajando")

        if not self.reporte:
            ctk.CTkLabel(
                self.contenedor, text=AppContext.t("Sin jornadas registradas en este periodo"),
                font=("Inter", 14), text_color=COLORS["subtext"],
            ).pack(pady=40)
            return

        for fila in self.reporte:
            card = ctk.CTkFrame(
                self.contenedor, fg_color=COLORS["card"], corner_radius=8,
                border_width=1, border_color=COLORS["border"],
            )
            card.pack(fill="x", pady=5)
            arriba = ctk.CTkFrame(card, fg_color="transparent")
            arriba.pack(fill="x", padx=14, pady=(11, 4))
            ctk.CTkLabel(arriba, text=fila["nombre"].upper(), font=("Inter", 13, "bold"), text_color=COLORS["text"]).pack(side="left")
            color = "#D1FAE5" if fila["estado"] == "Trabajando" else "#E2E8F0"
            texto = "#065F46" if fila["estado"] == "Trabajando" else "#475569"
            ctk.CTkLabel(
                arriba, text=fila["estado"].upper(), fg_color=color, text_color=texto,
                corner_radius=12, font=("Inter", 9, "bold"),
            ).pack(side="right", padx=4, ipadx=8, ipady=3)
            detalle = (
                f"Cuenta: {fila['cuenta'] or '-'}  |  Jornadas: {fila['jornadas']}  |  "
                f"Tiempo neto: {fila['tiempo_trabajado']}  |  Retardo: {fila['retardo']}  |  Extra: {fila['horas_extra']}\n"
                f"Primera entrada: {fila['primera_entrada'] or '-'}  |  Ultima salida: {fila['ultima_salida'] or '-'}"
            )
            ctk.CTkLabel(card, text=detalle, font=("Inter", 11), text_color=COLORS["subtext"], justify="left", anchor="w").pack(fill="x", padx=14, pady=(0, 5))
            ctk.CTkButton(
                card, text=AppContext.t("Corregir ultimo marcaje"),
                command=lambda usuario=fila: self.corregir_ultimo_marcaje(usuario),
                fg_color="transparent", border_width=1, border_color=COLORS["border"],
                text_color=COLORS["primary"], hover_color=COLORS["hover"], height=28,
            ).pack(anchor="e", padx=14, pady=(0, 10))

    def exportar_csv(self):
        if not self.reporte:
            return
        ruta = filedialog.asksaveasfilename(
            title=AppContext.t("Exportar reporte"), defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"reporte_asistencia_{self.fecha_inicio.get()}_{self.fecha_fin.get()}.csv",
        )
        if ruta:
            exportar_reporte_csv(ruta, self.reporte)

    def _crear_modal(self, titulo):
        modal = ctk.CTkToplevel(self)
        modal.title(titulo)
        modal.geometry("440x430")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()
        cuerpo = ctk.CTkFrame(modal, fg_color=COLORS["card"])
        cuerpo.pack(fill="both", expand=True, padx=14, pady=14)
        ctk.CTkLabel(cuerpo, text=titulo, font=("Inter", 20, "bold"), text_color=COLORS["text"]).pack(anchor="w", padx=16, pady=(16, 12))
        return modal, cuerpo

    @staticmethod
    def _campo(parent, etiqueta, valor):
        ctk.CTkLabel(parent, text=etiqueta, text_color=COLORS["subtext"]).pack(anchor="w", padx=16)
        entrada = ctk.CTkEntry(parent)
        entrada.insert(0, str(valor))
        entrada.pack(fill="x", padx=16, pady=(3, 9))
        return entrada

    def configurar_horario(self):
        config = obtener_configuracion_asistencia()
        modal, cuerpo = self._crear_modal(AppContext.t("Configurar horario"))
        hora = self._campo(cuerpo, AppContext.t("Hora de entrada (HH:MM)"), config["hora_entrada"])
        tolerancia = self._campo(cuerpo, AppContext.t("Tolerancia (minutos)"), config["tolerancia_minutos"])
        objetivo = self._campo(cuerpo, AppContext.t("Jornada objetivo (minutos)"), config["jornada_objetivo_minutos"])
        descanso = self._campo(cuerpo, AppContext.t("Descanso fijo (minutos)"), config["descanso_minutos"])

        def guardar():
            try:
                guardar_configuracion_asistencia(hora.get(), tolerancia.get(), objetivo.get(), descanso.get())
                modal.destroy()
                self.actualizar_reporte()
            except Exception as error:
                messagebox.showerror(AppContext.t("Error"), str(error), parent=modal)

        ctk.CTkButton(cuerpo, text=AppContext.t("Guardar"), command=guardar, fg_color=COLORS["primary"]).pack(pady=8)

    def corregir_ultimo_marcaje(self, usuario):
        inicio = self.fecha_inicio.get_date().strftime("%Y-%m-%d")
        fin = self.fecha_fin.get_date().strftime("%Y-%m-%d")
        jornada = obtener_ultima_jornada_usuario(usuario["id_usuario"], inicio, fin)
        if not jornada:
            return
        id_jornada, fecha_entrada, fecha_salida, _ = jornada
        modal, cuerpo = self._crear_modal(AppContext.t("Corregir ultimo marcaje"))
        entrada = self._campo(cuerpo, AppContext.t("Entrada (AAAA-MM-DD HH:MM:SS)"), fecha_entrada)
        salida = self._campo(cuerpo, AppContext.t("Salida (vacia si sigue trabajando)"), fecha_salida or "")

        def guardar():
            try:
                corregir_jornada(id_jornada, entrada.get().strip(), salida.get().strip() or None)
                modal.destroy()
                self.actualizar_reporte()
            except Exception as error:
                messagebox.showerror(AppContext.t("Error"), str(error), parent=modal)

        ctk.CTkButton(cuerpo, text=AppContext.t("Guardar correccion"), command=guardar, fg_color=COLORS["primary"]).pack(pady=10)
