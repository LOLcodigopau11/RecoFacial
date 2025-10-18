import sys

import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def crear_base_datos():
    """Crea la base de datos si no existe"""
    config = get_db_config()
    db_name = config.pop("database")

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"[OK] Base de datos '{db_name}' creada exitosamente.")
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"[ERROR] No se pudo crear la base de datos: {err}")
        return False


def crear_tablas():
    """Crea todas las tablas necesarias"""
    config = get_db_config()

    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS empleados (
            id_empleado INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellidos VARCHAR(100) NOT NULL,
            dni VARCHAR(20) UNIQUE NOT NULL,
            ruta_rostro VARCHAR(255) NOT NULL,
            estado ENUM('activo', 'inactivo') NOT NULL DEFAULT 'activo',
            nivel_acceso INT NOT NULL CHECK(nivel_acceso BETWEEN 1 AND 5),
            INDEX idx_dni (dni)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS areas (
            id_area INT AUTO_INCREMENT PRIMARY KEY,
            nombre_area VARCHAR(100) NOT NULL,
            descripcion TEXT,
            nivel_seguridad INT NOT NULL CHECK(nivel_seguridad BETWEEN 1 AND 5)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS permisos (
            id_permiso INT AUTO_INCREMENT PRIMARY KEY,
            id_empleado INT NOT NULL,
            id_area INT NOT NULL,
            fecha_concesion DATE NOT NULL,
            fecha_expiracion DATE,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE CASCADE,
            FOREIGN KEY (id_area) REFERENCES areas(id_area) ON DELETE CASCADE,
            INDEX idx_empleado_area (id_empleado, id_area)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS registros_acceso (
            id_registro INT AUTO_INCREMENT PRIMARY KEY,
            id_empleado INT,
            id_area INT NOT NULL,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            tipo_acceso ENUM('entrada', 'salida') NOT NULL,
            metodo_autenticacion ENUM('huella', 'reconocimiento_facial', 'tarjeta') NOT NULL,
            acceso_concedido BOOLEAN NOT NULL,
            FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado) ON DELETE SET NULL,
            FOREIGN KEY (id_area) REFERENCES areas(id_area) ON DELETE CASCADE,
            INDEX idx_fecha (fecha_hora),
            INDEX idx_empleado (id_empleado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS intentos_fallidos (
            id_intento INT AUTO_INCREMENT PRIMARY KEY,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_area INT NOT NULL,
            imagen_captura VARCHAR(255),
            FOREIGN KEY (id_area) REFERENCES areas(id_area) ON DELETE CASCADE,
            INDEX idx_fecha (fecha_hora)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS incidentes (
            id_incidente INT AUTO_INCREMENT PRIMARY KEY,
            fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            id_empleado_reporta INT,
            tipo_incidente VARCHAR(100) NOT NULL,
            descripcion TEXT NOT NULL,
            severidad ENUM('baja', 'media', 'alta', 'critica') NOT NULL,
            estado ENUM('reportado', 'investigacion', 'resuelto', 'escalado') DEFAULT 'reportado',
            acciones_tomadas TEXT,
            FOREIGN KEY (id_empleado_reporta) REFERENCES empleados(id_empleado) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        )

        conn.commit()
        cursor.close()
        conn.close()

        print("[OK] Tablas creadas exitosamente.")
        return True

    except mysql.connector.Error as err:
        print(f"[ERROR] No se pudieron crear las tablas: {err}")
        return False


if __name__ == "__main__":
    print("\n=== Creación de Base de Datos MySQL ===\n")

    if crear_base_datos():
        crear_tablas()
        print("\n[OK] Configuración completada.")
        print("Siguiente paso: pdm run python src/gestion_bd/agregar_areas.py")
    else:
        print("\n[ERROR] Verifica las credenciales en config/db_config.py")
