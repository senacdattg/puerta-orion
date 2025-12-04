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

