"""
Tests para el endpoint de listar eventos.

Endpoint: GET /api/eventos/calendario
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from tests.helpers import (
    assert_success_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestListarEventos:
    """Tests para el endpoint GET /api/eventos/calendario"""
    
    def test_listar_eventos_success(self, client, mock_token_required):
        """Test: Listar eventos exitosamente."""
        # Arrange
        mock_categorias = [1, 2, 3]
        
        # Crear mock de evento con los atributos necesarios
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.nombre = 'Torneo de Fútbol'
        mock_evento.fecha_evento = date(2024, 12, 31)
        mock_evento.to_dict.return_value = {
            'id_evento': 1,
            'nombre': 'Torneo de Fútbol',
            'fecha_evento': '2024-12-31'
        }
        # Mock de relaciones que pueden ser None
        mock_evento.categoria = None
        mock_evento.sesion = None
        mock_evento.tipo_evento = None
        
        # Act
        with patch('src.routes.eventos_routes.obtener_categorias_permitidas_usuario',
                   return_value=mock_categorias):
            with patch('src.routes.eventos_routes.Evento.query') as mock_query:
                # Configurar el mock para que count() retorne un entero
                mock_query.filter.return_value = mock_query
                mock_query.filter_by.return_value = mock_query
                mock_query.order_by.return_value = mock_query
                mock_query.count.return_value = 1  # Retornar entero en lugar de MagicMock
                mock_query.all.return_value = [mock_evento]  # Para cuando total <= per_page
                
                response = client.get('/api/eventos/calendario')
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        assert 'pagination' in data
    
    def test_listar_eventos_sin_categorias(self, client, mock_token_required):
        """Test: Usuario sin categorías asignadas."""
        # Arrange
        mock_categorias = []
        
        # Act
        with patch('src.routes.eventos_routes.obtener_categorias_permitidas_usuario',
                   return_value=mock_categorias):
            response = client.get('/api/eventos/calendario')
        
        # Assert
        data = assert_success_response(response)
        assert data['data'] == []
        assert 'No tienes eventos asignados' in data.get('message', '')

