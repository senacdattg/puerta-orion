"""
Tests para el endpoint de catálogos de galería.

Endpoint: GET /api/galeria/catalogos
Funcionalidad: Obtiene los catálogos disponibles para filtrar imágenes (tipos de evento, categorías).
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
class TestCatalogosGaleria:
    """Tests para el endpoint GET /api/galeria/catalogos"""
    
    def test_obtener_catalogos_success(self, client, mock_token_required):
        """Test: Obtener catálogos de galería exitosamente."""
        # Arrange
        mock_tipo_evento = MagicMock()
        mock_tipo_evento.to_dict.return_value = {'id_tipo_evento': 1, 'nombre': 'Torneo'}
        mock_categoria = MagicMock()
        mock_categoria.to_dict.return_value = {'id_categoria': 1, 'nombre_categoria': 'Sub-15'}
        
        # Act
        with patch('src.routes.galeria_routes.TipoEvento.query') as mock_tipo:
            with patch('src.routes.galeria_routes.Categoria.query') as mock_cat:
                mock_tipo.filter_by.return_value.all.return_value = [mock_tipo_evento]
                mock_cat.filter_by.return_value.all.return_value = [mock_categoria]
                
                response = client.get('/api/galeria/catalogos')
        
        # Assert
        assert_success_response(response)

