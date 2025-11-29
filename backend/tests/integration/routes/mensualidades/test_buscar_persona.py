"""
Tests para el endpoint de buscar persona por documento.

Endpoint: GET /api/mensualidades/buscar-persona
Funcionalidad: Busca una persona por documento y valida su rol asociado.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestBuscarPersona:
    """Tests para el endpoint GET /api/mensualidades/buscar-persona"""
    
    def test_buscar_persona_success(self, client, mock_token_required):
        """Test: Buscar persona exitosamente."""
        # Arrange
        class MockPersona:
            def __init__(self):
                self.id_persona = 1
                self.documento = '12345678'
                self.nombre = 'Juan Pérez'
                self.nombres = None
                self.nombre_persona = None
                self.nombre_completo = None
                self.estado = True
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento') as mock_buscar:
            mock_buscar.return_value = mock_persona
            with patch('src.routes.mensualidades_routes._persona_tiene_rol_deportista', return_value=True):
                response = client.get('/api/mensualidades/buscar-persona?documento=12345678')
        
        # Assert
        assert_success_response(response)
        assert response.json['success'] is True
        assert response.json['encontrado'] is True
        assert 'data' in response.json
        assert response.json['data']['id_persona'] == 1
        assert response.json['data']['rol_deportista'] is True
    
    def test_buscar_persona_no_encontrada(self, client, mock_token_required):
        """Test: Persona no encontrada."""
        # Act
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento', return_value=None):
            response = client.get('/api/mensualidades/buscar-persona?documento=99999999')
        
        # Assert
        assert_success_response(response)
        assert response.json['success'] is True
        assert response.json['encontrado'] is False
        assert 'message' in response.json
    
    def test_buscar_persona_sin_documento(self, client, mock_token_required):
        """Test: Error cuando no se proporciona documento."""
        # Act
        response = client.get('/api/mensualidades/buscar-persona')
        
        # Assert
        assert_success_response(response)
        assert response.json['success'] is False
        assert 'documento' in response.json['error'].lower()
    
    def test_buscar_persona_documento_invalido(self, client, mock_token_required):
        """Test: Error cuando el documento tiene formato inválido."""
        # Act
        with patch('src.routes.mensualidades_routes.validate_document') as mock_validate:
            from src.utils.validations import ValidationError
            mock_validate.side_effect = ValidationError('Formato de documento inválido')
            
            response = client.get('/api/mensualidades/buscar-persona?documento=abc')
        
        # Assert
        assert_success_response(response)
        assert response.json['success'] is False
        assert 'error' in response.json
    
    def test_buscar_persona_inactiva(self, client, mock_token_required):
        """Test: Persona encontrada pero inactiva."""
        # Arrange
        class MockPersona:
            def __init__(self):
                self.id_persona = 1
                self.documento = '12345678'
                self.nombre = 'Juan Pérez'
                self.nombres = None
                self.nombre_persona = None
                self.nombre_completo = None
                self.estado = False
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.routes.mensualidades_routes._buscar_persona_por_documento') as mock_buscar:
            mock_buscar.return_value = mock_persona
            with patch('src.routes.mensualidades_routes._persona_tiene_rol_deportista', return_value=False):
                response = client.get('/api/mensualidades/buscar-persona?documento=12345678')
        
        # Assert
        assert_success_response(response)
        assert response.json['encontrado'] is True
        assert response.json['data']['estado'] is False
        assert 'inactiva' in response.json['message'].lower()


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestDesactivarReactivarMensualidad:
    """Tests para los endpoints de desactivar/reactivar mensualidad"""
    
    def test_desactivar_mensualidad_success(self, client, mock_token_required):
        """Test: Desactivar mensualidad exitosamente."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'activo': False
        }
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.activo = True
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = client.patch('/api/mensualidades/1/desactivar')
        
        # Assert
        assert_success_response(response)
        assert mock_mensualidad.activo is False
    
    def test_desactivar_mensualidad_no_encontrada(self, client, mock_token_required):
        """Test: Error cuando la mensualidad no existe."""
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.patch('/api/mensualidades/999/desactivar')
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_reactivar_mensualidad_success(self, client, mock_token_required):
        """Test: Reactivar mensualidad exitosamente."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'activo': True
        }
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.activo = False
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = client.patch('/api/mensualidades/1/reactivar')
        
        # Assert
        assert_success_response(response)
        assert mock_mensualidad.activo is True
    
    def test_reactivar_mensualidad_no_encontrada(self, client, mock_token_required):
        """Test: Error cuando la mensualidad no existe."""
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.patch('/api/mensualidades/999/reactivar')
        
        # Assert
        assert_error_response(response, expected_status=404)

