"""
Tests para el endpoint de obtener evento.

Endpoint: GET /api/eventos/calendario/<evento_id>
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestObtenerEvento:
    """Tests para el endpoint GET /api/eventos/calendario/<evento_id>"""
    
    def test_obtener_evento_success(self, client, mock_token_required):
        """Test: Obtener evento exitosamente."""
        # Arrange
        mock_evento = MagicMock()
        mock_evento.to_dict.return_value = {
            'id_evento': 1,
            'nombre': 'Torneo de Fútbol',
            'fecha_evento': '2024-12-31'
        }
        mock_evento.categoria = None
        mock_evento.sesion = None
        mock_evento.id_tipo_evento = 1
        
        # Act
        with patch('src.routes.eventos_routes.Evento.query') as mock_query:
            mock_query.get.return_value = mock_evento
            with patch('src.routes.eventos_routes.TipoEvento.query') as mock_tipo:
                mock_tipo.get.return_value = None
                
                response = client.get('/api/eventos/calendario/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_evento_no_encontrado(self, client, mock_token_required):
        """Test: Evento no encontrado."""
        # Act
        with patch('src.routes.eventos_routes.Evento.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/eventos/calendario/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

