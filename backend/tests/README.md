# Tests para Puerta Orion

Este directorio contiene todos los tests de la aplicación, organizados de forma modular y profesional siguiendo las mejores prácticas de testing.

## 📁 Estructura

```
tests/
├── __init__.py                 # Módulo principal de tests
├── conftest.py                 # Fixtures globales compartidas
├── README.md                   # Este archivo
│
├── unit/                       # Tests unitarios
│   └── services/              # Tests de servicios
│       ├── test_mercadopago_service.py
│       └── auth/              # Tests de servicios de autenticación
│
├── integration/                # Tests de integración
│   ├── routes/                # Tests de endpoints/rutas
│   │   ├── test_auth_routes.py
│   │   ├── test_deportistas_routes.py
│   │   ├── test_eventos_routes.py
│   │   └── ...
│   └── seeders/               # Tests de seeders
│       └── test_seed_roles.py
│
├── fixtures/                   # Fixtures específicas por dominio
│   └── __init__.py
│
└── helpers/                    # Utilidades y helpers
    ├── assertions.py          # Assertions personalizadas
    ├── requests.py            # Utilidades para requests HTTP
    └── test_config.py         # Configuración de tests
```

## 🎯 Tipos de Tests

### Tests Unitarios (`unit/`)
Prueban componentes individuales de forma aislada, usando mocks para todas las dependencias externas.

**Ubicación:** `tests/unit/`

**Características:**
- Rápidos de ejecutar
- Aislados (no dependen de BD ni servicios externos)
- Usan mocks extensivamente
- Ejemplo: `unit/services/test_mercadopago_service.py`

### Tests de Integración (`integration/`)
Prueban la interacción entre múltiples componentes (rutas, servicios, base de datos).

**Ubicación:** `tests/integration/`

**Características:**
- Prueban flujos completos
- Usan base de datos real (SQLite en memoria)
- Pueden usar mocks para servicios externos
- Ejemplo: `integration/routes/test_eventos_routes.py`

## 🚀 Ejecutar Tests

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests específicos por tipo
```bash
# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/

# Solo tests de rutas
pytest tests/integration/routes/

# Solo tests de servicios
pytest tests/unit/services/
```

### Ejecutar tests con cobertura
```bash
pytest --cov=src --cov-report=html
```

### Ejecutar tests específicos
```bash
# Por archivo
pytest tests/integration/routes/test_eventos_routes.py

# Por clase
pytest tests/integration/routes/test_eventos_routes.py::TestListarEventos

# Por función
pytest tests/integration/routes/test_eventos_routes.py::TestListarEventos::test_listar_eventos_success
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

## 📚 Helpers Disponibles

### Assertions (`tests.helpers.assertions`)
```python
from tests.helpers import assert_success_response, assert_error_response

# Validar respuesta exitosa
data = assert_success_response(response, expected_status=201)

# Validar respuesta de error
data = assert_error_response(response, expected_status=400)
```

### Requests (`tests.helpers.requests`)
```python
from tests.helpers import make_json_request, create_auth_headers

# Hacer request JSON
response = make_json_request(client, 'POST', '/api/eventos', data={'nombre': 'Test'})

# Crear headers de autenticación
headers = create_auth_headers(token='jwt_token')
```

## 🔧 Fixtures Disponibles

Las fixtures están definidas en `conftest.py` y están disponibles automáticamente en todos los tests:

### Aplicación y Cliente
- `app`: Instancia de Flask para testing
- `client`: Cliente HTTP para hacer requests

### Mocks
- `mock_token_required`: Mock del decorador de autenticación
- `mock_get_current_user`: Mock de usuario autenticado

## 📖 Principios Aplicados

### 1. AAA Pattern (Arrange-Act-Assert)
Cada test sigue el patrón:
- **Arrange**: Preparar datos y mocks
- **Act**: Ejecutar la acción a probar
- **Assert**: Verificar el resultado

### 2. DRY (Don't Repeat Yourself)
- Fixtures reutilizables en `conftest.py`
- Helpers comunes en `helpers/`
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

## 📊 Cobertura de Código

El objetivo es mantener una cobertura mínima del 20%. Para ver el reporte:

```bash
pytest --cov=src --cov-report=html
```

Luego abre `htmlcov/index.html` en tu navegador.

## ✅ Buenas Prácticas

1. **Un test, una aserción**: Cada test debe verificar un comportamiento específico
2. **Tests independientes**: No depender de otros tests
3. **Nombres descriptivos**: El nombre del test debe explicar qué prueba
4. **Mocks apropiados**: Mockear dependencias externas, no código interno
5. **Datos realistas**: Usar datos que representen casos reales
6. **Limpieza**: Cada test debe limpiar después de sí mismo

## 📝 Ejemplo de Test

```python
def test_crear_evento_success(self, client, mock_token_required):
    """Test: Crear evento exitosamente."""
    # Arrange
    datos_evento = {
        'nombre': 'Torneo de Fútbol',
        'fecha_evento': '2024-12-31'
    }
    
    # Act
    response = make_json_request(
        client, 'POST', '/api/eventos/calendario',
        data=datos_evento
    )
    
    # Assert
    data = assert_success_response(response, expected_status=201)
    assert 'data' in data
    assert data['data']['nombre'] == 'Torneo de Fútbol'
```

## 🔍 Troubleshooting

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

## 📚 Documentación Adicional

Para más información, consulta:
- `docs/README.md` - Documentación detallada
- `docs/TROUBLESHOOTING.md` - Solución de problemas comunes
- `docs/TEST_STATUS.md` - Estado actual de los tests

## 🔄 CI/CD

Los tests deben ejecutarse automáticamente en CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Run tests
  run: |
    cd backend
    pytest --cov=src --cov-report=xml
```

