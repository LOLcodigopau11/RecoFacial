import glob
import os
import sys

import cv2
import mysql.connector
import numpy as np

sys.path.append(".")
from config.db_config import get_db_config


def obtener_id_empleado_por_dni(dni):
    """Obtiene el ID del empleado a partir de su DNI."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT id_empleado FROM empleados WHERE dni = %s", (dni,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    return None


def cargar_rostros_para_reentrenar(dni_empleado):
    """Carga los rostros de un solo empleado específico a partir de su DNI."""
    path = "data/rostros"
    rostros = []
    ruta_empleado = os.path.join(
        path, f"{dni_empleado}_*"
    )  # Buscar carpeta por DNI al inicio
    carpetas_empleado = glob.glob(ruta_empleado)

    if carpetas_empleado:
        carpeta_empleado = carpetas_empleado[0]  # Tomar la primera carpeta coincidente
        if os.path.isdir(carpeta_empleado):
            for archivo in os.listdir(carpeta_empleado):
                if archivo.endswith(".jpg"):
                    imagen = cv2.imread(
                        os.path.join(carpeta_empleado, archivo), cv2.IMREAD_GRAYSCALE
                    )
                    rostros.append(imagen)
    return rostros


def reentrenar_modelo(id_empleado, dni_empleado):
    """Reentrena un rostro específico."""
    rostros = cargar_rostros_para_reentrenar(dni_empleado)

    if len(rostros) == 0:
        print(
            f"[ADVERTENCIA] No se encontraron rostros para reentrenar - DNI: {dni_empleado}"
        )
        return

    modelo = cv2.face.LBPHFaceRecognizer_create()
    try:
        modelo.read("modelos/modelo_rostros.xml")
    except cv2.error as e:
        print(f"[ADVERTENCIA] Error al leer modelo existente: {e}")
        print("[INFO] Se entrenará un nuevo modelo.")
        modelo = cv2.face.LBPHFaceRecognizer_create()

    # Añade los nuevos rostros
    ids = [id_empleado] * len(
        rostros
    )  # Utiliza el mismo ID para el empleado reentrenado
    if rostros:
        if hasattr(modelo, "update"):
            modelo.update(rostros, np.array(ids))
        else:
            modelo.train(rostros, np.array(ids))
        modelo.save("modelos/modelo_rostros.xml")
        print(
            f"[OK] Modelo reentrenado exitosamente - DNI: {dni_empleado}, ID: {id_empleado}"
        )
    else:
        print("[ADVERTENCIA] No se encontraron rostros para reentrenar.")


if __name__ == "__main__":
    dni_reentrenar = input("Ingrese el DNI del empleado a reentrenar: ").strip()
    id_empleado = obtener_id_empleado_por_dni(dni_reentrenar)

    if id_empleado is not None:
        reentrenar_modelo(id_empleado, dni_reentrenar)
    else:
        print(f"[ADVERTENCIA] No se encontró empleado con DNI: {dni_reentrenar}")
