"""
Tests para el endpoint de creación de imagen.

Endpoint: POST /api/galeria
Funcionalidad: Crea una nueva imagen en la galería.
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
class TestCrearImagen:
    """Tests para el endpoint POST /api/galeria"""
    
    def test_crear_imagen_success(self, client, mock_token_required):
        """Test: Crear imagen exitosamente."""
        # Arrange
        datos_imagen = {
            'titulo': 'Nueva Imagen',
            'descripcion': 'Descripción de la imagen',
            'url_imagen': 'https://example.com/image.jpg',
            'id_tipo_evento': 1
        }
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1, 'titulo': 'Nueva Imagen'}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.TipoEvento.query') as mock_tipo:
            mock_tipo.get.return_value = MagicMock()
            with patch('src.routes.galeria_routes.Galeria') as mock_galeria_class:
                mock_galeria_class.query.filter_by.return_value.first.return_value = None
                mock_galeria_class.return_value = mock_imagen
                with patch('src.routes.galeria_routes.db') as mock_db:
                    mock_db.session.add = MagicMock()
                    mock_db.session.commit = MagicMock()
                    
                    response = make_json_request(
                        client, 'POST', '/api/galeria/',
                        data=datos_imagen
                    )
        
        # Assert
        assert response.status_code in [200, 201]
    
    def test_crear_imagen_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/galeria/', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_imagen_campos_faltantes(self, client, mock_token_required):
        """Test: Error cuando faltan campos requeridos."""
        # Arrange
        datos_incompletos = {
            'titulo': 'Imagen sin campos completos'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria/',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

