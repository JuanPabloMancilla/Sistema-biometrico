# 🗄️ Guía de Configuración - Sistema Biométrico Facial

## 📋 Cómo acceder a la base de datos con SQLite Browser

### 1. 📥 Descargar SQLite Browser
Ve a: https://sqlitebrowser.org/ y descarga la versión para Windows.

### 2. 🔓 Abrir la base de datos
- Abre SQLite Browser
- Ve a **File → Open Database**
- Navega a: `c:\xampp\htdocs\sistema-biometrico\app\database\sistema_biometrico.db`
- ¡Listo! Verás todas las tablas del sistema

### 3. 📊 Explorar las tablas
En la pestaña **"Browse Data"** encontrarás:
- `usuario_rol` - Roles (admin, docente, estudiante)
- `facultad` - Facultades académicas
- `carrera` - Carreras disponibles
- `usuario` - Datos de usuarios
- `biometria` - Datos biométricos
- `registro_acceso` - Historial de accesos

## 📦 Dependencias necesarias y comandos de instalación

### ⚠️ Importante: Activar entorno virtual primero
```powershell
# Activar el entorno virtual
& c:\xampp\htdocs\sistema-biometrico\.venv\Scripts\Activate.ps1
```

### 📚 Dependencias principales:

#### 1. **NumPy** - Computación numérica
```powershell
pip install numpy==1.24.3
```

#### 2. **OpenCV (cv2)** - Procesamiento de imágenes
```powershell
pip install opencv-python==4.8.1.78
```

#### 3. **face-recognition** - Reconocimiento facial
```powershell
# Esta es la más compleja de instalar
pip install face-recognition==1.3.0

# Si hay errores, instala dlib primero:
pip install dlib==19.24.2
```

#### 4. **CustomTkinter** - Interfaz gráfica moderna
```powershell
pip install customtkinter==5.2.2
```

#### 5. **Pillow** - Manipulación de imágenes
```powershell
pip install Pillow==10.0.1
```

### 🚀 Instalación automática (recomendado):
```powershell
# Instalar todas las dependencias de una vez
pip install -r requirements.txt
```

## 🛠️ Comandos para usar el proyecto

### 1. 🗄️ Crear/Inicializar base de datos
```powershell
python init_db.py
```

### 2. ▶️ Ejecutar la aplicación
```powershell
python main.py
```

### 3. 🔍 Verificar datos en BD (opcional)
```powershell
python -c "from app.database.database import get_connection; conn = get_connection(); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM usuario'); print(f'Usuarios: {cursor.fetchone()[0]}'); conn.close()"
```

## 👤 Crear usuarios de prueba

### Administrador (tu usuario):
```sql
INSERT INTO usuario (nombre, a_paterno, a_materno, fecha_registro, id_rol, id_facultad, id_carrera)
VALUES ('Juan Pablo', 'Mancilla', 'Rodriguez', datetime('now'), 1, 4, 35);
```

## 🔧 Solución de problemas comunes

### ❌ Error: "ModuleNotFoundError: No module named 'cv2'"
```powershell
pip install opencv-python==4.8.1.78
```

### ❌ Error: "face_recognition no se instala"
```powershell
# Windows: Instalar CMake primero
pip install cmake
pip install dlib==19.24.2
pip install face-recognition==1.3.0
```

### ❌ Error: "No se puede acceder a la cámara"
- Verifica que la cámara esté conectada
- Prueba cambiando el índice de cámara en el código (0, 1, 2...)

### ❌ Error: "Foreign Key constraint failed"
- Asegúrate de ejecutar las inserciones en el orden correcto
- Verifica que existan las facultades antes de insertar carreras

## 📊 Referencias de IDs

### Roles:
- 1 = admin

### Facultades:
- 1 = Facultad de Ciencias Marinas (FACIMAR)
- 2 = Facultad de Contabilidad y Administración (FCAM)
- 3 = Escuela de Enfermería
- 4 = Facultad de Ingeniería Electromecánica (FIE)

### Carreras (ejemplos):
- 1 = Ingeniería Oceánica (IO)
- 2 = Licenciatura en Sustentabilidad Marina
- 3 = Contador Público
- 4 = Licenciatura en Administración
- 35 = Ingeniería de Software (IS)

## 👤 Sistema de Roles

### ⚠️ **Importante**: Actualmente solo existe el rol "admin"

El sistema está diseñado para múltiples roles (admin, docente, estudiante, etc.), pero **inicialmente solo existe el rol de administrador**.

### 📋 Roles disponibles actualmente:
- **1 = admin** - Administrador del sistema (único rol disponible)

### 🔄 Para agregar más roles:
El sistema tiene la infraestructura para múltiples roles a través de la tabla `usuario_rol`, pero actualmente solo está configurado el rol de admin. Si necesitas agregar roles adicionales (docente, estudiante, etc.), puedes insertarlos manualmente en SQLite Browser:

```sql
-- Agregar rol docente
INSERT INTO usuario_rol (nombre, descripcion) VALUES ('docente', 'Docente');

-- Agregar rol estudiante
INSERT INTO usuario_rol (nombre, descripcion) VALUES ('estudiante', 'Estudiante');
```

### 💡 Nota sobre asignación de roles:
La aplicación probablemente tenga una interfaz para gestionar roles, pero actualmente solo el rol "admin" está disponible en el sistema.

## 🗄️ Configuración de base de datos con datos incluidos

Si quieres una base de datos con datos de prueba ya incluidos (facultades, carreras, usuarios, etc.), importa el archivo `schema_and_data.sql`:

### 1. 📥 Abrir SQLite Browser
- Abre SQLite Browser
- Ve a **File → Import → Database from SQL file**
- Selecciona: `c:\xampp\htdocs\sistema-biometrico\app\database\schema_and_data.sql`
- Elige un nombre para la nueva BD (ej: `sistema_biometrico_con_datos.db`)

### 2. 🔄 Reemplazar la base de datos
- Copia el archivo generado al directorio `app/database/`
- Renómbralo a `sistema_biometrico.db` (reemplaza el existente)

¡Listo! Tendrás la BD con esquema y datos de prueba.

---

**¡Con esta guía tienes todo lo necesario para configurar y usar el sistema biométrico!** 🎉