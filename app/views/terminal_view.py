import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image
import time
from app.recognition.encoding_manager import cargar_encodings
from app.detection.detector_rostro import find_best_match
from app.views.app_context import AppContext
from app.camara.camara import iniciar_camara, liberar_camara, obtener_frame
from app.detection.detector_rostro import procesar_frame
from app.services.usuario_service import usuario_activo
from app.database.database import get_connection
from datetime import datetime
from app.hardware.cerradura import Cerradura


# ── Paleta ────────────────────────────────────────────────────────────────────
BG_DEEP        = "#0b0b22"   # azul más claro/visible
BG_PANEL       = "#10103a"   # panel azul más notorio
BG_BANNER      = "#13133d"
BORDER_IDLE    = "#3d3880"
ACCENT_PURPLE  = "#9b87ff"
ACCENT_GREEN   = "#2dffaa"
ACCENT_RED     = "#ff4d5e"
ACCENT_AMBER   = "#ffb020"
ACCENT_CYAN    = "#20d4ff"
TEXT_PRIMARY   = "#ffffff"
TEXT_SECONDARY = "#a090d0"
TEXT_MUTED     = "#5a52a0"

BANNER_H = 100

TEMAS = {
    "escaneando": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#1c1508",
        "dot":      ACCENT_AMBER,
        "status":   "ESCANEANDO",
        "st_color": ACCENT_AMBER,
        "name":     "ANALIZANDO RASGOS BIOMÉTRICOS",
        "badge":    "LEYENDO",
        "b_color":  ACCENT_AMBER,
    },
    "autorizado": {
        "border":   ACCENT_GREEN,
        "bar":      ACCENT_GREEN,
        "banner":   "#071510",
        "dot":      ACCENT_GREEN,
        "status":   "ACCESO AUTORIZADO",
        "st_color": ACCENT_GREEN,
        "name":     "",
        "badge":    "✓  OK",
        "b_color":  ACCENT_GREEN,
    },
    "negado": {
        "border":   ACCENT_RED,
        "bar":      ACCENT_RED,
        "banner":   "#1a0508",
        "dot":      ACCENT_RED,
        "status":   "ACCESO DENEGADO",
        "st_color": ACCENT_RED,
        "name":     "USUARIO NO REGISTRADO",
        "badge":    "✗  ERROR",
        "b_color":  ACCENT_RED,
    },
    "multiples": {
        "border":   ACCENT_CYAN,
        "bar":      ACCENT_CYAN,
        "banner":   "#071520",
        "dot":      ACCENT_CYAN,
        "status":   "MÚLTIPLES ROSTROS DETECTADOS",
        "st_color": ACCENT_CYAN,
        "name":     "SOLO UN USUARIO A LA VEZ",
        "badge":    "⚠  ALERTA",
        "b_color":  ACCENT_CYAN,
    },
    "sin_camara": {
        "border":   ACCENT_RED,
        "bar":      ACCENT_RED,
        "banner":   "#1a0508",
        "dot":      ACCENT_RED,
        "status":   "SIN CÁMARA",
        "st_color": ACCENT_RED,
        "name":     "NO SE DETECTÓ NINGÚN DISPOSITIVO",
        "badge":    "✗  OFFLINE",
        "b_color":  ACCENT_RED,
    },
    "acercarse": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#1c1508",
        "dot":      ACCENT_AMBER,
        "status":   "ACÉRQUESE A LA CÁMARA",
        "st_color": ACCENT_AMBER,
        "name":     "ROSTRO DEMASIADO LEJOS O PEQUEÑO",
        "badge":    "⚠  AJUSTE",
        "b_color":  ACCENT_AMBER,
    },
    "iluminacion": {
        "border":   ACCENT_AMBER,
        "bar":      ACCENT_AMBER,
        "banner":   "#1c1508",
        "dot":      ACCENT_AMBER,
        "status":   "MEJORE LA ILUMINACIÓN",
        "st_color": ACCENT_AMBER,
        "name":     "AMBIENTE MUY OSCURO — ENCIENDA UNA LUZ",
        "badge":    "⚠  LUZ",
        "b_color":  ACCENT_AMBER,
    },
    "vacio": {
        "border":   BORDER_IDLE,
        "bar":      ACCENT_PURPLE,
        "banner":   BG_BANNER,
        "dot":      ACCENT_PURPLE,
        "status":   "POSICIONE SU ROSTRO",
        "st_color": TEXT_PRIMARY,
        "name":     "MIRANDO HACIA LA CÁMARA",
        "badge":    "LISTO",
        "b_color":  ACCENT_PURPLE,
    },
}


