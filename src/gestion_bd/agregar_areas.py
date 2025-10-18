import sys

import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def agregar_areas_iniciales():
    """Agrega las áreas predefinidas del sistema."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    areas = [
        ("Entrada Principal", "Acceso general", 1),
        ("Sala de Servidores", "Área restringida para personal de TI", 5),
        ("Laboratorio de Desarrollo", "Zona exclusiva para desarrolladores", 4),
        ("Área de Investigación", "Zona de pruebas y prototipos", 4),
        ("Oficina de Seguridad", "Monitoreo y control de accesos", 3),
        ("Depósito de Equipos", "Almacenamiento de hardware", 3),
        ("Sala de Juntas", "Reuniones corporativas", 3),
        ("Sala de Reuniones", "Reuniones generales", 2),
    ]

    print("\n=== Agregando áreas al sistema ===\n")
    for area in areas:
        try:
            cursor.execute(
                "INSERT INTO areas (nombre_area, descripcion, nivel_seguridad) VALUES (%s, %s, %s)",
                area,
            )
            print(f"[OK] {area[0]} - Nivel {area[2]}")
        except mysql.connector.IntegrityError:
            print(f"[INFO] {area[0]} ya existe")

    conn.commit()
    conn.close()
    print("\n[OK] Proceso completado.")


if __name__ == "__main__":
    agregar_areas_iniciales()
