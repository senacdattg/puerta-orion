"""
Tests para el endpoint de listado de mensualidades.

Endpoint: GET /api/mensualidades
Funcionalidad: Lista todas las mensualidades con opciones de paginación y filtrado.
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
@pytest.mark.mensualidades
class TestListarMensualidades:
    """Tests para el endpoint GET /api/mensualidades"""
    
    def test_listar_mensualidades_success(self, client, mock_token_required):
        """Test: Listar mensualidades exitosamente."""
        # Arrange
        from datetime import date
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'fecha_vencimiento': '2024-12-31',
            'monto': 50000.0
        }
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        
        # Crear un objeto simple en lugar de MagicMock para evitar problemas de serialización
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role', return_value=False):
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        mock_pagination = MagicMock()
                        mock_pagination.items = [mock_mensualidad]
                        mock_pagination.page = 1
                        mock_pagination.per_page = 20
                        mock_pagination.total = 1
                        mock_pagination.pages = 1
                        
                        mock_query.filter.return_value = mock_query
                        mock_query.order_by.return_value.paginate.return_value = mock_pagination
                        
                        # Mock db.session.get para _adjuntar_info_persona_dict
                        # Necesita retornar persona cuando se llama con Persona y id_persona
                        def mock_get(model, id_value):
                            if id_value == 1:
                                return mock_persona
                            return None
                        mock_db.session.get = mock_get
                        
                        response = client.get('/api/mensualidades')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_mensualidades_con_paginacion(self, client, mock_token_required):
        """Test: Listar mensualidades con parámetros de paginación."""
        # Arrange
        from datetime import date
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1}
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        
        # Crear un objeto simple en lugar de MagicMock para evitar problemas de serialización
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role', return_value=False):
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        mock_pagination = MagicMock()
                        mock_pagination.items = [mock_mensualidad]
                        mock_pagination.page = 2
                        mock_pagination.per_page = 10
                        mock_pagination.total = 25
                        mock_pagination.pages = 3
                        
                        mock_query.filter.return_value = mock_query
                        mock_query.order_by.return_value.paginate.return_value = mock_pagination
                        
                        # Mock db.session.get para _adjuntar_info_persona_dict
                        # Necesita retornar persona cuando se llama con Persona y id_persona
                        def mock_get(model, id_value):
                            if id_value == 1:
                                return mock_persona
                            return None
                        mock_db.session.get = mock_get
                        
                        response = client.get('/api/mensualidades?page=2&per_page=10')
        
        # Assert
        assert_success_response(response)

