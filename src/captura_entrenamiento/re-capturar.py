import os
import shutil  # Para eliminar la carpeta y su contenido
import sys
import time

import cv2
import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def verificar_dni_en_db(dni):
    """Verifica si el DNI está registrado en la base de datos y retorna el nombre de usuario."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, apellidos FROM empleados WHERE dni = %s", (dni,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        nombre, apellidos = resultado
        nombre_usuario = f"{nombre}_{apellidos}".replace(" ", "_")
        return nombre_usuario
    return None


def re_capturar_rostro(dni):
    """Re-captura las imágenes del rostro para un DNI existente, reemplazando las anteriores."""
    nombre_usuario = verificar_dni_en_db(dni)
    if not nombre_usuario:
        print(f"[ADVERTENCIA] No se encontró empleado con DNI: {dni}")
        return

    ruta_carpeta_rostro = f"data/rostros/{dni}_{nombre_usuario}"

    if not os.path.exists(ruta_carpeta_rostro):
        print(f"[ERROR] No se encontró carpeta de rostro para DNI: {dni}")
        return

    try:
        shutil.rmtree(ruta_carpeta_rostro)
        print(f"[INFO] Carpeta de rostro eliminada: {ruta_carpeta_rostro}")
    except OSError as e:
        print(f"[ERROR] No se pudo eliminar la carpeta: {e}")
        return

    os.makedirs(ruta_carpeta_rostro, exist_ok=True)
    print(f"[INFO] Carpeta de rostro creada: {ruta_carpeta_rostro}")

    # Simular la captura de rostros (puedes reutilizar tu función original capturar_rostros adaptándola)
    camara = cv2.VideoCapture(0)
    detector_rostro = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    contador = 0
    tiempo_total_captura = 10  # Duración total de la captura en segundos
    intervalo_captura = tiempo_total_captura / 100
    start_time = time.time()

    print("\n[INFO] Iniciando re-captura de rostro...")

    while contador < 100 and (time.time() - start_time) < tiempo_total_captura:
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            break

        gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = detector_rostro.detectMultiScale(
            gris, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
        )

        if len(rostros) > 0:
            for x, y, w, h in rostros:
                rostro = gris[y : y + h, x : x + w]
                image_path = f"{ruta_carpeta_rostro}/{contador}.jpg"
                cv2.imwrite(image_path, rostro)
                print(f"[INFO] Imagen guardada: {image_path}")
                contador += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        tiempo_transcurrido = time.time() - start_time
        tiempo_restante = int(tiempo_total_captura - tiempo_transcurrido)
        cv2.putText(
            frame,
            f"Re-capturando... {tiempo_restante} segundos restantes",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Re-captura de Rostros", frame)
        time.sleep(intervalo_captura)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camara.release()
    cv2.destroyAllWindows()
    print(
        f"\n[OK] Re-captura completada para DNI: {dni} - {contador} imágenes capturadas."
    )


if __name__ == "__main__":
    dni_re_capturar = input(
        "Ingrese el DNI del usuario para re-capturar su rostro: "
    ).strip()
    re_capturar_rostro(dni_re_capturar)
