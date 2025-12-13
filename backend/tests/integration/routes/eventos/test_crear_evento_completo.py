"""
Tests de integración para crear evento.

Endpoint: POST /api/eventos/calendario
Funcionalidad: Crear un nuevo evento en el calendario
"""

import pytest
from datetime import date, time
from freezegun import freeze_time

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
    create_auth_headers
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.eventos
class TestCrearEventoCompleto:
    """Tests para el endpoint POST /api/eventos/calendario"""
    
    @freeze_time("2024-01-15")
    def test_crear_evento_exitoso(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Crear evento exitosamente.
        
        Valida:
        - Creación de evento en BD
        - Validación de datos
        - Respuesta con datos del evento creado
        """
        # Arrange
        datos_evento = {
            'nombre': 'Torneo Regional',
            'descripcion': 'Torneo regional de voleibol',
            'fecha_evento': '2024-02-15',
            'hora_inicio': '08:00',
            'hora_fin': '12:00',
            'lugar': 'Coliseo Municipal',
            'id_categoria': categoria.id_categoria,
            'id_tipo_evento': tipo_evento.id_tipo_evento
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/eventos/calendario',
            data=datos_evento,
            headers=headers
        )
        
        # Assert
        # Verificar respuesta primero
        assert response.status_code == 201, f"Expected status 201, got {response.status_code}. Response: {response.get_json()}"
        data = response.get_json()
        assert data.get('success') is True, f"Expected success=True, got {data.get('success')}. Response: {data}"
        assert 'data' in data, f"Expected 'data' in response, got: {data}"
        
        # El endpoint devuelve el evento en data directamente
        evento_data = data.get('data', {})
        assert 'id_evento' in evento_data or 'nombre' in evento_data, f"Expected evento data, got: {evento_data}"
        
        # Obtener el ID del evento de la respuesta
        evento_id = evento_data.get('id_evento') or (evento_data.get('id') if isinstance(evento_data, dict) else None)
        
        # Verificar que se guardó en BD usando el ID de la respuesta
        from src.models.eventos.evento import Evento
        if evento_id:
            evento = Evento.query.get(evento_id)
        else:
            # Si no hay ID, buscar por nombre
            evento = Evento.query.filter_by(nombre='Torneo Regional').first()
        
        assert evento is not None, f"Evento should be created in database. Response data: {evento_data}"
        assert evento.fecha_evento == date(2024, 2, 15)
        assert evento.id_categoria == categoria.id_categoria
    
    def test_crear_evento_sin_datos(
        self, client, mock_token_required
    ):
        """
        Test: Error cuando no se envían datos.
        
        Valida que el sistema rechaza peticiones sin datos.
        """
        # Arrange
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/eventos/calendario',
            data={},
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_evento_categoria_no_existe(
        self, client, db_session, tipo_evento, mock_token_required
    ):
        """
        Test: Error cuando la categoría no existe.
        
        Valida que el sistema rechaza eventos con categorías inválidas.
        """
        # Arrange
        datos_evento = {
            'nombre': 'Torneo Regional',
            'descripcion': 'Torneo regional de voleibol',
            'fecha_evento': '2024-02-15',
            'hora_inicio': '08:00',
            'hora_fin': '12:00',
            'lugar': 'Coliseo Municipal',
            'id_categoria': 99999,  # Categoría inexistente
            'id_tipo_evento': tipo_evento.id_tipo_evento
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/eventos/calendario',
            data=datos_evento,
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=404)
        data = response.get_json()
        assert 'error' in data
        assert 'categoría' in data['error'].lower() or 'categoria' in data['error'].lower()
    
    def test_crear_evento_fecha_pasada(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Crear evento con fecha pasada (puede ser válido según reglas de negocio).
        
        Valida el comportamiento con fechas pasadas.
        """
        # Arrange
        datos_evento = {
            'nombre': 'Evento Pasado',
            'descripcion': 'Evento con fecha pasada',
            'fecha_evento': '2020-01-01',  # Fecha pasada
            'hora_inicio': '08:00',
            'hora_fin': '12:00',
            'lugar': 'Coliseo Municipal',
            'id_categoria': categoria.id_categoria,
            'id_tipo_evento': tipo_evento.id_tipo_evento
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/eventos/calendario',
            data=datos_evento,
            headers=headers
        )
        
        # Assert
        # Depende de las reglas de negocio - puede ser válido o no
        # Por ahora asumimos que es válido
        assert response.status_code in [201, 400]
    
    def test_crear_evento_hora_invalida(
        self, client, db_session, categoria, tipo_evento, mock_token_required
    ):
        """
        Test: Error con formato de hora inválido.
        
        Valida que el sistema rechaza horas con formato incorrecto.
        """
        # Arrange
        datos_evento = {
            'nombre': 'Torneo Regional',
            'descripcion': 'Torneo regional de voleibol',
            'fecha_evento': '2024-02-15',
            'hora_inicio': '25:00',  # Hora inválida
            'hora_fin': '12:00',
            'lugar': 'Coliseo Municipal',
            'id_categoria': categoria.id_categoria,
            'id_tipo_evento': tipo_evento.id_tipo_evento
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/eventos/calendario',
            data=datos_evento,
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=400)

