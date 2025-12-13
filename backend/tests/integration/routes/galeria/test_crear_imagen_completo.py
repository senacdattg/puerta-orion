"""
Tests de integración para crear imagen en galería.

Endpoint: POST /api/galeria/
Funcionalidad: Crear una nueva imagen en la galería
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
    create_auth_headers
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestCrearImagenCompleto:
    """Tests para el endpoint POST /api/galeria/"""
    
    def test_crear_imagen_exitoso(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Crear imagen exitosamente.
        
        Valida:
        - Creación de imagen en BD
        - Validación de datos
        - Respuesta con datos de la imagen creada
        """
        # Arrange
        datos_imagen = {
            'titulo': 'Imagen de Torneo',
            'descripcion': 'Imagen del torneo regional 2024',
            'url_imagen': 'https://example.com/imagen.jpg',
            'id_tipo_evento': tipo_evento.id_tipo_evento,
            'id_categoria': categoria.id_categoria
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria/',
            data=datos_imagen,
            headers=headers
        )
        
        # Assert
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is True, f"Expected success=True, got {data.get('success')}. Response: {data}"
        assert 'data' in data, f"Expected 'data' in response, got: {data}"
        
        # Verificar que se guardó en BD
        from src.models.galeria.galeria import Galeria
        # El título puede estar en mayúsculas según el servicio
        imagen = Galeria.query.filter(
            (Galeria.titulo == 'Imagen de Torneo') | 
            (Galeria.titulo == 'IMAGEN DE TORNEO')
        ).first()
        assert imagen is not None, f"Imagen should be created in database. Response: {data}"
        assert imagen.id_tipo_evento == tipo_evento.id_tipo_evento
        assert imagen.id_categoria == categoria.id_categoria
    
    def test_crear_imagen_sin_titulo(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Error cuando falta el título.
        
        Valida que el sistema rechaza imágenes sin título.
        """
        # Arrange
        datos_imagen = {
            'descripcion': 'Imagen del torneo regional 2024',
            'url_imagen': 'https://example.com/imagen.jpg',
            'id_tipo_evento': tipo_evento.id_tipo_evento,
            'id_categoria': categoria.id_categoria
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria/',
            data=datos_imagen,
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data
        assert 'título' in data['error'].lower() or 'titulo' in data['error'].lower()
    
    def test_crear_imagen_tipo_evento_no_existe(
        self, client, db_session, categoria, mock_token_required
    ):
        """
        Test: Error cuando el tipo de evento no existe.
        
        Valida que el sistema rechaza tipos de evento inválidos.
        """
        # Arrange
        datos_imagen = {
            'titulo': 'Imagen de Torneo',
            'descripcion': 'Imagen del torneo regional 2024',
            'url_imagen': 'https://example.com/imagen.jpg',
            'id_tipo_evento': 99999,  # Tipo de evento inexistente
            'id_categoria': categoria.id_categoria
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria/',
            data=datos_imagen,
            headers=headers
        )
        
        # Assert
        # El endpoint puede devolver 400 si valida antes de verificar existencia
        assert response.status_code in [400, 404], f"Expected status 400 or 404, got {response.status_code}. Response: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is False, f"Expected success=False, got {data.get('success')}"
        data = response.get_json()
        assert 'error' in data
        assert 'tipo de evento' in data['error'].lower()
    
    def test_crear_imagen_sin_url(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Error cuando falta la URL de la imagen.
        
        Valida que el sistema rechaza imágenes sin URL.
        """
        # Arrange
        datos_imagen = {
            'titulo': 'Imagen de Torneo',
            'descripcion': 'Imagen del torneo regional 2024',
            'id_tipo_evento': tipo_evento.id_tipo_evento,
            'id_categoria': categoria.id_categoria
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria/',
            data=datos_imagen,
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

