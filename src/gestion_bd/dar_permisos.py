import sys
from datetime import datetime, timedelta

import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def asignar_permisos_automaticos():
    """Asigna permisos automáticamente basados en nivel de acceso."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    cursor.execute("SELECT id_empleado, nivel_acceso FROM empleados")
    empleados = cursor.fetchall()

    cursor.execute("SELECT id_area, nivel_seguridad FROM areas")
    areas = cursor.fetchall()

    print("\n=== Asignando permisos automáticamente ===\n")

    contador = 0
    for emp in empleados:
        id_empleado, nivel_acceso = emp
        nivel_acceso = int(nivel_acceso)  # type: ignore

        for area in areas:
            id_area, nivel_seguridad = area
            nivel_seguridad = int(nivel_seguridad)  # type: ignore

            if nivel_acceso >= nivel_seguridad:
                fecha_inicio = datetime.now().date()
                fecha_expiracion = (datetime.now() + timedelta(days=365)).date()

                cursor.execute(
                    """
                    SELECT id_permiso FROM permisos
                    WHERE id_empleado = %s AND id_area = %s
                """,
                    (id_empleado, id_area),  # type: ignore
                )
                existing_permission = cursor.fetchone()

                if existing_permission is None:
                    cursor.execute(
                        "INSERT INTO permisos (id_empleado, id_area, fecha_concesion, fecha_expiracion) VALUES (%s, %s, %s, %s)",
                        (id_empleado, id_area, fecha_inicio, fecha_expiracion),  # type: ignore
                    )
                    contador += 1

    conn.commit()
    conn.close()

    print(f"[OK] {contador} permisos nuevos asignados exitosamente.")


if __name__ == "__main__":
    asignar_permisos_automaticos()
