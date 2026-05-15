BEGIN TRANSACTION;

-- 1. TABLA DE ROLES
CREATE TABLE IF NOT EXISTS "usuario_rol" (
    "id_rol" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre" TEXT NOT NULL UNIQUE,
    "descripcion" TEXT
);

-- 2. TABLA DE FACULTADES
CREATE TABLE IF NOT EXISTS "facultad" (
    "id_facultad" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre" TEXT NOT NULL UNIQUE,
    "estado" INTEGER DEFAULT 1
);

-- 3. TABLA DE CARRERAS
CREATE TABLE IF NOT EXISTS "carrera" (
    "id_carrera" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre" TEXT NOT NULL,
    "id_facultad" INTEGER NOT NULL,
    "estado" INTEGER DEFAULT 1,
    FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS "usuario" (
    "id_usuario" INTEGER PRIMARY KEY AUTOINCREMENT,
    "nombre" TEXT NOT NULL,
    "a_paterno" TEXT NOT NULL,
    "a_materno" TEXT,
    "cuenta" TEXT,
    "correo" TEXT,
    "tipo_usuario" INTEGER NOT NULL,
    "estado" INTEGER DEFAULT 1,
    "fecha_registro" TEXT NOT NULL,
    "fecha_actualizacion" TEXT,
    "id_facultad" INTEGER,
    "id_carrera" INTEGER,
    FOREIGN KEY("id_carrera") REFERENCES "carrera"("id_carrera"),
    FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad")
);

-- 5. TABLA DE BIOMETRÍA
CREATE TABLE IF NOT EXISTS "biometria" (
    "id_biometria" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_usuario" INTEGER NOT NULL,
    "embedding" BLOB NOT NULL,
    "fecha_registro" TEXT NOT NULL,
    "estado" INTEGER DEFAULT 1,
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
);

-- 6. REGISTROS DE ACCESO
CREATE TABLE IF NOT EXISTS "registro_acceso" (
    "id_registro" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_usuario" INTEGER,
    "fecha_hora" TEXT NOT NULL,
    "resultado" INTEGER NOT NULL,
    "confianza" REAL,
    "motivo" TEXT,
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);

-- -----------------------
-- DATOS (SIN DUPLICADOS)
-- -----------------------

-- ROLES
INSERT OR IGNORE INTO "usuario_rol" VALUES (1,'admin','Administrador del sistema');

-- FACULTADES
INSERT OR IGNORE INTO "facultad" VALUES (1,'Facultad de Ciencias Marinas (FACIMAR)',1);
INSERT OR IGNORE INTO "facultad" VALUES (2,'Facultad de Contabilidad y Administración (FCAM)',1);
INSERT OR IGNORE INTO "facultad" VALUES (3,'Escuela de Enfermería',1);
INSERT OR IGNORE INTO "facultad" VALUES (4,'Facultad de Ingeniería Electromecánica (FIE)',1);

-- CARRERAS
INSERT OR IGNORE INTO "carrera" VALUES (1,'Ingeniería Oceánica',1,1);
INSERT OR IGNORE INTO "carrera" VALUES (2,'Licenciatura en Sustentabilidad Marina',1,1);
INSERT OR IGNORE INTO "carrera" VALUES (3,'Contador Público',2,1);
INSERT OR IGNORE INTO "carrera" VALUES (4,'Licenciatura en Administración',2,1);
INSERT OR IGNORE INTO "carrera" VALUES (5,'Licenciatura en Negocios Digitales',2,1);
INSERT OR IGNORE INTO "carrera" VALUES (6,'Licenciatura en Enfermería',3,1);
INSERT OR IGNORE INTO "carrera" VALUES (7,'Ingeniero Mecánico Electricista (IME)',4,1);
INSERT OR IGNORE INTO "carrera" VALUES (8,'Ingeniería en Tecnologías Electrónicas (ITE)',4,1);
INSERT OR IGNORE INTO "carrera" VALUES (9,'Ingeniería en Mecatrónica (IMT)',4,1);
INSERT OR IGNORE INTO "carrera" VALUES (10,'Ingeniería de Software (IS)',4,1);


COMMIT;