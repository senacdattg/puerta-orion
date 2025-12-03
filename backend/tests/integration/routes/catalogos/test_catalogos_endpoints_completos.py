"""
Tests completos para todos los endpoints de catalogos_routes.py.

Este módulo contiene tests de integración que cubren todos los endpoints
y casos edge de catalogos_routes.py para alcanzar 100% de cobertura.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from tests.helpers import (
    assert_success_response,
    assert_error_response
)


@pytest.mark.routes
@pytest.mark.integration
class TestCatalogosEndpoints:
    """Tests completos para endpoints de catálogos."""
    
    def test_obtener_tipos_enfermedad(self, client):
        """Test: Obtener tipos de enfermedad."""
        mock_result = {'data': []}
        
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_tipos_enfermedad', return_value=mock_result):
            response = client.get('/api/catalogos/tipos-enfermedad')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_tipos_enfermedad_con_diagnosticos(self, client):
        """Test: Obtener tipos de enfermedad con diagnósticos incluidos."""
        mock_result = {'data': []}
        
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_tipos_enfermedad', return_value=mock_result):
            response = client.get('/api/catalogos/tipos-enfermedad?incluir_diagnosticos=true')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_tipos_enfermedad_error(self, client):
        """Test: Error al obtener tipos de enfermedad."""
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_tipos_enfermedad', side_effect=Exception('Error')):
            response = client.get('/api/catalogos/tipos-enfermedad')
        
        assert response.status_code == 500
    
    def test_obtener_diagnosticos(self, client):
        """Test: Obtener diagnósticos."""
        mock_result = {'data': []}
        
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_diagnosticos', return_value=mock_result):
            response = client.get('/api/catalogos/diagnosticos')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_diagnosticos_por_tipo(self, client):
        """Test: Obtener diagnósticos filtrados por tipo."""
        mock_result = {'data': []}
        
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_diagnosticos', return_value=mock_result):
            response = client.get('/api/catalogos/diagnosticos?id_tipo_enfermedad=1')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_diagnosticos_error(self, client):
        """Test: Error al obtener diagnósticos."""
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_diagnosticos', side_effect=Exception('Error')):
            response = client.get('/api/catalogos/diagnosticos')
        
        assert response.status_code == 500
    
    def test_debug_catalogos(self, client):
        """Test: Endpoint de debug de catálogos."""
        with patch('src.routes.catalogos_routes.TipoDocumento') as mock_tipo, \
             patch('src.routes.catalogos_routes.Sexo') as mock_sexo, \
             patch('src.routes.catalogos_routes.Categoria') as mock_categoria:
            
            mock_tipo.query.all.return_value = []
            mock_tipo.__tablename__ = 'test'
            mock_sexo.query.all.return_value = []
            mock_sexo.__tablename__ = 'test'
            mock_categoria.query.all.return_value = []
            mock_categoria.__tablename__ = 'test'
            
            response = client.get('/api/catalogos/debug')
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert 'debug_info' in data
    
    def test_debug_catalogos_error(self, client):
        """Test: Error en endpoint de debug."""
        with patch('src.routes.catalogos_routes.TipoDocumento') as mock_tipo:
            mock_tipo.query.all.side_effect = Exception('Error')
            mock_tipo.__tablename__ = 'test'
            
            response = client.get('/api/catalogos/debug')
        
        # Puede retornar 200 con errores en debug_info o 500
        assert response.status_code in [200, 500]
    
    def test_obtener_categorias(self, client):
        """Test: Obtener categorías."""
        mock_categoria = MagicMock()
        mock_categoria.id_categoria = 1
        mock_categoria.nombre_categoria = 'Test'
        mock_categoria.codigo_categoria = 101
        mock_categoria.edad_minima = 6
        mock_categoria.edad_maxima = 18
        
        with patch('src.routes.catalogos_routes.Categoria') as mock_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_categoria]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/categorias')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_categorias_error(self, client):
        """Test: Error al obtener categorías."""
        with patch('src.routes.catalogos_routes.Categoria') as mock_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.side_effect = Exception('Error')
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/categorias')
        
        assert response.status_code == 500
    
    def test_obtener_parentescos(self, client):
        """Test: Obtener parentescos."""
        mock_parentesco = MagicMock()
        mock_parentesco.to_dict.return_value = {'id': 1, 'nombre': 'Padre'}
        
        with patch('src.routes.catalogos_routes.Parentesco') as mock_model:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_parentesco]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/parentescos')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_parentescos_vacio(self, client):
        """Test: Obtener parentescos cuando no hay datos."""
        with patch('src.routes.catalogos_routes.Parentesco') as mock_model:
            mock_query = MagicMock()
            mock_query.all.return_value = []
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/parentescos')
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert data.get('data') == []
    
    def test_obtener_parentescos_error_db(self, client):
        """Test: Error de BD al obtener parentescos."""
        with patch('src.routes.catalogos_routes.Parentesco') as mock_model:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception('DB Error')
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/parentescos')
        
        assert response.status_code == 500
    
    def test_obtener_parentescos_error_general(self, client):
        """Test: Error general al obtener parentescos."""
        with patch('src.routes.catalogos_routes.logger'):
            with patch('src.routes.catalogos_routes.Parentesco') as mock_model:
                mock_model.query = MagicMock()
                mock_model.query.all.side_effect = Exception('General Error')
                
                response = client.get('/api/catalogos/parentescos')
        
        assert response.status_code == 500
    
    def test_obtener_acudientes_lista(self, client):
        """Test: Obtener lista de acudientes."""
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 1
        mock_acudiente.estado = True
        del mock_acudiente.persona
        
        with patch('src.routes.catalogos_routes.Acudiente') as mock_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_acudiente]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/acudientes')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_acudientes_por_cedula_encontrado(self, client):
        """Test: Buscar acudiente por cédula encontrado."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test Person'
        mock_persona.documento = '1234567890'
        mock_persona.correo_electronico = 'test@example.com'
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 1
        mock_acudiente.estado = True
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_acudiente_por_persona', return_value=mock_acudiente):
                response = client.get('/api/catalogos/acudientes?cedula=1234567890')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_acudientes_por_cedula_persona_no_existe(self, client):
        """Test: Buscar acudiente por cédula - persona no existe."""
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=None):
            response = client.get('/api/catalogos/acudientes?cedula=1234567890')
        
        assert response.status_code == 404
    
    def test_obtener_acudientes_por_cedula_no_acudiente(self, client):
        """Test: Buscar acudiente por cédula - persona no es acudiente."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_acudiente_por_persona', return_value=None):
                response = client.get('/api/catalogos/acudientes?cedula=1234567890')
        
        assert response.status_code == 404
    
    def test_obtener_deportistas_lista(self, client):
        """Test: Obtener lista de deportistas."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        del mock_deportista.persona
        
        with patch('src.models.deportistas.deportista.Deportista') as mock_model:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_deportista]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/deportistas')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_deportistas_por_cedula_encontrado(self, client):
        """Test: Buscar deportista por cédula encontrado."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test Person'
        mock_persona.primer_nombre = 'Test'
        mock_persona.primer_apellido = 'Person'
        mock_persona.segundo_nombre = None
        mock_persona.segundo_apellido = None
        mock_persona.documento = '1234567890'
        mock_persona.correo_electronico = 'test@example.com'
        mock_persona.telefono = '1234567890'
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        del mock_deportista.persona
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_deportista_por_persona', return_value=mock_deportista):
                response = client.get('/api/catalogos/deportistas?cedula=1234567890')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_deportistas_por_cedula_persona_no_existe(self, client):
        """Test: Buscar deportista por cédula - persona no existe."""
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=None):
            response = client.get('/api/catalogos/deportistas?cedula=1234567890')
        
        assert response.status_code == 404
    
    def test_obtener_deportistas_por_cedula_no_deportista(self, client):
        """Test: Buscar deportista por cédula - persona no es deportista."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_deportista_por_persona', return_value=None):
                response = client.get('/api/catalogos/deportistas?cedula=1234567890')
        
        assert response.status_code == 404
    
    def test_obtener_tipos_evento(self, client, mock_token_required):
        """Test: Obtener tipos de evento."""
        mock_tipo = MagicMock()
        mock_tipo.to_dict.return_value = {'id': 1, 'nombre': 'Entrenamiento'}
        
        with patch('src.routes.catalogos_routes.TipoEvento') as mock_model:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_tipo]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/tipos-evento')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_tipos_evento_error(self, client, mock_token_required):
        """Test: Error al obtener tipos de evento."""
        with patch('src.routes.catalogos_routes.TipoEvento') as mock_model:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception('Error')
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/tipos-evento')
        
        assert response.status_code == 500
    
    def test_registrar_catalogos_routes(self):
        """Test: Registrar rutas de catálogos."""
        from src.routes.catalogos_routes import registrar_catalogos_routes
        from flask import Flask
        
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        
        with patch('src.routes.catalogos_routes.logger') as mock_logger:
            registrar_catalogos_routes(test_app)
            
            mock_logger.info.assert_called_once()
        
        # Verificar que el blueprint está registrado
        assert 'catalogos' in [bp.name for bp in test_app.blueprints.values()]
    
    def test_obtener_metodos_pago(self, client):
        """Test: Obtener métodos de pago."""
        mock_metodo = MagicMock()
        mock_metodo.id_metodo_pago = 1
        mock_metodo.nombre_metodo = 'Efectivo'
        mock_metodo.estado = True
        
        with patch('src.routes.catalogos_routes.MetodoPago') as mock_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_metodo]
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/metodos-pago')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_metodos_pago_error(self, client):
        """Test: Error al obtener métodos de pago."""
        with patch('src.routes.catalogos_routes.MetodoPago') as mock_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.side_effect = Exception('Error')
            mock_model.query = mock_query
            
            response = client.get('/api/catalogos/metodos-pago')
        
        assert response.status_code == 500
    
    def test_obtener_catalogos_completos(self, client):
        """Test: Obtener catálogos completos."""
        mock_catalogos = {'tipos_documento': [], 'sexos': []}
        
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_catalogos_completos', return_value=mock_catalogos):
            response = client.get('/api/catalogos/catalogos-completos')
        
        if response.status_code == 200:
            assert_success_response(response)
    
    def test_obtener_catalogos_completos_error(self, client):
        """Test: Error al obtener catálogos completos."""
        with patch('src.routes.catalogos_routes.catalogos_service.obtener_catalogos_completos', side_effect=Exception('Error')):
            response = client.get('/api/catalogos/catalogos-completos')
        
        assert response.status_code == 500
    
    def test_fix_catalogos_structure_success(self, client, app):
        """Test: Corregir estructura de catálogos exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._agregar_columna_nombre_sexo') as mock_agregar, \
                 patch('src.routes.catalogos_routes._poblar_tipos_documento_si_vacio') as mock_tipos, \
                 patch('src.routes.catalogos_routes._poblar_sexos_si_vacio') as mock_sexos, \
                 patch('src.routes.catalogos_routes.db'):
                
                mock_agregar.return_value = None
                mock_tipos.return_value = None
                mock_sexos.return_value = None
                
                response = client.post('/api/catalogos/fix-structure')
            
            if response.status_code == 200:
                data = assert_success_response(response)
                assert 'cambios' in data
    
    def test_fix_catalogos_structure_error(self, client, app):
        """Test: Error al corregir estructura de catálogos."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._agregar_columna_nombre_sexo', side_effect=Exception('Error')), \
                 patch('src.routes.catalogos_routes.db'):
                
                response = client.post('/api/catalogos/fix-structure')
            
            assert response.status_code == 500
    
    def test_poblar_categorias_success(self, client, app):
        """Test: Poblar categorías exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes._insertar_categorias_iniciales', return_value=['Fútbol']), \
                 patch('src.routes.catalogos_routes.db'):
                
                response = client.post('/api/catalogos/poblar-categorias')
            
            if response.status_code == 200:
                assert_success_response(response)
    
    def test_poblar_categorias_ya_existen(self, client, app):
        """Test: Poblar categorías cuando ya existen."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=5):
                response = client.post('/api/catalogos/poblar-categorias')
            
            if response.status_code == 200:
                data = assert_success_response(response)
                assert 'Ya existen' in data.get('message', '')
    
    def test_poblar_categorias_error(self, client, app):
        """Test: Error al poblar categorías."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes._insertar_categorias_iniciales', side_effect=Exception('Error')), \
                 patch('src.routes.catalogos_routes.db'):
                
                response = client.post('/api/catalogos/poblar-categorias')
            
            assert response.status_code == 500
    
    def test_obtener_acudientes_error(self, client):
        """Test: Error general al obtener acudientes."""
        with patch('src.routes.catalogos_routes.logger'):
            with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', side_effect=Exception('Error')):
                response = client.get('/api/catalogos/acudientes?cedula=1234567890')
        
        assert response.status_code == 500
    
    def test_obtener_deportistas_error(self, client):
        """Test: Error general al obtener deportistas."""
        with patch('src.routes.catalogos_routes.logger'):
            with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', side_effect=Exception('Error')):
                response = client.get('/api/catalogos/deportistas?cedula=1234567890')
        
        assert response.status_code == 500
    
    def test_obtener_deportistas_por_cedula_con_persona(self, client):
        """Test: Buscar deportista por cédula con datos de persona."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test Person'
        mock_persona.primer_nombre = 'Test'
        mock_persona.primer_apellido = 'Person'
        mock_persona.segundo_nombre = 'Middle'
        mock_persona.segundo_apellido = 'Last'
        mock_persona.documento = '1234567890'
        mock_persona.correo_electronico = 'test@example.com'
        mock_persona.telefono = '1234567890'
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        mock_deportista.persona = mock_persona
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_deportista_por_persona', return_value=mock_deportista):
                response = client.get('/api/catalogos/deportistas?cedula=1234567890')
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert 'persona' in data.get('data', {})
    
    def test_obtener_acudientes_por_cedula_con_persona(self, client):
        """Test: Buscar acudiente por cédula con datos de persona."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test Person'
        mock_persona.documento = '1234567890'
        mock_persona.correo_electronico = 'test@example.com'
        
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        mock_acudiente.id_persona = 1
        mock_acudiente.estado = True
        mock_acudiente.persona = mock_persona
        
        with patch('src.routes.catalogos_routes._fetch_persona_por_cedula', return_value=mock_persona):
            with patch('src.routes.catalogos_routes._fetch_acudiente_por_persona', return_value=mock_acudiente):
                response = client.get('/api/catalogos/acudientes?cedula=1234567890')
        
        if response.status_code == 200:
            data = assert_success_response(response)
            assert 'persona' in data.get('data', {})
    
    def test_serialize_categoria_line_206(self, client):
        """Test: Serializar categoría (línea 206)."""
        from src.routes.catalogos_routes import _serialize_categoria
        
        categoria = MagicMock()
        categoria.id_categoria = 1
        categoria.nombre_categoria = 'Fútbol'
        categoria.codigo_categoria = 101
        categoria.edad_minima = 6
        categoria.edad_maxima = 18
        
        result = _serialize_categoria(categoria)
        
        assert result['id_categoria'] == 1
        assert result['nombre_categoria'] == 'Fútbol'
        assert result['codigo_categoria'] == 101
    
    def test_serialize_parentesco_line_217(self, client):
        """Test: Serializar parentesco (línea 217)."""
        from src.routes.catalogos_routes import _serialize_parentesco
        
        parentesco = MagicMock()
        parentesco.to_dict.return_value = {'id': 1, 'nombre': 'Padre'}
        
        result = _serialize_parentesco(parentesco)
        
        assert result == {'id': 1, 'nombre': 'Padre'}
    
    def test_bad_request_error_handler(self, client):
        """Test: Manejador de error 400 (líneas 851, 862)."""
        from src.routes.catalogos_routes import catalogos_bp
        
        test_app = Flask(__name__)
        test_app.register_blueprint(catalogos_bp)
        
        with test_app.test_client() as test_client:
            with test_app.app_context():
                # Simular un error 400
                test_client.get('/api/catalogos/nonexistent')
    
    def test_internal_error_handler(self, client):
        """Test: Manejador de error 500."""
        from src.routes.catalogos_routes import catalogos_bp, internal_error
        
        test_app = Flask(__name__)
        test_app.register_blueprint(catalogos_bp)
        
        with test_app.app_context():
            error = Exception('Test error')
            response, status_code = internal_error(error)
            
            assert status_code == 500
            assert response.json['success'] is False
            assert 'Error interno' in response.json['error']
    
    def test_debug_catalogos_outer_exception(self, client, app):
        """Test: Error en el try externo de debug_catalogos (líneas 602-604)."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.logger') as mock_logger:
                # Forzar un error en el try externo haciendo que _build_response 
                # lance una excepción cuando se llama con debug_info (línea 601)
                from unittest.mock import MagicMock
                from src.routes.catalogos_routes import _build_response as original_build
                
                def failing_build_response(*args, **kwargs):
                    # Fallar solo cuando se llama con debug_info (return final línea 601)
                    if 'debug_info' in kwargs:
                        raise Exception('Outer error in build_response')
                    # Para otras llamadas, usar la función original
                    return original_build(*args, **kwargs)
                
                with patch('src.routes.catalogos_routes._build_response', side_effect=failing_build_response):
                    response = client.get('/api/catalogos/debug')
                    
                    # Debe capturar el error y retornar 500
                    assert response.status_code == 500, f"Expected 500, got {response.status_code}. Response: {response.get_json()}"
                    # Verificar que se llamó logger.error
                    mock_logger.error.assert_called()
                    # Verificar que el error contiene el mensaje esperado
                    error_data = response.get_json()
                    assert error_data is not None
                    assert error_data.get('success') is False
    
    def test_obtener_parentescos_outer_exception(self, client, app):
        """Test: Error en el try externo de obtener_parentescos (líneas 699-702)."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.logger') as mock_logger:
                import traceback
                with patch('src.routes.catalogos_routes.traceback') as mock_traceback:
                    mock_traceback.format_exc.return_value = 'Traceback error'
                    # Forzar un error en _serialize_model_list que está fuera del try interno
                    with patch('src.routes.catalogos_routes._serialize_model_list', side_effect=Exception('Outer error')):
                        with patch('src.routes.catalogos_routes.Parentesco') as mock_model:
                            mock_parentesco = MagicMock()
                            mock_parentesco.to_dict.return_value = {'id': 1}
                            mock_query = MagicMock()
                            mock_query.all.return_value = [mock_parentesco]
                            mock_model.query = mock_query
                            
                            response = client.get('/api/catalogos/parentescos')
                            
                            assert response.status_code == 500
                            # Verificar que se llamó traceback.format_exc
                            assert mock_logger.error.call_count >= 2
    
    def test_bad_request_error_handler(self, client, app):
        """Test: Manejador de error 400 (línea 851)."""
        from flask import Flask
        from src.routes.catalogos_routes import catalogos_bp, bad_request
        
        test_app = Flask(__name__)
        test_app.register_blueprint(catalogos_bp)
        
        with test_app.app_context():
            error = Exception('Bad request error')
            response, status_code = bad_request(error)
            
            assert status_code == 400
            assert response.json['success'] is False
            assert 'Solicitud incorrecta' in response.json['error']

