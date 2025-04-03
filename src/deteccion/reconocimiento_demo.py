import cv2
import sqlite3
import numpy as np

def obtener_nombre_empleado(dni_empleado):
    """Consulta en la base de datos el nombre del empleado según su DNI."""
    conn = sqlite3.connect("database/sistema_accesos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, apellidos FROM empleados WHERE dni = ?", (dni_empleado,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return f"{resultado[0]} {resultado[1]}"
    return "Desconocido"

def main():
    # Cargar el modelo entrenado
    modelo = cv2.face.LBPHFaceRecognizer_create()
    modelo.read("modelos/modelo_rostros.xml")

    # Cargar el clasificador de rostros de OpenCV
    detector_rostro = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # Inicializar la cámara
    camara = cv2.VideoCapture(0)

    while True:
        ret, frame = camara.read()
        if not ret:
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convertir a escala de grises
        rostros = detector_rostro.detectMultiScale(gris, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        for (x, y, w, h) in rostros:
            rostro = gris[y:y+h, x:x+w]  # Extraer el rostro detectado
            id_predicho, confianza = modelo.predict(rostro)  # Predecir la identidad del rostro

            if confianza < 80:  # Umbral de confianza (ajustable)
                nombre = obtener_nombre_empleado(id_predicho)
                color = (0, 255, 0)  # Verde si se reconoce
            else:
                nombre = "Desconocido"
                color = (0, 0, 255)  # Rojo si no se reconoce

            # Dibujar rectángulo y mostrar el nombre
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, nombre, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Reconocimiento Facial - Demo", frame)

        # Presionar 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camara.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
