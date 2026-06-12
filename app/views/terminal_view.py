import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image
import time
from app.hardware import buzzer
from app.recognition.encoding_manager import cargar_encodings
from app.detection.detector_rostro import (
    find_best_match,
    reiniciar_cache_deteccion,
    UMBRAL_ACCESO,
)
from app.views.app_context import AppContext
from app.camara.camara import iniciar_camara, liberar_camara, obtener_frame
from app.detection.detector_rostro import procesar_frame
from app.services.usuario_service import usuario_activo
from app.services.asistencia_service import registrar_marcaje
from app.services.liveness_service import DetectorParpadeo
from app.database.database import get_connection
from datetime import datetime
from app.hardware.cerradura import Cerradura


# -- Paleta --------------------------------------------------------------------
BG_DEEP        = "#080B12"
BG_PANEL       = "#0F172A"
BG_BANNER      = "#111827"
BORDER_IDLE    = "#273449"
ACCENT_PURPLE  = "#F59E0B"
ACCENT_GREEN   = "#0F766E"
ACCENT_RED     = "#DC2626"
ACCENT_AMBER   = "#F59E0B"
ACCENT_CYAN    = "#2563EB"
TEXT_PRIMARY   = "#F8FAFC"
TEXT_SECONDARY = "#CBD5E1"
TEXT_MUTED     = "#94A3B8"

BANNER_H = 76
SCAN_DURATION = 3.0
MUESTRAS_BIOMETRICAS = 3

TEMAS = {
    "escaneando": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "ESCANEANDO",
        "st_color": ACCENT_AMBER,
        "name":     "ANALIZANDO RASGOS BIOMETRICOS",
        "b_color":  ACCENT_AMBER,
    },
    "parpadeo": {
        "border":   ACCENT_CYAN,
        "bar":      ACCENT_CYAN,
        "banner":   "#10213F",
        "dot":      ACCENT_CYAN,
        "status":   "PRUEBA DE VIDA",
        "st_color": ACCENT_CYAN,
        "name":     "PARPADEE UNA VEZ",
        "b_color":  ACCENT_CYAN,
    },
    "autorizado": {
        "border":   ACCENT_GREEN,
        "bar":      ACCENT_GREEN,
        "banner":   "#0F2E2B",
        "dot":      ACCENT_GREEN,
        "status":   "ACCESO AUTORIZADO",
        "st_color": ACCENT_GREEN,
        "name":     "",
        "b_color":  ACCENT_GREEN,
    },
    "entrada": {
        "border":   ACCENT_GREEN,
        "bar":      ACCENT_GREEN,
        "banner":   "#0F2E2B",
        "dot":      ACCENT_GREEN,
        "status":   "BIENVENIDO",
        "st_color": ACCENT_GREEN,
        "name":     "",
        "b_color":  ACCENT_GREEN,
    },
    "salida": {
        "border":   ACCENT_CYAN,
        "bar":      ACCENT_CYAN,
        "banner":   "#10213F",
        "dot":      ACCENT_CYAN,
        "status":   "QUE LE VAYA BIEN",
        "st_color": ACCENT_CYAN,
        "name":     "",
        "b_color":  ACCENT_CYAN,
    },
    "negado": {
        "border":   ACCENT_RED,
        "bar":      ACCENT_RED,
        "banner":   "#33131B",
        "dot":      ACCENT_RED,
        "status":   "ACCESO DENEGADO",
        "st_color": ACCENT_RED,
        "name":     "USUARIO NO REGISTRADO",
        "b_color":  ACCENT_RED,
    },
    "inactivo": {
        "border":   ACCENT_RED,
        "bar":      ACCENT_RED,
        "banner":   "#33131B",
        "dot":      ACCENT_RED,
        "status":   "USUARIO INACTIVO",
        "st_color": ACCENT_RED,
        "name":     "",
        "b_color":  ACCENT_RED,
    },
    "multiples": {
        "border":   ACCENT_CYAN,
        "bar":      ACCENT_CYAN,
        "banner":   "#10213F",
        "dot":      ACCENT_CYAN,
        "status":   "MULTIPLES ROSTROS DETECTADOS",
        "st_color": ACCENT_CYAN,
        "name":     "SOLO UN USUARIO A LA VEZ",
        "b_color":  ACCENT_CYAN,
    },
    "sin_camara": {
        "border":   ACCENT_RED,
        "bar":      ACCENT_RED,
        "banner":   "#33131B",
        "dot":      ACCENT_RED,
        "status":   "SIN CAMARA",
        "st_color": ACCENT_RED,
        "name":     "NO SE DETECTO NINGUN DISPOSITIVO",
        "b_color":  ACCENT_RED,
    },
    "acercarse": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "ACERQUESE A LA CAMARA",
        "st_color": ACCENT_AMBER,
        "name":     "ROSTRO DEMASIADO LEJOS O PEQUENO",
        "b_color":  ACCENT_AMBER,
    },
    "iluminacion": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "MEJORE LA ILUMINACION",
        "st_color": ACCENT_AMBER,
        "name":     "AMBIENTE MUY OSCURO - ENCIENDA UNA LUZ",
        "b_color":  ACCENT_AMBER,
    },
    "centrar": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "CENTRE SU ROSTRO",
        "st_color": ACCENT_AMBER,
        "name":     "MANTENGA LA CARA DENTRO DEL MARCO",
        "b_color":  ACCENT_AMBER,
    },
    "frente": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "MIRE AL FRENTE",
        "st_color": ACCENT_AMBER,
        "name":     "EVITE GIRAR LA CARA A LOS LADOS",
        "b_color":  ACCENT_AMBER,
    },
    "enderezar": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "ENDERECE SU ROSTRO",
        "st_color": ACCENT_AMBER,
        "name":     "MANTENGA LOS OJOS NIVELADOS",
        "b_color":  ACCENT_AMBER,
    },
    "alejarse": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#29210F",
        "dot":      ACCENT_AMBER,
        "status":   "ALEJESE UN POCO",
        "st_color": ACCENT_AMBER,
        "name":     "EL ROSTRO ESTA DEMASIADO CERCA",
        "b_color":  ACCENT_AMBER,
    },
    "vacio": {
        "border":   BORDER_IDLE,
        "bar":      ACCENT_PURPLE,
        "banner":   BG_BANNER,
        "dot":      ACCENT_PURPLE,
        "status":   "POSICIONE SU ROSTRO",
        "st_color": TEXT_PRIMARY,
        "name":     "MIRANDO HACIA LA CAMARA",
        "b_color":  ACCENT_PURPLE,
    },
}

