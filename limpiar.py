import sqlite3

conn = sqlite3.connect("app/database/sistema_biometrico.db")
cursor = conn.cursor()

cursor.execute("""
DELETE FROM usuario
WHERE nombre = 'Fabi'
AND a_paterno = 'Sanchez'
AND a_materno = 'Cervantes'
""")

conn.commit()
conn.close()

print("Usuarios eliminados")