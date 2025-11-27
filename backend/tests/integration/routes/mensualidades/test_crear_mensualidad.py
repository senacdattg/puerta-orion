"""
Tests para el endpoint de creación de mensualidad.

Endpoint: POST /api/mensualidades
Funcionalidad: Crea una nueva mensualidad para un deportista.
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
class TestCrearMensualidad:
    """Tests para el endpoint POST /api/mensualidades"""
    
    def test_crear_mensualidad_success(self, client, mock_token_required):
        """Test: Crear mensualidad exitosamente."""
        # Arrange
        datos_mensualidad = {
            'id_persona': 1,
            'fecha_vencimiento': '2024-12-31',
            'monto_pago': 50000.0,
            'id_metodo_pago': 1,
            'estado_ui': 'Pendiente',
            'saldo_pendiente': 50000.0
        }
        from datetime import date
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1}
        mock_mensualidad.id_persona = 1
        mock_mensualidad.persona = None
        mock_mensualidad.activo = True
        mock_mensualidad.saldo_pendiente = 50000.0
        mock_mensualidad.fecha_vencimiento = date(2024, 12, 31)
        mock_mensualidad.id_metodo_pago = 1
        mock_mensualidad.created_at = None
        
        # Crear un objeto simple en lugar de MagicMock para evitar problemas de serialización
        class MockPersona:
            def __init__(self):
                self.nombre_completo = 'Juan Pérez'
                self.documento = '12345678'
        
        mock_persona = MockPersona()
        
        # Act
        with patch('src.routes.mensualidades_routes.Persona.query') as mock_persona_query:
            mock_persona_query.get.return_value = mock_persona
            with patch('src.routes.mensualidades_routes.MetodoPago.query') as mock_metodo_query:
                mock_metodo_query.get.return_value = MagicMock()
                with patch('src.routes.mensualidades_routes._validar_persona_con_rol_deportista'):
                    with patch('src.routes.mensualidades_routes.Mensualidad') as mock_mensualidad_class:
                        # Mock para _validar_mensualidad_duplicada
                        # La función usa Mensualidad.query.filter(...).first()
                        mock_query_base = MagicMock()
                        mock_query_filtered = MagicMock()
                        mock_query_filtered.first.return_value = None  # No hay duplicados
                        mock_query_base.filter.return_value = mock_query_filtered
                        mock_mensualidad_class.query = mock_query_base
                        mock_mensualidad_class.return_value = mock_mensualidad
                        with patch('src.routes.mensualidades_routes.db') as mock_db:
                            mock_db.session.add = MagicMock()
                            mock_db.session.flush = MagicMock()
                            mock_db.session.commit = MagicMock()
                            # Mock db.session.get para _adjuntar_info_persona_dict
                            def mock_get(model, id_value):
                                if id_value == 1:
                                    return mock_persona
                                return None
                            mock_db.session.get = mock_get
                            
                            # Mock para _registrar_abono_inicial si se llama
                            with patch('src.routes.mensualidades_routes._registrar_abono_inicial'):
                                response = make_json_request(
                                    client, 'POST', '/api/mensualidades',
                                    data=datos_mensualidad
                                )
        
        # Assert
        assert response.status_code in [200, 201]
    
    def test_crear_mensualidad_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/mensualidades', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_mensualidad_campos_faltantes(self, client, mock_token_required):
        """Test: Error cuando faltan campos requeridos."""
        # Arrange
        datos_incompletos = {
            'fecha_vencimiento': '2024-12-31'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/mensualidades',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

