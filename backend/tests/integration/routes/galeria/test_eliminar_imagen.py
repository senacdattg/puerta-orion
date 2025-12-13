"""
Tests para el endpoint de eliminación de imagen.

Endpoint: DELETE /api/galeria/<id_galeria>
Funcionalidad: Elimina una imagen de la galería.
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
class TestEliminarImagen:
    """Tests para el endpoint DELETE /api/galeria/<id_galeria>"""
    
    def test_eliminar_imagen_success(self, client, mock_token_required):
        """Test: Eliminar imagen exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.url_imagen = 'https://example.com/image.jpg'
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            with patch('src.routes.galeria_routes.db') as mock_db:
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                
                response = client.delete('/api/galeria/1')
        
        # Assert
        assert response.status_code in [200, 204]
    
    def test_eliminar_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Error al eliminar imagen inexistente."""
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.delete('/api/galeria/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

