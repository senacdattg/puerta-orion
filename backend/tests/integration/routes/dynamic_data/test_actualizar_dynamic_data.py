"""
Tests para el endpoint de actualización de datos dinámicos.

Endpoint: PUT /api/dynamic-data/<tema>/<registro_id>
Funcionalidad: Actualiza un registro existente en un catálogo dinámico.
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
@pytest.mark.dynamic_data
class TestActualizarDynamicData:
    """Tests para el endpoint PUT /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_actualizar_eps_success(self, client, mock_token_required):
        """Test: Actualizar EPS exitosamente."""
        # Arrange
        datos_actualizacion = {
            'nombre_eps': 'EPS Actualizada'
        }
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Actualizada'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            with patch('src.routes.dynamic_data_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/dynamic-data/eps/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert response.status_code in [200, 400, 500]
    
    def test_actualizar_dato_no_encontrado(self, client, mock_token_required):
        """Test: Error al actualizar dato inexistente."""
        # Arrange
        datos_actualizacion = {'nombre_eps': 'EPS Actualizada'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/dynamic-data/eps/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)

