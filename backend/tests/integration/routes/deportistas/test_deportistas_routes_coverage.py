"""
Tests de integración para aumentar cobertura de deportistas_routes.py.

Este archivo complementa los tests existentes para cubrir líneas sin cubrir,
especialmente en endpoints y validaciones específicas.
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
@pytest.mark.deportistas
class TestRegistrarDeportistaCoverage:
    """Tests para aumentar cobertura de registrar_deportista endpoint."""

    def test_registrar_deportista_usuario_sin_persona(self, client, mock_token_required):
        """Test: Usuario sin persona asociada (línea 216-219)."""
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

    def test_registrar_deportista_persona_sin_id_persona(self, client, mock_token_required):
        """Test: Persona sin id_persona (línea 221-225)."""
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

    def test_registrar_deportista_datos_deportista_none(self, client, mock_token_required):
        """Test: datos_deportista es None (línea 228-229)."""
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
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo') as mock_registrar:
                mock_registrar.return_value = mock_result
                
                # Act - datos sin 'datos_deportista' o con None
                response = make_json_request(
                    client, 'POST', '/api/deportistas/registrar',
                    data={'datos_deportista': None}
                )
                
                # Assert
                # Debe inicializar datos_deportista como {} y llamar al servicio
                assert response.status_code in [200, 201]
                mock_registrar.assert_called_once()

    def test_registrar_deportista_persona_sin_id_persona_valor_none(self, client, mock_token_required):
        """Test: Persona con id_persona None (línea 225-228)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': None}  # id_persona es None
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registrar',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)
            data = response.get_json()
            assert 'No se pudo determinar la persona del usuario' in data.get('message', '')

    def test_registrar_deportista_request_validation_error(self, client, mock_token_required):
        """Test: RequestValidationError en registrar_deportista (línea 240-241)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        from src.utils.request_validators import RequestValidationError
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.obtener_json_requerido', 
                      side_effect=RequestValidationError("Error de validación")):
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/registrar',
                    data={'datos_deportista': {}}
                )
                
                # Assert
                assert_error_response(response, expected_status=400)

    def test_registrar_deportista_exception_generica(self, client, mock_token_required):
        """Test: Exception genérica en registrar_deportista (línea 242-243)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo',
                      side_effect=Exception("Error inesperado")):
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/registrar',
                    data={'datos_deportista': {}}
                )
                
                # Assert
                assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestRegistroCompletoCoverage:
    """Tests para aumentar cobertura de registro_deportista_completo endpoint."""

    def test_registro_completo_request_validation_error(self, client):
        """Test: RequestValidationError en registro_deportista_completo (línea 166-167)."""
        # Arrange
        from src.utils.request_validators import RequestValidationError
        
        with patch('src.routes.deportistas_routes.obtener_json_requerido',
                  side_effect=RequestValidationError("Error de validación")):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registro-completo',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=400)

    def test_registro_completo_exception_generica(self, client):
        """Test: Exception genérica en registro_deportista_completo (línea 168-169)."""
        # Arrange
        with patch('src.routes.deportistas_routes.RegistroDeportistaService.registrar_deportista_nuevo',
                  side_effect=Exception("Error inesperado")):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/registro-completo',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestAsociarAcudienteDeportistaCoverage:
    """Tests para aumentar cobertura de asociar_acudiente_deportista endpoint."""

    def test_asociar_acudiente_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Usuario no encontrado en contexto (línea 342-345)."""
        with patch('src.routes.deportistas_routes.get_current_user', return_value=None):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes',
                data={'id_parentesco': 1, 'es_responsable': False}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_asociar_acudiente_sin_id_persona(self, client, mock_token_required):
        """Test: Usuario sin id_persona (línea 367-372)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {}  # Sin id_persona
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes',
                data={'id_parentesco': 1, 'es_responsable': False}
            )
            
            # Assert
            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_no_es_acudiente(self, client, mock_token_required):
        """Test: Usuario no está registrado como acudiente (línea 375-379)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_acudiente_model.query = mock_query
                
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/1/acudientes',
                    data={'id_parentesco': 1, 'es_responsable': False}
                )
                
                # Assert
                assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_deportista_no_existe(self, client, mock_token_required):
        """Test: Deportista no existe (línea 382-387)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = None
                    mock_deportista_model.query = mock_query_deportista
                    
                    # Act
                    response = make_json_request(
                        client, 'POST', '/api/deportistas/999/acudientes',
                        data={'id_parentesco': 1, 'es_responsable': False}
                    )
                    
                    # Assert
                    assert_error_response(response, expected_status=404)

    def test_asociar_acudiente_auto_asociacion(self, client, mock_token_required):
        """Test: Deportista intenta acudirse a sí mismo (línea 389-394)."""
        # Arrange
        id_persona = 1
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': id_persona}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = id_persona  # Mismo id_persona
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    # Act
                    response = make_json_request(
                        client, 'POST', '/api/deportistas/1/acudientes',
                        data={'id_parentesco': 1, 'es_responsable': False}
                    )
                    
                    # Assert
                    assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_parentesco_no_existe(self, client, mock_token_required):
        """Test: Parentesco no existe (línea 397-402)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2  # Diferente al usuario
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = None
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        # Act
                        response = make_json_request(
                            client, 'POST', '/api/deportistas/1/acudientes',
                            data={'id_parentesco': 999, 'es_responsable': False}
                        )
                        
                        # Assert
                        assert_error_response(response, expected_status=404)

    def test_asociar_acudiente_relacion_duplicada(self, client, mock_token_required):
        """Test: Relación ya existe (línea 404-414)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        mock_relacion_existente = MagicMock()
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by.return_value.first.return_value = mock_relacion_existente
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes',
                                data={'id_parentesco': 1, 'es_responsable': False}
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_limite_acudiente_excedido(self, client, mock_token_required):
        """Test: Acudiente ya tiene 3 deportistas (línea 416-426)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Primera query: relación no existe
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by.return_value.first.return_value = None
                            
                            # Segunda query: count de deportistas = 3
                            mock_query_count = MagicMock()
                            mock_query_count.filter_by.return_value.count.return_value = 3
                            
                            mock_query_relacion.filter_by.return_value.count = mock_query_count.filter_by.return_value.count
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes',
                                data={'id_parentesco': 1, 'es_responsable': False}
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_limite_deportista_excedido(self, client, mock_token_required):
        """Test: Deportista ya tiene 3 acudientes (línea 428-438)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            mock_query_relacion = MagicMock()
                            # Relación no existe
                            mock_query_relacion.filter_by.return_value.first.return_value = None
                            
                            # Acudiente tiene menos de 3
                            mock_query_count_acudiente = MagicMock()
                            mock_query_count_acudiente.count.return_value = 2
                            mock_query_relacion.filter_by.return_value.count = MagicMock(return_value=2)
                            
                            # Deportista tiene 3 acudientes
                            def count_side_effect(*args, **kwargs):
                                if 'id_deportista' in kwargs:
                                    return MagicMock(count=MagicMock(return_value=3))
                                return mock_query_count_acudiente
                            
                            mock_query_relacion.filter_by = MagicMock(side_effect=count_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes',
                                data={'id_parentesco': 1, 'es_responsable': False}
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_success(self, client, mock_token_required):
        """Test: Asociación exitosa (línea 440-464)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        mock_relacion_nueva = MagicMock()
        mock_relacion_nueva.id_deportista_acudiente = 1
        mock_relacion_nueva.id_deportista = 1
        mock_relacion_nueva.id_acudiente = 1
        mock_relacion_nueva.id_parentesco = 1
        mock_relacion_nueva.es_responsable = False
        mock_relacion_nueva.fecha_registro = date.today()
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Configurar las queries de manera más explícita
                            # Query 1: Verificar si existe la relación (debe retornar None)
                            mock_query_check = MagicMock()
                            mock_query_check.first.return_value = None
                            
                            # Query 2: Contar deportistas del acudiente (debe retornar 2, menos de 3)
                            mock_query_count_acudiente = MagicMock()
                            mock_query_count_acudiente.count.return_value = 2
                            
                            # Query 3: Contar acudientes del deportista (debe retornar 2, menos de 3)
                            mock_query_count_deportista = MagicMock()
                            mock_query_count_deportista.count.return_value = 2
                            
                            # Configurar filter_by para devolver la query apropiada según los kwargs
                            def filter_by_side_effect(**kwargs):
                                # Si es para verificar existencia de relación (tiene ambos)
                                if 'id_deportista' in kwargs and 'id_acudiente' in kwargs:
                                    return mock_query_check
                                # Si es para contar deportistas del acudiente (solo id_acudiente)
                                elif 'id_acudiente' in kwargs and 'id_deportista' not in kwargs:
                                    return mock_query_count_acudiente
                                # Si es para contar acudientes del deportista (solo id_deportista)
                                elif 'id_deportista' in kwargs and 'id_acudiente' not in kwargs:
                                    return mock_query_count_deportista
                                return mock_query_check
                            
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by = MagicMock(side_effect=filter_by_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Crear un objeto mock para la nueva relación con todos los atributos necesarios
                            nueva_relacion_instancia = MagicMock()
                            nueva_relacion_instancia.id_deportista_acudiente = 1
                            nueva_relacion_instancia.id_deportista = 1
                            nueva_relacion_instancia.id_acudiente = 1
                            nueva_relacion_instancia.id_parentesco = 1
                            nueva_relacion_instancia.es_responsable = False
                            nueva_relacion_instancia.fecha_registro = date.today()  # Objeto date real para isoformat()
                            
                            # Configurar el constructor para que retorne directamente el objeto mock
                            mock_relacion_model.return_value = nueva_relacion_instancia
                            
                            # Parchear db - solo necesitamos parchear donde se usa
                            with patch('src.routes.deportistas_routes.db') as mock_db:
                                mock_db.session.add = MagicMock()
                                mock_db.session.commit = MagicMock()
                                
                                # También parchear el import dentro de la función
                                with patch('src.models.base.db', mock_db):
                                    # Act
                                    response = make_json_request(
                                        client, 'POST', '/api/deportistas/1/acudientes',
                                        data={'id_parentesco': 1, 'es_responsable': False}
                                    )
                                    
                                    # Assert
                                    assert_success_response(response, expected_status=201)

    def test_asociar_acudiente_sin_id_parentesco(self, client, mock_token_required):
        """Test: Falta id_parentesco (línea 352-356)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes',
                data={'es_responsable': False}  # Sin id_parentesco
            )
            
            # Assert
            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_limite_deportista_excedido(self, client, mock_token_required):
        """Test: Deportista ya tiene 3 acudientes (línea 437)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                    mock_query_deportista = MagicMock()
                    mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                    mock_deportista_model.query = mock_query_deportista
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Configurar las queries
                            # Query 1: Verificar si existe la relación (debe retornar None)
                            mock_query_check = MagicMock()
                            mock_query_check.first.return_value = None
                            
                            # Query 2: Contar deportistas del acudiente (debe retornar 2, menos de 3)
                            mock_query_count_acudiente = MagicMock()
                            mock_query_count_acudiente.count.return_value = 2
                            
                            # Query 3: Contar acudientes del deportista (debe retornar 3, igual o mayor a 3)
                            mock_query_count_deportista = MagicMock()
                            mock_query_count_deportista.count.return_value = 3
                            
                            # Configurar filter_by para devolver la query apropiada según los kwargs
                            def filter_by_side_effect(**kwargs):
                                # Si es para verificar existencia de relación (tiene ambos)
                                if 'id_deportista' in kwargs and 'id_acudiente' in kwargs:
                                    return mock_query_check
                                # Si es para contar deportistas del acudiente (solo id_acudiente)
                                elif 'id_acudiente' in kwargs and 'id_deportista' not in kwargs:
                                    return mock_query_count_acudiente
                                # Si es para contar acudientes del deportista (solo id_deportista)
                                elif 'id_deportista' in kwargs and 'id_acudiente' not in kwargs:
                                    return mock_query_count_deportista
                                return mock_query_check
                            
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by = MagicMock(side_effect=filter_by_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes',
                                data={'id_parentesco': 1, 'es_responsable': False}
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)
                            data = response.get_json()
                            assert 'Un deportista solo puede estar asociado a máximo 3 acudientes' in data.get('message', '')

    def test_asociar_acudiente_request_validation_error(self, client, mock_token_required):
        """Test: RequestValidationError en asociar_acudiente_deportista (línea 469-470)."""
        # Arrange
        from src.utils.request_validators import RequestValidationError
        
        with patch('src.routes.deportistas_routes.obtener_json_requerido',
                  side_effect=RequestValidationError("Error de validación")):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes',
                data={'id_parentesco': 1, 'es_responsable': False}
            )
            
            # Assert
            assert_error_response(response, expected_status=400)

    def test_asociar_acudiente_exception_generica(self, client, mock_token_required):
        """Test: Exception genérica en asociar_acudiente_deportista (línea 471-474)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.side_effect = Exception("Error inesperado en query")
                mock_acudiente_model.query = mock_query
                
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/1/acudientes',
                    data={'id_parentesco': 1, 'es_responsable': False}
                )
                
                # Assert
                assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestObtenerAcudientesPorDeportistaCoverage:
    """Tests para aumentar cobertura de obtener_acudientes_por_deportista endpoint."""

    def test_obtener_acudientes_deportista_no_existe(self, client, mock_token_required):
        """Test: Deportista no existe (línea 496-501)."""
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_model.query = mock_query
            
            # Act
            response = client.get('/api/deportistas/999/acudientes')
            
            # Assert
            assert_error_response(response, expected_status=404)

    def test_obtener_acudientes_sin_relaciones(self, client, mock_token_required):
        """Test: No hay relaciones (línea 507-511)."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_model.query = mock_query
            
            with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                mock_query_relacion = MagicMock()
                mock_query_relacion.filter_by.return_value.all.return_value = []
                mock_relacion_model.query = mock_query_relacion
                
                # Act
                response = client.get('/api/deportistas/1/acudientes')
                
                # Assert
                assert_success_response(response)
                data = response.get_json()
                assert data.get('data') == []

    def test_obtener_acudientes_con_acudientes_sin_persona(self, client, mock_token_required):
        """Test: Relaciones con acudientes sin persona (línea 518-519)."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        mock_relacion = MagicMock()
        mock_relacion.id_acudiente = 1
        
        mock_acudiente_sin_persona = MagicMock()
        mock_acudiente_sin_persona.id_acudiente = 1
        mock_acudiente_sin_persona.persona = None
        
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_model.query = mock_query
            
            with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                mock_query_relacion = MagicMock()
                mock_query_relacion.filter_by.return_value.all.return_value = [mock_relacion]
                mock_relacion_model.query = mock_query_relacion
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente_sin_persona
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    # Act
                    response = client.get('/api/deportistas/1/acudientes')
                    
                    # Assert
                    # Debe continuar y no agregar acudientes sin persona
                    assert_success_response(response)
                    data = response.get_json()
                    # La lista debe estar vacía o no contener el acudiente sin persona
                    assert isinstance(data.get('data'), list)

    def test_obtener_acudientes_con_relaciones_validas(self, client, mock_token_required):
        """Test: Obtener acudientes con relaciones válidas (línea 698-715)."""
        from types import SimpleNamespace
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        mock_relacion = MagicMock()
        mock_relacion.id_acudiente = 1
        mock_parentesco = SimpleNamespace()
        mock_parentesco.nombre = 'Padre'
        mock_relacion.parentesco = mock_parentesco
        mock_relacion.es_responsable = True
        
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.documento = '12345678'
        mock_persona.correo_electronico = 'juan@example.com'
        mock_persona.telefono = '1234567890'
        
        mock_acudiente = SimpleNamespace()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.persona = mock_persona
        
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_model.query = mock_query
            
            with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                mock_query_relacion = MagicMock()
                mock_query_relacion.filter_by.return_value.all.return_value = [mock_relacion]
                mock_relacion_model.query = mock_query_relacion
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    # Act
                    response = client.get('/api/deportistas/1/acudientes')
                    
                    # Assert
                    assert_success_response(response)
                    data = response.get_json()
                    assert isinstance(data.get('data'), list)
                    assert len(data.get('data')) == 1
                    acudiente_data = data.get('data')[0]
                    assert acudiente_data.get('id_acudiente') == 1
                    assert acudiente_data.get('nombre_completo') == 'Juan Pérez'
                    assert acudiente_data.get('parentesco') == 'Padre'
                    assert acudiente_data.get('es_responsable') is True
                    assert 'persona' in acudiente_data

    def test_obtener_acudientes_exception_generica(self, client, mock_token_required):
        """Test: Exception genérica en obtener_acudientes_por_deportista (línea 724-727)."""
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
            mock_query = MagicMock()
            mock_query.filter_by.side_effect = Exception("Error inesperado")
            mock_deportista_model.query = mock_query
            
            # Act
            response = client.get('/api/deportistas/1/acudientes')
            
            # Assert
            assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestObtenerDeportistasPorAcudienteCoverage:
    """Tests para aumentar cobertura de obtener_deportistas_por_acudiente endpoint."""

    def test_obtener_deportistas_id_invalido(self, client, mock_token_required):
        """Test: ID de acudiente inválido (línea 632-637)."""
        # Act
        response = client.get('/api/deportistas/acudientes/0/deportistas')
        
        # Assert
        assert_error_response(response, expected_status=400)

    def test_obtener_deportistas_sin_relaciones(self, client, mock_token_required):
        """Test: No hay relaciones (línea 642-647)."""
        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = []
            mock_relacion_model.query = mock_query
            
            # Act
            response = client.get('/api/deportistas/acudientes/1/deportistas')
            
            # Assert
            assert_success_response(response)
            data = response.get_json()
            assert data.get('data') == []

    def test_obtener_deportistas_con_deportistas_sin_persona(self, client, mock_token_required):
        """Test: Relaciones con deportistas sin persona (línea 656-658)."""
        from types import SimpleNamespace
        
        mock_relacion = MagicMock()
        mock_relacion.id_deportista = 1
        mock_relacion.id_acudiente = 1
        
        # Crear objeto simple sin atributo 'persona' para que getattr devuelva None
        mock_deportista_sin_persona = SimpleNamespace()
        mock_deportista_sin_persona.id_deportista = 1
        # No agregamos el atributo 'persona', así que getattr(deportista, "persona", None) devolverá None
        
        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_relacion]
            mock_relacion_model.query = mock_query
            
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista_sin_persona
                mock_deportista_model.query = mock_query_deportista
                
                # Act
                response = client.get('/api/deportistas/acudientes/1/deportistas')
                
                # Assert
                # Debe continuar y no agregar deportistas sin persona
                assert_success_response(response)
                data = response.get_json()
                assert isinstance(data.get('data'), list)
                assert len(data.get('data')) == 0  # No debe incluir el deportista sin persona

    def test_obtener_deportistas_deportista_no_encontrado(self, client, mock_token_required):
        """Test: Deportista no encontrado en relación (línea 653-655)."""
        mock_relacion = MagicMock()
        mock_relacion.id_deportista = 999
        mock_relacion.id_acudiente = 1
        
        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_relacion]
            mock_relacion_model.query = mock_query
            
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = None
                mock_deportista_model.query = mock_query_deportista
                
                # Act
                response = client.get('/api/deportistas/acudientes/1/deportistas')
                
                # Assert
                # Debe continuar y no agregar deportistas no encontrados
                assert_success_response(response)
                data = response.get_json()
                assert isinstance(data.get('data'), list)
                assert len(data.get('data')) == 0  # No debe incluir deportistas no encontrados

    def test_obtener_deportistas_exception_generica(self, client, mock_token_required):
        """Test: Exception genérica en obtener_deportistas_por_acudiente (línea 846-849)."""
        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
            mock_query = MagicMock()
            mock_query.filter_by.side_effect = Exception("Error inesperado")
            mock_relacion_model.query = mock_query
            
            # Act
            response = client.get('/api/deportistas/acudientes/1/deportistas')
            
            # Assert
            assert_error_response(response, expected_status=500)

    def test_obtener_deportistas_success_with_persona(self, client, mock_token_required):
        """Test: Obtener deportistas exitosamente cuando tienen persona (línea 659-661)."""
        from types import SimpleNamespace
        
        mock_relacion = MagicMock()
        mock_relacion.id_deportista = 1
        mock_relacion.id_acudiente = 1
        
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        
        mock_deportista = SimpleNamespace()
        mock_deportista.id_deportista = 1
        mock_deportista.persona = mock_persona  # Tiene persona
        
        mock_serialized_data = {
            'id_deportista': 1,
            'nombre_completo': 'Juan Pérez'
        }
        
        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_relacion]
            mock_relacion_model.query = mock_query
            
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.routes.deportistas_routes._serialize_deportista') as mock_serialize:
                    mock_serialize.return_value = mock_serialized_data
                    
                    # Act
                    response = client.get('/api/deportistas/acudientes/1/deportistas')
                    
                    # Assert
                    assert_success_response(response)
                    data = response.get_json()
                    assert isinstance(data.get('data'), list)
                    assert len(data.get('data')) == 1  # Debe incluir el deportista con persona
                    assert data.get('data')[0] == mock_serialized_data


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestBuscarDeportistaPorDocumentoCoverage:
    """Tests para aumentar cobertura de buscar_deportista_por_documento_para_acudiente endpoint."""

    def test_buscar_deportista_documento_vacio(self, client, mock_token_required):
        """Test: Documento vacío (línea 840-845)."""
        # Act
        response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=')
        
        # Assert
        assert_error_response(response, expected_status=400)

    def test_buscar_deportista_persona_no_encontrada(self, client, mock_token_required):
        """Test: Persona no encontrada (línea 854-856)."""
        from flask import Response
        from src.utils.http_responses import HttpResponseBuilder
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        # Crear una respuesta mock que simula HttpResponseBuilder.success con status 200
        mock_error_response = HttpResponseBuilder.success(
            data=None,
            encontrado=False,
            message='No encontramos una persona registrada con ese número de documento.'
        )
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.routes.deportistas_routes._buscar_persona_por_documento_multiple') as mock_buscar:
                    mock_buscar.return_value = (None, mock_error_response)  # Persona no encontrada con respuesta success
                    
                    # Act
                    response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                    
                    # Assert - La función helper retorna success (200) con encontrado=False
                    assert_success_response(response)
                    data = response.get_json()
                    assert data.get('encontrado') is False

    def test_buscar_deportista_sin_rol_deportista(self, client, mock_token_required):
        """Test: Persona sin rol deportista (línea 858-861)."""
        from flask import Response
        from src.utils.http_responses import HttpResponseBuilder
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        # Crear una respuesta mock que simula HttpResponseBuilder.success con status 200
        mock_error_response = HttpResponseBuilder.success(
            data=None,
            encontrado=False,
            message='La persona encontrada no tiene el rol de Deportista.'
        )
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.routes.deportistas_routes._buscar_persona_por_documento_multiple') as mock_buscar:
                    mock_buscar.return_value = (mock_persona, None)
                    
                    with patch('src.routes.deportistas_routes._verificar_rol_deportista') as mock_verificar:
                        mock_verificar.return_value = (False, mock_error_response)  # Sin rol deportista
                        
                        # Act
                        response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                        
                        # Assert - La función helper retorna success (200) con encontrado=False
                        assert_success_response(response)
                        data = response.get_json()
                        assert data.get('encontrado') is False

    def test_buscar_deportista_ya_asociado(self, client, mock_token_required):
        """Test: Deportista ya está asociado (línea 876-882)."""
        from types import SimpleNamespace
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        # Crear persona con atributos necesarios para _construir_datos_deportista
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.documento = '12345678'
        mock_persona.estado = True
        
        # Crear deportista con atributos necesarios
        mock_deportista = SimpleNamespace()
        mock_deportista.id_deportista = 1
        mock_deportista.categoria = None
        
        mock_relacion_existente = MagicMock()
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.routes.deportistas_routes._buscar_persona_por_documento_multiple') as mock_buscar:
                    mock_buscar.return_value = (mock_persona, None)
                    
                    with patch('src.routes.deportistas_routes._verificar_rol_deportista') as mock_verificar:
                        mock_verificar.return_value = (True, None)
                        
                        with patch('src.routes.deportistas_routes._obtener_deportista_con_categoria') as mock_obtener:
                            mock_obtener.return_value = (mock_deportista, None)
                            
                            with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                                mock_query_relacion = MagicMock()
                                mock_query_relacion.filter_by.return_value.first.return_value = mock_relacion_existente
                                mock_relacion_model.query = mock_query_relacion
                                
                                # Act
                                response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                                
                                # Assert
                                assert_success_response(response)
                                data = response.get_json()
                                assert data.get('ya_acudido') is True
                                assert data.get('encontrado') is False

    def test_buscar_deportista_disponible(self, client, mock_token_required):
        """Test: Deportista disponible para asociar (línea 884-888)."""
        from types import SimpleNamespace
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        # Crear persona con atributos necesarios para _construir_datos_deportista
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.documento = '12345678'
        mock_persona.estado = True
        
        # Crear deportista con atributos necesarios
        mock_deportista = SimpleNamespace()
        mock_deportista.id_deportista = 1
        mock_deportista.categoria = None
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.routes.deportistas_routes._buscar_persona_por_documento_multiple') as mock_buscar:
                    mock_buscar.return_value = (mock_persona, None)
                    
                    with patch('src.routes.deportistas_routes._verificar_rol_deportista') as mock_verificar:
                        mock_verificar.return_value = (True, None)
                        
                        with patch('src.routes.deportistas_routes._obtener_deportista_con_categoria') as mock_obtener:
                            mock_obtener.return_value = (mock_deportista, None)
                            
                            with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                                mock_query_relacion = MagicMock()
                                mock_query_relacion.filter_by.return_value.first.return_value = None
                                mock_relacion_model.query = mock_query_relacion
                                
                                # Act
                                response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                                
                                # Assert
                                assert_success_response(response)
                                data = response.get_json()
                                assert data.get('encontrado') is True
                                assert data.get('ya_acudido') is not True

    def test_buscar_deportista_error_obtener_acudiente(self, client, mock_token_required):
        """Test: Error al obtener acudiente desde usuario (línea 1028)."""
        from src.utils.http_responses import HttpResponseBuilder
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {}  # Sin persona válida
        }
        
        mock_error_response = HttpResponseBuilder.unauthorized(
            error='Usuario no autenticado',
            message='Debes estar autenticado para realizar esta búsqueda'
        )
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes._obtener_acudiente_desde_usuario') as mock_obtener:
                mock_obtener.return_value = (None, mock_error_response)
                
                # Act
                response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                
                # Assert
                assert_error_response(response, expected_status=401)

    def test_buscar_deportista_error_obtener_deportista(self, client, mock_token_required):
        """Test: Error al obtener deportista con categoría (línea 1043)."""
        from src.utils.http_responses import HttpResponseBuilder
        from types import SimpleNamespace
        
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        
        mock_error_response = HttpResponseBuilder.success(
            data=None,
            encontrado=False,
            message='No encontramos un deportista asociado a esta persona.'
        )
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_acudiente
                mock_acudiente_model.query = mock_query
                
                with patch('src.routes.deportistas_routes._buscar_persona_por_documento_multiple') as mock_buscar:
                    mock_buscar.return_value = (mock_persona, None)
                    
                    with patch('src.routes.deportistas_routes._verificar_rol_deportista') as mock_verificar:
                        mock_verificar.return_value = (True, None)
                        
                        with patch('src.routes.deportistas_routes._obtener_deportista_con_categoria') as mock_obtener:
                            mock_obtener.return_value = (None, mock_error_response)
                            
                            # Act
                            response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
                            
                            # Assert
                            assert_success_response(response)
                            data = response.get_json()
                            assert data.get('encontrado') is False

    def test_buscar_deportista_exception_generica(self, client, mock_token_required):
        """Test: Exception genérica en buscar_deportista_por_documento_para_acudiente (línea 1067-1070)."""
        with patch('src.routes.deportistas_routes._validar_documento_busqueda',
                  side_effect=Exception("Error inesperado")):
            # Act
            response = client.get('/api/deportistas/acudientes/buscar-deportista?documento=12345678')
            
            # Assert
            assert_error_response(response, expected_status=500)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestActualizarDeportistaCoverage:
    """Tests para aumentar cobertura de actualizar_deportista endpoint."""

    def test_actualizar_deportista_sin_autenticacion(self, client):
        """Test: Usuario no autenticado (línea 965-968)."""
        with patch('src.routes.deportistas_routes.get_current_user', return_value=None):
            # Act
            response = make_json_request(
                client, 'PUT', '/api/deportistas/1',
                data={}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)

    def test_actualizar_deportista_metodo_antiguo(self, client, mock_token_required):
        """Test: Usar método antiguo cuando no hay secciones (línea 977-979)."""
        mock_usuario = {'id_usuario': 1}
        
        mock_result = {
            'success': True,
            'data': {'id_deportista': 1},
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.DeportistaService.actualizar_deportista') as mock_actualizar:
                mock_actualizar.return_value = mock_result
                
                # Act - Con datos pero sin secciones específicas (para usar método antiguo)
                # Necesitamos enviar un JSON válido, pero sin las secciones que activan el método completo
                response = make_json_request(
                    client, 'PUT', '/api/deportistas/1',
                    data={'campo_cualquiera': 'valor'}  # Datos válidos pero sin secciones específicas
                )
                
                # Assert
                assert_success_response(response)
                mock_actualizar.assert_called_once()

    def test_actualizar_deportista_metodo_completo(self, client, mock_token_required):
        """Test: Usar método completo con secciones (línea 981-989)."""
        mock_usuario = {'id_usuario': 1}
        
        mock_result = {
            'success': True,
            'data': {'id_deportista': 1},
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.DeportistaService.actualizar_deportista_completo') as mock_actualizar:
                mock_actualizar.return_value = mock_result
                
                # Act - Con sección de datos_deportista
                response = make_json_request(
                    client, 'PUT', '/api/deportistas/1',
                    data={
                        'datos_deportista': {'peso': 70}
                    }
                )
                
                # Assert
                assert_success_response(response)
                mock_actualizar.assert_called_once()

    def test_actualizar_deportista_exception(self, client, mock_token_required):
        """Test: Manejo de excepciones generales (línea 995-998)."""
        mock_usuario = {'id_usuario': 1}
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.routes.deportistas_routes.DeportistaService.actualizar_deportista',
                       side_effect=Exception("Error inesperado")):
                # Act - Necesitamos datos válidos para pasar obtener_json_requerido
                response = make_json_request(
                    client, 'PUT', '/api/deportistas/1',
                    data={'campo': 'valor'}  # Datos válidos para pasar la validación
                )
                
                # Assert - El exception handler debería retornar 500
                assert_error_response(response, expected_status=500)

    def test_actualizar_deportista_usuario_no_autenticado(self, client, mock_token_required):
        """Test: Usuario no autenticado en actualizar_deportista (línea 1143-1146)."""
        # El mock_token_required permite que el decorador pase, pero necesitamos
        # que get_current_user retorne None dentro de la función
        # Necesitamos parchear get_current_user para que retorne None
        # y también limpiar g.current_user después de que el decorador lo haya configurado
        from flask import g
        
        # Función que limpia g.current_user y retorna None
        def get_current_user_none():
            # Limpiar g.current_user si existe
            if hasattr(g, 'current_user'):
                delattr(g, 'current_user')
            return None
        
        with patch('src.routes.deportistas_routes.get_current_user', side_effect=get_current_user_none):
            # Act
            response = make_json_request(
                client, 'PUT', '/api/deportistas/1',
                data={'datos_deportista': {}}
            )
            
            # Assert
            assert_error_response(response, expected_status=401)
            data = response.get_json()
            # Verificar que se ejecutó la línea 1143-1145
            assert 'Usuario no autenticado' in data.get('message', '') or 'Usuario no autenticado' in str(data)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestAsociarAcudienteADeportistaCoverage:
    """Tests para aumentar cobertura de asociar_acudiente_a_deportista endpoint."""

    def test_asociar_acudiente_a_deportista_usuario_no_encontrado(self, client, mock_token_required):
        """Test: Usuario no encontrado en contexto (línea 513-514)."""
        # Arrange
        with patch('src.routes.deportistas_routes.get_current_user', return_value=None):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                data={
                    'id_acudiente': 1,
                    'id_parentesco': 1,
                    'es_responsable': False
                }
            )
            
            # Assert
            assert_error_response(response, expected_status=401)
            data = response.get_json()
            assert 'Usuario no encontrado en el contexto' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_acudiente_no_existe(self, client, mock_token_required):
        """Test: Acudiente no existe (línea 559)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = None
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    # Act
                    response = make_json_request(
                        client, 'POST', '/api/deportistas/1/acudientes/asociar',
                        data={
                            'id_acudiente': 999,
                            'id_parentesco': 1,
                            'es_responsable': False
                        }
                    )
                    
                    # Assert
                    assert_error_response(response, expected_status=404)
                    data = response.get_json()
                    assert 'No se encontró un acudiente con ID' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_sin_id_acudiente(self, client, mock_token_required):
        """Test: Falta id_acudiente (línea 524-528)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                data={
                    'id_parentesco': 1,
                    'es_responsable': False
                }  # Sin id_acudiente
            )
            
            # Assert
            assert_error_response(response, expected_status=400)
            data = response.get_json()
            assert 'Se requiere id_acudiente' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_sin_id_parentesco(self, client, mock_token_required):
        """Test: Falta id_parentesco (línea 530-534)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            # Act
            response = make_json_request(
                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                data={
                    'id_acudiente': 1,
                    'es_responsable': False
                }  # Sin id_parentesco
            )
            
            # Assert
            assert_error_response(response, expected_status=400)
            data = response.get_json()
            assert 'Se requiere id_parentesco' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_deportista_no_existe(self, client, mock_token_required):
        """Test: Deportista no existe (línea 543-548)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = None
                mock_deportista_model.query = mock_query_deportista
                
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/999/acudientes/asociar',
                    data={
                        'id_acudiente': 1,
                        'id_parentesco': 1,
                        'es_responsable': False
                    }
                )
                
                # Assert
                assert_error_response(response, expected_status=404)
                data = response.get_json()
                assert 'No se encontró un deportista con ID' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_usuario_no_es_dueno(self, client, mock_token_required):
        """Test: Usuario no es dueño del deportista (línea 552-556)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 2  # Diferente al usuario
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                # Act
                response = make_json_request(
                    client, 'POST', '/api/deportistas/1/acudientes/asociar',
                    data={
                        'id_acudiente': 1,
                        'id_parentesco': 1,
                        'es_responsable': False
                    }
                )
                
                # Assert
                assert_error_response(response, expected_status=403)
                data = response.get_json()
                assert 'Solo puedes asociar acudientes a tu propio perfil de deportista' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_auto_asociacion(self, client, mock_token_required):
        """Test: Deportista intenta acudirse a sí mismo (línea 567-571)."""
        # Arrange
        id_persona = 1
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': id_persona}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = id_persona
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = id_persona  # Mismo id_persona
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    # Act
                    response = make_json_request(
                        client, 'POST', '/api/deportistas/1/acudientes/asociar',
                        data={
                            'id_acudiente': 1,
                            'id_parentesco': 1,
                            'es_responsable': False
                        }
                    )
                    
                    # Assert
                    assert_error_response(response, expected_status=400)
                    data = response.get_json()
                    assert 'Un deportista no puede acudirse a sí mismo' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_parentesco_no_existe(self, client, mock_token_required):
        """Test: Parentesco no existe (línea 574-579)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 2
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = None
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        # Act
                        response = make_json_request(
                            client, 'POST', '/api/deportistas/1/acudientes/asociar',
                            data={
                                'id_acudiente': 1,
                                'id_parentesco': 999,
                                'es_responsable': False
                            }
                        )
                        
                        # Assert
                        assert_error_response(response, expected_status=404)
                        data = response.get_json()
                        assert 'No se encontró un parentesco con ID' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_relacion_duplicada(self, client, mock_token_required):
        """Test: Relación ya existe (línea 587-591)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        mock_relacion_existente = MagicMock()
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by.return_value.first.return_value = mock_relacion_existente
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                                data={
                                    'id_acudiente': 1,
                                    'id_parentesco': 1,
                                    'es_responsable': False
                                }
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)
                            data = response.get_json()
                            assert 'Ya existe una relación entre este acudiente y este deportista' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_limite_deportista_excedido(self, client, mock_token_required):
        """Test: Deportista ya tiene 3 acudientes (línea 598-603)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Configurar las queries de manera más explícita
                            # Query 1: Verificar si existe la relación (debe retornar None)
                            mock_query_check = MagicMock()
                            mock_query_check.first.return_value = None
                            
                            # Query 2: Contar deportistas del acudiente (debe retornar 2, menos de 3)
                            mock_query_count_acudiente = MagicMock()
                            mock_query_count_acudiente.count.return_value = 2
                            
                            # Query 3: Contar acudientes del deportista (debe retornar 3, igual o mayor a 3)
                            mock_query_count_deportista = MagicMock()
                            mock_query_count_deportista.count.return_value = 3
                            
                            # Configurar filter_by para devolver la query apropiada según los kwargs
                            def filter_by_side_effect(**kwargs):
                                # Si es para verificar existencia de relación (tiene ambos)
                                if 'id_deportista' in kwargs and 'id_acudiente' in kwargs:
                                    return mock_query_check
                                # Si es para contar deportistas del acudiente (solo id_acudiente)
                                elif 'id_acudiente' in kwargs and 'id_deportista' not in kwargs:
                                    return mock_query_count_acudiente
                                # Si es para contar acudientes del deportista (solo id_deportista)
                                elif 'id_deportista' in kwargs and 'id_acudiente' not in kwargs:
                                    return mock_query_count_deportista
                                return mock_query_check
                            
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by = MagicMock(side_effect=filter_by_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                                data={
                                    'id_acudiente': 1,
                                    'id_parentesco': 1,
                                    'es_responsable': False
                                }
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)
                            data = response.get_json()
                            assert 'Un deportista solo puede estar asociado a máximo 3 acudientes' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_limite_acudiente_excedido(self, client, mock_token_required):
        """Test: Acudiente ya tiene 3 deportistas (línea 610-615)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Configurar las queries de manera más explícita
                            # Query 1: Verificar si existe la relación (debe retornar None)
                            mock_query_check = MagicMock()
                            mock_query_check.first.return_value = None
                            
                            # Query 2: Contar deportistas del acudiente (debe retornar 3, igual o mayor a 3)
                            mock_query_count_acudiente = MagicMock()
                            mock_query_count_acudiente.count.return_value = 3
                            
                            # Query 3: Contar acudientes del deportista (debe retornar 2, menos de 3)
                            mock_query_count_deportista = MagicMock()
                            mock_query_count_deportista.count.return_value = 2
                            
                            # Configurar filter_by para devolver la query apropiada según los kwargs
                            def filter_by_side_effect(**kwargs):
                                # Si es para verificar existencia de relación (tiene ambos)
                                if 'id_deportista' in kwargs and 'id_acudiente' in kwargs:
                                    return mock_query_check
                                # Si es para contar deportistas del acudiente (solo id_acudiente)
                                elif 'id_acudiente' in kwargs and 'id_deportista' not in kwargs:
                                    return mock_query_count_acudiente
                                # Si es para contar acudientes del deportista (solo id_deportista)
                                elif 'id_deportista' in kwargs and 'id_acudiente' not in kwargs:
                                    return mock_query_count_deportista
                                return mock_query_check
                            
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by = MagicMock(side_effect=filter_by_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Act
                            response = make_json_request(
                                client, 'POST', '/api/deportistas/1/acudientes/asociar',
                                data={
                                    'id_acudiente': 1,
                                    'id_parentesco': 1,
                                    'es_responsable': False
                                }
                            )
                            
                            # Assert
                            assert_error_response(response, expected_status=400)
                            data = response.get_json()
                            assert 'Un acudiente solo puede estar asociado a máximo 3 deportistas' in data.get('message', '')

    def test_asociar_acudiente_a_deportista_success(self, client, mock_token_required):
        """Test: Asociación exitosa (línea 617-641)."""
        # Arrange
        mock_usuario = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 2
        
        mock_parentesco = MagicMock()
        mock_parentesco.id_parentesco = 1
        
        mock_relacion_nueva = MagicMock()
        mock_relacion_nueva.id_deportista_acudiente = 1
        mock_relacion_nueva.id_deportista = 1
        mock_relacion_nueva.id_acudiente = 1
        mock_relacion_nueva.id_parentesco = 1
        mock_relacion_nueva.es_responsable = False
        mock_relacion_nueva.fecha_registro = date.today()
        
        with patch('src.routes.deportistas_routes.get_current_user', return_value=mock_usuario):
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model:
                mock_query_deportista = MagicMock()
                mock_query_deportista.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_model.query = mock_query_deportista
                
                with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
                    mock_query_acudiente = MagicMock()
                    mock_query_acudiente.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_model.query = mock_query_acudiente
                    
                    with patch('src.models.acudientes.parentesco.Parentesco') as mock_parentesco_model:
                        mock_query_parentesco = MagicMock()
                        mock_query_parentesco.filter_by.return_value.first.return_value = mock_parentesco
                        mock_parentesco_model.query = mock_query_parentesco
                        
                        with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente') as mock_relacion_model:
                            # Configurar las queries
                            def filter_by_side_effect(**kwargs):
                                # Si es para verificar existencia de relación (tiene ambos)
                                if 'id_deportista' in kwargs and 'id_acudiente' in kwargs:
                                    return MagicMock(first=MagicMock(return_value=None))
                                # Si es para contar deportistas del acudiente (solo id_acudiente)
                                elif 'id_acudiente' in kwargs and 'id_deportista' not in kwargs:
                                    return MagicMock(count=MagicMock(return_value=2))
                                # Si es para contar acudientes del deportista (solo id_deportista)
                                elif 'id_deportista' in kwargs and 'id_acudiente' not in kwargs:
                                    return MagicMock(count=MagicMock(return_value=2))
                                return MagicMock(first=MagicMock(return_value=None))
                            
                            mock_query_relacion = MagicMock()
                            mock_query_relacion.filter_by = MagicMock(side_effect=filter_by_side_effect)
                            mock_relacion_model.query = mock_query_relacion
                            
                            # Configurar el constructor para que retorne el objeto mock
                            mock_relacion_model.return_value = mock_relacion_nueva
                            
                            # Parchear db
                            with patch('src.routes.deportistas_routes.db') as mock_db:
                                mock_db.session.add = MagicMock()
                                mock_db.session.commit = MagicMock()
                                
                                with patch('src.models.base.db', mock_db):
                                    # Act
                                    response = make_json_request(
                                        client, 'POST', '/api/deportistas/1/acudientes/asociar',
                                        data={
                                            'id_acudiente': 1,
                                            'id_parentesco': 1,
                                            'es_responsable': False
                                        }
                                    )
                                    
                                    # Assert
                                    assert_success_response(response, expected_status=201)
                                    data = response.get_json()
                                    assert data.get('data') is not None
                                    assert data.get('data').get('id_deportista') == 1
                                    assert data.get('data').get('id_acudiente') == 1


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.deportistas
class TestCatalogosDeportistasCoverage:
    """Tests para aumentar cobertura de endpoints de catálogos."""

    def test_catalogo_ciudades_residencia(self, client):
        """Test: Obtener catálogo de ciudades de residencia (línea 1249-1251)."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [{'id_ciudad': 1, 'nombre': 'Bogotá'}],
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.CatalogosService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.obtener_ciudades_residencia.return_value = mock_result
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.get('/api/deportistas/catalogos/ciudades-residencia')
            
            # Assert
            assert_success_response(response)

    def test_catalogo_eps(self, client):
        """Test: Obtener catálogo de EPS (línea 1265-1267)."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [{'id_eps': 1, 'nombre': 'EPS Test'}],
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.CatalogosService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.obtener_eps.return_value = mock_result
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.get('/api/deportistas/catalogos/eps')
            
            # Assert
            assert_success_response(response)

    def test_catalogo_escuelas(self, client):
        """Test: Obtener catálogo de escuelas (línea 1297-1298)."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [{'id_escuela': 1, 'nombre': 'Escuela Test'}],
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.CatalogosService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.obtener_escuelas.return_value = mock_result
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.get('/api/deportistas/catalogos/escuelas')
            
            # Assert
            assert_success_response(response)

    def test_catalogo_instituciones_registro(self, client):
        """Test: Obtener catálogo de instituciones de registro (línea 1313-1314)."""
        # Arrange
        mock_result = {
            'success': True,
            'data': [{'id_institucion': 1, 'nombre': 'Institución Test'}],
            'status_code': 200
        }
        
        with patch('src.routes.deportistas_routes.CatalogosService') as mock_service_class:
            mock_service = MagicMock()
            mock_service.obtener_instituciones_registro.return_value = mock_result
            mock_service_class.return_value = mock_service
            
            # Act
            response = client.get('/api/deportistas/catalogos/instituciones-registro')
            
            # Assert
            assert_success_response(response)