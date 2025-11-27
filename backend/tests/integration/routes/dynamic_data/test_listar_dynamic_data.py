"""
Tests para el endpoint de listado de datos dinámicos.

Endpoint: GET /api/dynamic-data/<tema>
Funcionalidad: Lista todos los registros de un catálogo dinámico (EPS, sexos, etc.).
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
class TestListarDynamicData:
    """Tests para el endpoint GET /api/dynamic-data/<tema>"""
    
    def test_listar_eps_success(self, client, mock_token_required):
        """Test: Listar EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Test'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_eps]
            
            response = client.get('/api/dynamic-data/eps')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_sexos_success(self, client, mock_token_required):
        """Test: Listar sexos exitosamente."""
        # Arrange
        mock_sexo = MagicMock()
        mock_sexo.to_dict.return_value = {'id_sexo': 1, 'nombre_sexo': 'Masculino'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.Sexo.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_sexo]
            
            response = client.get('/api/dynamic-data/sexo')
        
        # Assert
        assert_success_response(response)

