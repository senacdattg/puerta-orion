# Sistema de Logs - Puerta Orion

## 📁 Estructura de Directorios

```
logs/
├── app/                    # Logs de la aplicación principal
│   ├── app.log            # Log general de la aplicación
│   ├── error.log          # Log de errores y excepciones
│   └── access.log         # Log de peticiones HTTP
├── database/              # Logs de base de datos
│   └── db.log            # Operaciones de BD
└── archive/               # Logs archivados por fecha
    └── (archivos rotados automáticamente)
```

## 🔧 Configuración

Las configuraciones de logs se definen en las variables de entorno:

```bash
# Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Directorio principal de logs
LOG_DIR=logs

# Archivos específicos de logs
LOG_FILE=logs/app/app.log
LOG_ERROR_FILE=logs/app/error.log
LOG_ACCESS_FILE=logs/app/access.log
LOG_DB_FILE=logs/database/db.log
LOG_ARCHIVE_DIR=logs/archive
```

## 📝 Tipos de Logs

### 1. **App Log** (`logs/app/app.log`)
- Logs generales de la aplicación
- Información de inicio y configuración
- Mensajes de debug en desarrollo

### 2. **Error Log** (`logs/app/error.log`)
- Errores y excepciones no manejadas
- Stack traces completos
- Información de contexto del error

### 3. **Access Log** (`logs/app/access.log`)
- Todas las peticiones HTTP
- Método, ruta, IP, User-Agent
- Código de respuesta y duración

### 4. **Database Log** (`logs/database/db.log`)
- Operaciones de base de datos
- Queries ejecutadas
- Tiempo de ejecución

## 🔄 Rotación Automática

- **Tamaño máximo**: 10MB por archivo
- **Archivos de backup**: 5 archivos por tipo
- **Rotación**: Automática cuando se alcanza el límite

## 💻 Uso en el Código

```python
from src.utils.logger import get_logger, log_error, log_database

# Logger general
logger = get_logger('app')
logger.info('Mensaje informativo')
logger.warning('Advertencia')

# Logger de errores
log_error(exception, {'context': 'información adicional'})

# Logger de base de datos
log_database('SELECT', 'usuarios', 'SELECT * FROM usuarios', 0.05)
```

## 🚀 Características

- ✅ **Rotación automática** de archivos
- ✅ **Diferentes niveles** de logging
- ✅ **Logs separados** por tipo de operación
- ✅ **Formato consistente** con timestamp
- ✅ **Configuración centralizada** via variables de entorno
- ✅ **Middleware automático** para peticiones HTTP
- ✅ **Manejo de errores** automático

## 📊 Monitoreo

Los logs se pueden monitorear usando:

```bash
# Ver logs en tiempo real
tail -f logs/app/app.log

# Ver errores
tail -f logs/app/error.log

# Ver peticiones
tail -f logs/app/access.log

# Ver operaciones de BD
tail -f logs/database/db.log
```

## 🔒 Seguridad

- Los archivos de logs están incluidos en `.gitignore`
- No contienen información sensible por defecto
- Se recomienda revisar logs antes de compartir





