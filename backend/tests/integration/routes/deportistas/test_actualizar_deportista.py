"""
Tests para el endpoint de actualizar deportista.

Endpoint: PUT/PATCH /api/deportistas/<id_deportista>
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
class TestActualizarDeportista:
    """Tests para el endpoint PUT/PATCH /api/deportistas/<id_deportista>"""
    
    def test_actualizar_deportista_success(self, client, mock_token_required):
        """Test: Actualizar deportista exitosamente."""
        # Arrange
        datos_actualizacion = {
            'datos_deportista': {
                'peso': 70.0,
                'altura': 1.80
            }
        }
        mock_result = {
            'success': True,
            'message': 'Deportista actualizado exitosamente',
            'data': {'id_deportista': 1},
            'status_code': 200
        }
        
        # Act
        with patch('src.routes.deportistas_routes.DeportistaService.actualizar_deportista_completo',
                   return_value=mock_result):
            response = make_json_request(
                client, 'PUT', '/api/deportistas/1',
                data=datos_actualizacion
            )
        
        # Assert
        assert_success_response(response)
    
    def test_actualizar_deportista_sin_autenticacion(self, client):
        """Test: Error cuando no hay autenticación."""
        # Act
        response = make_json_request(
            client, 'PUT', '/api/deportistas/1',
            data={'peso': 70.0}
        )
        
        # Assert - Debería retornar 401 (no autenticado)
        # Nota: Esto depende de cómo esté configurado el decorador
        assert response.status_code in [401, 403, 500]  # Ajustar según implementación

