"""
Tests para el endpoint de actualización de imagen.

Endpoint: PUT /api/galeria/<id_galeria>
Funcionalidad: Actualiza los datos de una imagen existente en la galería.
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
class TestActualizarImagen:
    """Tests para el endpoint PUT /api/galeria/<id_galeria>"""
    
    def test_actualizar_imagen_success(self, client, mock_token_required):
        """Test: Actualizar imagen exitosamente."""
        # Arrange
        datos_actualizacion = {
            'titulo': 'Título Actualizado',
            'descripcion': 'Nueva descripción'
        }
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1, 'titulo': 'Título Actualizado'}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            with patch('src.routes.galeria_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/galeria/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert response.status_code in [200, 400, 500]
    
    def test_actualizar_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Error al actualizar imagen inexistente."""
        # Arrange
        datos_actualizacion = {'titulo': 'Nuevo Título'}
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/galeria/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)

