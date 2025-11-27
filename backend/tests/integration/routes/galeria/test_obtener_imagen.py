"""
Tests para el endpoint de obtener imagen individual.

Endpoint: GET /api/galeria/<id_galeria>
Funcionalidad: Obtiene los detalles de una imagen específica de la galería.
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
class TestObtenerImagen:
    """Tests para el endpoint GET /api/galeria/<id_galeria>"""
    
    def test_obtener_imagen_success(self, client, mock_token_required):
        """Test: Obtener imagen exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {
            'id_galeria': 1,
            'titulo': 'Imagen Test'
        }
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            
            response = client.get('/api/galeria/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Imagen no encontrada."""
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/galeria/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

