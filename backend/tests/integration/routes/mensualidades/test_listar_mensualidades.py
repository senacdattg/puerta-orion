"""
Tests para el endpoint de listado de mensualidades.

Endpoint: GET /api/mensualidades
Funcionalidad: Lista todas las mensualidades con opciones de paginación y filtrado.
"""

import pytest
from unittest.mock import patch

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)
from tests.integration.test_utils import (
    create_mock_mensualidad,
    create_mock_persona,
    create_mock_pagination,
    setup_mock_db_session_get,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestListarMensualidades:
    """Tests para el endpoint GET /api/mensualidades"""
    
    def test_listar_mensualidades_success(self, client, mock_token_required):
        """Test: Listar mensualidades exitosamente."""
        # Arrange
        mock_mensualidad = create_mock_mensualidad(
            to_dict_data={
                'id_mensualidad': 1,
                'fecha_vencimiento': '2024-12-31',
                'monto': 50000.0
            }
        )
        mock_persona = create_mock_persona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role', return_value=False):
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        mock_pagination = create_mock_pagination(
                            items=[mock_mensualidad],
                            page=1,
                            per_page=20,
                            total=1,
                            pages=1
                        )
                        
                        mock_query.filter.return_value = mock_query
                        mock_query.order_by.return_value.paginate.return_value = mock_pagination
                        setup_mock_db_session_get(mock_db, {1: mock_persona})
                        
                        response = client.get('/api/mensualidades')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_mensualidades_con_paginacion(self, client, mock_token_required):
        """Test: Listar mensualidades con parámetros de paginación."""
        # Arrange
        mock_mensualidad = create_mock_mensualidad(to_dict_data={'id_mensualidad': 1})
        mock_persona = create_mock_persona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role', return_value=False):
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        mock_pagination = create_mock_pagination(
                            items=[mock_mensualidad],
                            page=2,
                            per_page=10,
                            total=25,
                            pages=3
                        )
                        
                        mock_query.filter.return_value = mock_query
                        mock_query.order_by.return_value.paginate.return_value = mock_pagination
                        setup_mock_db_session_get(mock_db, {1: mock_persona})
                        
                        response = client.get('/api/mensualidades?page=2&per_page=10')
        
        # Assert
        assert_success_response(response)

