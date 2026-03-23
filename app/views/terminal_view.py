import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from app.camara.camara import iniciar_camara, obtener_frame
from app.detection.detector_rostro import procesar_frame

class TerminalView(ctk.CTkFrame):
    def __init__(self, master, on_back):
        super().__init__(master, fg_color="#1A1A1B") # Fondo oscuro de terminal
        self.on_back = on_back
        self.cap = None
        self.loop_id = None

        # --- BOTÓN DE LOGIN / ENTRADA EN LA ESQUINA ---
        # Usamos un diseño circular o cuadrado redondeado muy discreto
        self.btn_login = ctk.CTkButton(
            self, 
            text="🚪",                # Icono de puerta o entrada
            width=45, 
            height=45, 
            corner_radius=12,
            fg_color="#2D2D2E",       # Mismo color que el contenedor de video para camuflarse
            hover_color="#3E3E3F",    # Un gris un poco más claro al pasar el mouse
            text_color="white", 
            font=("Inter", 20),
            command=self.cerrar_y_volver
        )
        # Posicionamiento absoluto: 2% desde la derecha, 2% desde arriba
        self.btn_login.place(relx=0.98, rely=0.02, anchor="ne")

        # Título Estilizado
        ctk.CTkLabel(self, text="TERMINAL DE RECONOCIMIENTO", 
                     font=("Inter", 28, "bold"), text_color="white").pack(pady=(40, 10))
        
        self.status_label = ctk.CTkLabel(self, text="Iniciando sistema...", 
                                         font=("Inter", 14), text_color="#94A3B8")
        self.status_label.pack(pady=(0, 20))

        # Contenedor de Video con bordes redondeados
        self.video_container = ctk.CTkFrame(self, fg_color="#2D2D2E", corner_radius=25)
        self.video_container.pack(expand=True, fill="both", padx=80, pady=(10, 50)) # Ajustado el pady inferior

        self.video_display = ctk.CTkLabel(self.video_container, text="")
        self.video_display.pack(expand=True, fill="both", padx=10, pady=10)

        # Iniciar hardware al entrar a la vista
        self.iniciar_sistema()

    def iniciar_sistema(self):
        # Intentar iniciar la cámara
        self.cap = iniciar_camara() 
        if self.cap:
            self.actualizar_video()
        else:
            self.status_label.configure(text="ERROR: NO SE ENCONTRÓ LA CÁMARA", text_color="#EF4444")

    def actualizar_video(self):
        if self.cap:
            frame = obtener_frame(self.cap)
            if frame is not None:
                # PROCESAR FRAME
                frame_dibujado, encoding, mensaje = procesar_frame(frame)
                
                # Actualizar mensaje de estado en la UI
                self.status_label.configure(text=mensaje.upper())

                # Convertir para mostrar en CustomTkinter
                cv2_rgb = cv2.cvtColor(frame_dibujado, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2_rgb)
                
                # Ajuste de tamaño manteniendo estética
                img = img.resize((750, 480), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(image=img)
                
                self.video_display.configure(image=img_tk)
                self.video_display.image = img_tk
            
            # Re-ejecutar cada 15ms para fluidez
            self.loop_id = self.after(15, self.actualizar_video)

    def cerrar_y_volver(self):
        # Detener procesos para liberar la cámara antes de cambiar de vista
        if self.loop_id:
            self.after_cancel(self.loop_id)
        if self.cap:
            self.cap.release()
        
        # Al ejecutar on_back(), como lo configuramos en main.py, irá al Login
        self.on_back()