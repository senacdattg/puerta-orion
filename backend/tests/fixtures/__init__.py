"""
Fixtures específicas por dominio.

Este módulo contiene fixtures organizadas por dominio funcional,
complementando las fixtures globales en conftest.py.

Estructura:
- app_fixtures.py: Fixtures de aplicación Flask
- data_fixtures.py: Fixtures de datos de prueba
- model_fixtures.py: Fixtures de modelos de BD
- mock_fixtures.py: Fixtures de mocks y stubs
"""

# Importar todas las fixtures para que estén disponibles automáticamente
from .app_fixtures import auth_headers
from .data_fixtures import (
    sample_persona_data,
    sample_deportista_data,
    sample_evento_data,
    sample_usuario_data
)
from .model_fixtures import (
    tipo_documento,
    sexo,
    categoria,
    tipo_evento,
    persona,
    usuario,
    deportista,
    rol
)
from .mock_fixtures import (
    mock_get_current_user,
    mock_token_required,
    mock_logger
)

__all__ = [
    # App fixtures
    'auth_headers',
    # Data fixtures
    'sample_persona_data',
    'sample_deportista_data',
    'sample_evento_data',
    'sample_usuario_data',
    # Model fixtures
    'tipo_documento',
    'sexo',
    'categoria',
    'tipo_evento',
    'persona',
    'usuario',
    'deportista',
    'rol',
    # Mock fixtures
    'mock_get_current_user',
    'mock_token_required',
    'mock_logger',
]

