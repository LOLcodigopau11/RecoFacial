"""
Tests del sistema de reconocimiento facial
Ejecutar con: pdm run pytest tests/
"""

import sys

import pytest

sys.path.append(".")


class TestDependencias:
    """Tests de verificación de dependencias instaladas"""

    def test_opencv_instalado(self):
        """Verifica que OpenCV esté instalado"""
        try:
            import cv2

            assert cv2.__version__ is not None
        except ImportError:
            pytest.fail("OpenCV no está instalado")

    def test_opencv_contrib_disponible(self):
        """Verifica que opencv-contrib esté instalado para reconocimiento facial"""
        try:
            import cv2

            modelo = cv2.face.LBPHFaceRecognizer_create()
            assert modelo is not None
        except (ImportError, AttributeError) as e:
            pytest.fail(f"OpenCV Contrib no está disponible: {e}")

    def test_mysql_connector_instalado(self):
        """Verifica que MySQL Connector esté instalado"""
        try:
            import mysql.connector

            assert mysql.connector is not None
        except ImportError:
            pytest.fail("MySQL Connector no está instalado")

    def test_numpy_instalado(self):
        """Verifica que NumPy esté instalado"""
        try:
            import numpy as np

            assert np.__version__ is not None
        except ImportError:
            pytest.fail("NumPy no está instalado")


class TestConfiguracion:
    """Tests de configuración del sistema"""

    def test_archivo_configuracion_existe(self):
        """Verifica que el archivo de configuración exista"""
        try:
            from config.db_config import get_db_config

            config = get_db_config()
            assert config is not None
            assert isinstance(config, dict)
        except ImportError:
            pytest.fail("Archivo config/db_config.py no encontrado")

    def test_configuracion_tiene_campos_requeridos(self):
        """Verifica que la configuración tenga todos los campos necesarios"""
        from config.db_config import get_db_config

        config = get_db_config()
        campos_requeridos = ["host", "user", "password", "database", "port"]

        for campo in campos_requeridos:
            assert campo in config, f"Falta el campo '{campo}' en la configuración"

    def test_configuracion_valores_validos(self):
        """Verifica que los valores de configuración sean válidos"""
        from config.db_config import get_db_config

        config = get_db_config()

        assert isinstance(config["host"], str), "Host debe ser string"
        assert isinstance(config["user"], str), "User debe ser string"
        assert isinstance(config["database"], str), "Database debe ser string"
        assert isinstance(config["port"], int), "Port debe ser int"
        assert config["port"] > 0, "Port debe ser mayor a 0"


class TestConexionBD:
    """Tests de conexión a la base de datos"""

    def test_conexion_mysql_exitosa(self):
        """Verifica que se pueda conectar a MySQL"""
        import mysql.connector

        from config.db_config import get_db_config

        try:
            config = get_db_config()
            conn = mysql.connector.connect(**config)
            assert conn is not None
            assert conn.is_connected()
            conn.close()
        except mysql.connector.Error as e:
            pytest.fail(f"No se pudo conectar a MySQL: {e}")

    def test_base_datos_tiene_tablas(self):
        """Verifica que la base de datos tenga las tablas necesarias"""
        import mysql.connector

        from config.db_config import get_db_config

        config = get_db_config()
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("SHOW TABLES")
        tablas = [tabla[0] for tabla in cursor.fetchall()]

        tablas_requeridas = [
            "empleados",
            "areas",
            "permisos",
            "registros_acceso",
            "intentos_fallidos",
            "incidentes",
        ]

        for tabla in tablas_requeridas:
            assert tabla in tablas, f"Falta la tabla '{tabla}' en la base de datos"

        conn.close()

    def test_tabla_empleados_estructura(self):
        """Verifica que la tabla empleados tenga la estructura correcta"""
        import mysql.connector

        from config.db_config import get_db_config

        config = get_db_config()
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()

        cursor.execute("DESCRIBE empleados")
        columnas = [col[0] for col in cursor.fetchall()]

        columnas_requeridas = [
            "id_empleado",
            "nombre",
            "apellidos",
            "dni",
            "ruta_rostro",
            "estado",
            "nivel_acceso",
        ]

        for columna in columnas_requeridas:
            assert (
                columna in columnas
            ), f"Falta la columna '{columna}' en tabla empleados"

        conn.close()


class TestEstructuraArchivos:
    """Tests de estructura de directorios y archivos"""

    def test_directorio_data_existe(self):
        """Verifica que el directorio data exista"""
        import os

        assert os.path.exists("data"), "Directorio 'data' no existe"

    def test_directorio_rostros_existe(self):
        """Verifica que el directorio de rostros exista"""
        import os

        assert os.path.exists("data/rostros"), "Directorio 'data/rostros' no existe"

    def test_directorio_intentos_fallidos_existe(self):
        """Verifica que el directorio de intentos fallidos exista"""
        import os

        assert os.path.exists(
            "data/intentos_fallidos"
        ), "Directorio 'data/intentos_fallidos' no existe"

    def test_directorio_modelos_existe(self):
        """Verifica que el directorio de modelos exista"""
        import os

        assert os.path.exists("modelos"), "Directorio 'modelos' no existe"

    def test_archivo_modelo_existe(self):
        """Verifica que el archivo del modelo entrenado exista"""
        import os

        if os.path.exists("data/rostros"):
            rostros_dirs = [
                d
                for d in os.listdir("data/rostros")
                if os.path.isdir(os.path.join("data/rostros", d))
            ]
            if len(rostros_dirs) > 0:
                assert os.path.exists(
                    "modelos/modelo_rostros.xml"
                ), "Archivo 'modelos/modelo_rostros.xml' no existe (entrenar modelo primero)"


class TestModulos:
    """Tests de importación de módulos del proyecto"""

    def test_importar_db_config(self):
        """Verifica que se pueda importar db_config"""
        from config.db_config import get_db_config

        assert callable(get_db_config)

    def test_importar_db_utils(self):
        """Verifica que se pueda importar db_utils"""
        from utils.db_utils import conectar_bd

        assert callable(conectar_bd)

    def test_importar_captura_rostros(self):
        """Verifica que se pueda importar captura_rostros"""
        from src.captura_entrenamiento.captura_rostros import (
            guardar_empleado,
            verificar_dni,
        )

        assert callable(verificar_dni)
        assert callable(guardar_empleado)

    def test_importar_entrenar_modelo(self):
        """Verifica que se pueda importar entrenar_modelo"""
        from src.captura_entrenamiento.entrenar_modelo import (
            cargar_rostros,
            entrenar_modelo,
        )

        assert callable(cargar_rostros)
        assert callable(entrenar_modelo)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
