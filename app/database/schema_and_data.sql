BEGIN TRANSACTION;

-- 1. TABLA DE ROLES
CREATE TABLE IF NOT EXISTS "usuario_rol" (
    "id_rol"      INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre"      TEXT NOT NULL UNIQUE,
    "descripcion" TEXT
);

-- 2. TABLA DE FACULTADES
CREATE TABLE IF NOT EXISTS "facultad" (
    "id_facultad" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre"      TEXT NOT NULL UNIQUE,
    "estado"      INTEGER DEFAULT 1
);

-- 3. TABLA DE CARRERAS
CREATE TABLE IF NOT EXISTS "carrera" (
    "id_carrera"  INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre"      TEXT NOT NULL,
    "id_facultad" INTEGER NOT NULL,
    "estado"      INTEGER DEFAULT 1,
    FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad") ON DELETE CASCADE
);

-- 4. TABLA DE USUARIOS (CON CUENTA Y CORREO)
CREATE TABLE IF NOT EXISTS "usuario" (
    "id_usuario"          INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre"              TEXT NOT NULL,
    "a_paterno"           TEXT NOT NULL,
    "a_materno"           TEXT,
    "cuenta"              TEXT NOT NULL UNIQUE, -- IMPORTANTE: 8 números
    "correo"              TEXT NOT NULL,        -- IMPORTANTE: con @
    "estado"              INTEGER DEFAULT 1,
    "fecha_registro"      TEXT NOT NULL,
    "fecha_actualizacion" TEXT,
    "id_rol"              INTEGER NOT NULL,
    "id_facultad"         INTEGER,
    "id_carrera"          INTEGER,
    FOREIGN KEY("id_carrera") REFERENCES "carrera"("id_carrera"),
    FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad"),
    FOREIGN KEY("id_rol") REFERENCES "usuario_rol"("id_rol")
);

-- 5. TABLA DE BIOMETRÍA
CREATE TABLE IF NOT EXISTS "biometria" (
    "id_biometria"   INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_usuario"     INTEGER NOT NULL,
    "embedding"      BLOB NOT NULL,
    "fecha_registro" TEXT NOT NULL,
    "estado"         INTEGER DEFAULT 1,
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
);

-- 6. REGISTROS DE ACCESO
CREATE TABLE IF NOT EXISTS "registro_acceso" (
    "id_registro" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_usuario"  INTEGER,
    "fecha_hora"  TEXT NOT NULL,
    "resultado"   INTEGER NOT NULL,
    "confianza"   REAL,
    "motivo"      TEXT,
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);

-- --- DATOS INICIALES ---

-- ROLES
INSERT OR IGNORE INTO "usuario_rol" (id_rol, nombre, descripcion) VALUES (1, 'ADMIN', 'Administrador');
INSERT OR IGNORE INTO "usuario_rol" (id_rol, nombre, descripcion) VALUES (2, 'ESTUDIANTE', 'Alumno regular');
INSERT OR IGNORE INTO "usuario_rol" (id_rol, nombre, descripcion) VALUES (3, 'DOCENTE', 'Profesor');
INSERT OR IGNORE INTO "usuario_rol" (id_rol, nombre, descripcion) VALUES (4, 'AUXILIAR', 'Personal de apoyo');

-- FACULTADES
INSERT OR IGNORE INTO "facultad" (id_facultad, nombre) VALUES (1, 'Ciencias Marinas');
INSERT OR IGNORE INTO "facultad" (id_facultad, nombre) VALUES (2, 'FCAM');
INSERT OR IGNORE INTO "facultad" (id_facultad, nombre) VALUES (3, 'Ingeniería Electromecánica');

-- CARRERAS
INSERT OR IGNORE INTO "carrera" (id_carrera, nombre, id_facultad) VALUES (1, 'Software', 3);
INSERT OR IGNORE INTO "carrera" (id_carrera, nombre, id_facultad) VALUES (2, 'Mecatrónica', 3);

COMMIT;