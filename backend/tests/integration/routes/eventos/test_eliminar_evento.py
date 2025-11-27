"""
Tests para el endpoint de eliminar evento.

Endpoint: DELETE /api/eventos/calendario/<evento_id>
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestEliminarEvento:
    """Tests para el endpoint DELETE /api/eventos/calendario/<evento_id>"""
    
    def test_eliminar_evento_success(self, client, mock_token_required):
        """Test: Eliminar evento exitosamente."""
        # Arrange
        mock_evento = MagicMock()
        mock_evento.nombre = 'Torneo de Fútbol'
        
        # Act
        with patch('src.routes.eventos_routes.Evento.query') as mock_query:
            with patch('src.routes.eventos_routes.db') as mock_db:
                mock_query.get.return_value = mock_evento
                # Configurar db.session para que delete y commit no fallen
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                mock_db.session.rollback = MagicMock()
                
                response = client.delete('/api/eventos/calendario/1')
        
        # Assert
        assert response.status_code in [200, 204]
    
    def test_eliminar_evento_no_encontrado(self, client, mock_token_required):
        """Test: Error al eliminar evento inexistente."""
        # Act
        with patch('src.routes.eventos_routes.Evento.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.delete('/api/eventos/calendario/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

