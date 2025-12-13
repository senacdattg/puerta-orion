"""
Tests para el endpoint de crear deportista.

Endpoint: POST /api/deportistas/
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
class TestCrearDeportista:
    """Tests para el endpoint POST /api/deportistas/"""
    
    def test_crear_deportista_success(self, client, sample_deportista_data):
        """Test: Crear deportista exitosamente."""
        # Arrange
        mock_result = {
            'success': True,
            'message': 'Deportista creado exitosamente',
            'data': {'id_deportista': 1, 'id_persona': 1},
            'status_code': 201
        }
        
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista', 
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/deportistas/',
                data=sample_deportista_data
            )
        
        # Assert
        data = assert_success_response(response, expected_status=201)
        assert 'data' in data
        assert data['data']['id_deportista'] == 1
    
    def test_crear_deportista_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post(
            '/api/deportistas/',
            data='not json',
            content_type='text/plain'
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_deportista_cuerpo_vacio(self, client):
        """Test: Error cuando el cuerpo está vacío."""
        # Act
        response = make_json_request(client, 'POST', '/api/deportistas/', data={})
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_deportista_error_servicio(self, client, sample_deportista_data):
        """Test: Manejo de error del servicio."""
        # Arrange
        mock_result = {
            'success': False,
            'error': 'Error de validación',
            'message': 'Datos inválidos',
            'status_code': 400
        }
        
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista',
                   return_value=mock_result):
            response = make_json_request(
                client, 'POST', '/api/deportistas/',
                data=sample_deportista_data
            )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_deportista_excepcion(self, client, sample_deportista_data):
        """Test: Manejo de excepciones inesperadas."""
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista',
                   side_effect=Exception('Error inesperado')):
            response = make_json_request(
                client, 'POST', '/api/deportistas/',
                data=sample_deportista_data
            )
        
        # Assert
        assert_error_response(response, expected_status=500)

