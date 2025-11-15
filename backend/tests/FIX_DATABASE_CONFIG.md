# Solución al Problema de Configuración de Base de Datos en Tests

## Problema

Los tests intentan conectarse a MySQL en lugar de usar SQLite en memoria porque:

1. La clase `Config` en `config.py` construye `SQLALCHEMY_DATABASE_URI` en tiempo de importación (cuando se define la clase)
2. Esto ocurre ANTES de que el fixture `clean_env_for_tests` pueda limpiar las variables de entorno
3. Flask-SQLAlchemy cachea el engine cuando se llama `db.init_app()`, y luego no se actualiza aunque cambiemos la configuración

## Solución Implementada

1. **Fixture `clean_env_for_tests` con `autouse=True`**: Se ejecuta automáticamente antes de cada test para limpiar variables de entorno
2. **Fixture `app` actualiza configuración**: Fuerza `SQLALCHEMY_DATABASE_URI` a SQLite en memoria
3. **Limpieza del cache de engines**: Limpia el cache interno de Flask-SQLAlchemy para forzar recreación del engine

## Si Aún Falla

### Opción 1: Limpiar variables de entorno manualmente

```powershell
# Windows PowerShell
$env:DATABASE_URL = ""
$env:DB_HOST = ""
$env:MYSQL_HOST = ""
$env:FLASK_ENV = "testing"
cd backend
pytest
```

### Opción 2: Verificar archivo .env

Si hay un archivo `.env` en `backend/` con variables de MySQL, puede estar interfiriendo. Considera:
- Renombrarlo temporalmente: `mv .env .env.backup`
- O asegurarte de que `TestingConfig` tenga prioridad

### Opción 3: Modificar config.py (Solución más robusta)

Hacer que `Config` construya la URI de forma lazy (cuando se accede, no cuando se define):

```python
class Config:
    @property
    def SQLALCHEMY_DATABASE_URI(self):
        # Construir URI aquí en lugar de en tiempo de importación
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            # ... lógica de construcción ...
        return database_url
```

Pero esto requeriría cambios más extensos en el código.

## Verificación

Para verificar que funciona:

```bash
cd backend
pytest tests/routes/test_catalogos_routes.py::TestCatalogosGenerales::test_obtener_tipos_documento -v
```

Si este test pasa, los demás deberían funcionar también.

