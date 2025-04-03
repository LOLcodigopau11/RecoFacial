import sqlite3

def conectar_bd():
    return sqlite3.connect("database/sistema_accesos.db")

def mostrar_empleados():
    """Muestra el contenido de la tabla empleados."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM empleados")
    empleados = cursor.fetchall()
    print("\n--- Empleados ---")
    for empleado in empleados:
        print(f"ID: {empleado[0]}, Nombre: {empleado[1]}, Apellidos: {empleado[2]}, DNI: {empleado[3]}, Estado: {empleado[5]}, Nivel de Acceso: {empleado[6]}")
    conn.close()

def mostrar_areas():
    """Muestra el contenido de la tabla áreas."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM areas")
    areas = cursor.fetchall()
    print("\n--- Áreas ---")
    for area in areas:
        print(f"ID: {area[0]}, Nombre: {area[1]}, Descripción: {area[2]}, Nivel de Seguridad: {area[3]}")
    conn.close()

def mostrar_permisos():
    """Muestra el contenido de la tabla permisos."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM permisos")
    permisos = cursor.fetchall()
    print("\n--- Permisos ---")
    for permiso in permisos:
        print(f"ID Permiso: {permiso[0]}, ID Empleado: {permiso[1]}, ID Área: {permiso[2]}, Fecha Concesión: {permiso[3]}, Fecha Expiración: {permiso[4]}")
    conn.close()

def mostrar_registros_acceso():
    """Muestra el contenido de la tabla registros de acceso."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM registros_acceso")
    registros = cursor.fetchall()
    print("\n--- Registros de Acceso ---")
    for registro in registros:
        print(f"ID Registro: {registro[0]}, ID Empleado: {registro[1]}, ID Área: {registro[2]}, Fecha/Hora: {registro[3]}, Tipo de Acceso: {registro[4]}, Método de Autenticación: {registro[5]}, Acceso Concedido: {registro[6]}")
    conn.close()

def mostrar_intentos_fallidos():
    """Muestra el contenido de la tabla intentos fallidos."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM intentos_fallidos")
    intentos = cursor.fetchall()
    print("\n--- Intentos Fallidos ---")
    for intento in intentos:
        print(f"ID Intento: {intento[0]}, Fecha/Hora: {intento[1]}, ID Área: {intento[2]}, Imagen Captura: {intento[3]}")
    conn.close()

def mostrar_incidentes():
    """Muestra el contenido de la tabla incidentes."""
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM incidentes")
    incidentes = cursor.fetchall()
    print("\n--- Incidentes ---")
    for incidente in incidentes:
        print(f"ID Incidente: {incidente[0]}, Fecha/Hora: {incidente[1]}, ID Empleado (Reporta): {incidente[2]}, Tipo de Incidente: {incidente[3]}, Descripción: {incidente[4]}, Severidad: {incidente[5]}, Estado: {incidente[6]}, Acciones Tomadas: {incidente[7]}")
    conn.close()

def mostrar_menu():
    """Muestra las opciones en el terminal."""
    while True:
        print("\n--- Menú de Opciones ---")
        print("1. Ver empleados")
        print("2. Ver áreas")
        print("3. Ver permisos")
        print("4. Ver registros de acceso")
        print("5. Ver intentos fallidos")
        print("6. Ver incidentes")
        print("7. Salir")
        
        opcion = input("Seleccione una opción (1-7): ").strip()
        
        if opcion == '1':
            mostrar_empleados()
        elif opcion == '2':
            mostrar_areas()
        elif opcion == '3':
            mostrar_permisos()
        elif opcion == '4':
            mostrar_registros_acceso()
        elif opcion == '5':
            mostrar_intentos_fallidos()
        elif opcion == '6':
            mostrar_incidentes()
        elif opcion == '7':
            print("Saliendo del sistema...")
            break
        else:
            print("⚠️ Opción no válida, por favor ingrese un número entre 1 y 7.")

if __name__ == "__main__":
    mostrar_menu()
