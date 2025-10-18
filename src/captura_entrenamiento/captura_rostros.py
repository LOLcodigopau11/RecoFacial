import os
import sys
import time

import cv2
import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def verificar_dni(dni):
    """Verifica si el DNI ya está registrado en la base de datos."""
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("SELECT id_empleado FROM empleados WHERE dni = %s", (dni,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None


def guardar_empleado(nombre, apellidos, dni, nivel_acceso):
    """Guarda el nuevo empleado en la base de datos y retorna su ID."""
    nombre_usuario = f"{nombre}_{apellidos}".replace(" ", "_")
    ruta_rostro = f"data/rostros/{dni}_{nombre_usuario}"

    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO empleados (nombre, apellidos, dni, estado, ruta_rostro, nivel_acceso)
        VALUES (%s, %s, %s, 'activo', %s, %s)
    """,
        (nombre, apellidos, dni, ruta_rostro, nivel_acceso),
    )
    conn.commit()
    empleado_id = cursor.lastrowid
    conn.close()

    os.makedirs(ruta_rostro, exist_ok=True)

    return empleado_id


def capturar_rostros(empleado_id, nombre_usuario, ruta_rostro):
    """Captura imágenes del rostro con una cuenta regresiva inicial y una duración de captura."""
    carpeta = ruta_rostro

    camara = cv2.VideoCapture(0)
    detector_rostro = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    for i in range(3, 0, -1):
        ret, frame = camara.read()
        if not ret:
            print("[ERROR] No se pudo acceder a la cámara.")
            camara.release()
            cv2.destroyAllWindows()
            return
        cv2.putText(
            frame,
            f"Iniciando captura en {i}...",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )
        cv2.imshow("Captura de Rostros", frame)
        time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            camara.release()
            cv2.destroyAllWindows()
            return

    contador = 0
    tiempo_total_captura = 10
    intervalo_captura = tiempo_total_captura / 100
    start_time = time.time()

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
                image_path = f"{carpeta}/{contador}.jpg"
                cv2.imwrite(image_path, rostro)
                print(f"[INFO] Imagen guardada: {image_path}")
                contador += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        tiempo_transcurrido = time.time() - start_time
        tiempo_restante = int(tiempo_total_captura - tiempo_transcurrido)
        cv2.putText(
            frame,
            f"Capturando... {tiempo_restante}s restantes",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.imshow("Captura de Rostros", frame)
        time.sleep(intervalo_captura)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camara.release()
    cv2.destroyAllWindows()
    print(f"[OK] Captura completada - {contador} imágenes de {nombre_usuario}")


if __name__ == "__main__":
    nombre = input("Ingrese el nombre: ").strip()
    apellidos = input("Ingrese los apellidos: ").strip()
    dni = input("Ingrese el DNI: ").strip()

    print("\nSeleccione el nivel de acceso del empleado:")
    print("1 - Básico (Entrada Principal, Sala de Reuniones)")
    print("2 - Intermedio (Acceso a más áreas)")
    print("3 - Avanzado (Acceso a áreas de equipos y seguridad)")
    print("4 - Técnico (Laboratorio de Desarrollo e Investigación)")
    print("5 - Administrador (Acceso Total)\n")

    while True:
        try:
            nivel_acceso = int(input("Ingrese un nivel de acceso (1-5): ").strip())
            if 1 <= nivel_acceso <= 5:
                break
            else:
                print("[ADVERTENCIA] Nivel de acceso no válido. Debe ser entre 1 y 5.")
        except ValueError:
            print("[ERROR] Entrada no válida. Ingrese un número del 1 al 5.")

    if verificar_dni(dni):
        print("[ADVERTENCIA] El DNI ya está registrado. No se capturarán imágenes.")
    else:
        empleado_id = guardar_empleado(nombre, apellidos, dni, nivel_acceso)
        nombre_usuario = f"{nombre}_{apellidos}".replace(" ", "_")
        ruta_rostro = f"data/rostros/{dni}_{nombre_usuario}"
        capturar_rostros(empleado_id, nombre_usuario, ruta_rostro)
        print(
            f"[OK] Empleado registrado - ID: {empleado_id}, Nivel de acceso: {nivel_acceso}"
        )
