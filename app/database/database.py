import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_biometrico.db")
SQL_PATH = os.path.join(BASE_DIR, "schema_and_data.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def inicializar_bd():

    # Si la base ya existe no la recrea
    if os.path.exists(DB_PATH):
        print("Base de datos ya existe.")
        return

    conn = get_connection()

    with open(SQL_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    conn.commit()
    conn.close()

    print("Base de datos creada con schema_and_data.sql")