import sqlite3

# Ruta donde se guardará la base de datos
db_path = "database/sistema_accesos.db"

# Conectar a SQLite (si no existe, la crea)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear tabla de empleados
cursor.execute("""
CREATE TABLE IF NOT EXISTS empleados (
    id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    dni TEXT UNIQUE NOT NULL,
    ruta_rostro TEXT NOT NULL,
    estado TEXT CHECK(estado IN ('activo', 'inactivo')) NOT NULL DEFAULT 'activo',
    nivel_acceso INTEGER CHECK(nivel_acceso BETWEEN 1 AND 5) NOT NULL
);
""")

# Crear tabla de áreas
cursor.execute("""
CREATE TABLE IF NOT EXISTS areas (
    id_area INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_area TEXT NOT NULL,
    descripcion TEXT,
    nivel_seguridad INTEGER CHECK(nivel_seguridad BETWEEN 1 AND 5) NOT NULL
);
""")

# Crear tabla de permisos
cursor.execute("""
CREATE TABLE IF NOT EXISTS permisos (
    id_permiso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER NOT NULL,
    id_area INTEGER NOT NULL,
    fecha_concesion DATE NOT NULL,
    fecha_expiracion DATE,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_area) REFERENCES areas(id_area)
);
""")

# Crear tabla de registros de acceso
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros_acceso (
    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER,
    id_area INTEGER NOT NULL,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_acceso TEXT CHECK(tipo_acceso IN ('entrada', 'salida')) NOT NULL,
    metodo_autenticacion TEXT CHECK(metodo_autenticacion IN ('huella', 'reconocimiento_facial', 'tarjeta')) NOT NULL,
    acceso_concedido BOOLEAN NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_area) REFERENCES areas(id_area)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS intentos_fallidos (
    id_intento INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_area INTEGER NOT NULL,
    imagen_captura TEXT,  -- Ruta de la imagen almacenada
    FOREIGN KEY (id_area) REFERENCES areas(id_area)
);
""")


# Crear tabla de incidentes
cursor.execute("""
CREATE TABLE IF NOT EXISTS incidentes (
    id_incidente INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_empleado_reporta INTEGER,
    tipo_incidente TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    severidad TEXT CHECK(severidad IN ('baja', 'media', 'alta', 'critica')) NOT NULL,
    estado TEXT CHECK(estado IN ('reportado', 'investigacion', 'resuelto', 'escalado')) DEFAULT 'reportado',
    acciones_tomadas TEXT,
    FOREIGN KEY (id_empleado_reporta) REFERENCES empleados(id_empleado)
);
""")

# Confirmar cambios y cerrar conexión
conn.commit()
conn.close()

print("✅ Base de datos creada exitosamente y tablas generadas.")
print("   Puedes encontrar la base de datos en la ruta:", db_path)
