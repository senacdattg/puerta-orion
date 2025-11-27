"""
Tests para el endpoint de obtención de dato dinámico individual.

Endpoint: GET /api/dynamic-data/<tema>/<registro_id>
Funcionalidad: Obtiene los detalles de un registro específico de un catálogo dinámico.
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
class TestObtenerDynamicData:
    """Tests para el endpoint GET /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_obtener_eps_success(self, client, mock_token_required):
        """Test: Obtener EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Test'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            
            response = client.get('/api/dynamic-data/eps/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_dato_no_encontrado(self, client, mock_token_required):
        """Test: Dato no encontrado."""
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/dynamic-data/eps/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

