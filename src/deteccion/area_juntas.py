import cv2
import sqlite3
import numpy as np
import os
from datetime import datetime

# Configuración inicial
AREA_OBJETIVO = "Sala de Juntas"  # Área a simular
MODELO_PATH = "modelos/modelo_rostros.xml"
DB_PATH = "database/sistema_accesos.db"
INTENTOS_FALLIDOS_DIR = "data/intentos_fallidos"

# Crear directorios si no existen
os.makedirs(f"{INTENTOS_FALLIDOS_DIR}/acceso_denegado", exist_ok=True)
os.makedirs(f"{INTENTOS_FALLIDOS_DIR}/intrusos", exist_ok=True)

# Cargar modelo y clasificador
modelo = cv2.face.LBPHFaceRecognizer_create()
modelo.read(MODELO_PATH)
detector_rostro = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def obtener_info_empleado(dni):
    """Obtiene información completa del empleado desde la BD"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_empleado, nombre, apellidos, nivel_acceso 
        FROM empleados 
        WHERE dni = ? AND estado = 'activo'
    """, (dni,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado if resultado else None

def obtener_info_area(nombre_area):
    """Obtiene información del área desde la BD"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id_area, nivel_seguridad FROM areas WHERE nombre_area = ?", (nombre_area,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado if resultado else None

def registrar_acceso(id_empleado, id_area, concedido, metodo):
    """Registra el intento de acceso en la BD"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO registros_acceso 
        (id_empleado, id_area, tipo_acceso, metodo_autenticacion, acceso_concedido)
        VALUES (?, ?, 'entrada', ?, ?)
    """, (id_empleado, id_area, metodo, int(concedido)))
    conn.commit()
    conn.close()

def registrar_intento_fallido(id_area, imagen_path=None):
    """Registra intento fallido en la BD"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO intentos_fallidos 
        (id_area, imagen_captura)
        VALUES (?, ?)
    """, (id_area, imagen_path))
    conn.commit()
    conn.close()

def mostrar_texto(frame, texto, posicion, color=(0, 255, 0)):
    """Muestra texto en el frame en una posición específica"""
    cv2.putText(frame, texto, posicion, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

def capturar_rostro(camara):
    """Captura un rostro con cuenta regresiva usando la cámara existente"""
    for i in range(5, 0, -1):
        ret, frame = camara.read()
        if not ret:
            return None
        mostrar_texto(frame, f"Captura en {i}...", (50, 50), (0, 0, 255))
        cv2.imshow("Control de Acceso", frame)
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            return None
    ret, frame = camara.read()
    return frame if ret else None

def procesar_acceso():
    """Procesa el flujo completo de control de acceso"""
    area_info = obtener_info_area(AREA_OBJETIVO)
    if not area_info:
        print(f"Error: Área '{AREA_OBJETIVO}' no encontrada en la BD")
        return
    
    id_area, nivel_seguridad_area = area_info
    camara = cv2.VideoCapture(0)
    
    try:
        while True:
            frame = capturar_rostro(camara)
            if frame is None:
                break
            
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = detector_rostro.detectMultiScale(gris, scaleFactor=1.3, minNeighbors=5)
            
            mostrar_texto(frame, AREA_OBJETIVO, (50, 30), (255, 0, 0))
            
            if len(rostros) == 0:
                mostrar_texto(frame, "No se detectaron rostros", (50, 80), (0, 0, 255))
                cv2.imshow("Control de Acceso", frame)
                key = cv2.waitKey(2000) & 0xFF
                if key == ord('q'):
                    break
                continue
            
            (x, y, w, h) = rostros[0]
            rostro = gris[y:y+h, x:x+w]
            
            dni_predicho, confianza = modelo.predict(rostro)
            empleado_info = obtener_info_empleado(dni_predicho) if confianza < 80 else None
            
            if empleado_info:
                id_empleado, nombre, apellidos, nivel_acceso = empleado_info
                nombre_completo = f"{nombre} {apellidos}"
                
                if nivel_acceso >= nivel_seguridad_area:
                    color = (0, 255, 0)
                    mensaje = "Acceso autorizado"
                    registrar_acceso(id_empleado, id_area, True, "reconocimiento_facial")
                else:
                    color = (0, 0, 255)
                    mensaje = "Acceso denegado"
                    registrar_acceso(id_empleado, id_area, False, "reconocimiento_facial")
                    
                    # Guardar imagen de intento fallido
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    img_path = f"{INTENTOS_FALLIDOS_DIR}/acceso_denegado/{timestamp} - {AREA_OBJETIVO} - {nombre_completo}.jpg"
                    cv2.imwrite(img_path, frame)
                    registrar_intento_fallido(id_area, img_path)
            else:
                color = (0, 0, 255)
                mensaje = "Intruso Detectado"
                
                # Guardar imagen de intruso
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                img_path = f"{INTENTOS_FALLIDOS_DIR}/intrusos/{timestamp} - {AREA_OBJETIVO}.jpg"
                cv2.imwrite(img_path, frame)
                registrar_intento_fallido(id_area, img_path)
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            mostrar_texto(frame, mensaje, (x, y-10), color)
            if empleado_info:
                mostrar_texto(frame, nombre_completo, (x, y+30), color)
            
            cv2.imshow("Control de Acceso", frame)
            
            key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n'):  # Espera a que se presione 'n' para continuar con un nuevo intento
                continue  # Nuevamente captura el rostro y procesa el acceso
            
    finally:
        camara.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    print(f"\n=== Sistema de Control de Acceso ===")
    print(f"Área seleccionada: {AREA_OBJETIVO}")
    print("Instrucciones:")
    print("- El sistema hará una cuenta regresiva de 5 segundos")
    print("- Mantenga su rostro frente a la cámara")
    print("- Presione 'n' para nuevo intento o 'q' para salir\n")
    
    try:
        procesar_acceso()
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cv2.destroyAllWindows()