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
            'monto': 50000.0,
            'id_metodo_pago': 1,
            'estado': 'Pendiente'
        }
        mock_mensualidad = MagicMock()
        mock_mensualidad.to_dict.return_value = {'id_mensualidad': 1}
        
        # Act
        with patch('src.routes.mensualidades_routes.Persona.query') as mock_persona:
            mock_persona.get.return_value = MagicMock()
            with patch('src.routes.mensualidades_routes.MetodoPago.query') as mock_metodo:
                mock_metodo.get.return_value = MagicMock()
                with patch('src.routes.mensualidades_routes.Mensualidad') as mock_mensualidad_class:
                    mock_mensualidad_class.query.filter_by.return_value.first.return_value = None
                    mock_mensualidad_class.return_value = mock_mensualidad
                    with patch('src.routes.mensualidades_routes.db') as mock_db:
                        mock_db.session.add = MagicMock()
                        mock_db.session.commit = MagicMock()
                        
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

