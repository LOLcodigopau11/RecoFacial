import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("database/sistema_accesos.db")
cursor = conn.cursor()

# Insertar áreas (si no existen)
areas = [
    ("Entrada Principal", "Acceso general", 1),
    ("Sala de Servidores", "Área restringida para personal de TI", 5),
    ("Laboratorio de Desarrollo", "Zona exclusiva para desarrolladores", 4),
    ("Área de Investigación", "Zona de pruebas y prototipos", 4),
    ("Oficina de Seguridad", "Monitoreo y control de accesos", 3),
    ("Depósito de Equipos", "Almacenamiento de hardware", 3),
    ("Sala de Juntas", "Reuniones corporativas", 3),
    ("Sala de Reuniones", "Reuniones generales", 2)
]

for area in areas:
    cursor.execute("INSERT INTO areas (nombre_area, descripcion, nivel_seguridad) VALUES (?, ?, ?)", area)

conn.commit()
conn.close()

print("Áreas registradas correctamente.")
