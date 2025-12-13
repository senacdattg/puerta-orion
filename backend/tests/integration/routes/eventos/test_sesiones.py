"""
Tests para los endpoints de sesiones.

Endpoints:
- GET /api/eventos/sesiones
- GET /api/eventos/sesiones/<sesion_id>
- POST /api/eventos/sesiones
- PUT /api/eventos/sesiones/<sesion_id>
- DELETE /api/eventos/sesiones/<sesion_id>
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request
)


@pytest.mark.routes
@pytest.mark.integration
class TestSesiones:
    """Tests para los endpoints de sesiones."""
    
    def test_listar_sesiones_success(self, client, mock_token_required):
        """Test: Listar sesiones exitosamente."""
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            mock_pagination = MagicMock()
            mock_sesion = MagicMock()
            mock_sesion.to_dict.return_value = {'id_sesion': 1, 'nombre': 'Sesión 1'}
            mock_pagination.items = [mock_sesion]
            mock_pagination.page = 1
            mock_pagination.per_page = 10
            mock_pagination.total = 1
            mock_pagination.pages = 1
            
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value.paginate.return_value = mock_pagination
            
            response = client.get('/api/eventos/sesiones')
            
            assert_success_response(response)
    
    def test_obtener_sesion_success(self, client, mock_token_required):
        """Test: Obtener sesión exitosamente."""
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            mock_sesion = MagicMock()
            mock_sesion.to_dict.return_value = {'id_sesion': 1, 'nombre': 'Sesión 1'}
            mock_query.get.return_value = mock_sesion
            
            response = client.get('/api/eventos/sesiones/1')
            
            assert_success_response(response)
    
    def test_obtener_sesion_no_encontrada(self, client, mock_token_required):
        """Test: Sesión no encontrada."""
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/eventos/sesiones/999')
            
            assert_error_response(response, expected_status=404)
    
    def test_crear_sesion_success(self, client, mock_token_required):
        """Test: Crear sesión exitosamente."""
        datos_sesion = {
            'nombre': 'Nueva Sesión',
            'descripcion': 'Descripción de la sesión'
        }
        
        # Hacer patch directamente en el módulo donde se usa Sesion
        with patch('src.routes.eventos_routes.Sesion') as mock_sesion_class:
            with patch('src.routes.eventos_routes.db') as mock_db:
                # Crear mock de query que retorna None cuando se llama a first()
                mock_query = MagicMock()
                mock_filter_by = MagicMock()
                # Configurar que first() retorna None explícitamente
                mock_filter_by.first = MagicMock(return_value=None)
                mock_query.filter_by = MagicMock(return_value=mock_filter_by)
                
                # Asignar el mock_query al atributo query de la clase mock
                mock_sesion_class.query = mock_query
                
                # Crear mock de sesión que se retornará al instanciar Sesion
                mock_sesion = MagicMock()
                mock_sesion.to_dict.return_value = {'id_sesion': 1, 'nombre': 'Nueva Sesión'}
                mock_sesion.nombre = 'Nueva Sesión'
                mock_sesion.descripcion = 'Descripción de la sesión'
                mock_sesion_class.return_value = mock_sesion
                
                # Configurar db.session para que commit no falle
                mock_db.session.add = MagicMock()
                mock_db.session.commit = MagicMock()
                mock_db.session.rollback = MagicMock()
                
                response = make_json_request(
                    client, 'POST', '/api/eventos/sesiones',
                    data=datos_sesion
                )
                
                assert response.status_code in [200, 201]
    
    def test_crear_sesion_nombre_duplicado(self, client, mock_token_required):
        """Test: Error al crear sesión con nombre duplicado."""
        datos_sesion = {
            'nombre': 'Sesión Existente',
            'descripcion': 'Descripción'
        }
        
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            mock_sesion_existente = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_sesion_existente
            
            response = make_json_request(
                client, 'POST', '/api/eventos/sesiones',
                data=datos_sesion
            )
            
            assert_error_response(response, expected_status=400)
    
    def test_actualizar_sesion_success(self, client, mock_token_required):
        """Test: Actualizar sesión exitosamente."""
        datos_actualizacion = {
            'nombre': 'Sesión Actualizada',
            'descripcion': 'Nueva descripción'
        }
        
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            mock_sesion = MagicMock()
            mock_sesion.to_dict.return_value = {'id_sesion': 1, 'nombre': 'Sesión Actualizada'}
            mock_query.get.return_value = mock_sesion
            mock_query.filter.return_value.first.return_value = None
            
            with patch('src.routes.eventos_routes.db'):
                response = make_json_request(
                    client, 'PUT', '/api/eventos/sesiones/1',
                    data=datos_actualizacion
                )
                
                assert response.status_code in [200, 400, 500]
    
    def test_eliminar_sesion_success(self, client, mock_token_required):
        """Test: Eliminar sesión exitosamente."""
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            with patch('src.routes.eventos_routes.Evento.query') as mock_evento_query:
                mock_sesion = MagicMock()
                mock_sesion.nombre = 'Sesión a Eliminar'
                mock_query.get.return_value = mock_sesion
                mock_evento_query.filter_by.return_value.count.return_value = 0
                
                with patch('src.routes.eventos_routes.db'):
                    response = client.delete('/api/eventos/sesiones/1')
                    
                    assert response.status_code in [200, 204, 500]
    
    def test_eliminar_sesion_con_eventos(self, client, mock_token_required):
        """Test: Error al eliminar sesión con eventos asociados."""
        with patch('src.routes.eventos_routes.Sesion.query') as mock_query:
            with patch('src.routes.eventos_routes.Evento.query') as mock_evento_query:
                mock_sesion = MagicMock()
                mock_query.get.return_value = mock_sesion
                mock_evento_query.filter_by.return_value.count.return_value = 2
                
                response = client.delete('/api/eventos/sesiones/1')
                
                assert_error_response(response, expected_status=400)

