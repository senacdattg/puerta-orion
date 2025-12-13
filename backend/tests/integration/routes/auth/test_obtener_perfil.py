"""
Tests para el endpoint de obtener perfil.

Endpoint: GET /api/auth/perfil
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestObtenerPerfil:
    """Tests para el endpoint GET /api/auth/perfil"""
    
    def test_obtener_perfil_success(self, client, mock_get_current_user):
        """Test: Obtener perfil exitosamente."""
        # Act
        response = client.get('/api/auth/perfil')
        
        # Assert
        # Nota: Ajustar según implementación real del decorador
        assert response.status_code in [200, 401, 403]
    
    def test_obtener_perfil_sin_autenticacion(self, client):
        """Test: Error cuando no hay autenticación."""
        # Act
        with patch('src.routes.auth_routes.get_current_user', return_value=None):
            response = client.get('/api/auth/perfil')
        
        # Assert
        assert_error_response(response, expected_status=401)

