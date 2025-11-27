"""
Tests para el endpoint de listado de galería.

Endpoint: GET /api/galeria
Funcionalidad: Lista todas las imágenes de la galería con opciones de filtrado.
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
@pytest.mark.galeria
class TestListarGaleria:
    """Tests para el endpoint GET /api/galeria"""
    
    def test_listar_galeria_success(self, client, mock_token_required):
        """Test: Listar imágenes de galería exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {
            'id_galeria': 1,
            'titulo': 'Imagen Test',
            'url_imagen': 'https://example.com/image.jpg'
        }
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_imagen]
            
            response = client.get('/api/galeria')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_galeria_con_filtros(self, client, mock_token_required):
        """Test: Listar galería con filtros de tipo evento y categoría."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_imagen]
            
            response = client.get('/api/galeria?id_tipo_evento=1&id_categoria=1')
        
        # Assert
        assert_success_response(response)

