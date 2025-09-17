# Base de Datos - Puerta Orion

## 📋 Configuración

### Variables de Entorno Requeridas

```bash
# Configuración de MySQL
DB_HOST=localhost
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_contraseña_mysql
DB_NAME=puerta_orion
```

### Instalación de Dependencias

```bash
pip install mysql-connector-python==8.2.0
```

## 🗄️ Estructura de la Base de Datos

### Conexión
- **Clase**: `ConexionDB`
- **Archivo**: `conexion.py`
- **Responsabilidad**: Gestionar conexiones a MySQL

### Características
- ✅ **Conexión automática** con variables de entorno
- ✅ **Logging integrado** de operaciones
- ✅ **Manejo de errores** robusto
- ✅ **Cursors con diccionarios** para fácil acceso a datos
- ✅ **Test de conexión** incluido

## 🧪 Testing de Conexión

### 1. Script de Configuración Inicial
```bash
python setup_database.py
```

### 2. Test Completo de Conexión
```bash
python test_conexion.py
```

### 3. Test Simple de Conexión
```bash
python test_conexion.py --simple
```

### 4. Test via API
```bash
curl http://localhost:5000/test-db
```

## 💻 Uso en el Código

### Conexión Básica
```python
from src.database.conexion import ConexionDB

# Crear instancia
db = ConexionDB()

# Conectar
conexion = db.conectar()
if conexion:
    # Obtener cursor
    cursor = db.obtener_cursor()
    
    # Ejecutar consulta
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    
    # Cerrar conexión
    db.cerrar()
```

### Test de Conexión
```python
from src.database.conexion import ConexionDB

db = ConexionDB()
resultado = db.test_conexion()

if resultado['exito']:
    print("✅ Conexión exitosa")
    print(f"Tiempo: {resultado['tiempo_conexion']:.3f}s")
    print(f"Versión MySQL: {resultado['detalles']['version_mysql']}")
else:
    print(f"❌ Error: {resultado['mensaje']}")
```

## 📊 Logging de Base de Datos

Todas las operaciones se registran automáticamente en:
- **Archivo**: `logs/database/db.log`
- **Formato**: Timestamp - Operación - Tabla - Duración

### Ejemplos de Logs
```
2024-01-09 10:30:15 - base_datos - INFO - BaseDatos: {'operacion': 'CONEXION', 'tabla': 'sistema', 'consulta': 'Conectando a localhost/puerta_orion', 'duracion': 0.023}
2024-01-09 10:30:16 - base_datos - INFO - BaseDatos: {'operacion': 'SELECT', 'tabla': 'usuarios', 'consulta': 'SELECT * FROM usuarios', 'duracion': 0.005}
```

## 🔧 Configuración de MySQL

### Crear Base de Datos
```sql
CREATE DATABASE puerta_orion;
```

### Crear Usuario
```sql
CREATE USER 'puerta_orion_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON puerta_orion.* TO 'puerta_orion_user'@'localhost';
FLUSH PRIVILEGES;
```

### Verificar Permisos
```sql
SHOW GRANTS FOR 'puerta_orion_user'@'localhost';
```

## 🚨 Solución de Problemas

### Error: "Access denied for user"
- Verificar credenciales en `.env`
- Confirmar que el usuario existe en MySQL
- Verificar permisos del usuario

### Error: "Can't connect to MySQL server"
- Verificar que MySQL esté ejecutándose
- Confirmar host y puerto correctos
- Verificar firewall/red

### Error: "Unknown database"
- Ejecutar `python setup_database.py` para crear la BD
- Verificar nombre de la base de datos en `.env`

### Error: "Connection timeout"
- Verificar conectividad de red
- Aumentar timeout en configuración si es necesario
- Verificar carga del servidor MySQL

## 📈 Monitoreo

### Ver Logs de Base de Datos
```bash
tail -f logs/database/db.log
```

### Verificar Estado de Conexiones
```sql
SHOW PROCESSLIST;
SHOW STATUS LIKE 'Threads_connected';
```

### Monitorear Rendimiento
```sql
SHOW STATUS LIKE 'Slow_queries';
SHOW STATUS LIKE 'Questions';
```

## 🔒 Seguridad

- ✅ **Variables de entorno** para credenciales
- ✅ **Logs sin información sensible**
- ✅ **Conexiones con timeout**
- ✅ **Manejo seguro de errores**
- ✅ **Archivos .env en .gitignore**
