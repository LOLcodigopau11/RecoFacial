import sys
from datetime import datetime

import mysql.connector

sys.path.append(".")
from config.db_config import get_db_config


def conectar_bd():
    config = get_db_config()
    return mysql.connector.connect(**config)


def obtener_empleado_por_dni(conn, dni):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id_empleado, nombre, apellidos, nivel_acceso FROM empleados WHERE dni = %s",
        (dni,),
    )
    return cursor.fetchone()


def obtener_empleado_por_id(conn, id_empleado):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nombre, apellidos, dni, nivel_acceso FROM empleados WHERE id_empleado = %s",
        (id_empleado,),
    )
    return cursor.fetchone()


def obtener_permisos_empleado(conn, id_empleado):
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT p.id_permiso, a.nombre_area, p.fecha_expiracion
        FROM permisos p
        JOIN areas a ON p.id_area = a.id_area
        WHERE p.id_empleado = %s
    """,
        (id_empleado,),
    )
    return cursor.fetchall()


def obtener_id_area_por_nombre(conn, nombre_area):
    cursor = conn.cursor()
    cursor.execute("SELECT id_area FROM areas WHERE nombre_area = %s", (nombre_area,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None


def eliminar_permiso(conn, id_empleado, id_area):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM permisos WHERE id_empleado = %s AND id_area = %s",
        (id_empleado, id_area),
    )
    conn.commit()
    return cursor.rowcount > 0


def actualizar_fecha_expiracion(conn, id_empleado, id_area, nueva_fecha):
    cursor = conn.cursor()
    try:
        datetime.strptime(nueva_fecha, "%Y-%m-%d")  # Validar formato de fecha
        cursor.execute(
            "UPDATE permisos SET fecha_expiracion = %s WHERE id_empleado = %s AND id_area = %s",
            (nueva_fecha, id_empleado, id_area),
        )
        conn.commit()
        return cursor.rowcount > 0
    except ValueError:
        print("[ERROR] Formato de fecha incorrecto. Debe ser YYYY-MM-DD.")
        return False


def mostrar_menu():
    print("\n--- Gestión de Permisos ---")
    print("1. Buscar empleado")
    print("2. Quitar permiso de un área")
    print("3. Cambiar fecha de expiración de un permiso")
    print("4. Salir")
    return input("Seleccione una opción: ")


def gestionar_permisos():
    conn = conectar_bd()
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            tipo_busqueda = input("Buscar por (1) DNI o (2) ID: ")
            if tipo_busqueda == "1":
                dni = input("Ingrese el DNI del empleado: ").strip()
                empleado = obtener_empleado_por_dni(conn, dni)
                if empleado:
                    print(
                        f"Empleado encontrado: ID={empleado[0]}, Nombre={empleado[1]}, Apellidos={empleado[2]}, Nivel={empleado[3]}"
                    )
                    permisos = obtener_permisos_empleado(conn, empleado[0])
                    if permisos:
                        print("Permisos actuales:")
                        for permiso in permisos:
                            print(f"- Área: {permiso[1]}, Expira: {permiso[2]}")
                    else:
                        print("El empleado no tiene permisos asignados.")
                else:
                    print("[ADVERTENCIA] No se encontró ningún empleado con ese DNI.")
            elif tipo_busqueda == "2":
                try:
                    id_empleado = int(input("Ingrese el ID del empleado: ").strip())
                    empleado = obtener_empleado_por_id(conn, id_empleado)
                    if empleado:
                        print(
                            f"Empleado encontrado: Nombre={empleado[0]}, Apellidos={empleado[1]}, DNI={empleado[2]}, ID={id_empleado}, Nivel={empleado[3]}"
                        )
                        permisos = obtener_permisos_empleado(conn, id_empleado)
                        if permisos:
                            print("Permisos actuales:")
                            for permiso in permisos:
                                print(f"- Área: {permiso[1]}, Expira: {permiso[2]}")
                        else:
                            print("El empleado no tiene permisos asignados.")
                    else:
                        print(
                            "[ADVERTENCIA] No se encontró ningún empleado con ese ID."
                        )
                except ValueError:
                    print("[ERROR] El ID del empleado debe ser un número.")
            else:
                print("[ERROR] Opción de búsqueda no válida.")

        elif opcion == "2":
            dni_empleado = input(
                "Ingrese el DNI del empleado al que quitar permiso: "
            ).strip()
            empleado = obtener_empleado_por_dni(conn, dni_empleado)
            if empleado:
                id_empleado = empleado[0]
                permisos = obtener_permisos_empleado(conn, id_empleado)
                if permisos:
                    print("Permisos actuales:")
                    for i, permiso in enumerate(permisos):
                        print(f"{i+1}. Área: {permiso[1]}, Expira: {permiso[2]}")
                    try:
                        seleccion = (
                            int(
                                input(
                                    "Ingrese el número del área para quitar el permiso: "
                                )
                            )
                            - 1
                        )
                        if 0 <= seleccion < len(permisos):
                            nombre_area_quitar = permisos[seleccion][1]
                            id_area_quitar = obtener_id_area_por_nombre(
                                conn, nombre_area_quitar
                            )
                            if id_area_quitar:
                                if eliminar_permiso(conn, id_empleado, id_area_quitar):
                                    print(
                                        f"[OK] Permiso para '{nombre_area_quitar}' removido exitosamente."
                                    )
                                else:
                                    print("[ERROR] No se pudo remover el permiso.")
                            else:
                                print("[ERROR] No se encontró el ID del área.")
                        else:
                            print("[ERROR] Selección inválida.")
                    except ValueError:
                        print("[ERROR] Ingrese un número válido.")
                else:
                    print("El empleado no tiene permisos asignados.")
            else:
                print("[ADVERTENCIA] No se encontró ningún empleado con ese DNI.")

        elif opcion == "2":
            dni_empleado = input(
                "Ingrese el DNI del empleado para cambiar la fecha de expiración: "
            ).strip()
            empleado = obtener_empleado_por_dni(conn, dni_empleado)
            if empleado:
                id_empleado = empleado[0]
                permisos = obtener_permisos_empleado(conn, id_empleado)
                if permisos:
                    print("Permisos actuales:")
                    for i, permiso in enumerate(permisos):
                        print(f"{i+1}. Área: {permiso[1]}, Expira: {permiso[2]}")
                    try:
                        seleccion = (
                            int(
                                input(
                                    "Ingrese el número del área para cambiar la fecha: "
                                )
                            )
                            - 1
                        )
                        if 0 <= seleccion < len(permisos):
                            nombre_area_cambiar = permisos[seleccion][1]
                            id_area_cambiar = obtener_id_area_por_nombre(
                                conn, nombre_area_cambiar
                            )
                            if id_area_cambiar:
                                nueva_fecha = input(
                                    "Ingrese la nueva fecha de expiración (YYYY-MM-DD): "
                                ).strip()
                                if actualizar_fecha_expiracion(
                                    conn, id_empleado, id_area_cambiar, nueva_fecha
                                ):
                                    print(
                                        f"[OK] Fecha de expiración para '{nombre_area_cambiar}' actualizada."
                                    )
                                else:
                                    print(
                                        "[ERROR] No se pudo actualizar la fecha de expiración."
                                    )
                            else:
                                print("[ERROR] No se encontró el ID del área.")
                        else:
                            print("[ERROR] Selección inválida.")
                    except ValueError:
                        print("[ERROR] Ingrese un número válido.")
                else:
                    print("El empleado no tiene permisos asignados.")
            else:
                print("[ADVERTENCIA] No se encontró ningún empleado con ese DNI.")

        elif opcion == "4":
            break

        else:
            print("[ERROR] Opción inválida. Seleccione una opción del menú.")

    conn.close()


if __name__ == "__main__":
    gestionar_permisos()
