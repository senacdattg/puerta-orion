"""
Tests para el endpoint de registro completo de deportista.

Endpoint: POST /api/deportistas/registro-completo
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
class TestRegistroCompleto:
    """Tests para el endpoint POST /api/deportistas/registro-completo"""
    
    def test_registro_completo_success(self, client, sample_deportista_data):
        """Test: Registro completo exitoso."""
        # Arrange
        mock_result = {
            'success': True,
            'message': 'Deportista registrado exitosamente',
            'data': {'id_deportista': 1},
            'status_code': 201
        }
        
        # Act
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo',
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/deportistas/registro-completo',
                data=sample_deportista_data
            )
        
        # Assert
        assert_success_response(response, expected_status=201)
    
    def test_registro_completo_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/deportistas/registro-completo')
        
        # Assert
        assert_error_response(response, expected_status=400)

