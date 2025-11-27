"""
Utilidades y helpers para tests.

Funciones auxiliares reutilizables para:
- Assertions personalizadas
- Requests HTTP
- Factories de datos de prueba
- Validaciones comunes
"""

# Exportar funciones principales para compatibilidad
from .assertions import assert_success_response, assert_error_response
from .requests import make_json_request, create_auth_headers

__all__ = [
    'assert_success_response',
    'assert_error_response',
    'make_json_request',
    'create_auth_headers',
]

