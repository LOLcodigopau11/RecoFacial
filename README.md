# 🔐 Sistema de Reconocimiento Facial

Sistema de control de accesos que usa **reconocimiento facial con IA** para identificar empleados y gestionar permisos de acceso a diferentes áreas.

---

## 🎯 ¿Cómo Funciona?

1. **Captura** → Tomas 100 fotos del rostro de un empleado
2. **Entrena** → La IA aprende a reconocer esa cara
3. **Detecta** → La webcam identifica a la persona en tiempo real
4. **Controla** → Permite o deniega acceso según el nivel de seguridad (1-5)

**Tecnologías:** Python + OpenCV + MySQL

---

## 📋 Requisitos

- Python 3.9+ ([Descargar](https://www.python.org/downloads/))
- XAMPP con MySQL ([Descargar](https://www.apachefriends.org/))
- Webcam

---

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/LOLcodigopau11/RecoFacial.git
cd RecoFacial
```

### 2. Instalar PDM

```bash
pip install pdm
```

### 3. Instalar Dependencias

```bash
pdm install
```

### 4. Iniciar MySQL en XAMPP

Abre XAMPP → Click en **Start** junto a MySQL

### 5. Configurar Base de Datos

Edita `config/db_config.py` con tus credenciales:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",  # Vacío para XAMPP por defecto
    "database": "sistema_accesos",
    "port": 3306,
}
```

### 6. Crear Tablas

```bash
pdm run python database/crear_bd.py
pdm run python src/gestion_bd/agregar_areas.py
```

---

## 🎮 Uso Básico

### Registrar Empleado

```bash
pdm run python src/captura_entrenamiento/captura_rostros.py
```

Ingresa: Nombre, Apellidos, DNI, Nivel (1-5)

### Entrenar Modelo

```bash
pdm run python src/captura_entrenamiento/entrenar_modelo.py
```

### Asignar Permisos

```bash
pdm run python src/gestion_bd/dar_permisos.py
```

### Probar Reconocimiento

```bash
# Demo simple
pdm run python main.py

# Control de acceso (Sala Servidores)
pdm run python src/deteccion/area_servidores.py
```

**Controles:** `ESPACIO` = intentar acceso, `Q` = salir

---

## 📊 Niveles de Acceso

| Nivel | Acceso |
|-------|--------|
| 1 | Entrada Principal |
| 2 | Nivel 1 + Sala Reuniones |
| 3 | Nivel 2 + Oficina Seguridad + Sala Juntas |
| 4 | Nivel 3 + Laboratorio + Área Investigación |
| 5 | **TODO** (incluye Sala Servidores) |

---

## ❓ Problemas Comunes

**❌ "Module 'cv2' not found"**  
→ Usa siempre `pdm run python` en lugar de solo `python`

**❌ "Can't connect to MySQL"**  
→ Verifica que MySQL esté corriendo en XAMPP (luz verde)

**❌ "No se encontraron rostros"**  
→ Primero registra un empleado, luego entrena el modelo

---

## 📝 Resumen Rápido

```bash
# Instalar
pip install pdm
pdm install

# Configurar (edita config/db_config.py)
pdm run python database/crear_bd.py
pdm run python src/gestion_bd/agregar_areas.py

# Usar
pdm run python src/captura_entrenamiento/captura_rostros.py
pdm run python src/captura_entrenamiento/entrenar_modelo.py
pdm run python src/gestion_bd/dar_permisos.py
pdm run python main.py
```

---
