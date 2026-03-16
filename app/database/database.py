import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_biometrico.db")
SQL_PATH = os.path.join(BASE_DIR, "schema_and_data.sql")


def get_connection():
    # Se agrega 'timeout=20' para dar tiempo a que otros procesos (como DB Browser) 
    # suelten la base de datos antes de fallar
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_bd():
    # Si la base ya existe no la recrea
    if os.path.exists(DB_PATH):
        print("Base de datos ya existe.")
        return

    conn = get_connection()
    try:
        with open(SQL_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())
        conn.commit()
        print("Base de datos creada con schema_and_data.sql")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close() # Asegura que la conexión se cierre siempre