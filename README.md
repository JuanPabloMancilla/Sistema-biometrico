# Sistema Biométrico Facial - Control de Acceso

Proyecto universitario desarrollado en Python para la detección y reconocimiento facial utilizando visión por computadora.

## 📋 Descripción

Este sistema permite capturar rostros mediante una cámara, procesarlos y almacenarlos en una base de datos para su posterior reconocimiento facial en tiempo real. Incluye una interfaz gráfica completa para administración de usuarios, facultades y carreras.

## ✨ Características

- 🔐 **Control de acceso biométrico** con reconocimiento facial
- 👥 **Gestión completa de usuarios** (estudiantes, docentes, administradores)
- 🏫 **Organización académica** (facultades y carreras)
- 📊 **Base de datos SQLite** para almacenamiento persistente
- 🎨 **Interfaz gráfica moderna** con CustomTkinter
- 📈 **Registro de accesos** con historial completo

## 🛠️ Tecnologías utilizadas

- **Python 3.8+**
- **OpenCV** - Procesamiento de imágenes y visión por computadora
- **face-recognition** - Biblioteca de reconocimiento facial
- **SQLite** - Base de datos ligera y embebida
- **CustomTkinter** - Interfaz gráfica moderna
- **NumPy** - Computación numérica
- **Pillow** - Procesamiento de imágenes

## 📁 Estructura del proyecto

```
sistema-biometrico/
├── app/
│   ├── camara/
│   │   └── camara.py              # Control de cámara
│   ├── database/
│   │   └── database.py            # Conexión y configuración BD
│   ├── detection/
│   │   └── detector_rostro.py     # Detección de rostros
│   ├── recognition/
│   │   ├── embedding_generator.py # Generación de embeddings
│   │   ├── face_detector.py       # Detector facial
│   │   ├── matcher.py             # Comparación de rostros
│   │   ├── recognition_service.py # Servicio de reconocimiento
│   │   └── registro_usuario.py    # Registro de usuarios
│   ├── services/
│   │   ├── biometria.py           # Gestión datos biométricos
│   │   ├── carrera.py             # Gestión carreras
│   │   ├── facial_service.py      # Servicios faciales
│   │   ├── facultad.py            # Gestión facultades
│   │   ├── registro_acceso.py     # Registro de accesos
│   │   ├── usuario.py             # Gestión usuarios
│   │   └── usuario_rol.py         # Gestión roles
│   └── views/
│       ├── account_view.py        # Vista cuenta
│       ├── app_context.py         # Contexto aplicación
│       ├── dashboard_view.py      # Panel principal
│       ├── home_view.py           # Vista inicio
│       ├── landing_view.py        # Vista landing
│       ├── login_view.py          # Vista login
│       ├── terminal_view.py       # Vista terminal
│       └── user_management_view.py # Gestión usuarios
├── init_db.py                     # Inicialización base de datos
├── main.py                        # Archivo principal
├── requirements.txt               # Dependencias Python
└── README.md                      # Este archivo
```

## Seguridad de datos sensibles

Este proyecto trabaja con informacion biometrica y registros de acceso, por lo que algunos archivos se generan solo de forma local y no deben subirse al repositorio:

- `encodings.json`: contiene representaciones numericas de rostros registrados. Aunque no sea una fotografia, sigue siendo informacion biometrica sensible.
- `logs_accesos.json`: contiene historial de accesos, fechas, horas e intentos de ingreso, informacion que puede revelar patrones de uso o actividad de personas.

Por seguridad, estos archivos estan incluidos en `.gitignore`. En su lugar se incluyen archivos de ejemplo vacios:

- `encodings.example.json`
- `logs_accesos.example.json`

Esto permite documentar la estructura esperada sin exponer datos reales de usuarios, credenciales, registros internos o informacion perteneciente a una institucion/equipo.

## 🚀 Instalación y Configuración

### 1. 📥 Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd sistema-biometrico
```

### 2. 🐍 Crear entorno virtual

```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. 📦 Instalar dependencias

```powershell
pip install -r requirements.txt
```

#### ⚠️ Dependencias principales:

- **customtkinter** - Interfaz gráfica moderna
- **opencv-python** - Procesamiento de imágenes
- **numpy** - Computación numérica
- **face-recognition** - Reconocimiento facial
- **Pillow** - Manipulación de imágenes
- **dlib** - Biblioteca base para face-recognition

#### 🔧 Instalación manual (si es necesario):

```powershell
# Instalar OpenCV
pip install opencv-python==4.8.1.78

# Instalar NumPy
pip install numpy==1.24.3

# Instalar face-recognition (incluye dlib)
pip install face-recognition==1.3.0

# Instalar CustomTkinter
pip install customtkinter==5.2.2

# Instalar Pillow
pip install Pillow==10.0.1
```

### 4. 🗄️ Configurar base de datos

#### Crear la base de datos:
```powershell
python init_db.py
```

#### Acceder a la base de datos con SQLite Browser:

1. **Descargar SQLite Browser**: https://sqlitebrowser.org/
2. **Abrir la aplicación**
3. **File → Open Database**
4. **Seleccionar archivo**: `app/database/sistema_biometrico.db`
5. **¡Listo!** Puedes ver todas las tablas y datos

#### Tablas principales:
- `usuario_rol` - Roles de usuario
- `facultad` - Facultades académicas
- `carrera` - Carreras disponibles
- `usuario` - Datos de usuarios
- `biometria` - Datos biométricos
- `registro_acceso` - Historial de accesos

### 5. ▶️ Ejecutar la aplicación

```powershell
python main.py
```

## 👤 Usuarios de prueba

Para probar el sistema, puedes crear usuarios desde SQLite Browser:

### Administrador de ejemplo:
```sql
INSERT INTO usuario (nombre, a_paterno, a_materno, fecha_registro, id_rol, id_facultad, id_carrera)
VALUES ('Juan Pablo', 'Mancilla', 'Rodriguez', datetime('now'), 1, 4, 35);
```

## 🎯 Uso del sistema

1. **Login**: Inicia sesión con credenciales de usuario
2. **Dashboard**: Panel principal con opciones disponibles
3. **Gestión de usuarios**: Crear, editar y eliminar usuarios
4. **Reconocimiento facial**: Capturar y registrar rostros
5. **Control de acceso**: Verificar identidad en tiempo real

## 🔧 Solución de problemas

### Error al instalar face-recognition:
```powershell
# Instalar CMake primero (Windows)
pip install cmake

# Instalar dlib por separado
pip install dlib==19.24.2

# Luego face-recognition
pip install face-recognition
```

### Error de cámara:
- Asegúrate de que la cámara esté conectada
- Verifica permisos de acceso a cámara
- Prueba con diferentes índices de cámara (0, 1, 2...)

### Base de datos corrupta:
```powershell
# Recrear base de datos
python init_db.py
```

## 📊 Estado del proyecto

- ✅ **Base de datos**: Configurada y poblada
- ✅ **Interfaz gráfica**: Completa y funcional
- ✅ **Reconocimiento facial**: Implementado
- ✅ **Gestión de usuarios**: Funcional
- 🔄 **Registro biométrico**: En desarrollo
- 🔄 **Control de acceso**: En desarrollo

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de uso educativo y universitario.


---

**¡El sistema biométrico está listo para usar!** 🎉



