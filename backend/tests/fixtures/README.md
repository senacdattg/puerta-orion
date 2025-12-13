# Fixtures Organizadas por Dominio

Este directorio contiene fixtures organizadas por dominio funcional para mantener el código de tests limpio y modular.

## 📁 Estructura

```
fixtures/
├── __init__.py              # Exporta todas las fixtures
├── app_fixtures.py          # Fixtures de aplicación Flask
├── data_fixtures.py          # Fixtures de datos de prueba
├── model_fixtures.py         # Fixtures de modelos de BD
├── mock_fixtures.py          # Fixtures de mocks y stubs
└── README.md                # Este archivo
```

## 🎯 Organización

### `app_fixtures.py`
Fixtures relacionadas con la aplicación Flask y cliente HTTP:
- `auth_headers`: Headers de autenticación para requests

### `data_fixtures.py`
Fixtures que proporcionan datos de ejemplo (diccionarios):
- `sample_persona_data`: Datos para crear una persona
- `sample_deportista_data`: Datos para crear un deportista
- `sample_evento_data`: Datos para crear un evento
- `sample_usuario_data`: Datos para crear un usuario

### `model_fixtures.py`
Fixtures que crean instancias de modelos en la base de datos:
- `tipo_documento`: Tipo de documento creado
- `sexo`: Sexo creado
- `categoria`: Categoría creada
- `tipo_evento`: Tipo de evento creado
- `persona`: Persona creada
- `usuario`: Usuario creado
- `deportista`: Deportista creado

### `mock_fixtures.py`
Fixtures que mockean dependencias externas:
- `mock_get_current_user`: Mock de usuario autenticado
- `mock_token_required`: Mock del decorador de autenticación
- `mock_logger`: Mock del logger

## 🔧 Uso

Todas las fixtures están disponibles automáticamente en todos los tests gracias a `conftest.py`:

```python
def test_crear_persona(client, sample_persona_data, mock_token_required):
    """Test que usa fixtures de datos y mocks."""
    response = client.post(
        '/api/personas',
        json=sample_persona_data,
        headers=auth_headers
    )
    assert response.status_code == 201
```

## 📝 Convenciones

1. **Nombres descriptivos**: Los nombres deben indicar claramente qué proporcionan
2. **Dependencias explícitas**: Las fixtures deben declarar sus dependencias
3. **Scope apropiado**: Usar `function` para datos que cambian entre tests
4. **Documentación**: Cada fixture debe tener un docstring claro

## ✅ Beneficios

- **Organización**: Fácil encontrar fixtures por dominio
- **Mantenimiento**: Cambios aislados por archivo
- **Reutilización**: Fixtures compartidas automáticamente
- **Legibilidad**: Código más limpio y fácil de entender

