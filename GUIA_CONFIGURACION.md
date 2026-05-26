# Guia de configuracion - SecureWork

Esta guia resume como preparar, ejecutar y diagnosticar el sistema biometrico facial SecureWork en Windows y Raspberry Pi.

## 1. Requisitos

### Windows

- Python 3.10 recomendado.
- Camara web disponible.
- PowerShell.
- SQLite Browser opcional para inspeccionar la base de datos.
- Visual Studio Build Tools con C++ si necesitas compilar `dlib`.

### Raspberry Pi

- Raspberry Pi OS con entorno grafico.
- Camara compatible.
- Python 3.
- Fuente externa para cerradura electrica.
- Rele, buzzer y PIR si se usara hardware fisico.

## 2. Preparar entorno virtual en Windows

Desde la carpeta del proyecto:

```powershell
cd C:\Users\vinel\Documents\sistema-biometrico
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Si el entorno ya existe:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Dependencias probadas

El proyecto debe quedar con estas versiones:

```text
customtkinter==5.2.2
opencv-contrib-python==4.10.0.84
numpy==1.26.4
face-recognition==1.3.0
Pillow==10.0.1
dlib==20.0.1
mediapipe==0.10.14
```

Verifica dependencias:

```powershell
python -m pip check
python -c "import numpy, cv2, mediapipe, face_recognition; print(numpy.__version__, cv2.__version__, mediapipe.__version__)"
```

Importante: evita `numpy 2.x` en este proyecto. Con `face_recognition/dlib` puede provocar que el encoding facial falle.

## 4. Base de datos

La app verifica/crea la base al iniciar. Para hacerlo manualmente:

```powershell
python init_db.py
```

Archivos relevantes:

- Base local: `app/database/sistema_biometrico.db`
- Esquema y datos: `app/database/schema_and_data.sql`
- Proyecto SQLite Browser: `app/database/sistema_biometrico.sqbpro`

### Abrir con SQLite Browser

1. Instala SQLite Browser desde `https://sqlitebrowser.org/`.
2. Abre SQLite Browser.
3. Usa `File -> Open Database`.
4. Selecciona `app/database/sistema_biometrico.db`.
5. Revisa tablas desde `Browse Data`.

Tablas principales:

- `usuario_rol`: roles de usuario.
- `facultad`: areas/facultades.
- `carrera`: puestos/carreras.
- `usuario`: datos de usuarios.
- `biometria`: datos biometricos asociados.
- `registro_acceso`: historial de accesos.

## 5. Ejecutar la aplicacion

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

La aplicacion inicia en la terminal biometrica. Para entrar al panel administrativo:

1. Presiona `Salir` en la terminal.
2. Inicia sesion en el login.
3. Credenciales de prueba:

```text
usuario: 1
contrasena: 1
```

## 6. Configuracion de camara

La camara se maneja desde `app/camara/camara.py`.

En PC Windows se usa:

- OpenCV con backend `CAP_DSHOW`.
- Resolucion 640x480.
- FPS objetivo 30.
- Buffer minimo para evitar retraso.
- Lectura en segundo plano para tomar siempre el frame mas reciente.

En Raspberry Pi se intenta usar `picamera2`.

### Deteccion y reconocimiento

El pipeline esta en `app/detection/detector_rostro.py`:

- MediaPipe detecta rostros rapidamente.
- `face_recognition/dlib` genera embeddings para comparar identidad.
- Se reutiliza el ultimo resultado algunos frames para mantener fluidez.
- Los frames se convierten a `RGB uint8` contiguo para evitar errores de dlib.

## 7. Problemas comunes

### La camara se queda en "Iniciando camara..."

1. Cierra Zoom, Teams, navegador u otra app que use camara.
2. Revisa que la app no tenga una excepcion en consola.
3. Ejecuta:

```powershell
python -m pip check
python -c "import numpy, cv2, face_recognition; print(numpy.__version__, cv2.__version__)"
```

Debe mostrar `numpy 1.26.4` y OpenCV `4.10.0`.

### Error: Unsupported image type, must be 8bit gray or RGB image

