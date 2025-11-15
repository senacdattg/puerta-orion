# Tests para Puerta Orion

Este directorio contiene todos los tests de la aplicación, organizados siguiendo las mejores prácticas de testing.

## Estructura

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartidas
├── test_helpers.py          # Utilidades y helpers
├── README.md                # Este archivo
└── routes/
    ├── __init__.py
    ├── test_deportistas_routes.py
    ├── test_eventos_routes.py
    ├── test_catalogos_routes.py
    └── test_auth_routes.py
```

## Instalación de Dependencias

```bash
pip install -r requirements.txt
```

Las dependencias de testing incluyen:
- `pytest`: Framework de testing
- `pytest-flask`: Extensión para Flask
- `pytest-cov`: Cobertura de código
- `pytest-mock`: Mocks y stubs
- `faker`: Generación de datos de prueba
- `freezegun`: Control de tiempo en tests

## Ejecutar Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests con cobertura
```bash
pytest --cov=src --cov-report=html
```

### Ejecutar tests específicos
```bash
# Por archivo
pytest tests/routes/test_deportistas_routes.py

# Por clase
pytest tests/routes/test_deportistas_routes.py::TestCrearDeportista

# Por función
pytest tests/routes/test_deportistas_routes.py::TestCrearDeportista::test_crear_deportista_success
```

### Ejecutar tests por marcadores
```bash
# Solo tests de rutas
pytest -m routes

# Solo tests de autenticación
pytest -m auth

# Solo tests unitarios
pytest -m unit

# Excluir tests lentos
pytest -m "not slow"
```

### Ejecutar con verbosidad
```bash
pytest -v          # Verboso
pytest -vv         # Muy verboso
pytest -s          # Mostrar prints
```

## Principios Aplicados

### 1. AAA Pattern (Arrange-Act-Assert)
Cada test sigue el patrón:
- **Arrange**: Preparar datos y mocks
- **Act**: Ejecutar la acción a probar
- **Assert**: Verificar el resultado

### 2. DRY (Don't Repeat Yourself)
- Fixtures reutilizables en `conftest.py`
- Helpers comunes en `test_helpers.py`
- Datos de prueba estandarizados

### 3. Isolation (Aislamiento)
- Cada test es independiente
- Base de datos limpia por test
- Mocks para dependencias externas

### 4. Fast (Rápido)
- SQLite en memoria para tests
- Mocks para servicios pesados
- Tests paralelos cuando sea posible

### 5. Clear Names (Nombres Claros)
- Nombres descriptivos que explican qué se prueba
- Clases agrupadas por funcionalidad
- Tests que documentan el comportamiento

## Fixtures Disponibles

### Aplicación y Cliente
- `app`: Instancia de Flask para testing
- `client`: Cliente HTTP para hacer requests

### Datos de Prueba
- `sample_persona_data`: Datos de persona
- `sample_deportista_data`: Datos de deportista
- `sample_evento_data`: Datos de evento
- `sample_usuario_data`: Datos de usuario

### Modelos de BD
- `tipo_documento`: Tipo de documento creado
- `sexo`: Sexo creado
- `categoria`: Categoría creada
- `persona`: Persona creada
- `usuario`: Usuario creado
- `deportista`: Deportista creado

### Mocks
- `mock_get_current_user`: Mock de usuario autenticado
- `mock_token_required`: Mock del decorador de autenticación
- `mock_logger`: Mock del logger

## Helpers Disponibles

### Validación de Respuestas
- `assert_success_response()`: Valida respuesta exitosa
- `assert_error_response()`: Valida respuesta de error

### Requests
- `make_json_request()`: Hace request JSON de forma conveniente
- `create_auth_headers()`: Crea headers de autenticación

## Cobertura de Código

El objetivo es mantener una cobertura mínima del 70%. Para ver el reporte:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # En macOS/Linux
```

## Buenas Prácticas

1. **Un test, una aserción**: Cada test debe verificar un comportamiento específico
2. **Tests independientes**: No depender de otros tests
3. **Nombres descriptivos**: El nombre del test debe explicar qué prueba
4. **Mocks apropiados**: Mockear dependencias externas, no código interno
5. **Datos realistas**: Usar datos que representen casos reales
6. **Limpieza**: Cada test debe limpiar después de sí mismo

## Ejemplo de Test

```python
def test_crear_deportista_success(self, client, sample_deportista_data):
    """Test: Crear deportista exitosamente."""
    # Arrange
    mock_result = {
        'success': True,
        'message': 'Deportista creado exitosamente',
        'data': {'id_deportista': 1},
        'status_code': 201
    }
    
    # Act
    with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista',
               return_value=mock_result):
        response = make_json_request(
            client, 'POST', '/api/deportistas/',
            data=sample_deportista_data
        )
    
    # Assert
    data = assert_success_response(response, expected_status=201)
    assert 'data' in data
    assert data['data']['id_deportista'] == 1
```

## Troubleshooting

### Error: "Module not found"
Asegúrate de ejecutar los tests desde el directorio `backend/`:
```bash
cd backend
pytest
```

### Error: "Database locked"
Los tests usan SQLite en memoria, no debería ocurrir. Si pasa, verifica que no haya conexiones abiertas.

### Tests muy lentos
- Usa mocks para servicios externos
- Evita tests de integración cuando no sean necesarios
- Usa `pytest-xdist` para paralelización

## CI/CD

Los tests deben ejecutarse automáticamente en CI/CD:
```yaml
# Ejemplo para GitHub Actions
- name: Run tests
  run: |
    cd backend
    pytest --cov=src --cov-report=xml
```

