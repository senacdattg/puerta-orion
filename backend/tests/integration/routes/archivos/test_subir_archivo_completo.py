"""
Tests de integración para subir archivo.

Endpoint: POST /api/archivos/upload
Funcionalidad: Subir un archivo (imagen) al servidor
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
class TestSubirArchivoCompleto:
    """Tests para el endpoint POST /api/archivos/upload"""
    
    @patch('src.routes.archivos_routes._obtener_upload_folder')
    def test_subir_archivo_exitoso(
        self, mock_upload_folder, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Subir archivo exitosamente.
        
        Valida:
        - Validación de tipo de archivo
        - Validación de tamaño
        - Guardado del archivo
        - Creación de registro en BD
        """
        # Arrange
        from pathlib import Path
        import tempfile
        
        # Crear directorio temporal para uploads
        temp_dir = Path(tempfile.mkdtemp())
        mock_upload_folder.return_value = temp_dir
        
        # Crear archivo de imagen simulado
        imagen_data = b'fake image data'
        imagen_file = BytesIO(imagen_data)
        imagen_file.name = 'test_image.jpg'
        
        headers = create_auth_headers('test_token')
        headers.pop('Content-Type')  # No usar Content-Type para multipart/form-data
        
        # Act
        response = client.post(
            '/api/archivos/upload',
            data={
                'file': (imagen_file, 'test_image.jpg'),
                'titulo': 'Imagen de Prueba',
                'descripcion': 'Descripción de prueba',
                'id_tipo_evento': tipo_evento.id_tipo_evento,
                'id_categoria': categoria.id_categoria
            },
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is True, f"Expected success=True, got {data.get('success')}. Response: {data}"
        assert 'data' in data, f"Expected 'data' in response, got: {data}"
        assert 'url' in data['data'] or 'url_imagen' in data['data']
        
        # Verificar que se creó el registro en BD
        from src.models.galeria.galeria import Galeria
        # El servicio puede guardar el título en mayúsculas
        imagen = Galeria.query.filter(
            (Galeria.titulo == 'Imagen de Prueba') | 
            (Galeria.titulo == 'IMAGEN DE PRUEBA')
        ).first()
        assert imagen is not None, f"Imagen should be created in database. Response: {data}"
    
    def test_subir_archivo_tipo_invalido(
        self, client, mock_token_required
    ):
        """
        Test: Error cuando el tipo de archivo no está permitido.
        
        Valida que el sistema rechaza tipos de archivo no permitidos.
        """
        # Arrange
        archivo_data = b'fake file data'
        archivo_file = BytesIO(archivo_data)
        archivo_file.name = 'test_file.pdf'  # PDF no permitido
        
        headers = create_auth_headers('test_token')
        headers.pop('Content-Type')
        
        # Act
        response = client.post(
            '/api/archivos/upload',
            data={
                'file': (archivo_file, 'test_file.pdf')
            },
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data
        assert 'tipo' in data['error'].lower() or 'permitido' in data['error'].lower()
    
    def test_subir_archivo_sin_archivo(
        self, client, mock_token_required
    ):
        """
        Test: Error cuando no se envía ningún archivo.
        
        Valida que el sistema rechaza peticiones sin archivo.
        """
        # Arrange
        headers = create_auth_headers('test_token')
        headers.pop('Content-Type')
        
        # Act
        response = client.post(
            '/api/archivos/upload',
            data={},
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data
        assert 'archivo' in data['error'].lower() or 'file' in data['error'].lower()
    
    @patch('src.routes.archivos_routes._obtener_upload_folder')
    def test_subir_archivo_tamano_excedido(
        self, mock_upload_folder, client, mock_token_required
    ):
        """
        Test: Error cuando el archivo excede el tamaño máximo.
        
        Valida que el sistema rechaza archivos demasiado grandes.
        """
        # Arrange
        from pathlib import Path
        import tempfile
        
        temp_dir = Path(tempfile.mkdtemp())
        mock_upload_folder.return_value = temp_dir
        
        # Crear archivo grande simulado (más de 16MB)
        archivo_grande = BytesIO(b'x' * (17 * 1024 * 1024))
        archivo_grande.name = 'large_image.jpg'
        
        headers = create_auth_headers('test_token')
        headers.pop('Content-Type')
        
        # Act
        response = client.post(
            '/api/archivos/upload',
            data={
                'file': (archivo_grande, 'large_image.jpg')
            },
            headers=headers,
            content_type='multipart/form-data'
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
        data = response.get_json()
        assert 'error' in data
        assert 'grande' in data['error'].lower() or 'tamaño' in data['error'].lower() or 'size' in data['error'].lower()

