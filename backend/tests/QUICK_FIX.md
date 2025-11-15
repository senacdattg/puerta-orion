# Solución Rápida para Tests

Si los tests aún fallan con errores de conexión a MySQL, ejecuta estos comandos antes de correr los tests:

## Windows PowerShell

```powershell
# Limpiar variables de entorno de MySQL
$env:DATABASE_URL = ""
$env:DB_HOST = ""
$env:MYSQL_HOST = ""
$env:DB_PORT = ""
$env:DB_USERNAME = ""
$env:DB_USER = ""
$env:DB_PASSWORD = ""
$env:MYSQL_PASSWORD = ""
$env:DB_NAME = ""

# Establecer entorno de testing
$env:FLASK_ENV = "testing"

# Ejecutar tests
cd backend
pytest
```

## Linux/Mac

```bash
# Limpiar variables de entorno de MySQL
unset DATABASE_URL
unset DB_HOST
unset MYSQL_HOST
unset DB_PORT
unset DB_USERNAME
unset DB_USER
unset DB_PASSWORD
unset MYSQL_PASSWORD
unset DB_NAME

# Establecer entorno de testing
export FLASK_ENV=testing

# Ejecutar tests
cd backend
pytest
```

## Verificar que funciona

```bash
# Ejecutar un solo test primero para verificar
pytest tests/routes/test_catalogos_routes.py::TestCatalogosGenerales::test_obtener_tipos_documento -v

# Si funciona, ejecutar todos
pytest
```

## Si aún falla

1. Verifica que no haya un archivo `.env` en el directorio `backend/` con variables de MySQL
2. Verifica que `TestingConfig` en `config.py` tenga `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'`
3. Ejecuta los tests con `--no-cov` para evitar problemas de cobertura:
   ```bash
   pytest --no-cov
   ```

