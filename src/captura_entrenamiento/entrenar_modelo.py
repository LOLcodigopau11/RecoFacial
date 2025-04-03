import cv2
import os
import numpy as np
import sqlite3

def cargar_rostros():
    """Carga los rostros desde las imágenes capturadas y los nombres asociados."""
    path = 'data/rostros'
    rostros = []
    ids = []

    for directorio in os.listdir(path):
        ruta = os.path.join(path, directorio)
        if os.path.isdir(ruta):
            try:
                # El directorio tiene el formato 'DNI_nombre_apellidos', así que se puede tomar el DNI directamente
                dni_str = directorio.split('_')[0]  # Tomamos la primera parte como el DNI
                dni_int = int(dni_str)  # Convertimos el DNI a un entero
                for archivo in os.listdir(ruta):
                    if archivo.endswith(".jpg"):
                        imagen = cv2.imread(os.path.join(ruta, archivo), cv2.IMREAD_GRAYSCALE)
                        rostro = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                        rostros_detectados = rostro.detectMultiScale(imagen, 1.3, 5)
                        for (x, y, w, h) in rostros_detectados:
                            rostros.append(imagen[y:y+h, x:x+w])
                            ids.append(dni_int)  # Usamos el DNI como ID (ahora como entero)
            except ValueError:
                # Si no se puede convertir el directorio a un número o hay otro error, lo ignoramos
                continue

    return rostros, ids


def entrenar_modelo():
    """Entrena el modelo de reconocimiento facial."""
    rostros, ids = cargar_rostros()

    if len(rostros) == 0:
        print("⚠️ No se encontraron rostros para entrenar.")
        return

    modelo = cv2.face.LBPHFaceRecognizer_create()  # Usar Local Binary Pattern Histogram para reconocimiento facial
    modelo.train(rostros, np.array(ids))
    modelo.save('modelos/modelo_rostros.xml')
    print("✅ Modelo de rostros entrenado y guardado con éxito.")

if __name__ == "__main__":
    entrenar_modelo()