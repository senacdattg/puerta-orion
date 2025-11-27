"""
Tests para el endpoint de eventos por categoría.

Endpoint: GET /api/eventos/categoria/<categoria_id>
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestEventosPorCategoria:
    """Tests para el endpoint GET /api/eventos/categoria/<categoria_id>"""
    
    def test_eventos_por_categoria_success(self, client, mock_token_required):
        """Test: Obtener eventos por categoría exitosamente."""
        with patch('src.routes.eventos_routes.Categoria.query') as mock_cat_query:
            with patch('src.routes.eventos_routes.Evento.query') as mock_evento_query:
                mock_categoria = MagicMock()
                mock_categoria.to_dict.return_value = {'id_categoria': 1, 'nombre_categoria': 'Sub-15'}
                mock_cat_query.get.return_value = mock_categoria
                
                mock_evento = MagicMock()
                mock_evento_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_evento]
                
                with patch('src.routes.eventos_routes._serializar_evento',
                           return_value={'id_evento': 1, 'nombre': 'Evento'}):
                    response = client.get('/api/eventos/categoria/1')
                    
                    assert_success_response(response)
    
    def test_eventos_por_categoria_no_encontrada(self, client, mock_token_required):
        """Test: Categoría no encontrada."""
        with patch('src.routes.eventos_routes.Categoria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/eventos/categoria/999')
            
            assert_error_response(response, expected_status=404)