class TerminalView(ctk.CTkFrame):
    def __init__(self, master, user_id=None, on_back=None, on_capture=None, modo="acceso"):
        super().__init__(master, fg_color=BG_DEEP)
        self.on_back = on_back
        self.on_capture = on_capture  # 🔥 ESTE ES EL NUEVO
        self.modo = modo
        self.user_id = user_id
        self.cap = None
        self.loop_id = None
        self.estado_actual = None
        self.running = True
        self.cerradura = None

        #  SOLO usar cerradura en modo acceso
        if self.modo != "registro":
            self.cerradura = Cerradura()

        self.escaneando = False
        self.inicio_escaneo = 0.0
        self.pos_linea = 0
        self.subiendo = False
        self.usuario_detectado = ""
        self.ultimo_rostro_visto = 0.0
        self.face_box = None
        self.esperando_reset = False
        self.inicio_espera_reset = 0.0

        self._pending_style = None

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self._build_ui()
        self.iniciar_sistema()

    # ══════════════════════════════════════════════════════════════════════════
    # Construcción de la UI
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        ctk.CTkFrame(self, fg_color=ACCENT_PURPLE, height=2).pack(fill="x", side="top")

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(pady=(20, 4))
        # 🔥 SOLO mostrar botón salir en modo normal
        if self.modo != "registro":
            self.btn_salir = ctk.CTkButton(
                self, text="🚪", width=42, height=42,
                corner_radius=8,
                fg_color=BG_PANEL, hover_color="#1e1860",
                text_color=TEXT_SECONDARY,
                font=("Segoe UI Emoji", 18),
                border_width=1, border_color=BORDER_IDLE,
                command=self.cerrar_y_volver,
            )
            self.btn_salir.place(relx=0.974, rely=0.046, anchor="ne")
            # 🔥 BOTÓN CERRAR SOLO PARA MODO REGISTRO
        if self.modo == "registro":
            self.btn_cerrar = ctk.CTkButton(
                self,
                text="✖",
                width=40,
                height=40,
                corner_radius=10,
                fg_color="#1e1e3f",
                hover_color="#ff4d5e",
                text_color="white",
                font=("Segoe UI", 16, "bold"),
                border_width=1,
                border_color=BORDER_IDLE,
                command=self.cerrar_y_volver
            )

            self.btn_cerrar.place(relx=0.974, rely=0.046, anchor="ne")

        ctk.CTkLabel(
            hdr, text="K O D A",
            font=("Courier New", 43, "bold"),
            text_color=TEXT_PRIMARY,
        ).pack()

        ctk.CTkLabel(
            hdr,
            text=AppContext.t("▸  RECONOCIMIENTO FACIAL  ◂") if self.modo == "registro" else AppContext.t("▸  RECONOCIMIENTO FACIAL  ◂"),
            font=("Courier New", 23),
            text_color=TEXT_MUTED,
        ).pack(pady=(4, 0))

        

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(expand=True, fill="both", padx=44, pady=(8, 28))

        self.video_container = ctk.CTkFrame(
            main, fg_color=BG_PANEL, corner_radius=16,
            border_width=2, border_color=BORDER_IDLE,
        )
        self.video_container.pack(expand=True, fill="both")

        # ── Banner ────────────────────────────────────────────────────────────
        self.data_banner = ctk.CTkFrame(
            self.video_container,
            fg_color=BG_BANNER,
            corner_radius=0,
            height=BANNER_H,
        )
        self.data_banner.pack(side="top", fill="x")
        self.data_banner.pack_propagate(False)

        self.accent_bar = ctk.CTkFrame(
            self.data_banner, fg_color=ACCENT_PURPLE, width=5, corner_radius=0
        )
        self.accent_bar.pack(side="left", fill="y")

        center = ctk.CTkFrame(self.data_banner, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True)

        row = ctk.CTkFrame(center, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(18, 0))

        self.dot_indicator = ctk.CTkLabel(
            row, text="●", font=("Courier New", 14), text_color=ACCENT_PURPLE
        )
        self.dot_indicator.pack(side="left", padx=(0, 10))

        self.status_label = ctk.CTkLabel(
            row,
            text=AppContext.t("SISTEMA ACTIVO"),
            font=("Courier New", 25, "bold"),
            text_color=TEXT_PRIMARY,
        )
        self.status_label.pack(side="left")

        ctk.CTkFrame(center, fg_color=BORDER_IDLE, height=1).pack(
            fill="x", padx=20, pady=(8, 0)
        )

        self.lbl_nombre = ctk.CTkLabel(
            center,
            text=AppContext.t("ESPERANDO DETECCIÓN..."),
            font=("Courier New", 20),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.lbl_nombre.pack(fill="x", padx=24, pady=(5, 0))

        self.accent_line = ctk.CTkFrame(
            self.data_banner, fg_color=ACCENT_PURPLE, height=2, corner_radius=0
        )
        self.accent_line.pack(side="bottom", fill="x")

        # ── Badge esquina superior-derecha, sin cuadro de fondo ──────────────
        self.badge_label = ctk.CTkLabel(
            self.data_banner,
            text=AppContext.t("LISTO"),
            font=("Courier New", 19, "bold"),
            text_color=ACCENT_PURPLE,
            fg_color="transparent",   # sin cuadro
        )
        self.badge_label.place(relx=0.955, rely=0.23, anchor="ne")

        # ── Área de video ────────────────────────────────────────────────────
        self.video_display = ctk.CTkLabel(
            self.video_container,
            text=AppContext.t("Iniciando cámara..."),
            text_color=TEXT_MUTED,
            font=("Courier New", 13),
        )
        self.video_display.pack(side="bottom", fill="both", expand=True)

        # Footer
        ctk.CTkLabel(
            self,
            text=AppContext.t("Sistema Biométrico v2.0") + "  //  " + AppContext.t("Acceso Seguro") + "  //  " + AppContext.t("Cifrado AES-256"),
            font=("Courier New", 9),
            text_color=TEXT_MUTED,
        ).pack(side="bottom", pady=(0, 10))
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

        nombre = t["name"]
        if estado == "autorizado":
            nombre = f"BIENVENIDO:  {usuario}" if usuario else "ACCESO CONCEDIDO"

        self.video_container.configure(border_color=t["border"])
        self.data_banner.configure(fg_color=t["banner"])
        self.accent_bar.configure(fg_color=t["bar"])
        self.accent_line.configure(fg_color=t["bar"])
        self.dot_indicator.configure(text_color=t["dot"])
        self.status_label.configure(text=t["status"], text_color=t["st_color"])
        self.lbl_nombre.configure(text=nombre, text_color=t["b_color"])
        self.badge_label.configure(text=t["badge"], text_color=t["b_color"])
        # 🔥 MODO REGISTRO (sobrescribe textos)
        if self.modo == "registro" and estado != "negado":
            self.status_label.configure(
               text="REGISTRANDO BIOMETRÍA",
               text_color=ACCENT_AMBER   # 🔥 amarillo
            )
            self.lbl_nombre.configure(
               text="COLOQUE SU ROSTRO FRENTE A LA CÁMARA",
               text_color=ACCENT_AMBER   # 🔥 amarillo también
            )

    def detectar_rostros(self, frame):
        """Devuelve lista de todas las cajas detectadas."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        return list(faces) if len(faces) > 0 else []

    def _rostro_principal(self, faces):
        """Retorna caja del rostro más grande con padding."""
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])
        pad = 40
        return (max(0, x - pad), max(0, y - pad), w + pad * 2, h + pad * 2)

    # ══════════════════════════════════════════════════════════════════════════
    # Dibujo sobre frame
    # ══════════════════════════════════════════════════════════════════════════

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

    def _aplicar_vignette(self, frame):
        # Normalizar a BGR 3 canales — fix del crash original
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

    # ══════════════════════════════════════════════════════════════════════════
    # Loop de video
    # ══════════════════════════════════════════════════════════════════════════

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

        # 🔴 Evitar errores si la vista ya fue destruida
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
            self.loop_id = self.after(16, self.actualizar_video)
            return

        frame_dibujado, face_encoding, mensaje, usuario_id  = procesar_frame(frame)
        fh_orig, fw_orig = frame_dibujado.shape[:2]

        # ── Detectar todos los rostros ────────────────────────────────────────
        faces    = self.detectar_rostros(frame_dibujado)
        num_caras = len(faces)
        ahora     = time.time()

        # ── Reset tras 4 s ───────────────────────────────────────────────────
        if self.esperando_reset and ahora - self.inicio_espera_reset > 4.0:
            self.esperando_reset = False
            self.escaneando = False
            self.face_box = None
            self.estado_actual = None
            self.ultimo_rostro_visto = 0.0
            self.aplicar_estilo_visual("vacio")

        # ── Múltiples rostros ─────────────────────────────────────────────────
        if num_caras > 1 and not self.esperando_reset:
            if self.escaneando:
                self.escaneando = False
            if self.estado_actual != "multiples":
                self.aplicar_estilo_visual("multiples")
            for (x, y, w, h) in faces:
                self._dibujar_esquinas(frame_dibujado, x, y, w, h, ACCENT_CYAN)
            self.face_box = None

        # ── Un solo rostro ────────────────────────────────────────────────────
        elif num_caras == 1:
            self.face_box = self._rostro_principal(faces)
            self.ultimo_rostro_visto = ahora

            # ── Validar iluminación ───────────────────────────────────────────
            gris = cv2.cvtColor(frame_dibujado, cv2.COLOR_BGR2GRAY)
            brillo_medio = float(np.mean(gris))
            muy_oscuro = brillo_medio < 40  # umbral: 0-255

            # ── Validar tamaño del rostro (lejos/cerca) ───────────────────────
            fx0, fy0, fw0, fh0 = self.face_box
            area_cara = fw0 * fh0
            area_frame = frame_dibujado.shape[0] * frame_dibujado.shape[1]
            muy_lejos = (area_cara / area_frame) < 0.04  # menos del 4% del frame

            if not self.escaneando and not self.esperando_reset:
                if muy_oscuro:
                    if self.estado_actual != "iluminacion":
                        self.aplicar_estilo_visual("iluminacion")
                elif muy_lejos:
                    if self.estado_actual != "acercarse":
                        self.aplicar_estilo_visual("acercarse")
                elif self.estado_actual not in ("autorizado", "negado"):
                    self.escaneando = True
                    self.inicio_escaneo = ahora
                    self.usuario_detectado = ""   # se irá llenando frame a frame
                    if self.modo == "registro":
                        self.aplicar_estilo_visual("escaneando")
                    else:
                        self.aplicar_estilo_visual("escaneando")

            if self.escaneando and self.face_box is not None:
                fx, fy, fw, fh = self.face_box
                self._dibujar_linea_escaneo(frame_dibujado, fx, fy, fw, fh, ACCENT_AMBER)

                # Actualizar usuario_detectado en cada frame mientras escaneamos.
                # Se descarta cualquier mensaje genérico y se guarda solo el nombre real.
                msg_actual = str(mensaje).upper().strip()
                MENSAJES_GENERICOS = (
                    "CARA DETECTADA", "DETECTADA CORRECTAMENTE",
                    "PROCESANDO", "ANALIZANDO", "NINGUNO", "NONE",
                    "CORRECTO", "DETECTADO", "CARA", "ROSTRO", "",
                )
                if msg_actual and not any(g in msg_actual for g in MENSAJES_GENERICOS):
                    self.usuario_detectado = msg_actual

                if ahora - self.inicio_escaneo > 3.0:
                    self.escaneando = False
                    self.pos_linea = 0
                    self.esperando_reset = True
                    self.inicio_espera_reset = ahora

                    # =========================================================
                    # MODO REGISTRO
                    # =========================================================

                    if self.modo == "registro":

                        if face_encoding is not None:

                            
                            # ?? Verificar si el rostro ya existe
                            match_id, distancia = find_best_match(
                                face_encoding,
                                cargar_encodings()[0],
                                cargar_encodings()[1]
                            )

                            # ? Rostro duplicado
                            if match_id is not None and distancia < 0.45:

                                self.status_label.configure(
                                    text="USUARIO YA REGISTRADO",
                                    text_color=ACCENT_RED
                                )

                                self.lbl_nombre.configure(
                                    text="ESTE ROSTRO YA EXISTE EN EL SISTEMA",
                                    text_color=ACCENT_RED
                                )

                                self.badge_label.configure(
                                    text="? DUPLICADO",
                                    text_color=ACCENT_RED
                                )

                                # ?? volver a permitir escaneo
                                self.esperando_reset = False
                                self.escaneando = False
                                self.pos_linea = 0

                                self.loop_id = self.after(1500, self.actualizar_video)
                                return


                            # ? Rostro nuevo
                            self.running = False

                            if self.on_capture:
                                self.on_capture(face_encoding)

                            return
                        
                        # =========================================================
                        # MODO ACCESO / RECONOCIMIENTO
                        # =========================================================
                    
                    else:
                    
                    # Si nunca se resolvió un nombre, usar el último mensaje disponible
                        if not self.usuario_detectado:
                            self.usuario_detectado = msg_actual
                        
                        # Usuario desconocido
                        if any(p in self.usuario_detectado for p in ("DESCONOCIDO", "ERROR", "NO REGISTRADO")):

                            self.aplicar_estilo_visual("negado")

                            self.registrar_acceso_bd(
                                usuario_id,
                                0,
                                None,
                                "Acceso denegado"
                            )

                            # ?? mantener bloqueada
                            if self.cerradura:
                                self.cerradura.bloquear()


                        else:

                            # USUARIO ACTIVO
                            if usuario_id is not None and usuario_activo(usuario_id):

                                self.aplicar_estilo_visual(
                                    "autorizado",
                                    usuario=self.usuario_detectado
                                )

                                self.registrar_acceso_bd(
                                    usuario_id,
                                    1,
                                    None,
                                    "Acceso autorizado"
                                )

                                # ?? abrir temporalmente
                                if self.cerradura:
                                    self.cerradura.desbloquear_temporal(2)

                            # USUARIO INACTIVO
                            else:

                                self.estado_actual = "negado"

                                self.registrar_acceso_bd(
                                    usuario_id,
                                    0,
                                    None,
                                    "Usuario inactivo"
                                )

                                # ?? mantener cerrada
                                if self.cerradura:
                                    self.cerradura.bloquear()

                                self.status_label.configure(
                                    text="USUARIO INACTIVO",
                                    text_color=ACCENT_RED
                                )

                                self.lbl_nombre.configure(
                                    text=f"{self.usuario_detectado}\nUSUARIO INACTIVO",
                                    text_color=ACCENT_RED
                                )

                                self.badge_label.configure(
                                    text="? BLOQUEADO",
                                    text_color=ACCENT_RED
                                )

                    

            if self.face_box is not None:
                fx, fy, fw, fh = self.face_box
                color_esq = (
                    ACCENT_AMBER if self.escaneando else
                    ACCENT_GREEN if self.estado_actual == "autorizado" else
                    ACCENT_RED   if self.estado_actual == "negado"     else
                    ACCENT_PURPLE
                )
                self._dibujar_esquinas(frame_dibujado, fx, fy, fw, fh, color_esq)

        # ── Sin cara ──────────────────────────────────────────────────────────
        else:
            if not self.escaneando and not self.esperando_reset:
                if ahora - self.ultimo_rostro_visto > 0.8:
                    if self.estado_actual != "vacio":
                        self.aplicar_estilo_visual("vacio")
                    self.face_box = None

        # ── Vignette ─────────────────────────────────────────────────────────
        frame_dibujado = self._aplicar_vignette(frame_dibujado)


        try:
            cw, ch = self._get_video_area()
        except:
            return
        # ── Renderizado ──────────────────────────────────────────────────────
        
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
            self.loop_id = self.after(16, self.actualizar_video)

    # ══════════════════════════════════════════════════════════════════════════
    # Ciclo de vida
    # ══════════════════════════════════════════════════════════════════════════

    def iniciar_sistema(self):
        self.cap = iniciar_camara()
        if self.cap:
            self.aplicar_estilo_visual("vacio")
            self.after(200, self.actualizar_video)
        else:
            # Banner + área de video muestran el error
            self.aplicar_estilo_visual("sin_camara")
            self._flush_pending_style()
            self.video_display.configure(
                text="⚠  ERROR: no se pudo acceder a la cámara\n\n"
                    "Verifique que el dispositivo esté conectado\n"
                    "y no esté en uso por otra aplicación.",
                text_color=ACCENT_RED,
            )

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

        if self.on_back:
            self.on_back()

    
        
    def on_close(self):
        print("🛑 Cerrando terminal biométrica")

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
            print("Error liberando cámara:", e)

        self.cap = None
        
    
    
    
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

            print("✔ Acceso registrado en BD:", motivo)

        except Exception as e:
            print("❌ Error registrando acceso:", e)