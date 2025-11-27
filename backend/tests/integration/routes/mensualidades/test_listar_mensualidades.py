"""
Tests para el endpoint de listado de mensualidades.

Endpoint: GET /api/mensualidades
Funcionalidad: Lista todas las mensualidades con opciones de paginación y filtrado.
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
@pytest.mark.mensualidades
class TestListarMensualidades:
    """Tests para el endpoint GET /api/mensualidades"""
    
    def test_listar_mensualidades_success(self, client, mock_token_required):
        """Test: Listar mensualidades exitosamente."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'fecha_vencimiento': '2024-12-31',
            'monto': 50000.0
        }
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.paginate.return_value.items = [mock_mensualidad]
            mock_query.paginate.return_value.page = 1
            mock_query.paginate.return_value.per_page = 20
            mock_query.paginate.return_value.total = 1
            mock_query.paginate.return_value.pages = 1
            
            response = client.get('/api/mensualidades')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_mensualidades_con_paginacion(self, client, mock_token_required):
        """Test: Listar mensualidades con parámetros de paginación."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1}
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.paginate.return_value.items = [mock_mensualidad]
            mock_query.paginate.return_value.page = 2
            mock_query.paginate.return_value.per_page = 10
            mock_query.paginate.return_value.total = 25
            mock_query.paginate.return_value.pages = 3
            
            response = client.get('/api/mensualidades?page=2&per_page=10')
        
        # Assert
        assert_success_response(response)

