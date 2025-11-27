"""
Tests para el endpoint de obtener deportista por ID.

Endpoint: GET /api/deportistas/<id_deportista>
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestObtenerDeportistaPorId:
    """Tests para el endpoint GET /api/deportistas/<id_deportista>"""
    
    def test_obtener_deportista_success(self, client):
        """Test: Obtener deportista exitosamente."""
        # Arrange
        mock_result = {
            'success': True,
            'data': {
                'id_deportista': 1,
                'nombre': 'Juan Pérez',
                'categoria': 'Sub-15'
            },
            'status_code': 200
        }
        
        # Act
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.obtener_informacion_completa_deportista',
                   return_value=mock_result):
            response = client.get('/api/deportistas/1')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert data['data']['id_deportista'] == 1
    
    def test_obtener_deportista_id_invalido_cero(self, client):
        """Test: Error con ID igual a cero."""
        # Act
        response = client.get('/api/deportistas/0')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_obtener_deportista_no_encontrado(self, client):
        """Test: Deportista no encontrado."""
        # Arrange
        mock_result = {
            'success': False,
            'error': 'Deportista no encontrado',
            'status_code': 404
        }
        
        # Act
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.obtener_informacion_completa_deportista',
                   return_value=mock_result):
            response = client.get('/api/deportistas/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

