"""
Tests para el endpoint de eliminación de datos dinámicos.

Endpoint: DELETE /api/dynamic-data/<tema>/<registro_id>
Funcionalidad: Elimina un registro de un catálogo dinámico.
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
class TestEliminarDynamicData:
    """Tests para el endpoint DELETE /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_eliminar_eps_success(self, client, mock_token_required):
        """Test: Eliminar EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.nombre_eps = 'EPS a Eliminar'
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            with patch('src.routes.dynamic_data_routes.db') as mock_db:
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                
                response = client.delete('/api/dynamic-data/eps/1')
        
        # Assert
        assert response.status_code in [200, 204]
    
    def test_eliminar_dato_no_encontrado(self, client, mock_token_required):
        """Test: Error al eliminar dato inexistente."""
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.delete('/api/dynamic-data/eps/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

