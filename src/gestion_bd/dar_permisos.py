# igual sin ejecutar este codigo funciona el reconocimiento de nivel y areaa en los simuladores
import sqlite3
from datetime import datetime, timedelta

# Conectar a la base de datos
conn = sqlite3.connect("database/sistema_accesos.db")
cursor = conn.cursor()

# Obtener todos los empleados
cursor.execute("SELECT id_empleado, nivel_acceso FROM empleados")
empleados = cursor.fetchall()

# Obtener todas las áreas
cursor.execute("SELECT id_area, nivel_seguridad FROM areas")
areas = cursor.fetchall()

# Asignar permisos según nivel de acceso
for emp in empleados:
    id_empleado, nivel_acceso = emp

    for area in areas:
        id_area, nivel_seguridad = area

        if nivel_acceso >= nivel_seguridad:  # Permitir acceso si el nivel del empleado es suficiente
            fecha_inicio = datetime.now().date()
            fecha_expiracion = (datetime.now() + timedelta(days=365)).date()  # Permiso válido por 1 año

            # Verificar si ya existe un permiso para este empleado y área
            cursor.execute("""
                SELECT id_permiso FROM permisos
                WHERE id_empleado = ? AND id_area = ?
            """, (id_empleado, id_area))
            existing_permission = cursor.fetchone()

            if existing_permission is None:
                cursor.execute("INSERT INTO permisos (id_empleado, id_area, fecha_concesion, fecha_expiracion) VALUES (?, ?, ?, ?)",
                                (id_empleado, id_area, fecha_inicio, fecha_expiracion))

conn.commit()
conn.close()

print("Permisos asignados correctamente.")