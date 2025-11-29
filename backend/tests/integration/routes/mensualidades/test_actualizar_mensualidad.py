"""
Tests para el endpoint de actualizar mensualidad.

Endpoint: PUT /api/mensualidades/<id>
Funcionalidad: Actualiza una mensualidad existente aplicando validaciones de negocio.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestActualizarMensualidad:
    """Tests para el endpoint PUT /api/mensualidades/<id>"""
    
    def test_actualizar_mensualidad_success(self, client, mock_token_required):
        """Test: Actualizar mensualidad exitosamente."""
        # Arrange
        datos_actualizacion = {
            'monto_pago': 60000.0,
            'fecha_vencimiento': '2025-01-31',
            'saldo_pendiente': 30000.0,
            'id_metodo_pago': 2
        }
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'id_persona': 1,
            'monto_pago': 60000.0
        }
        # Asegurar que id_mensualidad sea un valor real (int), no MagicMock
        # para que pueda usarse en consultas SQL
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.activo = True
        mock_mensualidad.created_at = None
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.MetodoPago.query') as mock_metodo_query:
                mock_metodo_query.get.return_value = MagicMock()
                with patch('src.routes.mensualidades_routes._validar_mensualidad_duplicada'):
                    # Mockear la consulta de AbonoMensualidad para evitar que intente usar id_mensualidad en SQL
                    with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
                        mock_abono_query.filter_by.return_value.order_by.return_value.first.return_value = None
                        with patch('src.routes.mensualidades_routes.db') as mock_db:
                            mock_db.session.commit = MagicMock()
                            def mock_get(model, id_value):
                                if id_value == 1:
                                    return mock_persona
                                return None
                            mock_db.session.get = mock_get
                            
                            response = make_json_request(
                                client, 'PUT', '/api/mensualidades/1',
                                data=datos_actualizacion
                            )
        
        # Assert
        assert_success_response(response)
    
    def test_actualizar_mensualidad_no_encontrada(self, client, mock_token_required):
        """Test: Error cuando la mensualidad no existe."""
        # Arrange
        datos_actualizacion = {'monto_pago': 60000.0}
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/mensualidades/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_actualizar_mensualidad_monto_invalido(self, client, mock_token_required):
        """Test: Error cuando el monto es inválido."""
        # Arrange
        datos_actualizacion = {'monto_pago': -100}
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_persona = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/mensualidades/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_actualizar_mensualidad_fecha_invalida(self, client, mock_token_required):
        """Test: Error cuando la fecha de vencimiento es inválida."""
        # Arrange
        datos_actualizacion = {'fecha_vencimiento': 'fecha-invalida'}
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_persona = 1
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/mensualidades/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_actualizar_mensualidad_saldo_supera_monto(self, client, mock_token_required):
        """Test: Error cuando el saldo pendiente supera el monto."""
        # Arrange
        datos_actualizacion = {
            'monto_pago': 50000.0,
            'saldo_pendiente': 60000.0
        }
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_persona = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/mensualidades/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert_error_response(response, expected_status=400)
        assert 'saldo' in response.json['error'].lower()
    
    def test_actualizar_mensualidad_cambiar_documento(self, client, mock_token_required):
        """Test: Actualizar mensualidad cambiando el documento asociado."""
        # Arrange
        datos_actualizacion = {
            'numero_documento': '87654321',
            'monto_pago': 50000.0
        }
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1, 'id_persona': 2}
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.activo = True
        mock_mensualidad.created_at = None
        mock_mensualidad.estado = False
        
        class MockPersona:
            def __init__(self):
                self.id_persona = 2
                self.nombre_completo = 'María García'
                self.documento = '87654321'
        
        mock_persona_nueva = MockPersona()
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes._buscar_persona_por_documento') as mock_buscar:
                mock_buscar.return_value = mock_persona_nueva
                with patch('src.routes.mensualidades_routes._persona_tiene_rol_deportista', return_value=True):
                    with patch('src.routes.mensualidades_routes._validar_mensualidad_duplicada'):
                        with patch('src.routes.mensualidades_routes.db') as mock_db:
                            mock_db.session.commit = MagicMock()
                            def mock_get(model, id_value):
                                if id_value == 2:
                                    return mock_persona_nueva
                                return None
                            mock_db.session.get = mock_get
                            
                            response = make_json_request(
                                client, 'PUT', '/api/mensualidades/1',
                                data=datos_actualizacion
                            )
        
        # Assert
        assert_success_response(response)
        assert mock_mensualidad.id_persona == 2

