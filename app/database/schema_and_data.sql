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

-- 5. TABLA DE BIOMETRÃA
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

-- 7. JORNADAS DE TRABAJO
CREATE TABLE IF NOT EXISTS "jornada_laboral" (
    "id_jornada" INTEGER PRIMARY KEY AUTOINCREMENT,
    "id_usuario" INTEGER NOT NULL,
    "fecha_entrada" TEXT NOT NULL,
    "fecha_salida" TEXT,
    "duracion_segundos" INTEGER,
    "estado" TEXT NOT NULL DEFAULT 'trabajando',
    FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);

CREATE INDEX IF NOT EXISTS "idx_jornada_usuario_estado"
ON "jornada_laboral" ("id_usuario", "estado");

-- -----------------------
-- DATOS (SIN DUPLICADOS)
-- -----------------------

-- ROLES
INSERT OR IGNORE INTO "usuario_rol" VALUES (1,'admin','Administrador del sistema');

-- AREAS DE TRABAJO
INSERT OR IGNORE INTO "facultad" VALUES (1,'Dirección Operativa',1);
INSERT OR IGNORE INTO "facultad" VALUES (2,'Recursos Humanos',1);
INSERT OR IGNORE INTO "facultad" VALUES (3,'Seguridad y Accesos',1);
INSERT OR IGNORE INTO "facultad" VALUES (4,'Tecnologías de Información',1);

-- PUESTOS
INSERT OR IGNORE INTO "carrera" VALUES (1,'Operador de Planta',1,1);
INSERT OR IGNORE INTO "carrera" VALUES (2,'Supervisor de Turno',1,1);
INSERT OR IGNORE INTO "carrera" VALUES (3,'Analista de Recursos Humanos',2,1);
INSERT OR IGNORE INTO "carrera" VALUES (4,'Coordinador de Personal',2,1);
INSERT OR IGNORE INTO "carrera" VALUES (5,'Guardia de Seguridad',3,1);
INSERT OR IGNORE INTO "carrera" VALUES (6,'Monitor de Accesos',3,1);
INSERT OR IGNORE INTO "carrera" VALUES (7,'Soporte Técnico',4,1);
INSERT OR IGNORE INTO "carrera" VALUES (8,'Administrador de Sistemas',4,1);


COMMIT;
