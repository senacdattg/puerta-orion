"""
Tests para el endpoint de eventos próximos.

Endpoint: GET /api/eventos/proximos
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestEventosProximos:
    """Tests para el endpoint GET /api/eventos/proximos"""
    
    def test_eventos_proximos_success(self, client, mock_token_required):
        """Test: Obtener eventos próximos exitosamente."""
        with patch('src.routes.eventos_routes.obtener_categorias_permitidas_usuario',
                   return_value=[1, 2, 3]):
            with patch('src.routes.eventos_routes.Evento.query') as mock_query:
                mock_evento = MagicMock()
                mock_evento.id_evento = 1
                mock_query.filter.return_value = mock_query
                mock_query.order_by.return_value.limit.return_value.all.return_value = [mock_evento]
                
                with patch('src.routes.eventos_routes._serializar_evento',
                           return_value={'id_evento': 1, 'nombre': 'Evento Próximo'}):
                    with patch('src.routes.eventos_routes._obtener_categoria_todos',
                               return_value=None):
                        response = client.get('/api/eventos/proximos')
                        
                        assert_success_response(response)
    
    def test_eventos_proximos_sin_categorias(self, client, mock_token_required):
        """Test: Usuario sin categorías para eventos próximos."""
        with patch('src.routes.eventos_routes.obtener_categorias_permitidas_usuario',
                   return_value=[]):
            response = client.get('/api/eventos/proximos')
            
            data = assert_success_response(response)
            assert data['data'] == []
            assert 'No tienes eventos próximos' in data.get('message', '')