class TerminalView(ctk.CTkFrame):
    def __init__(self, master, user_id=None, on_back=None, on_capture=None, modo="acceso"):
        super().__init__(master, fg_color=BG_DEEP)
        self.on_back = on_back
        self.on_capture = on_capture
        self.modo = modo
        self.user_id = user_id
        self.cap = None
        self.loop_id = None
        self.estado_actual = None
        self.running = True
        self.cerradura = None

        if self.modo != "registro":
            self.cerradura = Cerradura()

        self.escaneando = False
        self.inicio_escaneo = 0.0
        self.pos_linea = 0
        self.subiendo = False
        self.usuario_detectado = ""
        self.ids_detectados_escaneo = []
        self.detector_parpadeo = DetectorParpadeo()
        self.muestras_registro = []
        self.ultimo_rostro_visto = 0.0
        self.face_box = None
        self._haar_frame_count = 0
        self._last_faces = []
        self.esperando_reset = False
        self.requiere_retirar_rostro = False
        self.inicio_espera_reset = 0.0
        self.encodings_conocidos, self.ids_conocidos = cargar_encodings()

        self._pending_style = None
        self.compact_ui = (
            self.winfo_screenwidth() < 1100 or self.winfo_screenheight() < 700
        )

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self._build_ui()
        self.iniciar_sistema()

    def _build_ui(self):
        ctk.CTkFrame(self, fg_color=ACCENT_GREEN, height=3).pack(fill="x", side="top")

        if self.modo != "registro":
            self.btn_panel_compacto = ctk.CTkButton(
                self,
                text=AppContext.t("Panel"),
                width=92,
                height=34,
                corner_radius=8,
                fg_color=ACCENT_GREEN,
                hover_color="#0B5F59",
                text_color="#FFFFFF",
                font=("Inter", 12, "bold"),
                command=self.cerrar_y_volver,
            )
            self.btn_panel_compacto.place(relx=1.0, y=12, x=-16, anchor="ne")

        main = ctk.CTkFrame(self, fg_color="transparent")
        page_pad = 7 if self.compact_ui else 14
        main.pack(expand=True, fill="both", padx=page_pad, pady=(page_pad, page_pad))

        # -- Panel lateral -----------------------------------------------------
        self.data_banner = ctk.CTkFrame(
            main,
            fg_color=BG_BANNER,
            corner_radius=8,
            width=220 if self.compact_ui else 292,
            border_width=1,
            border_color=BORDER_IDLE,
        )
        self.data_banner.pack(side="left", fill="y", padx=(0, 7 if self.compact_ui else 12))
        self.data_banner.pack_propagate(False)

        self.accent_bar = ctk.CTkFrame(
            self.data_banner, fg_color=ACCENT_PURPLE, width=5, corner_radius=0
        )
        self.accent_bar.pack(side="left", fill="y")

        side = ctk.CTkFrame(self.data_banner, fg_color="transparent")
        side.pack(
            side="left", fill="both", expand=True,
            padx=12 if self.compact_ui else 20,
            pady=10 if self.compact_ui else 20,
        )

        ctk.CTkLabel(
            side,
            text="SECUREWORK",
            font=("Inter", 18 if self.compact_ui else 24, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w")

        ctk.CTkLabel(
            side,
            text=AppContext.t("CONTROL DE ACCESO"),
            font=("Inter", 11, "bold"),
            text_color=TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, 10))

        if self.modo != "registro":
            self.btn_panel = ctk.CTkButton(
                side,
                text=AppContext.t("Entrar al panel de control"),
                height=38,
                corner_radius=8,
                fg_color=ACCENT_GREEN,
                hover_color="#0B5F59",
                text_color="#FFFFFF",
                font=("Inter", 12, "bold"),
                command=self.cerrar_y_volver,
            )
            self.btn_panel.pack(fill="x", pady=(0, 12 if self.compact_ui else 18))

        ctk.CTkLabel(
            side,
            text=AppContext.t("ESTADO ACTUAL"),
            font=("Inter", 10, "bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        row = ctk.CTkFrame(side, fg_color="transparent")
        row.pack(fill="x", pady=(8, 4))

        self.dot_indicator = ctk.CTkLabel(
            row, text="●", font=("Segoe UI Symbol", 15), text_color=ACCENT_PURPLE
        )
        self.dot_indicator.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            row,
            text=AppContext.t("SISTEMA ACTIVO"),
            font=("Inter", 14 if self.compact_ui else 18, "bold"),
            text_color=TEXT_PRIMARY,
            wraplength=170 if self.compact_ui else 220,
            justify="left",
        )
        self.status_label.pack(side="left")

        ctk.CTkFrame(side, fg_color=BORDER_IDLE, height=1).pack(fill="x", pady=(14, 16))

        self.lbl_nombre = ctk.CTkLabel(
            side,
            text=AppContext.t("ESPERANDO DETECCION..."),
            font=("Inter", 13),
            text_color=TEXT_SECONDARY,
            anchor="w",
            wraplength=175 if self.compact_ui else 230,
            justify="left",
        )
        self.lbl_nombre.pack(fill="x", anchor="w")

        if not self.compact_ui:
            ctk.CTkFrame(side, fg_color=BORDER_IDLE, height=1).pack(fill="x", pady=(22, 16))
            ctk.CTkLabel(
                side,
                text=AppContext.t("GUIA RAPIDA"),
                font=("Inter", 10, "bold"),
                text_color=TEXT_MUTED,
            ).pack(anchor="w")

            for texto in [
                AppContext.t("Mantenga una sola cara visible"),
                AppContext.t("Mire de frente a la camara"),
                AppContext.t("Evite sombras sobre el rostro"),
            ]:
                ctk.CTkLabel(
                    side,
                    text=texto,
                    font=("Inter", 11),
                    text_color=TEXT_SECONDARY,
                    wraplength=230,
                    justify="left",
                ).pack(anchor="w", pady=(8, 0))

        ctk.CTkFrame(side, fg_color="transparent").pack(fill="both", expand=True)

        if self.modo == "registro":
            self.btn_salir = ctk.CTkButton(
                side,
                text=AppContext.t("Cerrar"),
                height=38 if self.compact_ui else 44,
                corner_radius=8,
                fg_color=ACCENT_RED,
                hover_color="#7F1D1D",
                text_color="#FFFFFF",
                font=("Inter", 13, "bold"),
                command=self.cerrar_y_volver,
            )
            self.btn_salir.pack(fill="x", side="bottom", pady=(16, 0))

        self.accent_line = ctk.CTkFrame(
            self.data_banner, fg_color=ACCENT_PURPLE, height=2, corner_radius=0
        )
        self.accent_line.pack(side="bottom", fill="x")

        # -- Area de video -----------------------------------------------------
        self.video_container = ctk.CTkFrame(
            main, fg_color=BG_PANEL, corner_radius=8,
            border_width=1, border_color=BORDER_IDLE,
        )
        self.video_container.pack(side="left", expand=True, fill="both")

        # -- Area de video -----------------------------------------------------
        self.video_display = ctk.CTkLabel(
            self.video_container,
            text=AppContext.t("Iniciando camara..."),
            text_color=TEXT_MUTED,
            font=("Inter", 12),
        )
        self.video_display.pack(fill="both", expand=True)

        # Footer
        if not self.compact_ui:
            ctk.CTkLabel(
                self,
                text=(
                    AppContext.t("Sistema Biometrico v2.0") + "  //  " +
                    AppContext.t("Acceso Seguro") + "  //  " +
                    AppContext.t("Cifrado AES-256")
                ),
                font=("Inter", 9),
                text_color=TEXT_MUTED,
            ).pack(side="bottom", pady=(0, 4))
            ctk.CTkFrame(self, fg_color=BORDER_IDLE, height=1).pack(fill="x", side="bottom")

    def aplicar_estilo_visual(self, estado: str, usuario: str = ""):
        self._pending_style = (estado, usuario)

    def _flush_pending_style(self):
        if self._pending_style is None:
            return
        estado, usuario = self._pending_style
        self._pending_style = None

        self.estado_actual = estado
        t = TEMAS.get(estado, TEMAS["vacio"])

        nombre = AppContext.t(t["name"])
        if estado == "autorizado":
            nombre = f"{AppContext.t('BIENVENIDO')}:  {usuario}" if usuario else AppContext.t("ACCESO CONCEDIDO")
        elif estado == "entrada":
            nombre = f"{usuario}\nESTADO: TRABAJANDO" if usuario else "ESTADO: TRABAJANDO"
        elif estado == "salida":
            nombre = usuario
        elif estado == "inactivo":
            nombre = f"{usuario}\n{AppContext.t('USUARIO INACTIVO')}" if usuario else AppContext.t("USUARIO INACTIVO")

        self.video_container.configure(border_color=t["border"])
        self.data_banner.configure(fg_color=t["banner"])
        self.accent_bar.configure(fg_color=t["bar"])
        self.accent_line.configure(fg_color=t["bar"])
        self.dot_indicator.configure(text_color=t["dot"])
        self.status_label.configure(text=AppContext.t(t["status"]), text_color=t["st_color"])
        self.lbl_nombre.configure(text=nombre, text_color=t["b_color"])

        # Override texts in registro mode only when the face posture is already usable.
        estados_guia = {"centrar", "frente", "enderezar", "acercarse", "alejarse", "iluminacion"}
        if self.modo == "registro" and estado not in estados_guia and estado != "negado":
            self.status_label.configure(
                text=AppContext.t("REGISTRANDO BIOMETRIA"),
                text_color=ACCENT_AMBER
            )
            self.lbl_nombre.configure(
                text=AppContext.t("COLOQUE SU ROSTRO FRENTE A LA CAMARA"),
                text_color=ACCENT_AMBER
            )

    def detectar_rostros(self, frame):
        self._haar_frame_count += 1
        if self._haar_frame_count % 5 != 0:
            return self._last_faces

        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.25, 4)
        self._last_faces = [
            (int(x * 2), int(y * 2), int(w * 2), int(h * 2))
            for (x, y, w, h) in faces
        ]
        return self._last_faces

    def _rostro_principal(self, faces):
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
        pad = 40
        return (max(0, x - pad), max(0, y - pad), w + pad * 2, h + pad * 2)

    def _estado_postura_desde_mensaje(self, mensaje):
        msg = str(mensaje or "").upper()
        if "CENTRE" in msg:
            return "centrar"
        if "MIRE AL FRENTE" in msg:
            return "frente"
        if "ENDERECE" in msg:
            return "enderezar"
        if "ACERQUESE" in msg:
            return "acercarse"
        if "ALEJESE" in msg:
            return "alejarse"
        if "ILUMINACION" in msg:
            return "iluminacion"
        return None

    # --------------------------------------------------------------------------
    # Dibujo sobre frame
    # --------------------------------------------------------------------------

    @staticmethod
    def _hex_to_bgr(hex_color):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (b, g, r)

    def _dibujar_esquinas(self, frame, fx, fy, fw, fh, color_hex, grosor=3, longitud=48):
        c = self._hex_to_bgr(color_hex)
        x1, y1, x2, y2 = fx, fy, fx + fw, fy + fh
        L = longitud
        for sx, sy, dx, dy in [
            (x1, y1,  1,  1), (x2, y1, -1,  1),
            (x1, y2,  1, -1), (x2, y2, -1, -1),
        ]:
            cv2.line(frame, (sx, sy), (sx + dx * L, sy), c, grosor)
            cv2.line(frame, (sx, sy), (sx, sy + dy * L), c, grosor)

    def _dibujar_linea_escaneo(self, frame, fx, fy, fw, fh, color_hex):
        self.pos_linea += 10 if not self.subiendo else -10
        if self.pos_linea >= fh - 10:
            self.subiendo = True
        if self.pos_linea <= 10:
            self.subiendo = False
        y = int(fy + self.pos_linea)
        c = self._hex_to_bgr(color_hex)
        cv2.line(frame, (fx, y),     (fx + fw, y),     c, 3)
        cv2.line(frame, (fx, y - 1), (fx + fw, y - 1), c, 1)
        cv2.line(frame, (fx, y + 1), (fx + fw, y + 1), c, 1)

    @staticmethod
    def _calidad_captura(brillo, area_relativa):
        brillo_score = max(0, 100 - abs(brillo - 125) * 0.8)
        area_score = min(100, max(0, area_relativa / 0.18 * 100))
        return int((brillo_score * 0.55) + (area_score * 0.45))

    def _aplicar_vignette(self, frame):
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        Y, X = np.ogrid[:h, :w]
        dist = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)
        vignette = np.clip((dist / np.sqrt(cx ** 2 + cy ** 2)) ** 2.2, 0, 1)
        overlay = np.repeat((vignette * 100).astype(np.uint8)[:, :, np.newaxis], 3, axis=2)
        return cv2.subtract(frame, overlay)

    def _get_video_area(self):
        self.update_idletasks()
        cw = self.video_container.winfo_width()
        ch = self.video_container.winfo_height()
        if cw < 10:
            cw = self.winfo_width() or 900
        if ch < 10:
            ch = self.winfo_height() or 600
        ch = max(ch - BANNER_H, 80)
        return cw, ch

    def actualizar_video(self):

        if not self.winfo_exists():
            return

        if not hasattr(self, "video_container"):
            return

        if not self.video_container.winfo_exists():
            return

        if not self.cap:
            return

        if not self.running:
            return

        self._flush_pending_style()

        frame = obtener_frame(self.cap)
        if frame is None:
            self.loop_id = self.after(33, self.actualizar_video)
            return

        frame_dibujado, face_encoding, mensaje, usuario_id, ojos_cerrados = procesar_frame(frame)
        fh_orig, fw_orig = frame_dibujado.shape[:2]

        faces     = self.detectar_rostros(frame_dibujado)
        num_caras = len(faces)
        ahora     = time.time()

        # -- Reset tras 4 s ---------------------------------------------------
        if (
            self.esperando_reset
            and not self.requiere_retirar_rostro
            and ahora - self.inicio_espera_reset > 4.0
        ):
            self.esperando_reset = False
            self.escaneando = False
            self.face_box = None
            self.estado_actual = None
            self.ultimo_rostro_visto = 0.0
            self.aplicar_estilo_visual("vacio")

        # -- Multiples rostros -------------------------------------------------
        if num_caras > 1 and not self.esperando_reset:
            if self.escaneando:
                self.escaneando = False
            if self.estado_actual != "multiples":
                self.aplicar_estilo_visual("multiples")
            for (x, y, w, h) in faces:
                self._dibujar_esquinas(frame_dibujado, x, y, w, h, ACCENT_CYAN)
            self.face_box = None

        elif num_caras == 1:
            self.face_box = self._rostro_principal(faces)
            self.ultimo_rostro_visto = ahora

            gris = cv2.cvtColor(frame_dibujado, cv2.COLOR_BGR2GRAY)
            brillo_medio = float(np.mean(gris))
            muy_oscuro = brillo_medio < 40

            fx0, fy0, fw0, fh0 = self.face_box
            area_cara  = fw0 * fh0
            area_frame = frame_dibujado.shape[0] * frame_dibujado.shape[1]
            area_relativa = area_cara / max(area_frame, 1)
            muy_lejos  = (area_cara / area_frame) < 0.04
            estado_postura = self._estado_postura_desde_mensaje(mensaje)

            if self.escaneando and estado_postura and not self.esperando_reset:
                self.escaneando = False
                self.pos_linea = 0
                if self.estado_actual != estado_postura:
                    self.aplicar_estilo_visual(estado_postura)

            if not self.escaneando and not self.esperando_reset:
                if estado_postura:
                    if self.estado_actual != estado_postura:
                        self.aplicar_estilo_visual(estado_postura)
                elif muy_oscuro:
                    if self.estado_actual != "iluminacion":
                        self.aplicar_estilo_visual("iluminacion")
                elif muy_lejos:
                    if self.estado_actual != "acercarse":
                        self.aplicar_estilo_visual("acercarse")
                elif self.estado_actual not in ("autorizado", "negado"):
                    self.escaneando = True
                    self.inicio_escaneo = ahora
                    self.usuario_detectado = ""
                    self.ids_detectados_escaneo = []
                    self.detector_parpadeo.reiniciar()
                    self.aplicar_estilo_visual("parpadeo" if self.modo != "registro" else "escaneando")
                    if self.modo == "registro":
                        self.lbl_nombre.configure(
                            text=f"MUESTRA {len(self.muestras_registro) + 1} DE {MUESTRAS_BIOMETRICAS}",
                            text_color=ACCENT_AMBER,
                        )

            if self.escaneando and self.face_box is not None:
                fx, fy, fw, fh = self.face_box
                self._dibujar_linea_escaneo(frame_dibujado, fx, fy, fw, fh, ACCENT_AMBER)

                msg_actual = str(mensaje).upper().strip()
                MENSAJES_GENERICOS = (
                    "CARA DETECTADA", "DETECTADA CORRECTAMENTE",
                    "PROCESANDO", "ANALIZANDO", "NINGUNO", "NONE",
                    "CORRECTO", "DETECTADO", "CARA", "ROSTRO", "",
                )
                if msg_actual and not any(g in msg_actual for g in MENSAJES_GENERICOS):
                    self.usuario_detectado = msg_actual
                if face_encoding is not None:
                    self.ids_detectados_escaneo.append(usuario_id)
                if self.modo != "registro":
                    parpadeo_confirmado = self.detector_parpadeo.actualizar(ojos_cerrados)
                    if parpadeo_confirmado and self.estado_actual == "parpadeo":
                        self.aplicar_estilo_visual("escaneando")
                    elif self.estado_actual == "parpadeo":
                        if self.detector_parpadeo.vio_cerrados:
                            instruccion = AppContext.t("ABRA LOS OJOS")
                        elif self.detector_parpadeo.vio_abiertos:
                            instruccion = AppContext.t("PARPADEE AHORA")
                        else:
                            instruccion = AppContext.t("MIRE A LA CAMARA")
                        self.lbl_nombre.configure(text=instruccion, text_color=ACCENT_CYAN)
                elif face_encoding is not None:
                    calidad_actual = self._calidad_captura(brillo_medio, area_relativa)
                    self.lbl_nombre.configure(
                        text=(
                            f"MUESTRA {len(self.muestras_registro) + 1} DE {MUESTRAS_BIOMETRICAS}"
                            f"  |  CALIDAD {calidad_actual}%"
                        ),
                        text_color=ACCENT_AMBER,
                    )

                if ahora - self.inicio_escaneo > SCAN_DURATION:
                    self.escaneando = False
                    self.pos_linea = 0
                    self.esperando_reset = True
                    self.inicio_espera_reset = ahora

                    if self.modo == "registro":

                        if face_encoding is not None:

                            match_id, distancia = find_best_match(
                                face_encoding,
                                self.encodings_conocidos,
                                self.ids_conocidos
                            )

                            rostro_de_otro_usuario = (
                                match_id is not None
                                and distancia < UMBRAL_ACCESO
                                and str(match_id) != str(self.user_id)
                            )

                            if rostro_de_otro_usuario:

                                self.status_label.configure(
                                    text=AppContext.t("USUARIO YA REGISTRADO"),
                                    text_color=ACCENT_RED
                                )
                                self.lbl_nombre.configure(
                                    text=AppContext.t("ESTE ROSTRO YA EXISTE EN EL SISTEMA"),
                                    text_color=ACCENT_RED
                                )

                                self.esperando_reset = False
                                self.escaneando = False
                                self.pos_linea = 0

                                self.loop_id = self.after(1500, self.actualizar_video)
                                return

                            calidad = self._calidad_captura(brillo_medio, area_relativa)
                            self.muestras_registro.append(face_encoding)
                            if len(self.muestras_registro) < MUESTRAS_BIOMETRICAS:
                                self.requiere_retirar_rostro = True
                                self._last_faces = []
                                self.face_box = None
                                reiniciar_cache_deteccion()
                                self.status_label.configure(
                                    text=f"MUESTRA GUARDADA - CALIDAD {calidad}%",
                                    text_color=ACCENT_GREEN,
                                )
                                self.lbl_nombre.configure(
                                    text=AppContext.t("RETIRE EL ROSTRO PARA CONTINUAR"),
                                    text_color=ACCENT_GREEN,
                                )
                            else:
                                self.running = False
                                self.status_label.configure(
                                    text="BIOMETRIA COMPLETA",
                                    text_color=ACCENT_GREEN,
                                )
                                if self.on_capture:
                                    self.on_capture(self.muestras_registro)
                                return

                    else:
                        ids_validos = [
                            detectado for detectado in self.ids_detectados_escaneo
                            if detectado is not None
                        ]
                        identidad_consistente = (
                            usuario_id is not None
                            and len(ids_validos) >= 3
                            and len(ids_validos) == len(self.ids_detectados_escaneo)
                            and all(detectado == usuario_id for detectado in ids_validos)
                        )

                        if not self.usuario_detectado:
                            self.usuario_detectado = msg_actual

                        if any(p in self.usuario_detectado for p in ("DESCONOCIDO", "ERROR", "NO REGISTRADO")):

                            self.aplicar_estilo_visual("negado")
                            self.registrar_acceso_bd(usuario_id, 0, None, "Acceso denegado")
                            if self.cerradura:
                                self.cerradura.bloquear()
                            self._activar_buzzer("denegado")

                        else:

                            if not self.usuario_detectado:
                                self.usuario_detectado = msg_actual

                            if any(p in self.usuario_detectado for p in ("DESCONOCIDO", "ERROR", "NO REGISTRADO")):

                                self.aplicar_estilo_visual("negado")
                                self.registrar_acceso_bd(None, 0, None, "Acceso denegado")
                                if self.cerradura:
                                    self.cerradura.bloquear()
                                self._activar_buzzer("denegado")

                            elif not identidad_consistente:

                                self.aplicar_estilo_visual("negado")
                                self.registrar_acceso_bd(None, 0, None, "Identidad no confirmada")
                                if self.cerradura:
                                    self.cerradura.bloquear()
                                self._activar_buzzer("denegado")

                            elif not self.detector_parpadeo.parpadeo_confirmado:

                                self.aplicar_estilo_visual("negado")
                                self.registrar_acceso_bd(usuario_id, 0, None, "Prueba de vida no superada")
                                if self.cerradura:
                                    self.cerradura.bloquear()
                                self._activar_buzzer("denegado")

                            elif usuario_activo(usuario_id):
                                marcaje = registrar_marcaje(usuario_id)
                                if marcaje["tipo"] == "entrada":
                                    estado_marcaje = "entrada"
                                    detalle_marcaje = self.usuario_detectado
                                    motivo_marcaje = "Entrada - Trabajando"
                                else:
                                    estado_marcaje = "salida"
                                    detalle_marcaje = (
                                        f"{self.usuario_detectado}\n"
                                        f"TIEMPO TRABAJADO: {marcaje['duracion_texto']}"
                                    )
                                    motivo_marcaje = (
                                        "Salida - Tiempo trabajado: "
                                        f"{marcaje['duracion_texto']}"
                                    )

                                self.aplicar_estilo_visual(estado_marcaje, usuario=detalle_marcaje)
                                self.requiere_retirar_rostro = True
                                if self.cerradura:
                                    apertura_enviada = self.cerradura.desbloquear_temporal()
                                    print(
                                        f"MARCAJE {marcaje['tipo'].upper()}: "
                                        f"usuario={usuario_id}, apertura_enviada={apertura_enviada}"
                                    )
                                self.registrar_acceso_bd(usuario_id, 1, None, motivo_marcaje)
                                self._activar_buzzer("autorizado")

                            else:

                                self.aplicar_estilo_visual("inactivo", usuario=self.usuario_detectado)
                                self.registrar_acceso_bd(usuario_id, 0, None, "Usuario inactivo")
                                if self.cerradura:
                                    self.cerradura.bloquear()
                                self._activar_buzzer("inactivo")

            if self.face_box is not None:
                fx, fy, fw, fh = self.face_box
                color_esq = (
                    ACCENT_AMBER if self.escaneando else
                    ACCENT_GREEN if self.estado_actual in ("autorizado", "entrada") else
                    ACCENT_CYAN  if self.estado_actual == "salida"     else
                    ACCENT_RED   if self.estado_actual == "negado"     else
                    ACCENT_PURPLE
                )
                self._dibujar_esquinas(frame_dibujado, fx, fy, fw, fh, color_esq)

        else:
            if (
                self.esperando_reset
                and self.requiere_retirar_rostro
                and ahora - self.ultimo_rostro_visto > 0.8
            ):
                self.requiere_retirar_rostro = False
                self.esperando_reset = False
                self.escaneando = False
                self.face_box = None
                self.estado_actual = None
                self.aplicar_estilo_visual("vacio")

            if not self.escaneando and not self.esperando_reset:
                if ahora - self.ultimo_rostro_visto > 0.8:
                    if self.estado_actual != "vacio":
                        self.aplicar_estilo_visual("vacio")
                    self.face_box = None

        frame_dibujado = self._aplicar_vignette(frame_dibujado)

        try:
            cw, ch = self._get_video_area()
        except Exception:
            return

        img_ratio  = fw_orig / fh_orig
        cont_ratio = cw / ch

        if img_ratio > cont_ratio:
            nw, nh = cw, int(cw / img_ratio)
        else:
            nh, nw = ch, int(ch * img_ratio)

        nw = max(nw, 2)
        nh = max(nh, 2)

        cv2_rgb = cv2.cvtColor(frame_dibujado, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2_rgb).resize((nw, nh), Image.Resampling.LANCZOS)

        bg_color = tuple(int(BG_PANEL.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        background = Image.new("RGB", (cw, ch), bg_color)
        background.paste(img, ((cw - nw) // 2, (ch - nh) // 2))

        ctk_image = ctk.CTkImage(light_image=background, dark_image=background, size=(cw, ch))
        self.video_display.configure(image=ctk_image, text="")
        self.video_display.image = ctk_image

        if self.running:
            self.loop_id = self.after(33, self.actualizar_video)

    # --------------------------------------------------------------------------
    # Ciclo de vida
    # --------------------------------------------------------------------------

    def iniciar_sistema(self):
        self.cap = iniciar_camara()
        if self.cap:
            self.aplicar_estilo_visual("vacio")
            self.after(200, self.actualizar_video)
        else:
            self.aplicar_estilo_visual("sin_camara")
            self._flush_pending_style()
            self.video_display.configure(
                text=(
                    "  ERROR: no se pudo acceder a la camara\n\n"
                    "Verifique que el dispositivo este conectado\n"
                    "y no este en uso por otra aplicacion."
                ),
                text_color=ACCENT_RED,
            )

    def _activar_buzzer(self, tipo):
        if self.modo == "registro":
            return

        duraciones = {
            "autorizado": 0.08,
            "denegado": 0.18,
            "inactivo": 0.25,
        }

        try:
            buzzer.buzz_async(duraciones.get(tipo, 0.15))
        except Exception:
            pass

    def _cerrar_hardware(self):
        if self.cerradura:
            try:
                self.cerradura.cerrar()
            except Exception:
                pass
            self.cerradura = None

        try:
            buzzer.close()
        except Exception:
            pass

    def cerrar_y_volver(self):
        self.running = False

        if self.loop_id:
            try:
                self.after_cancel(self.loop_id)
            except Exception:
                pass
            self.loop_id = None

        if self.cap:
            liberar_camara(self.cap)
            self.cap = None

        self._cerrar_hardware()

        if self.on_back:
            self.on_back()

    def on_close(self):
        print("Cerrando terminal biometrica")

        self.running = False

        if self.loop_id:
            try:
                self.after_cancel(self.loop_id)
            except Exception:
                pass
            self.loop_id = None

        try:
            from app.camara.camara import liberar_camara
            liberar_camara(self.cap)
        except Exception as e:
            print("Error liberando camara:", e)

        self.cap = None
        self._cerrar_hardware()

    def registrar_acceso_bd(self, id_usuario, resultado, confianza=None, motivo=""):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO registro_acceso
                (id_usuario, fecha_hora, resultado, confianza, motivo)
                VALUES (?, ?, ?, ?, ?)
            """, (
                id_usuario,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                resultado,
                confianza,
                motivo
            ))

            conn.commit()
            conn.close()

            print("Acceso registrado en BD:", motivo)

        except Exception as e:
            print("Error registrando acceso:", e)
