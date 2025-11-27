"""
Fixtures para la aplicación Flask y cliente HTTP.

Este módulo contiene fixtures relacionadas con la configuración
y creación de la aplicación Flask para testing.
"""

import pytest
from flask.testing import FlaskClient


@pytest.fixture(scope='function')
def auth_headers(client: FlaskClient) -> dict[str, str]:
    """
    Crea headers de autenticación con un token válido.
    
    Returns:
        Dict con headers de Authorization
    """
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test_token_12345'
    }

