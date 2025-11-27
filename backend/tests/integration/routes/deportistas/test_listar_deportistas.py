"""
Tests para el endpoint de listar deportistas.

Endpoint: GET /api/deportistas/
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestListarDeportistas:
    """Tests para el endpoint GET /api/deportistas/"""
    
    def test_listar_deportistas_success(self, client):
        """Test: Listar deportistas exitosamente."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [
                {'id_deportista': 1, 'nombre': 'Juan Pérez'},
                {'id_deportista': 2, 'nombre': 'María García'}
            ],
            'status_code': 200
        }
        
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.listar_deportistas',
                   return_value=mock_result):
            response = client.get('/api/deportistas/')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) == 2
    
    def test_listar_deportistas_con_paginacion(self, client):
        """Test: Listar deportistas con parámetros de paginación."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [{'id_deportista': 1}],
            'status_code': 200
        }
        
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.listar_deportistas',
                   return_value=mock_result):
            response = client.get('/api/deportistas/?page=1&per_page=10')
        
        # Assert
        assert_success_response(response)

