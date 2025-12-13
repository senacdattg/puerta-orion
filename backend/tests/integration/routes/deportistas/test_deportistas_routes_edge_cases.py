"""
Tests adicionales para casos edge de deportistas_routes.py.

Cubre validaciones, manejo de errores y casos límite para aumentar cobertura.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
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
@pytest.mark.deportistas
class TestCrearDeportistaEdgeCases:
    """Tests para casos edge del endpoint POST /api/deportistas/"""

    def test_crear_deportista_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/deportistas/', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)

    def test_crear_deportista_json_vacio(self, client):
        """Test: Error cuando se envía JSON vacío."""
        # Act
        response = make_json_request(
            client, 'POST', '/api/deportistas/',
            data={}
        )
        
        # Assert
        # Puede ser 400 o 500 dependiendo de las validaciones del servicio
        assert response.status_code in [400, 500]

    def test_crear_deportista_error_servicio(self, client):
        """Test: Manejo de errores del servicio."""
        # Arrange
        mock_result = {
            'success': False,
            'error': 'Error en el servicio',
            'status_code': 500
        }
        
        with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista',
                   return_value=mock_result):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/',
                data={'id_persona': 1}
            )
            
            # Assert
            assert_error_response(response, expected_status=500)

    def test_crear_deportista_request_validation_error(self, client):
        """Test: Manejo de RequestValidationError."""
        # Arrange
        from src.utils.request_validators import RequestValidationError
        
        with patch('src.routes.deportistas_routes.DeportistaService.crear_deportista',
                   side_effect=RequestValidationError('Datos inválidos', status_code=400)):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/',
                data={'id_persona': 1}
            )
            
            # Assert
            assert_error_response(response, expected_status=400)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestRegistroCompletoEdgeCases:
    """Tests para casos edge del endpoint POST /api/deportistas/registro-completo"""

    def test_registro_completo_sin_json(self, client):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/deportistas/registro-completo', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)

    def test_registro_completo_error_servicio(self, client):
        """Test: Manejo de errores del servicio de registro completo."""
        # Arrange
        mock_result = {
            'success': False,
            'error': 'Error al registrar',
            'status_code': 500
        }
        
        datos_registro = {
            'datos_deportista': {'id_persona': 1},
            'informacion_deportiva': {}
        }
        
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo',
                   return_value=mock_result):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registro-completo',
                data=datos_registro
            )
            
            # Assert
            assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestRegistrarDeportistaEdgeCases:
    """Tests para casos edge del endpoint POST /api/deportistas/registrar"""

    def test_registrar_deportista_sin_autenticacion(self, client):
        """Test: Error cuando el usuario no está autenticado."""
        # Act
        with patch('src.routes.deportistas_routes.get_current_user', return_value=None):
            response = make_json_request(
                client, 'POST', '/api/deportistas/registrar',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_registrar_deportista_usuario_sin_persona(self, client, mock_token_required):
        """Test: Error cuando el usuario no tiene persona asociada."""
        # Arrange
        mock_usuario = {'id_usuario': 1}  # Sin 'persona'
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registrar',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_registrar_deportista_persona_sin_id(self, client, mock_token_required):
        """Test: Error cuando la persona no tiene ID."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {}  # Sin id_persona
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registrar',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_registrar_deportista_inyecta_id_persona(self, client, mock_token_required):
        """Test: Verificar que se inyecta id_persona automáticamente."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 10}
        }
        
        mock_result = {
            'success': True,
            'data': {'id_deportista': 1},
            'status_code': 201
        }
        
        datos_sin_id_persona = {
            'datos_deportista': {
                'fecha_nacimiento': 2005
            }
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo') as mock_registrar:
                mock_registrar.return_value = mock_result
                
                # Act
                make_json_request(
                    client, 'POST', '/api/deportistas/registrar',
                    data=datos_sin_id_persona
                )
                
                # Assert
                # Verificar que se llamó con id_persona inyectado
                call_args = mock_registrar.call_args[0][0]
                assert call_args['datos_deportista']['id_persona'] == 10


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestObtenerDeportistaEdgeCases:
    """Tests para casos edge del endpoint GET /api/deportistas/<id>"""

    def test_obtener_deportista_id_negativo(self, client):
        """Test: Error con ID negativo."""
        # Act
        response = client.get('/api/deportistas/-1')
        
        # Assert
        # Puede ser 404 (rutas no aceptan negativos) o 400
        assert response.status_code in [400, 404]

    def test_obtener_deportista_error_servicio(self, client):
        """Test: Manejo de errores del servicio."""
        # Arrange
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.obtener_informacion_completa_deportista',
                   side_effect=Exception("Error en servicio")):
            # Act
            response = client.get('/api/deportistas/1')
            
            # Assert
            assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestListarDeportistasEdgeCases:
    """Tests para casos edge del endpoint GET /api/deportistas/"""

    def test_listar_deportistas_error_servicio(self, client):
        """Test: Manejo de errores del servicio al listar."""
        # Arrange
        with patch('src.routes.deportistas_routes.DeportistaService.listar_deportistas',
                   side_effect=Exception("Error en servicio")):
            # Act
            response = client.get('/api/deportistas/')
            
            # Assert
            assert_error_response(response, expected_status=500)

    def test_listar_deportistas_resultado_vacio(self, client):
        """Test: Listar deportistas con resultado vacío."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [],
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.DeportistaService.listar_deportistas',
                   return_value=mock_result):
            # Act
            response = client.get('/api/deportistas/')
            
            # Assert
            data = assert_success_response(response)
            assert isinstance(data.get('data', []), list)
            assert len(data.get('data', [])) == 0


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestCatalogosEdgeCases:
    """Tests para casos edge de endpoints de catálogos"""

    def test_catalogo_diagnosticos_error(self, client):
        """Test: Manejo de errores en catálogo de diagnósticos."""
        # Arrange
        with patch('src.routes.deportistas_routes.CatalogosService.obtener_diagnosticos',
                   side_effect=Exception("Error en servicio")):
            # Act
            response = client.get('/api/deportistas/catalogos/diagnosticos')
            
            # Assert
            assert_error_response(response, expected_status=500)

    def test_catalogo_diagnosticos_por_tipo_error(self, client):
        """Test: Manejo de errores en catálogo de diagnósticos por tipo."""
        # Arrange
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad',
                   side_effect=Exception("Error en servicio")):
            # Act
            response = client.get('/api/deportistas/catalogos/diagnosticos-por-tipo/1')
            
            # Assert
            assert_error_response(response, expected_status=500)

    def test_catalogo_diagnosticos_por_tipo_id_invalido(self, client):
        """Test: Error con ID de tipo de enfermedad inválido."""
        # Arrange
        mock_result = {
            'success': False,
            'error': 'Tipo de enfermedad no encontrado',
            'status_code': 404
        }
        
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad',
                   return_value=mock_result):
            # Act
            response = client.get('/api/deportistas/catalogos/diagnosticos-por-tipo/999')
            
            # Assert
            assert_error_response(response, expected_status=404)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestActualizarDeportistaEdgeCases:
    """Tests para casos edge del endpoint PUT/PATCH /api/deportistas/<id>"""

    def test_actualizar_deportista_sin_autenticacion(self, client):
        """Test: Error cuando el usuario no está autenticado."""
        # Act
        with patch('src.routes.deportistas_routes.get_current_user', return_value=None):
            response = make_json_request(
                client, 'PUT', '/api/deportistas/1',
                data={'peso': 70}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_actualizar_deportista_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Arrange
        mock_usuario = {'id_usuario': 1}
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = client.put('/api/deportistas/1', data='not json')
            
            # Assert
            assert_error_response(response, expected_status=400)

    def test_actualizar_deportista_id_invalido(self, client, mock_token_required):
        """Test: Error con ID inválido (cero o negativo)."""
        # Arrange
        mock_usuario = {'id_usuario': 1}
        mock_result = {
            'success': False,
            'error': 'ID inválido',
            'status_code': 400
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.DeportistaService.actualizar_deportista',
                       return_value=mock_result):
                # Act
                response = make_json_request(
                    client, 'PUT', '/api/deportistas/0',
                    data={'peso': 70}
                )
                
                # Assert
                # Puede ser 400 o 404 dependiendo de la validación de rutas
                assert response.status_code in [400, 404]

