import sys

import cv2
import mysql.connector
import numpy as np

sys.path.append(".")
from config.db_config import get_db_config


def obtener_nombre_empleado(dni_empleado):
    """Consulta en la base de datos el nombre del empleado según su DNI."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre, apellidos FROM empleados WHERE dni = %s", (dni_empleado,)
    )
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return f"{resultado[0]} {resultado[1]}"
    return "Desconocido"


def main():
    modelo = cv2.face.LBPHFaceRecognizer_create()
    modelo.read("modelos/modelo_rostros.xml")

    detector_rostro = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    camara = cv2.VideoCapture(0)

    while True:
        ret, frame = camara.read()
        if not ret:
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector_rostro.detectMultiScale(
            gris, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
        )

        for x, y, w, h in rostros:
            rostro = gris[y : y + h, x : x + w]
            id_predicho, confianza = modelo.predict(rostro)

            if confianza < 80:
                nombre = obtener_nombre_empleado(id_predicho)
                color = (0, 255, 0)
            else:
                nombre = "Desconocido"
                color = (0, 0, 255)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                frame, nombre, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
            )

        cv2.imshow("Reconocimiento Facial - Demo", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camara.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
