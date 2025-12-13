# Tests de Integración - Rutas

## Estructura Modular

Los tests de integración de rutas están organizados de manera modular, con cada clase de test en su propio archivo, agrupados por funcionalidad.

## Organización

```
backend/tests/integration/routes/
├── archivos/                      # Tests de subida de archivos
│   └── test_subir_archivo.py     # Subir archivo (imágenes, documentos)
│
├── auth/                          # Tests de autenticación
│   ├── test_forgot_password.py   # Solicitar recuperación de contraseña
│   ├── test_reset_password.py    # Resetear contraseña con token
│   ├── test_registro_usuario.py  # Registro de nuevo usuario
│   ├── test_login.py             # Inicio de sesión
│   └── test_obtener_perfil.py    # Obtener perfil del usuario autenticado
│
├── catalogos/                     # Tests de catálogos generales
│   └── test_catalogos_generales.py  # Tipos documento, sexos, catálogos completos
│
├── deportistas/                   # Tests de gestión de deportistas
│   ├── test_crear_deportista.py      # Crear nuevo deportista
│   ├── test_registro_completo.py    # Registro completo de deportista
│   ├── test_obtener_deportista.py   # Obtener deportista por ID
│   ├── test_listar_deportistas.py   # Listar deportistas con paginación
│   ├── test_actualizar_deportista.py # Actualizar datos de deportista
│   ├── test_catalogos_deportistas.py # Catálogos específicos (diagnósticos, enfermedades, etc.)
│   └── test_deportistas_integration.py # Tests de integración con BD real
│
├── eventos/                       # Tests de gestión de eventos
│   ├── test_listar_eventos.py       # Listar eventos del calendario
│   ├── test_crear_evento.py         # Crear nuevo evento
│   ├── test_obtener_evento.py       # Obtener evento por ID
│   ├── test_actualizar_evento.py    # Actualizar evento existente
│   ├── test_eliminar_evento.py      # Eliminar evento
│   ├── test_sesiones.py            # Gestión de sesiones (CRUD)
│   ├── test_eventos_proximos.py    # Obtener eventos próximos
│   ├── test_eventos_por_categoria.py # Eventos filtrados por categoría
│   └── test_funciones_auxiliares.py # Funciones helper del módulo
│
├── galeria/                       # Tests de galería de imágenes
│   ├── test_listar_galeria.py    # Listar imágenes con filtros
│   ├── test_obtener_imagen.py    # Obtener imagen individual
│   ├── test_crear_imagen.py      # Crear nueva imagen
│   ├── test_actualizar_imagen.py # Actualizar imagen existente
│   ├── test_eliminar_imagen.py   # Eliminar imagen
│   └── test_catalogos_galeria.py # Obtener catálogos (tipos evento, categorías)
│
├── mensualidades/                 # Tests de mensualidades
│   ├── test_listar_mensualidades.py  # Listar mensualidades con paginación
│   └── test_crear_mensualidad.py     # Crear nueva mensualidad
│
├── pagos/                         # Tests de pagos con Mercado Pago
│   ├── test_crear_preferencia.py     # Crear preferencia de pago
│   ├── test_verificar_pago.py        # Verificar estado de pago
│   ├── test_webhook_mercadopago.py   # Procesar webhook de Mercado Pago
│   └── test_estadisticas_pagos.py    # Obtener estadísticas de pagos
│
├── personas/                      # Tests de gestión de personas
│   └── test_personas_routes.py      # Obtener y crear personas
│
├── usuarios/                      # Tests de gestión de usuarios
│   ├── test_listar_usuarios.py       # Listar usuarios con filtros
│   ├── test_obtener_detalle_usuario.py  # Obtener detalle completo
│   ├── test_actualizar_usuario.py   # Actualizar datos de usuario
│   ├── test_cambiar_rol_usuario.py  # Cambiar rol de usuario
│   └── test_cambiar_estado_usuario.py  # Activar/desactivar usuario
│
└── dynamic_data/                  # Tests de datos dinámicos (catálogos)
    ├── test_listar_dynamic_data.py    # Listar registros de catálogo
    ├── test_crear_dynamic_data.py     # Crear registro en catálogo
    ├── test_actualizar_dynamic_data.py  # Actualizar registro
    ├── test_eliminar_dynamic_data.py    # Eliminar registro
    └── test_obtener_dynamic_data.py     # Obtener registro individual
```

## Convenciones de Nomenclatura

