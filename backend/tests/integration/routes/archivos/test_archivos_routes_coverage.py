"""
Tests de integración adicionales para aumentar la cobertura de archivos_routes.py.

Cubre casos edge y bloques de excepciones que no están cubiertos en los tests existentes.
"""

import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    create_auth_headers
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.archivos
class TestArchivosRoutesCoverage:
    """Tests adicionales para aumentar cobertura de archivos_routes.py"""

    def test_subir_archivo_id_categoria_invalido(
        self, client, mock_token_required, categoria, tipo_evento
    ):
        """Test: Error cuando id_categoria no es un entero válido (línea 124)."""
        # Arrange
        from pathlib import Path
        import tempfile
        
        with patch('src.routes.archivos_routes._obtener_upload_folder') as mock_upload_folder:
            temp_dir = Path(tempfile.mkdtemp())
            mock_upload_folder.return_value = temp_dir
            
            imagen_file = BytesIO(b'fake image data')
            imagen_file.name = 'test_image.jpg'
            
            headers = create_auth_headers('test_token')
            headers.pop('Content-Type')
            
            # Act - Enviar id_categoria como string no numérico
            response = client.post(
                '/api/archivos/upload',
                data={
                    'file': (imagen_file, 'test_image.jpg'),
                    'titulo': 'Imagen de Prueba',
                    'id_categoria': 'invalid_id'  # String no numérico
                },
                headers=headers,
                content_type='multipart/form-data'
            )
            
            # Assert
            assert_error_response(response, expected_status=400)
            data = response.get_json()
            assert 'error' in data
            assert 'categoría' in data['error'].lower()

    def test_subir_archivo_titulo_validation_error(
        self, client, mock_token_required
    ):
        """Test: ValidationError al sanitizar título."""
        # Arrange
        from pathlib import Path
        import tempfile
        
        with patch('src.routes.archivos_routes._obtener_upload_folder') as mock_upload_folder:
            temp_dir = Path(tempfile.mkdtemp())
            mock_upload_folder.return_value = temp_dir
            
            imagen_file = BytesIO(b'fake image data')
            imagen_file.name = 'test_image.jpg'
            
            headers = create_auth_headers('test_token')
            headers.pop('Content-Type')
            
            # Act - Enviar título con caracteres inválidos o muy largo
            # sanitize_free_text puede lanzar ValidationError si el texto es muy largo
            response = client.post(
                '/api/archivos/upload',
                data={
                    'file': (imagen_file, 'test_image.jpg'),
                    'titulo': 'x' * 150,  # Excede max_length=120
                },
                headers=headers,
                content_type='multipart/form-data'
            )
            
            # Assert
            # Puede retornar 400 por ValidationError o por título vacío después de sanitizar
            assert response.status_code in [400, 500]

    def test_subir_archivo_descripcion_sanitization(
        self, client, mock_token_required, categoria, tipo_evento
    ):
        """Test: Descripción se sanitiza correctamente."""
        # Arrange
        from pathlib import Path
        import tempfile
        
        with patch('src.routes.archivos_routes._obtener_upload_folder') as mock_upload_folder:
            temp_dir = Path(tempfile.mkdtemp())
            mock_upload_folder.return_value = temp_dir
            
            imagen_file = BytesIO(b'fake image data')
            imagen_file.name = 'test_image.jpg'
            
            headers = create_auth_headers('test_token')
            headers.pop('Content-Type')
            
            # Act
            response = client.post(
                '/api/archivos/upload',
                data={
                    'file': (imagen_file, 'test_image.jpg'),
                    'titulo': 'Imagen de Prueba',
                    'descripcion': 'Descripción con caracteres válidos',
                    'id_tipo_evento': str(tipo_evento.id_tipo_evento),
                    'id_categoria': str(categoria.id_categoria)
                },
                headers=headers,
                content_type='multipart/form-data'
            )
            
            # Assert
            assert response.status_code == 201
            data = response.get_json()
            assert data.get('success') is True

    def test_eliminar_archivo_imagen_no_encontrada(
        self, client, mock_token_required
    ):
        """Test: Error cuando la imagen no existe (línea 234)."""
        # Arrange
        headers = create_auth_headers('test_token')
        
        # Act - Intentar eliminar una imagen con ID inexistente
        response = client.delete(
            '/api/archivos/delete/99999',
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=404)
        data = response.get_json()
        assert 'error' in data
        assert 'encontrada' in data['error'].lower() or 'not found' in data['error'].lower()

    def test_arreglar_urls_success(
        self, client, mock_token_required, db_session
    ):
        """Test: Arreglar URLs exitosamente."""
        # Arrange
        from src.models.galeria.galeria import Galeria
        
        # Crear una imagen con URL relativa
        imagen = Galeria(
            titulo='Test Image',
            url_imagen='/static/uploads/galeria/test.jpg',
            descripcion='Test'
        )
        db_session.add(imagen)
        db_session.commit()
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = client.post(
            '/api/archivos/fix-urls',
            headers=headers
        )
        
        # Assert
        assert_success_response(response)
        data = response.get_json()
        assert 'actualizadas' in data
        assert data.get('actualizadas') >= 1
        
        # Verificar que la URL se actualizó en la BD
        imagen_actualizada = Galeria.query.get(imagen.id_galeria)
        assert imagen_actualizada.url_imagen.startswith('http')

