"""
Tests para el endpoint de obtener mensualidad por ID.

Endpoint: GET /api/mensualidades/<id>
Funcionalidad: Obtiene una mensualidad específica aplicando restricciones de rol.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from tests.helpers import (
    assert_success_response,
    assert_error_response,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestObtenerMensualidad:
    """Tests para el endpoint GET /api/mensualidades/<id>"""
    
    def test_obtener_mensualidad_success(self, client, mock_token_required):
        """Test: Obtener mensualidad exitosamente."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'id_persona': 1,
            'fecha_vencimiento': '2024-12-31',
            'monto_pago': 50000.0
        }
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.estado = False
        
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role', return_value=False):
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    mock_query.get.return_value = mock_mensualidad
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        def mock_get(model, id_value):
                            if id_value == 1:
                                return mock_persona
                            return None
                        mock_db.session.get = mock_get
                        
                        response = client.get('/api/mensualidades/1')
        
        # Assert
        assert_success_response(response)
        assert response.json['success'] is True
        assert 'data' in response.json
    
    def test_obtener_mensualidad_no_encontrada(self, client, mock_token_required):
        """Test: Error cuando la mensualidad no existe."""
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/mensualidades/999')
        
        # Assert
        assert_error_response(response, expected_status=404)
        assert 'no encontrada' in response.json['error'].lower()
    
    def test_obtener_mensualidad_deportista_propia(self, client, mock_token_required):
        """Test: Deportista puede obtener su propia mensualidad."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1, 'id_persona': 1}
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 0.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.estado = True
        
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user') as mock_user:
            mock_user.return_value = {
                'id_usuario': 1,
                'persona': {'id_persona': 1}
            }
            with patch('src.middleware.auth_decorator.has_role') as mock_has_role:
                def has_role_side_effect(role):
                    return role == 'Deportista'
                mock_has_role.side_effect = has_role_side_effect
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    mock_query.get.return_value = mock_mensualidad
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        def mock_get(model, id_value):
                            if id_value == 1:
                                return mock_persona
                            return None
                        mock_db.session.get = mock_get
                        
                        response = client.get('/api/mensualidades/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_mensualidad_deportista_ajena(self, client, mock_token_required):
        """Test: Deportista NO puede obtener mensualidad ajena."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_persona = 999  # Diferente al usuario autenticado
        mock_mensualidad.persona = None
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1}
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.estado = False
        
        # Act - Similar al test que funciona, pero con id_persona diferente
        # Mockear en el módulo de rutas donde se usan las funciones
        with patch('src.routes.mensualidades_routes.get_current_user') as mock_user:
            mock_user.return_value = {
                'id_usuario': 1,
                'persona': {'id_persona': 1}
            }
            with patch('src.routes.mensualidades_routes.has_role') as mock_has_role:
                def has_role_side_effect(role):
                    return role == 'Deportista'
                mock_has_role.side_effect = has_role_side_effect
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    mock_query.get.return_value = mock_mensualidad
                    
                    response = client.get('/api/mensualidades/1')
        
        # Assert
        assert_error_response(response, expected_status=403)
        assert 'autorizado' in response.json['error'].lower()
    
    def test_obtener_mensualidad_acudiente(self, client, mock_token_required):
        """Test: Acudiente puede obtener mensualidad de su acudido."""
        # Arrange
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1, 'id_persona': 2}
        mock_mensualidad.id_persona = 2
        mock_mensualidad.persona = None
        mock_mensualidad.created_at = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.estado = False
        
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.middleware.auth_decorator.get_current_user', return_value={'id_usuario': 1}):
            with patch('src.middleware.auth_decorator.has_role') as mock_has_role:
                def has_role_side_effect(role):
                    return role == 'Acudiente'
                mock_has_role.side_effect = has_role_side_effect
                with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                    mock_query.get.return_value = mock_mensualidad
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        def mock_get(model, id_value):
                            if id_value == 2:
                                return mock_persona
                            return None
                        mock_db.session.get = mock_get
                        
                        response = client.get('/api/mensualidades/1?persona_id=2')
        
        # Assert
        assert_success_response(response)

