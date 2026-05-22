# app/services/traductor.py
import argostranslate.package
import argostranslate.translate

class TraductorOffline:
    def __init__(self):
        self.model = None 

    def procesar_texto(self, texto, idioma_destino):
        if idioma_destino == "es":
            return texto
            
        traducciones_fijas = {
            # --- TUS TRADUCCIONES ORIGINALES ---
            "Panel de Control": "Control Panel",
            "🏠   Panel de Control": "🏠   Control Panel",
            "Gestión de Usuarios": "User Management",
            "👥   Gestión de Usuarios": "👥   User Management",
            "Gestión de Facultades": "Faculty Management",
            "🏫   Gestión de Facultades": "🏫   Faculty Management",
            "Gestión de Carreras": "Career Management",
            "📚   Gestión de Carreras": "📚   Career Management",
            "Configuración Cuenta": "Account Setup",
            "⚙️   Configuración Cuenta": "⚙️   Account Setup",
            "Cerrar Sesión": "Logout",
            "Logout": "Logout",
            "Agregar Facultad": "Add Faculty",
            "Agregar Usuario": "Add User",
            "Agregar Carrera": "Add Career",
            "Estado": "Status",
            "Acciones": "Actions",
            "Activa": "Active",
            "Inactiva": "Inactive",
            "ACTIVA": "ACTIVE",
            "INACTIVA": "INACTIVE",
            "ACTIVO": "ACTIVE",
            "INACTIVO": "INACTIVE",
            "Buscar usuario...": "Search user...",
            "Buscar carrera por nombre...": "Search career by name...",
            "ESTUDIANTE": "STUDENT",
            "ADMINISTRADOR": "ADMINISTRATOR",
            "Tipo de Usuario": "User Type",
            "Facultad": "Faculty",
            "Carrera": "Career",
            "Nombres": "First Name",
            "Apellido Paterno": "Paternal Last Name",
            "Apellido Materno": "Maternal Last Name",
            "cuenta": "Account / ID",
            "correo": "Email Address",
            "Teléfono": "Phone",
            "Nombre de la Facultad": "Faculty Name",
            "Nombre de la Carrera": "Career Name",
            "Status": "Status",
            "Información Personal": "Personal Info",
            "Identificación": "Identification",
            "Personal Info": "Personal Info",
            "Identification": "Identification",
            "Nuevo Registro": "New User",
            "New User": "New User",
            "Editar Registro": "Edit Profile",
            "Editar Registro...": "Editing Profile...",
            "Crear Nueva Facultad": "Create New Faculty",
            "Nueva Carrera": "New Career",
            "Configura tu perfil y preferencias": "Configure your profile and preferences",
            "Personalización": "Customization",
            "Modo Oscuro": "Dark Mode",
            "Idioma del Sistema": "System Language",
            "Detalles de la Cuenta": "Account Details",
            "Actualizar Foto": "Update Photo",
            "ADMINISTRADOR DEL SISTEMA": "SYSTEM ADMINISTRATOR",
            "Biometric Control": "Biometric Control",
            "Guardar": "Save",
            "Guardar Facultad": "Save Faculty",
            "Guardar Carrera": "Save Career",
            "Cancelar": "Cancel",
            "Registrar Biometría": "Register Biometrics",
            "Register Biometrics": "Register Biometrics",
            "¿Está seguro de eliminar al usuario?": "Are you sure you want to delete this user?",
            "Esta acción desactivará al usuario permanentemente.": "This will deactivate the user permanently.",
            "Confirmar y Borrar": "Confirm and Delete",
            "▸  RECONOCIMIENTO FACIAL  ◂": "▸  FACIAL RECOGNITION  ◂",
            "SISTEMA ACTIVO": "SYSTEM ACTIVE",
            "ESPERANDO DETECCIÓN...": "WAITING FOR DETECTION...",
            "Iniciando cámara...": "Starting camera...",
            "Sistema Biométrico v2.0": "Biometric System v2.0",
            "Acceso Seguro": "Secure Access",
            "Cifrado AES-256": "AES-256 Encryption",
            "REGISTRANDO BIOMETRÍA": "REGISTERING BIOMETRICS",
            "COLOQUE SU ROSTRO FRENTE A LA CÁMARA": "PLACE YOUR FACE IN FRONT OF THE CAMERA",
            "LISTO": "READY",
            "👥 Gestión de Usuarios": "👥 User Management",
            "➕ Agregar Usuario": "➕ Add User",
            "🔍 Buscar usuario...": "🔍 Search user...",
            "⚙️ Filtrar ⌵": "⚙️ Filter ⌵",
            "👤 Información Personal": "👤 Personal Information",
            "🆔 Identificación": "🆔 Identification",
            "📷 Registrar Biometría": "📷 Register Biometrics",
            "❌ Cancelar": "❌ Cancel",
            "💾 Guardar": "💾 Save",
            "✔ Biometría guardada temporalmente": "✔ Biometrics saved temporarily",
            "✔ Biometría registrada": "✔ Biometrics registered",
            "Administra las unidades académicas del sistema": "Manage system academic units",
            "No hay facultades registradas": "No faculties registered",
            "Editar Facultad": "Edit Faculty",
            "¿Está seguro de eliminar esta facultad?": "Are you sure you want to delete this faculty?",
            "Se eliminará": "Will be deleted",

            # --- NUEVAS PALABRAS FALTANTES DE LAS CAPTURAS ---
            # Textos del Dashboard
            "Resumen general y actividad reciente": "General overview and recent activity",
            "Total Registros": "Total Records",
            "Accesos Hoy": "Accesses Today",
            "Autorizados": "Authorized",
            "Denegados": "Denied",
            "Tendencia de Accesos por Hora": "Hourly Access Trend",
            "Fecha:": "Date:",
            "Registro de últimos accesos": "Recent access log",
            
            # Encabezados de Tablas (Usuarios y Carreras)
            "FOTOGRAFÍA": "PHOTOGRAPH",
            "INFORMACIÓN": "INFORMATION",
            "ESTADO": "STATUS",
            "ACCIONES": "ACTIONS",
            "NOMBRE": "NAME",
            "FACULTAD": "FACULTY",
            
            # Badges y Roles (Manejo de minúsculas/capitalización)
            "Estudiante": "Student",
            "Administrador": "Administrator",
            
            # Títulos con iconos que podrían no estar mapeados
            "🎓 Gestión de Carreras": "🎓 Career Management",
            "🎓  Gestión de Carreras": "🎓  Career Management",
            "🎓   Gestión de Carreras": "🎓   Career Management",
            
            # --- LOGIN Y ACCOUNT SETUP ---
            "Sistema de Reconocimiento\nFacial": "Facial Recognition\nSystem",
            "Sistema de Reconocimiento Facial": "Facial Recognition System",
            "Ingresa tus credenciales para continuar": "Enter your credentials to continue",
            "CORREO ÓNICO": "EMAIL ADDRESS",
            "Escribe tu correo": "Enter your email",
            "CONTRASEÑA": "PASSWORD",
            "Escribe tu contraseña": "Enter your password",
            "INICIAR SESIÓN": "SIGN IN",
            "Credenciales incorrectas.": "Incorrect credentials.",
            
            # Account/Customization
            "Account Setup": "Account Setup",
            "Configure your profile and preferences": "Configure your profile and preferences",
            "Customization": "Customization",
            "System Language": "System Language",
            "Account Details": "Account Details",
            "First Name": "First Name",
            "Email Address": "Email Address",
            "Phone": "Phone",
            "Faculty": "Faculty",
            "Editar Perfil": "Edit Profile",
            
            # Modales y confirmaciones
            "¿Desactivar esta carrera?": "Deactivate this career?",
            "¿Desactivar esta facultad?": "Deactivate this faculty?",
            "Desactivar": "Deactivate",
            "Reactivar": "Reactivate",
            "🔄 Activar": "🔄 Activate",
            
            # Filtros
            "Rol": "Role",
            "Todos": "All",
            "DOCENTE": "TEACHER",
            "TRABAJADOR": "STAFF",
            
            # Otros textos faltantes
            "Buscar facultad por nombre...": "Search faculty by name...",
            "Nombre de Facultad": "Faculty Name",
            "Administra las unidades académicas del sistema": "Manage system academic units",
            "No hay facultades registradas": "No faculties registered",
            "Editar Facultad": "Edit Faculty",
            "Nombre de la Carrera": "Career Name",
            "Seleccionar facultad": "Select faculty",
            "Active": "Active",
            "Inactive": "Inactive",
        }

        # Búsqueda exacta (limpiando espacios por si acaso)
        clave = texto.strip()
        if clave in traducciones_fijas:
            return traducciones_fijas[clave]

        # Respaldo IA (Argos Translate)
        try:
            if self.model:
                return self.model.translate(texto)
        except:
            pass
            
        return texto

if __name__ == "__main__":
    pass