Este error suele venir de una version incompatible de NumPy con dlib. Repara el entorno:

```powershell
pip install numpy==1.26.4 opencv-contrib-python==4.10.0.84
pip install -r requirements.txt
```

### MediaPipe imprime advertencias

Mensajes como estos son normales:

```text
INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
Feedback manager requires a model with a single signature inference.
```

No indican fallo de camara.

### No se instala dlib o face-recognition

Recomendado:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Si falla en Windows, instala Visual Studio Build Tools con C++ y vuelve a ejecutar el comando.

### SQLite dice "database is locked"

- Cierra SQLite Browser si esta editando la base.
- Cierra otra instancia de la app.
- Espera unos segundos; la conexion usa timeout para evitar fallos rapidos.

## 8. Datos sensibles y archivos locales

No subas al repositorio:

- `encodings.json`
- `logs_accesos.json`
- `app/data/perfil_usuario.json`
- `app/data/fotos/`
- `app/database/sistema_biometrico.db`

Estos archivos pueden contener datos biometricos, accesos, usuarios o informacion personal.

## 9. Variables de entorno de hardware

El archivo `app/config.py` permite ajustar hardware sin tocar codigo:

```text
PIN_RELEVADOR=22
PIN_BUZZER=18
PIN_PIR=17
SIMULATE_HARDWARE=0
UNLOCK_TIMEOUT=2.0
```

Ejemplo en PowerShell:

```powershell
$env:SIMULATE_HARDWARE="1"
$env:UNLOCK_TIMEOUT="2"
python main.py
```

Usa `UNLOCK_TIMEOUT=none` solo si quieres mantener la cerradura abierta sin cierre automatico.

## 10. Conexion de hardware en Raspberry Pi

### Rele y cerradura

- No alimentes la cerradura desde la Raspberry Pi.
- Usa una fuente externa adecuada para la cerradura.
- Conecta la cerradura en serie con COM/NO del rele.
- Conecta `IN` del rele al GPIO configurado, por defecto `PIN_RELEVADOR=22`.
- Comparte GND entre Raspberry Pi y fuente externa.

### Buzzer

- Pin por defecto: `PIN_BUZZER=18`.
- Si el buzzer consume mucha corriente, usa transistor o modulo dedicado.

### PIR

- Pin por defecto: `PIN_PIR=17`.
- Conecta VCC, GND y salida al GPIO configurado.

### Seguridad electrica

- Usa fusible para la cerradura.
- Si la cerradura es inductiva, usa diodo flyback o rele con proteccion.
- Verifica voltajes antes de energizar el circuito.

## 11. Despliegue en Raspberry Pi con systemd

Existe una plantilla:

```text
deploy/sistema-biometrico.service
```

Y un instalador:

```text
scripts/install_service.sh
```

Pasos:

```bash
cd /ruta/al/sistema-biometrico
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gpiozero pigpio picamera2
sudo bash scripts/install_service.sh
sudo systemctl status sistema-biometrico.service
```

Si tu usuario o ruta no coinciden, ajusta en el servicio:

- `User`
- `WorkingDirectory`
- `ExecStart`
- `DISPLAY`
- `XAUTHORITY`

## 12. Pruebas utiles

### Verificar imports criticos

```powershell
python -c "import cv2, mediapipe, face_recognition, customtkinter; print('OK')"
```

### Verificar pipeline de encoding

```powershell
python -c "import numpy as np, face_recognition; img=np.zeros((100,100,3), dtype=np.uint8); face_recognition.face_encodings(img, [(10,90,90,10)]); print('encoding ok')"
```

### Probar hardware

```bash
python app/hardware/test_hardware.py
```

## 13. Notas operativas

- Buena iluminacion mejora mucho la deteccion.
- Debe haber una sola cara frente a la camara.
- Evita mover demasiado la cabeza durante el escaneo.
- El tiempo de escaneo visual se configura en `SCAN_DURATION` dentro de `app/views/terminal_view.py`.
- La deteccion rapida con MediaPipe se activa si `mediapipe` esta instalado correctamente.
