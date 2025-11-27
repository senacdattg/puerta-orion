"""
Tests para el endpoint de registro de usuario.

Endpoint: POST /api/auth/register
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.auth
class TestRegistroUsuario:
    """Tests para el endpoint POST /api/auth/register"""
    
    def test_registro_usuario_success(self, client, sample_usuario_data):
        """Test: Registro de usuario exitoso."""
        # Arrange
        mock_result = {
            'id_usuario': 1,
            'usuario': 'testuser',
            'persona': {'id_persona': 1}
        }
        
        # Act
        with patch('src.routes.auth_routes.usuario_service.registrar_usuario_completo',
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/auth/register',
                data=sample_usuario_data
            )
        
        # Assert
        data = assert_success_response(response, expected_status=201)
        assert 'data' in data
        assert data['data']['id_usuario'] == 1
    
    def test_registro_usuario_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/auth/register', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_registro_usuario_datos_faltantes(self, client):
        """Test: Error cuando faltan datos requeridos."""
        # Arrange
        datos_incompletos = {
            'persona': {
                'primer_nombre': 'Test'
                # Faltan otros campos requeridos
            }
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/auth/register',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

