import os
import sqlite3

import cv2
import numpy as np


def cargar_rostros():
    """Carga los rostros desde las imágenes capturadas."""
    path = "data/rostros"
    rostros = []
    ids = []

    for directorio in os.listdir(path):
        ruta = os.path.join(path, directorio)
        if os.path.isdir(ruta):
            try:
                dni_str = directorio.split("_")[0]
                dni_int = int(dni_str)
                for archivo in os.listdir(ruta):
                    if archivo.endswith(".jpg"):
                        imagen = cv2.imread(
                            os.path.join(ruta, archivo), cv2.IMREAD_GRAYSCALE
                        )
                        rostro = cv2.CascadeClassifier(
                            cv2.data.haarcascades
                            + "haarcascade_frontalface_default.xml"
                        )
                        rostros_detectados = rostro.detectMultiScale(imagen, 1.3, 5)
                        for x, y, w, h in rostros_detectados:
                            rostros.append(imagen[y : y + h, x : x + w])
                            ids.append(dni_int)
            except ValueError:
                continue

    return rostros, ids


def entrenar_modelo():
    """Entrena el modelo de reconocimiento facial."""
    rostros, ids = cargar_rostros()

    if len(rostros) == 0:
        print("[ADVERTENCIA] No se encontraron rostros para entrenar.")
        return

    modelo = cv2.face.LBPHFaceRecognizer_create()
    modelo.train(rostros, np.array(ids))
    modelo.save("modelos/modelo_rostros.xml")
    print("[OK] Modelo entrenado y guardado exitosamente.")


if __name__ == "__main__":
    entrenar_modelo()
