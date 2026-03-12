BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "biometria" (
	"id_biometria"	INTEGER,
	"id_usuario"	INTEGER NOT NULL,
	"embedding"	BLOB NOT NULL,
	"fecha_registro"	TEXT NOT NULL,
	"estado"	INTEGER DEFAULT 1,
	PRIMARY KEY("id_biometria" AUTOINCREMENT),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "carrera" (
	"id_carrera"	INTEGER,
	"nombre"	TEXT NOT NULL,
	"id_facultad"	INTEGER NOT NULL,
	"estado"	INTEGER DEFAULT 1,
	PRIMARY KEY("id_carrera" AUTOINCREMENT),
	FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "facultad" (
	"id_facultad"	INTEGER,
	"nombre"	TEXT NOT NULL UNIQUE,
	"estado"	INTEGER DEFAULT 1,
	PRIMARY KEY("id_facultad" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "registro_acceso" (
	"id_registro"	INTEGER,
	"id_usuario"	INTEGER,
	"fecha_hora"	TEXT NOT NULL,
	"resultado"	INTEGER NOT NULL,
	"confianza"	REAL,
	"motivo"	TEXT,
	PRIMARY KEY("id_registro" AUTOINCREMENT),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);
CREATE TABLE IF NOT EXISTS "usuario" (
	"id_usuario"	INTEGER,
	"nombre"	TEXT NOT NULL,
	"a_paterno"	TEXT NOT NULL,
	"a_materno"	TEXT,
	"estado"	INTEGER DEFAULT 1,
	"fecha_registro"	TEXT NOT NULL,
	"fecha_actualizacion"	TEXT,
	"id_rol"	INTEGER NOT NULL,
	"id_facultad"	INTEGER,
	"id_carrera"	INTEGER,
	PRIMARY KEY("id_usuario" AUTOINCREMENT),
	FOREIGN KEY("id_carrera") REFERENCES "carrera"("id_carrera"),
	FOREIGN KEY("id_facultad") REFERENCES "facultad"("id_facultad"),
	FOREIGN KEY("id_rol") REFERENCES "usuario_rol"("id_rol")
);
CREATE TABLE IF NOT EXISTS "usuario_rol" (
	"id_rol"	INTEGER,
	"nombre"	TEXT NOT NULL UNIQUE,
	"descripcion"	TEXT,
	PRIMARY KEY("id_rol" AUTOINCREMENT)
);
-- ROLES
INSERT INTO "usuario_rol" VALUES (1,'admin','Administrador del sistema');

-- FACULTADES
INSERT INTO "facultad" VALUES (1,'Facultad de Ciencias Marinas (FACIMAR)',1);
INSERT INTO "facultad" VALUES (2,'Facultad de Contabilidad y Administración (FCAM)',1);
INSERT INTO "facultad" VALUES (3,'Escuela de Enfermería',1);
INSERT INTO "facultad" VALUES (4,'Facultad de Ingeniería Electromecánica (FIE)',1);

-- CARRERAS
INSERT INTO "carrera" VALUES (1,'Ingeniería Oceánica',1,1);
INSERT INTO "carrera" VALUES (2,'Licenciatura en Sustentabilidad Marina',1,1);
INSERT INTO "carrera" VALUES (3,'Contador Público',2,1);
INSERT INTO "carrera" VALUES (4,'Licenciatura en Administración',2,1);
INSERT INTO "carrera" VALUES (5,'Licenciatura en Negocios Digitales',2,1);
INSERT INTO "carrera" VALUES (6,'Licenciatura en Enfermería',3,1);
INSERT INTO "carrera" VALUES (7,'Ingeniero Mecánico Electricista (IME)',4,1);
INSERT INTO "carrera" VALUES (8,'Ingeniería en Tecnologías Electrónicas (ITE)',4,1);
INSERT INTO "carrera" VALUES (9,'Ingeniería en Mecatrónica (IMT)',4,1);
INSERT INTO "carrera" VALUES (10,'Ingeniería de Software (IS)',4,1);

-- USUARIO ADMIN
INSERT INTO "usuario"
VALUES (1,'Juan Pablo','Mancilla','Rodriguez',1,'2026-03-08 18:45:43',NULL,1,4,10);
COMMIT;
