# app/context.py
TRADUCCIONES = {
    
        # Agregar en la seccion TERMINAL BIOMoTRICA
    "ESCANEANDO":                           {"en": "SCANNING"},
    "ANALIZANDO RASGOS BIOMETRICOS":        {"en": "ANALYZING BIOMETRIC FEATURES"},
    "ACCESO AUTORIZADO":                    {"en": "ACCESS AUTHORIZED"},   # ya existe
    "ACCESO DENEGADO":                      {"en": "ACCESS DENIED"},        # ya existe
    "USUARIO NO REGISTRADO":                {"en": "UNREGISTERED USER"},    # ya existe
    "MULTIPLES ROSTROS DETECTADOS":         {"en": "MULTIPLE FACES DETECTED"},
    "SOLO UN USUARIO A LA VEZ":             {"en": "ONE USER AT A TIME"},
    "SIN CAMARA":                           {"en": "NO CAMERA"},
    "NO SE DETECTO NINGUN DISPOSITIVO":     {"en": "NO DEVICE DETECTED"},
    "ACERQUESE A LA CAMARA":                {"en": "MOVE CLOSER TO THE CAMERA"},
    "ROSTRO DEMASIADO LEJOS O PEQUENO":     {"en": "FACE TOO FAR OR SMALL"},
    "MEJORE LA ILUMINACION":                {"en": "IMPROVE LIGHTING"},
    "AMBIENTE MUY OSCURO - ENCIENDA UNA LUZ": {"en": "TOO DARK - TURN ON A LIGHT"},
    "POSICIONE SU ROSTRO":                  {"en": "POSITION YOUR FACE"},
    "MIRANDO HACIA LA CAMARA":              {"en": "LOOKING AT THE CAMERA"},
    "BIENVENIDO":                           {"en": "WELCOME"},
    "ACCESO CONCEDIDO":                     {"en": "ACCESS GRANTED"},
    "REGISTRANDO BIOMETRIA":                {"en": "REGISTERING BIOMETRICS"},
    "COLOQUE SU ROSTRO FRENTE A LA CAMARA": {"en": "PLACE YOUR FACE IN FRONT OF THE CAMERA"},
    "USUARIO YA REGISTRADO":                {"en": "USER ALREADY REGISTERED"},
    "ESTE ROSTRO YA EXISTE EN EL SISTEMA":  {"en": "THIS FACE ALREADY EXISTS IN THE SYSTEM"},
    "ESPERANDO DETECCION...":               {"en": "WAITING FOR DETECTION..."},
    "Iniciando camara...":                  {"en": "Starting camera..."},
    "Sistema Biometrico v2.0":              {"en": "Biometric System v2.0"},
    "RECONOCIMIENTO FACIAL":                {"en": "FACIAL RECOGNITION"},
    "ANALIZANDO RASGOS BIOMETRICOS":        {"en": "ANALYZING BIOMETRIC FEATURES"},
    "ANALIZANDO RASGOS BIOMETRICOS":        {"en": "ANALYZING BIOMETRIC FEATURES"},

    # --------------------------------------------------------------
    # TABLA DE ACCESOS  motivos y resultados
    # --------------------------------------------------
    "Acceso denegado":              {"en": "Access denied"},
    "Usuario inactivo":             {"en": "Inactive user"},
    "Usuario no identificado":      {"en": "User not identified"},
    "AUTORIZADO":                   {"en": "AUTHORIZED"},
    "DENEGADO":                     {"en": "DENIED"},

    # Tabla de accesos  textos faltantes
    "Sin cuenta":                   {"en": "No account"},
    "Sin correo":                   {"en": "No email"},
    "USUARIO NO REGISTRADO":        {"en": "UNREGISTERED USER"},

    # Cat�logo usuarios � badges de rol
    "Estudiante":                   {"en": "Student"},
    "Docente":                      {"en": "Teacher"},
    "Trabajador":                   {"en": "Worker"},
    "ESTUDIANTE":                   {"en": "STUDENT"},
    "DOCENTE":                      {"en": "TEACHER"},
    "TRABAJADOR":                   {"en": "WORKER"},

    # Cat�logo usuarios � estado
    "? ACTIVO":                     {"en": "? ACTIVE"},
    "? INACTIVO":                   {"en": "? INACTIVE"},
    "ACTIVO":                       {"en": "ACTIVE"},
    "INACTIVO":                     {"en": "INACTIVE"},

     # --------------------------------------------------------------
    # NAVEGACI�N / SIDEBAR
    # --------------------------------------------------------------
    "Panel de Control":                             {"en": "Control Panel"},
    "??   Panel de Control":                        {"en": "??   Control Panel"},
    "?? Panel de Control":                          {"en": "?? Control Panel"},
    "Gestión de Usuarios":                          {"en": "User Management"},
    "Gestion de Usuarios":                          {"en": "User Management"},
    "??   Gestión de Usuarios":                     {"en": "??   User Management"},
    "?? Gestion de Usuarios":                       {"en": "?? User Management"},
    "Gestión de Facultades":                        {"en": "Faculty Management"},
    "Gestion de Facultades":                        {"en": "Faculty Management"},
    "??   Gestión de Facultades":                   {"en": "??   Faculty Management"},
    "?? Gestion de Facultades":                     {"en": "?? Faculty Management"},
    "Gestión de Carreras":                          {"en": "Career Management"},
    "Gestion de Carreras":                          {"en": "Career Management"},
    "??   Gestión de Carreras":                     {"en": "??   Career Management"},
    "?? Gestion de Carreras":                       {"en": "?? Career Management"},
    "Configuración":                                {"en": "Settings"},
    "Configuración Cuenta":                         {"en": "Account Settings"},
    "??   Configuración Cuenta":                    {"en": "??   Account Settings"},
    "?? Configuración Cuenta":                      {"en": "?? Account Settings"},
    "Cerrar Sesión":                                {"en": "Log Out"},
    "?? Cerrar Sesión":                             {"en": "?? Log Out"},
    "ADMINISTRADOR":                                {"en": "ADMINISTRATOR"},
    "Control Biométrico":                           {"en": "Biometric Control"},

    # --------------------------------------------------------------
    # DASHBOARD � encabezado y stats
    # --------------------------------------------------------------
    "??  Panel de Control":                         {"en": "??  Control Panel"},
    "Resumen general y actividad reciente":         {"en": "General summary and recent activity"},
    "Total Registros":                              {"en": "Total Records"},
    "Accesos Hoy":                                  {"en": "Today's Access"},
    "Autorizados":                                  {"en": "Authorized"},
    "Denegados":                                    {"en": "Denied"},

    # DASHBOARD � gr�fica
    "?? Tendencia de Accesos por Hora":             {"en": "?? Access Trend by Hour"},
    "Fecha:":                                       {"en": "Date:"},
    "Accesos por hora":                             {"en": "Access by hour"},
    "Sin accesos registrados en esta fecha":        {"en": "No access records for this date"},

    # DASHBOARD � tabla �ltimos accesos
    "Registro de últimos accesos":                  {"en": "Latest access log"},
    "Sin accesos registrados":                      {"en": "No access records found"},

    # DASHBOARD � filtro roles
    "?? Rol:":                                      {"en": "?? Role:"},
    "Todos":                                        {"en": "All"},
    "?? Filtrar ?":                                 {"en": "?? Filter ?"},
    "?? Filtrar ?":                                 {"en": "?? Filter ?"},
    "Filtrar ?":                                    {"en": "Filter ?"},
    "Filtrar ?":                                    {"en": "Filter ?"},


    # --------------------------------------------------------------
    # GESTI�N DE USUARIOS � tabla
    # --------------------------------------------------------------
    "?? Gestión de Usuarios":                       {"en": "?? User Management"},
    "Agregar Usuario":                              {"en": "Add User"},
    "? Agregar Usuario":                           {"en": "? Add User"},
    "Buscar usuario...":                            {"en": "Search user..."},
    "No hay usuarios registrados":                  {"en": "No registered users"},
    "FOTOGRAFA":                                   {"en": "PHOTO"},
    "INFORMACIÓN":                                  {"en": "INFORMATION"},
    "ESTADO":                                       {"en": "STATUS"},
    "ACCIONES":                                     {"en": "ACTIONS"},

    # GESTI�N DE USUARIOS � formulario secciones
    "Editar Registro":                              {"en": "Edit Record"},
    "?? Editar Registro":                           {"en": "?? Edit Record"},
    "Nuevo Registro":                               {"en": "New Record"},
    "? Nuevo Registro":                            {"en": "? New Record"},
    "?? Información Personal":                      {"en": "?? Personal Information"},
    "Información Personal":                         {"en": "Personal Information"},
    "?? Identificación":                            {"en": "?? Identification"},
    "Identificación":                               {"en": "Identification"},
    "?? Estado del usuario":                        {"en": "?? User Status"},
    "Usuario activo":                               {"en": "Active user"},

    # GESTI�N DE USUARIOS � labels de campos
    "Nombres":                                      {"en": "First Name(s)"},
    "Apellido Paterno":                             {"en": "Last Name"},
    "Apellido Materno":                             {"en": "Second Last Name"},
    "cuenta":                                       {"en": "account"},
    "correo":                                       {"en": "email"},

    # GESTI�N DE USUARIOS � biometr�a
    "Registrar Biometría":                          {"en": "Register Biometrics"},
    "?? Registrar Biometría":                       {"en": "?? Register Biometrics"},
    "Abriendo cámara...":                           {"en": "Opening camera..."},
    "?? Abriendo cámara...":                        {"en": "?? Opening camera..."},
    "Biometría registrada":                         {"en": "Biometrics registered"},
    "? Biometría registrada":                       {"en": "? Biometrics registered"},
    "Biometría requerida":                          {"en": "Biometrics required"},
    "? Biometría requerida":                        {"en": "? Biometrics required"},
    "Corrige los datos primero":                    {"en": "Fix the data first"},
    "? Corrige los datos primero":                  {"en": "? Fix the data first"},

    # GESTI�N DE USUARIOS � modal
    "🗑️Desactivar este usuario?":                    {"en": "Desactivate this user?"},
    "El usuario perderá acceso al sistema.":        {"en": "The user will lose system access."},
    "Desactivar":                                   {"en": "Desactivate"},
    "??? Desactivar":                                {"en": "??? Desactivate"},
    "🔄Activar este usuario?":                       {"en": "Activate this user?"},
    "El usuario recuperará acceso al sistema.":     {"en": "The user will regain system access."},
    "Activar":                                      {"en": "Activate"},
    "?? Activar":                                   {"en": "?? Activate"},
    "Cancelar":                                     {"en": "Cancel"},
    "? Cancelar":                                  {"en": "? Cancel"},

    # --------------------------------------------------------------
    # GESTI�N DE FACULTADES � tabla
    # --------------------------------------------------------------
    "?? Gestión de Facultades":                     {"en": "?? Faculty Management"},
    "??   Gestión de Facultades":                   {"en": "??   Faculty Management"},
    "Administra las unidades académicas":           {"en": "Manage academic units"},
    "Administra las unidades académicas del sistema": {"en": "Manage the system's academic units"},
    "Agregar Facultad":                             {"en": "Add Faculty"},
    "? Agregar Facultad":                          {"en": "? Add Faculty"},
    "Buscar facultad por nombre...":                {"en": "Search faculty by name..."},
    "No hay facultades registradas":                {"en": "No registered faculties"},
    "NOMBRE DE LA FACULTAD":                        {"en": "FACULTY NAME"},
    "ACTIVA":                                       {"en": "ACTIVE"},
    "INACTIVA":                                     {"en": "INACTIVE"},

    # GESTI�N DE FACULTADES � modal
    "🗑️Desactivar esta facultad?":                   {"en": "Desactivate this faculty?"},
    "La facultad dejará de estar disponible.":      {"en": "The faculty will no longer be available."},
    "Activar esta facultad?":                      {"en": "Activate this faculty?"},
    "La facultad volver a estar disponible.":      {"en": "The faculty will be available again."},

    # GESTI�N DE FACULTADES � formulario
    "Editar Facultad":                              {"en": "Edit Faculty"},
    "?? Editar Facultad":                           {"en": "?? Edit Faculty"},
    "Crear Nueva Facultad":                         {"en": "Create New Faculty"},
    "? Crear Nueva Facultad":                      {"en": "? Create New Faculty"},
    "Nombre de la Facultad":                        {"en": "Faculty Name"},
    "??? Nombre de la Facultad":                    {"en": "??? Faculty Name"},
    "Estado":                                       {"en": "Status"},
    "?? Estado":                                    {"en": "?? Status"},
    "Activa":                                       {"en": "Active"},
    "Inactiva":                                     {"en": "Inactive"},
    "Guardar Facultad":                             {"en": "Save Faculty"},
    "?? Guardar Facultad":                          {"en": "?? Save Faculty"},

    # --------------------------------------------------------------
    # GESTI�N DE CARRERAS � tabla
    # --------------------------------------------------------------
    "?? Gestión de Carreras":                       {"en": "?? Career Management"},
    "??   Gestión de Carreras":                     {"en": "??   Career Management"},
    "Agregar Carrera":                              {"en": "Add Career"},
    "? Agregar Carrera":                           {"en": "? Add Career"},
    "Buscar carrera por nombre...":                 {"en": "Search career by name..."},
    "No hay carreras registradas":                  {"en": "No registered careers"},
    "NOMBRE":                                       {"en": "NAME"},
    "FACULTAD":                                     {"en": "FACULTY"},

    # GESTI�N DE CARRERAS � modal
    "Desactivar esta carrera?":                    {"en": "Desactivate this career?"},
    "La carrera dejar de estar disponible.":       {"en": "The career will no longer be available."},
    "🔄Activar esta carrera?":                       {"en": "Activate this career?"},
    "La carrera volverá a estar disponible.":       {"en": "The career will be available again."},

    # GESTI�N DE CARRERAS � formulario
    "Editar Carrera":                               {"en": "Edit Career"},
    "?? Editar Carrera":                            {"en": "?? Edit Career"},
    "Nueva Carrera":                                {"en": "New Career"},
    "? Nueva Carrera":                             {"en": "? New Career"},
    "Nombre de la Carrera":                         {"en": "Career Name"},
    "?? Nombre de la Carrera":                      {"en": "?? Career Name"},
    "Facultad":                                     {"en": "Faculty"},
    "?? Facultad":                                  {"en": "?? Faculty"},
    "Seleccionar facultad":                         {"en": "Select faculty"},
    "Guardar Carrera":                              {"en": "Save Career"},
    "?? Guardar Carrera":                           {"en": "?? Save Career"},

    # --------------------------------------------------------------
    # CUENTA / PERFIL
    # --------------------------------------------------------------
    "Configura tu perfil y preferencias":           {"en": "Configure your profile and preferences"},
    "Editar":                                       {"en": "Edit"},
    "Editar Perfil":                                {"en": "Edit Profile"},
    "?? Editar":                                    {"en": "?? Edit"},
    "?? Editar Perfil":                             {"en": "?? Edit Profile"},
    "Detalles de la Cuenta":                        {"en": "Account Details"},
    "?? Detalles de la Cuenta":                     {"en": "?? Account Details"},
    "Correo":                                       {"en": "Email"},
    "Telofono":                                     {"en": "Phone"},
    "?? Personalizacin":                           {"en": "?? Customization"},
    "Personalización":                              {"en": "Customization"},
    "Idioma del Sistema":                           {"en": "System Language"},
    "?? Idioma del Sistema":                        {"en": "?? System Language"},
    "ADMINISTRADOR DEL SISTEMA":                    {"en": "SYSTEM ADMINISTRATOR"},
    "??   Editar Registro":                         {"en": "??   Edit Record"},
    "Modifica tu información personal":             {"en": "Modify your personal information"},
    "?? Información Personal":                      {"en": "?? Personal Information"},
    "Guardar Cambios":                              {"en": "Save Changes"},
    "?? Guardar Cambios":                           {"en": "?? Save Changes"},
    "El nombre y correo son obligatorios.":         {"en": "Name and email are required."},
    "Cambios guardados correctamente.":             {"en": "Changes saved successfully."},
    "?? Actualizar Foto":                           {"en": "?? Update Photo"},
    "Actualizar Foto":                              {"en": "Update Photo"},
    "Editar Registro...":                           {"en": "Edit Record..."},

    # --------------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------------
    "Sistema de Reconocimiento\nFacial":            {"en": "Facial Recognition\nSystem"},
    "Ingresa tus credenciales para continuar":      {"en": "Enter your credentials to continue"},
    "CORREO ÓNICO":                           {"en": "EMAIL ADDRESS"},
    "Escribe tu correo":                            {"en": "Enter your email"},
    "CONTRASEÑA":                                   {"en": "PASSWORD"},
    "Escribe tu contraseña":                        {"en": "Enter your password"},
    "INICIAR SESIÓN":                               {"en": "LOG IN"},
    "Credenciales incorrectas.":                    {"en": "Incorrect credentials."},

    # --------------------------------------------------------------
    # TERMINAL BIOM�TRICA
    # --------------------------------------------------------------
    "?  RECONOCIMIENTO FACIAL  ?":                  {"en": "?  FACIAL RECOGNITION  ?"},
    "SISTEMA ACTIVO":                               {"en": "SYSTEM ACTIVE"},
    "ESPERANDO DETECCIÓN...":                       {"en": "WAITING FOR DETECTION..."},
    "LISTO":                                        {"en": "READY"},
    "Iniciando cámara...":                          {"en": "Starting camera..."},
    "Sistema Biométrico v2.0":                      {"en": "Biometric System v2.0"},
    "Acceso Seguro":                                {"en": "Secure Access"},
    "Cifrado AES-256":                              {"en": "AES-256 Encryption"},

    # Terminal � mensajes de detecci�n y estado
    "ROSTRO DETECTADO":                             {"en": "FACE DETECTED"},
    "PROCESANDO...":                                {"en": "PROCESSING..."},
    "CAPTURANDO...":                                {"en": "CAPTURING..."},
    "CAPTURA EXITOSA":                              {"en": "CAPTURE SUCCESSFUL"},
    "IDENTIFICANDO...":                             {"en": "IDENTIFYING..."},
    "ACCESO AUTORIZADO":                            {"en": "ACCESS AUTHORIZED"},
    "ACCESO DENEGADO":                              {"en": "ACCESS DENIED"},
    "USUARIO INACTIVO":                             {"en": "INACTIVE USER"},
    "SIN DETECCIÓN":                                {"en": "NO DETECTION"},
    "CÁMARA NO DISPONIBLE":                         {"en": "CAMERA NOT AVAILABLE"},
    "ERROR DE CÁMARA":                              {"en": "CAMERA ERROR"},
    "Cámara no disponible":                         {"en": "Camera not available"},
    "Error al iniciar cámara":                      {"en": "Error starting camera"},
    "Biometría no encontrada":                      {"en": "Biometrics not found"},
    "REGISTRANDO ROSTRO":                           {"en": "REGISTERING FACE"},
    "REGISTRO EXITOSO":                             {"en": "REGISTRATION SUCCESSFUL"},
    "MANTÉN EL ROSTRO EN EL CENTRO":               {"en": "KEEP YOUR FACE IN THE CENTER"},
    "ROSTRO MUY LEJOS":                             {"en": "FACE TOO FAR"},
    "ROSTRO MUY CERCA":                             {"en": "FACE TOO CLOSE"},
    "ILUMINACIÓN INSUFICIENTE":                     {"en": "INSUFFICIENT LIGHTING"},
    "Volver":                                       {"en": "Back"},
    "? Volver":                                     {"en": "? Back"},
    "CANCELAR":                                     {"en": "CANCEL"},

    # --------------------------------------------------------------
    # BOTONES COMUNES
    # --------------------------------------------------------------
    "Guardar":                                      {"en": "Save"},
    "?? Guardar":                                   {"en": "?? Save"},
    "Editar":                                       {"en": "Edit"},
    "?? Editar":                                    {"en": "?? Edit"},
    "Fecha:":                                       {"en": "Date:"},
}

class AppContext:
    idioma_actual = "es"
    traductor = None

    @classmethod
    def t(cls, texto: str) -> str:
        """Devuelve la traducción del texto según el idioma actual."""
        if cls.idioma_actual == "es":
            return texto
        entrada = TRADUCCIONES.get(texto)
        if entrada:
            return entrada.get(cls.idioma_actual, texto)
        # Aviso en consola durante desarrollo � quitar en producci�n
        print(f"[i18n] Sin traducción EN para: {repr(texto)}")
        return texto

    @classmethod
    def set_idioma(cls, nuevo_idioma: str) -> None:
        cls.idioma_actual = nuevo_idioma