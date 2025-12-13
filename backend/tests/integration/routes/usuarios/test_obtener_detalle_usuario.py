"""
Tests para el endpoint de detalle de usuario.

Endpoint: GET /api/usuarios/<id_usuario>/detalle
Funcionalidad: Obtiene información detallada de un usuario específico.
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
@pytest.mark.usuarios
class TestObtenerDetalleUsuario:
    """Tests para el endpoint GET /api/usuarios/<id_usuario>/detalle"""
    
    def test_obtener_detalle_usuario_success(self, client, mock_token_required):
        """Test: Obtener detalle de usuario exitosamente."""
        # Arrange
        mock_detalle = {
            'id_usuario': 1,
            'usuario': 'testuser',
            'persona': {'id_persona': 1, 'nombre_completo': 'Test User'}
        }
        
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.obtener_detalle_completo_usuario',
                   return_value=mock_detalle):
            response = client.get('/api/usuarios/1/detalle')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert data['data']['id_usuario'] == 1
    
    def test_obtener_detalle_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Usuario no encontrado."""
        # Act
        with patch('src.routes.usuarios_routes.usuario_service.obtener_detalle_completo_usuario',
                   return_value=None):
            response = client.get('/api/usuarios/999/detalle')
        
        # Assert
        assert_error_response(response, expected_status=404)