### Archivos
- **Formato**: `test_<accion>_<entidad>.py`
- **Ejemplos**:
  - `test_listar_usuarios.py` - Lista usuarios
  - `test_crear_mensualidad.py` - Crea mensualidad
  - `test_obtener_detalle_usuario.py` - Obtiene detalle de usuario

### Clases
- **Formato**: `Test<Accion><Entidad>`
- **Ejemplos**:
  - `TestListarUsuarios`
  - `TestCrearMensualidad`
  - `TestObtenerDetalleUsuario`

### Métodos
- **Formato**: `test_<accion>_<escenario>`
- **Ejemplos**:
  - `test_listar_usuarios_success` - Caso exitoso
  - `test_crear_mensualidad_sin_json` - Error sin JSON
  - `test_obtener_detalle_usuario_no_encontrado` - Error no encontrado

## Estructura de un Test

Cada archivo de test sigue esta estructura:

```python
"""
Tests para el endpoint de [descripción].

Endpoint: [MÉTODO] /api/[ruta]
Funcionalidad: [Descripción breve de la funcionalidad]
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.[marca_especifica]
class Test[Accion][Entidad]:
    """Tests para el endpoint [MÉTODO] /api/[ruta]"""
    
    def test_[accion]_[escenario](self, client, mock_token_required):
        """Test: [Descripción del test]."""
        # Arrange
        # ... configuración ...
        
        # Act
        # ... ejecución ...
        
        # Assert
        # ... verificaciones ...
```

## Marcadores Pytest

Cada test utiliza marcadores para organización:

- `@pytest.mark.routes` - Identifica tests de rutas
- `@pytest.mark.integration` - Identifica tests de integración
- `@pytest.mark.[especifico]` - Marcador específico del módulo:
  - `@pytest.mark.auth` - Tests de autenticación
  - `@pytest.mark.galeria` - Tests de galería
  - `@pytest.mark.mensualidades` - Tests de mensualidades
  - `@pytest.mark.pagos` - Tests de pagos
  - `@pytest.mark.usuarios` - Tests de usuarios
  - `@pytest.mark.dynamic_data` - Tests de datos dinámicos
  - `@pytest.mark.slow` - Tests de integración con BD real (más lentos)
  - `@pytest.mark.unit` - Tests unitarios de funciones auxiliares

## Ejecutar Tests

### Todos los tests de rutas
```bash
pytest tests/integration/routes/ -v
```

### Tests de un módulo específico
```bash
# Tests de autenticación
pytest tests/integration/routes/auth/ -v

# Tests de galería
pytest tests/integration/routes/galeria/ -v

# Tests de usuarios
pytest tests/integration/routes/usuarios/ -v

# Tests de eventos
pytest tests/integration/routes/eventos/ -v

# Tests de deportistas
pytest tests/integration/routes/deportistas/ -v

# Tests de archivos
pytest tests/integration/routes/archivos/ -v

# Tests de catálogos
pytest tests/integration/routes/catalogos/ -v

# Tests de personas
pytest tests/integration/routes/personas/ -v
```

### Tests por marcador
```bash
# Todos los tests de autenticación
pytest -m auth -v

# Todos los tests de pagos
pytest -m pagos -v
```

### Un archivo específico
```bash
pytest tests/integration/routes/usuarios/test_listar_usuarios.py -v
```

### Una clase específica
```bash
pytest tests/integration/routes/usuarios/test_listar_usuarios.py::TestListarUsuarios -v
```

## Ventajas de la Estructura Modular

1. **Claridad**: Cada archivo tiene un propósito único y claro
2. **Mantenibilidad**: Fácil encontrar y modificar tests específicos
3. **Escalabilidad**: Fácil agregar nuevos tests sin afectar otros
4. **Organización**: Tests agrupados por funcionalidad
5. **Legibilidad**: Nombres descriptivos facilitan el análisis

## Agregar Nuevos Tests

Para agregar un nuevo test:

1. Identifica el módulo correspondiente (auth, archivos, catalogos, deportistas, eventos, galeria, mensualidades, pagos, personas, usuarios, dynamic_data)
2. Crea un nuevo archivo siguiendo la convención: `test_<accion>_<entidad>.py`
3. Copia la estructura base de un archivo existente
4. Implementa los tests siguiendo el patrón AAA (Arrange-Act-Assert)
5. Usa los marcadores apropiados

## Notas

- Todos los tests usan mocks para aislar las dependencias
- Los tests siguen el patrón AAA (Arrange-Act-Assert)
- Cada test es independiente y puede ejecutarse por separado
- Los helpers en `tests/helpers/` proporcionan funciones reutilizables

