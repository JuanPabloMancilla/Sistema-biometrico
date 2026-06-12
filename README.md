# SecureWork - Sistema Biometrico Facial

SecureWork es una aplicacion de escritorio en Python para control de acceso mediante reconocimiento facial. El sistema inicia en una terminal biometrica, valida rostros con camara en tiempo real y permite administrar personal, areas, puestos, perfil administrativo y registros de acceso desde un dashboard grafico.

## Funcionalidades principales

- Terminal de acceso con camara en vivo.
- Deteccion facial acelerada con MediaPipe y OpenCV.
- Reconocimiento facial con `face-recognition` y `dlib`.
- Prueba de vida mediante parpadeo antes de autorizar entradas y salidas.
- Indicaciones visuales en vivo para completar la prueba de parpadeo.
- Registro guiado de tres muestras biometricas con indicador de calidad.
- Dashboard con metricas, grafica por hora y ultimos accesos.
- Reportes de asistencia por rango de fechas con exportacion CSV.
- Reglas configurables de horario, tolerancia, descanso y horas extra.
- Correccion manual del ultimo marcaje desde Reportes.
- Gestion de personal, areas y puestos.
- Perfil administrativo con foto e idioma.
- Soporte para tema claro/oscuro e idioma ES/EN.
- Base de datos SQLite con esquema y datos iniciales.
- Integracion opcional con hardware en Raspberry Pi: rele, cerradura, buzzer y PIR.

## Tecnologias

- Python 3.10 recomendado.
- CustomTkinter para la interfaz grafica.
- OpenCV contrib para camara y procesamiento de imagen.
- MediaPipe para deteccion rapida de rostro.
- face-recognition y dlib para embeddings y comparacion facial.
- NumPy, Pillow, SciPy, Matplotlib y tkcalendar.
- SQLite para persistencia local.

## Estructura del proyecto

```text
sistema-biometrico/
|-- app/
|   |-- camara/                 # Lectura de camara y captura en segundo plano
|   |-- database/               # Conexion SQLite y schema_and_data.sql
|   |-- detection/              # Pipeline de deteccion/reconocimiento en vivo
|   |-- hardware/               # Rele, buzzer, GPIO y pruebas de hardware
|   |-- recognition/            # Registro, embeddings y comparacion facial
|   |-- services/               # Servicios de usuarios, areas, puestos y tema
|   |-- views/                  # Pantallas CustomTkinter
|-- deploy/                     # Servicio systemd para Raspberry Pi
|-- scripts/                    # Scripts de instalacion/despliegue
|-- main.py                     # Punto de entrada de la aplicacion
|-- init_db.py                  # Inicializacion de base de datos
|-- requirements.txt            # Dependencias Python
|-- GUIA_CONFIGURACION.md       # Guia operativa de instalacion y soporte
```

## Instalacion rapida

```powershell
cd C:\Users\vinel\Documents\sistema-biometrico
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si ya tienes el entorno creado:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Dependencias clave

El proyecto usa esta combinacion probada:

```text
customtkinter==5.2.2
opencv-contrib-python==4.10.0.84
numpy==1.26.4
face-recognition==1.3.0
Pillow==10.0.1
dlib==20.0.1
mediapipe==0.10.14
```

Importante: no subir `numpy` a 2.x en este proyecto, porque puede romper `face_recognition/dlib` con el error `Unsupported image type, must be 8bit gray or RGB image`.

## Base de datos

La base se crea y verifica automaticamente al iniciar la app. Tambien puedes inicializarla manualmente:

```powershell
python init_db.py
```

Ruta de la base:

```text
app/database/sistema_biometrico.db
```

El esquema y datos base viven en:

```text
app/database/schema_and_data.sql
```

Tablas principales:

- `usuario_rol`
- `facultad`
- `carrera`
- `usuario`
- `biometria`
- `registro_acceso`

## Ejecucion

```powershell
.\venv\Scripts\Activate.ps1
python main.py
```

La aplicacion inicia en la terminal biometrica. Desde ahi puedes ir al login con el boton `Salir` y entrar al dashboard. Las credenciales de prueba actuales son:

```text
usuario: 1
contrasena: 1
```

## Flujo de uso

1. Iniciar la aplicacion con `python main.py`.
2. Usar la terminal biometrica para validar accesos.
   La terminal solicita un parpadeo durante el escaneo para comprobar que hay
   una persona presente y no una fotografia estatica.
3. Presionar `Salir` para entrar al login administrativo.
4. Iniciar sesion con las credenciales de prueba.
5. Administrar personal, areas, puestos y ajustes desde el dashboard.
6. Registrar biometria desde el formulario de personal.
7. Revisar metricas y ultimos accesos en el panel principal.

## Rendimiento de camara

La camara usa lectura en segundo plano para evitar frames viejos. La deteccion de rostro usa MediaPipe cuando esta instalado; si no esta disponible, el sistema cae al detector HOG de `face_recognition`.

Recomendaciones:

- Cerrar otras aplicaciones que usen la camara.
- Usar buena iluminacion frontal.
- Mantener una sola cara visible.
- Evitar actualizar `numpy` y OpenCV fuera de las versiones del `requirements.txt`.
- Si la Raspberry Pi necesita mayor fluidez, aumentar el intervalo del
  reconocimiento pesado, por ejemplo: `FACE_RECOGNITION_INTERVAL=12`.

## Datos sensibles

Estos archivos contienen informacion local sensible y no deben subirse al repositorio:

- `encodings.json`: embeddings/representaciones numericas de rostros.
- `logs_accesos.json`: historial de accesos e intentos.
- `app/data/perfil_usuario.json`: datos de perfil administrativo.
- `app/data/fotos/`: fotos de perfil.
- `app/database/sistema_biometrico.db`: base local con usuarios y registros.

Se incluyen archivos `.example.json` para documentar la estructura sin exponer datos reales.

## Solucion de problemas

### La camara no muestra video

- Verifica que otra aplicacion no este usando la camara.
- Reinstala dependencias con `pip install -r requirements.txt`.
- Ejecuta `python -m pip check`.
- Si aparece `Unsupported image type`, confirma:

```powershell
python -c "import numpy, cv2; print(numpy.__version__, cv2.__version__)"
```

Debe mostrar `numpy 1.26.4` y OpenCV `4.10.0`.

### MediaPipe muestra advertencias

Mensajes como `TensorFlow Lite XNNPACK delegate` o `Feedback manager...` son advertencias normales de MediaPipe. No bloquean la camara.

### Error instalando dlib o face-recognition

En Windows, usa Python 3.10 y actualiza pip:

```powershell
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

Si sigue fallando, instala Visual Studio Build Tools con soporte para C++.

## Raspberry Pi y hardware

El proyecto incluye soporte opcional para cerradura, rele, buzzer y PIR. Consulta [GUIA_CONFIGURACION.md](GUIA_CONFIGURACION.md) para cableado, variables de entorno y despliegue con systemd.

## Estado actual

- Base de datos: funcional.
- Interfaz grafica: funcional.
- Dashboard: funcional.
- Gestion de personal, areas y puestos: funcional.
- Terminal biometrica: funcional con MediaPipe/OpenCV.
- Registro de accesos: funcional.
- Hardware Raspberry Pi: preparado con modo simulacion y servicio systemd.

## Licencia

Proyecto de uso educativo/universitario.
