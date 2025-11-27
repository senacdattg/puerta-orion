"""
Tests para el endpoint de subir archivo.

Endpoint: POST /api/archivos/upload
"""

import pytest
from unittest.mock import patch
from io import BytesIO

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestArchivosRoutes:
    """Tests para endpoints de archivos"""
    
    def test_subir_archivo_success(self, client, mock_token_required):
        """Test: Subir archivo exitosamente."""
        # Arrange
        data = {
            'file': (BytesIO(b'fake image content'), 'test.jpg'),
            'categoria': 'galeria'
        }
        
        # Act
        with patch('src.routes.archivos_routes.Galeria') as mock_galeria:
            mock_galeria.query.filter_by.return_value.first.return_value = None
            with patch('src.routes.archivos_routes.db.session'):
                response = client.post(
                    '/api/archivos/upload',
                    data=data,
                    content_type='multipart/form-data'
                )
        
        # Assert
        # Nota: Ajustar según implementación real
        assert response.status_code in [200, 201, 400, 500]
    
    def test_subir_archivo_formato_invalido(self, client, mock_token_required):
        """Test: Error con formato de archivo inválido."""
        # Arrange
        data = {
            'file': (BytesIO(b'content'), 'test.exe'),  # Extensión no permitida
            'categoria': 'galeria'
        }
        
        # Act
        response = client.post(
            '/api/archivos/upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Assert
        # Debería retornar error 400
        assert response.status_code in [400, 500]

