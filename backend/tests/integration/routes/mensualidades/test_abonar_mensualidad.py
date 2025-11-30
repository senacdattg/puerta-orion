"""
Tests para el endpoint de abonar mensualidad.

Endpoint: POST /api/mensualidades/<id>/abonar
Funcionalidad: Registra un abono para una mensualidad existente.
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
class TestAbonarMensualidad:
    """Tests para el endpoint POST /api/mensualidades/<id>/abonar"""
    
    def test_abonar_mensualidad_success(self, client, mock_token_required):
        """Test: Abonar mensualidad exitosamente."""
        # Arrange
        datos_abono = {
            'monto_abonado': 30000.0,
            'fecha_abono': '2024-12-15',
            'id_metodo_pago': 1
        }
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        mock_mensualidad.id_persona = 1
        mock_mensualidad.created_at = None
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.persona = None
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'saldo_pendiente': 20000.0,
            'monto_pago': 50000.0,
            'estado': False,
            'fecha_vencimiento': '2024-12-31',
            'fecha_pago': None
        }
        
        mock_abono = MagicMock()
        mock_abono.to_dict.return_value = {
            'id_abono': 1,
            'monto': 30000.0,
            'fecha_abono': '2024-12-15',
            'id_mensualidad': 1
        }
        
        # Mock para _serializar_mensualidad
        mock_serialized = {
            'id_mensualidad': 1,
            'saldo_pendiente': 20000.0,
            'monto_pago': 50000.0,
            'estado': False,
            'estado_texto': 'Pendiente',
            'persona_nombre': None,
            'numero_documento': None
        }
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.AbonoMensualidad') as mock_abono_class:
                mock_abono_class.return_value = mock_abono
                with patch('src.routes.mensualidades_routes.db') as mock_db:
                    mock_db.session.add = MagicMock()
                    mock_db.session.commit = MagicMock()
                    mock_db.session.refresh = MagicMock()
                    with patch('src.routes.mensualidades_routes._serializar_mensualidad') as mock_serializar:
                        mock_serializar.return_value = mock_serialized
                        
                        response = make_json_request(
                            client, 'POST', '/api/mensualidades/1/abonar',
                            data=datos_abono
                        )
        
        # Assert
        assert_success_response(response)
        assert 'meses_cubiertos' in response.json
        assert 'abono' in response.json
    
    def test_abonar_mensualidad_no_encontrada(self, client, mock_token_required):
        """Test: Error cuando la mensualidad no existe."""
        # Arrange
        datos_abono = {'monto_abonado': 30000.0}
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'POST', '/api/mensualidades/999/abonar',
                data=datos_abono
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_abonar_mensualidad_monto_excede_saldo(self, client, mock_token_required):
        """Test: Error cuando el monto abonado excede el saldo pendiente."""
        # Arrange
        datos_abono = {'monto_abonado': 60000.0}
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'POST', '/api/mensualidades/1/abonar',
                    data=datos_abono
                )
        
        # Assert
        assert_error_response(response, expected_status=400)
        assert 'monto abonado' in response.json['error'].lower()
    
    def test_abonar_mensualidad_monto_invalido(self, client, mock_token_required):
        """Test: Error cuando el monto abonado es inválido."""
        # Arrange
        datos_abono = {'monto_abonado': -100}
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.db') as mock_db:
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'POST', '/api/mensualidades/1/abonar',
                    data=datos_abono
                )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_abonar_mensualidad_completa_pago(self, client, mock_token_required):
        """Test: Abono que completa el pago de la mensualidad."""
        # Arrange
        datos_abono = {
            'monto_abonado': 50000.0,
            'fecha_abono': '2024-12-15'
        }
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        mock_mensualidad.id_persona = 1
        mock_mensualidad.created_at = None
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.persona = None
        
        # Configurar to_dict para retornar el estado y saldo actualizados dinámicamente
        def to_dict_side_effect():
            # Después de que la función actualiza el saldo y estado, retornar los valores actualizados
            return {
                'id_mensualidad': mock_mensualidad.id_mensualidad,
                'estado': mock_mensualidad.estado,
                'saldo_pendiente': mock_mensualidad.saldo_pendiente,
                'fecha_pago': mock_mensualidad.fecha_pago.isoformat() if mock_mensualidad.fecha_pago else None,
                'monto_pago': mock_mensualidad.monto_pago,
                'fecha_vencimiento': mock_mensualidad.fecha_vencimiento.isoformat() if mock_mensualidad.fecha_vencimiento else None
            }
        mock_mensualidad.to_dict.side_effect = to_dict_side_effect
        
        mock_abono = MagicMock()
        mock_abono.to_dict.return_value = {'id_abono': 1, 'monto': 50000.0}
        
        # Mock para _serializar_mensualidad
        mock_serialized = {
            'id_mensualidad': 1,
            'saldo_pendiente': 0.0,
            'monto_pago': 50000.0,
            'estado': True,
            'estado_texto': 'Pagado',
            'persona_nombre': None,
            'numero_documento': None
        }
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.AbonoMensualidad') as mock_abono_class:
                mock_abono_class.return_value = mock_abono
                with patch('src.routes.mensualidades_routes.db') as mock_db:
                    mock_db.session.add = MagicMock()
                    mock_db.session.commit = MagicMock()
                    mock_db.session.refresh = MagicMock()
                    with patch('src.routes.mensualidades_routes._serializar_mensualidad') as mock_serializar:
                        mock_serializar.return_value = mock_serialized
                        
                        response = make_json_request(
                            client, 'POST', '/api/mensualidades/1/abonar',
                            data=datos_abono
                        )
        
        # Assert
        assert_success_response(response)
        assert response.json.get('success') is True
        assert 'meses_cubiertos' in response.json
        assert 'abono' in response.json


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestListarAbonos:
    """Tests para el endpoint GET /api/mensualidades/<id>/abonos"""
    
    def test_listar_abonos_success(self, client, mock_token_required):
        """Test: Listar abonos exitosamente."""
        # Arrange
        mock_abono = MagicMock()
        mock_abono.to_dict.return_value = {
            'id_abono': 1,
            'monto': 30000.0,
            'fecha_abono': '2024-12-15'
        }
        mock_abono.id_abono = 1
        mock_abono.fecha_abono = date(2024, 12, 15)
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.estado = False
        mock_mensualidad.fecha_pago = None
        mock_mensualidad.monto_pago = 50000.0
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
                mock_abono_query.filter_by.return_value.order_by.return_value.all.return_value = [mock_abono]
                
                response = client.get('/api/mensualidades/1/abonos')
        
        # Assert
        assert_success_response(response)
        assert 'data' in response.json
        assert isinstance(response.json['data'], list)
    
    def test_listar_abonos_mensualidad_pagada(self, client, mock_token_required):
        """Test: Listar abonos incluye pago final si la mensualidad está pagada."""
        # Arrange
        fecha_pago = date(2024, 12, 20)
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.estado = True
        mock_mensualidad.fecha_pago = fecha_pago
        # Asegurar que monto_pago e id_metodo_pago sean valores reales, no MagicMock
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.id_metodo_pago = 1
        
        # Act
        with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
            mock_query.get.return_value = mock_mensualidad
            with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
                mock_abono_query.filter_by.return_value.order_by.return_value.all.return_value = []
                
                response = client.get('/api/mensualidades/1/abonos')
        
        # Assert
        assert_success_response(response)
        assert len(response.json['data']) > 0
        # Debe incluir un abono virtual con es_pago_final=True
        pago_final = next((a for a in response.json['data'] if a.get('es_pago_final')), None)
        assert pago_final is not None


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestActualizarAbono:
    """Tests para el endpoint PUT /api/mensualidades/<id>/abonos/<abono_id>"""
    
    def test_actualizar_abono_success(self, client, mock_token_required):
        """Test: Actualizar abono exitosamente."""
        # Arrange
        datos_actualizacion = {
            'monto': 35000.0,
            'fecha_abono': '2024-12-16',
            'id_metodo_pago': 2
        }
        
        mock_abono = MagicMock()
        mock_abono.to_dict.return_value = {
            'id_abono': 1,
            'monto': 35000.0,
            'fecha_abono': '2024-12-16',
            'id_mensualidad': 1,
            'id_metodo_pago': 2
        }
        mock_abono.id_abono = 1
        mock_abono.id_mensualidad = 1
        mock_abono.fecha_abono = date(2024, 12, 15)
        mock_abono.monto = 30000.0
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.id_persona = 1
        mock_mensualidad.created_at = None
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.persona = None
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'monto_pago': 50000.0,
            'estado': False
        }
        
        # Mock para _serializar_mensualidad
        mock_serialized = {
            'id_mensualidad': 1,
            'saldo_pendiente': 15000.0,
            'monto_pago': 50000.0,
            'estado': False,
            'estado_texto': 'Pendiente',
            'persona_nombre': None,
            'numero_documento': None
        }
        
        # Act
        with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
            mock_abono_query.get.return_value = mock_abono
            with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                mock_query.get.return_value = mock_mensualidad
                with patch('src.routes.mensualidades_routes.db') as mock_db:
                    mock_db.session.commit = MagicMock()
                    with patch('src.routes.mensualidades_routes._serializar_mensualidad') as mock_serializar:
                        mock_serializar.return_value = mock_serialized
                        
                        response = make_json_request(
                            client, 'PUT', '/api/mensualidades/1/abonos/1',
                            data=datos_actualizacion
                        )
        
        # Assert
        assert_success_response(response)
    
    def test_actualizar_abono_no_encontrado(self, client, mock_token_required):
        """Test: Error cuando el abono no existe."""
        # Arrange
        datos_actualizacion = {'monto': 35000.0}
        
        # Act
        with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
            mock_abono_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/mensualidades/1/abonos/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)
    
    def test_actualizar_abono_id_invalido(self, client, mock_token_required):
        """Test: Error cuando el abono no pertenece a la mensualidad."""
        # Arrange
        datos_actualizacion = {'monto': 35000.0}
        
        mock_abono = MagicMock()
        mock_abono.id_abono = 999
        mock_abono.id_mensualidad = 999  # Diferente a la mensualidad en la URL
        
        # Act
        with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
            mock_abono_query.get.return_value = mock_abono
            
            response = make_json_request(
                client, 'PUT', '/api/mensualidades/1/abonos/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.mensualidades
class TestEliminarAbono:
    """Tests para el endpoint DELETE /api/mensualidades/<id>/abonos/<abono_id>"""
    
    def test_eliminar_abono_success(self, client, mock_token_required):
        """Test: Eliminar abono exitosamente."""
        # Arrange
        mock_abono = MagicMock()
        mock_abono.id_abono = 1
        mock_abono.id_mensualidad = 1
        
        mock_mensualidad = MagicMock()
        mock_mensualidad.id_mensualidad = 1
        mock_mensualidad.monto_pago = 50000.0
        mock_mensualidad.id_persona = 1
        mock_mensualidad.created_at = None
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.persona = None
        mock_mensualidad.to_dict.return_value = {
            'id_mensualidad': 1,
            'monto_pago': 50000.0,
            'estado': False
        }
        
        # Mock para _serializar_mensualidad
        mock_serialized = {
            'id_mensualidad': 1,
            'saldo_pendiente': 50000.0,
            'monto_pago': 50000.0,
            'estado': False,
            'estado_texto': 'Pendiente',
            'persona_nombre': None,
            'numero_documento': None
        }
        
        # Act
        with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
            mock_abono_query.get.return_value = mock_abono
            with patch('src.routes.mensualidades_routes.Mensualidad.query') as mock_query:
                mock_query.get.return_value = mock_mensualidad
                with patch('src.routes.mensualidades_routes.db') as mock_db:
                    mock_db.session.delete = MagicMock()
                    mock_db.session.commit = MagicMock()
                    with patch('src.routes.mensualidades_routes._serializar_mensualidad') as mock_serializar:
                        mock_serializar.return_value = mock_serialized
                        
                        response = client.delete('/api/mensualidades/1/abonos/1')
        
        # Assert
        assert_success_response(response)
    
    def test_eliminar_abono_no_encontrado(self, client, mock_token_required):
        """Test: Error cuando el abono no existe."""
        # Act
        with patch('src.routes.mensualidades_routes.AbonoMensualidad.query') as mock_abono_query:
            mock_abono_query.get.return_value = None
            
            response = client.delete('/api/mensualidades/1/abonos/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

