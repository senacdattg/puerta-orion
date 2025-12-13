"""
Tests unitarios para funciones helper de catalogos_routes.py.

Este módulo contiene tests que verifican las funciones
auxiliares de catalogos_routes.py de forma aislada.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import os
from src.routes.catalogos_routes import (
    _get_cors_allowed_origins,
    _build_response,
    _serialize_model_list,
    _serialize_tipo_documento,
    _serialize_sexo,
    _serialize_metodo_pago,
    _serialize_categoria,
    _serialize_parentesco,
    _serialize_acudiente,
    _serialize_deportista,
    _handle_unexpected_error,
    _fetch_persona_por_cedula,
    _fetch_acudiente_por_persona,
    _fetch_deportista_por_persona,
    _parametro_es_true,
    _serialize_tipo_documento_debug,
    _serialize_sexo_debug,
    _serialize_categoria_debug,
    _obtener_debug_info,
    _consultar_pragma_table,
    _obtener_nombres_columnas,
    _contar_registros,
    _agregar_columna_nombre_sexo,
    _poblar_tipos_documento_si_vacio,
    _poblar_sexos_si_vacio,
    _insertar_categorias_iniciales,
    MAPEO_TIPOS_DOCUMENTO,
    MAPEO_SEXOS,
)


@pytest.mark.unit
class TestGetCorsAllowedOrigins:
    """Tests para _get_cors_allowed_origins."""
    
    def test_get_cors_allowed_origins_production_with_https(self):
        """Test: CORS origins en producción con HTTPS válidos."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production', 'CORS_ALLOWED_ORIGINS': 'https://example.com,https://app.example.com'}):
            result = _get_cors_allowed_origins()
            assert 'https://example.com' in result
            assert 'https://app.example.com' in result
    
    def test_get_cors_allowed_origins_production_with_http_ignored(self):
        """Test: CORS origins HTTP ignorados en producción."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production', 'CORS_ALLOWED_ORIGINS': 'http://example.com,https://app.example.com'}):
            result = _get_cors_allowed_origins()
            assert 'http://example.com' not in result
            assert 'https://app.example.com' in result
    
    def test_get_cors_allowed_origins_production_no_https_raises(self):
        """Test: Error cuando no hay HTTPS origins en producción."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production', 'CORS_ALLOWED_ORIGINS': 'http://example.com'}):
            with pytest.raises(ValueError) as exc_info:
                _get_cors_allowed_origins()
            assert 'HTTPS origin' in str(exc_info.value)
    
    def test_get_cors_allowed_origins_production_no_env_var_raises(self):
        """Test: Error cuando falta CORS_ALLOWED_ORIGINS en producción."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}, clear=True):
            with patch.dict(os.environ, {}, clear=False):
                os.environ.pop('CORS_ALLOWED_ORIGINS', None)
                with pytest.raises(ValueError) as exc_info:
                    _get_cors_allowed_origins()
                assert 'CORS_ALLOWED_ORIGINS' in str(exc_info.value)
    
    def test_get_cors_allowed_origins_development_with_env_var(self):
        """Test: CORS origins en desarrollo con variable de entorno."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development', 'CORS_ALLOWED_ORIGINS': 'http://localhost:5000'}):
            result = _get_cors_allowed_origins()
            assert 'http://localhost:5000' in result
    
    def test_get_cors_allowed_origins_development_default(self):
        """Test: CORS origins en desarrollo con valores por defecto."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}, clear=True):
            os.environ.pop('CORS_ALLOWED_ORIGINS', None)
            result = _get_cors_allowed_origins()
            assert 'http://localhost:5173' in result


@pytest.mark.unit
class TestBuildResponse:
    """Tests para _build_response."""
    
    def test_build_response_success(self, app):
        """Test: Construir respuesta exitosa."""
        with app.app_context():
            response, status_code = _build_response(True, message='Test')
            
            assert status_code == 200
            assert response.json['success'] is True
            assert response.json['message'] == 'Test'
    
    def test_build_response_error(self, app):
        """Test: Construir respuesta de error."""
        with app.app_context():
            response, status_code = _build_response(False, status_code=500, error='Error')
            
            assert status_code == 500
            assert response.json['success'] is False
            assert response.json['error'] == 'Error'
    
    def test_build_response_with_data(self, app):
        """Test: Construir respuesta con datos."""
        with app.app_context():
            response, status_code = _build_response(True, data={'id': 1})
            
            assert response.json['data'] == {'id': 1}


@pytest.mark.unit
class TestSerializeTipoDocumento:
    """Tests para _serialize_tipo_documento."""
    
    def test_serialize_tipo_documento_mapped(self):
        """Test: Serializar tipo de documento con mapeo conocido."""
        tipo = MagicMock()
        tipo.id_documento = 1
        tipo.nombre_documento = 'Cédula de Ciudadanía'
        
        result = _serialize_tipo_documento(tipo)
        
        assert result['id'] == 1
        assert result['codigo'] == 'cc'
        assert result['nombre'] == 'Cédula de Ciudadanía'
    
    def test_serialize_tipo_documento_unmapped(self):
        """Test: Serializar tipo de documento sin mapeo."""
        tipo = MagicMock()
        tipo.id_documento = 1
        tipo.nombre_documento = 'Otro Documento'
        
        result = _serialize_tipo_documento(tipo)
        
        assert result['codigo'] == 'otro_documento'


@pytest.mark.unit
class TestSerializeSexo:
    """Tests para _serialize_sexo."""
    
    def test_serialize_sexo_mapped(self):
        """Test: Serializar sexo con mapeo conocido."""
        sexo = MagicMock()
        sexo.id_sexo = 1
        sexo.nombre = 'Masculino'
        
        result = _serialize_sexo(sexo)
        
        assert result['id'] == 1
        assert result['valor'] == 'masculino'
        assert result['nombre'] == 'Masculino'
    
    def test_serialize_sexo_unmapped(self):
        """Test: Serializar sexo sin mapeo."""
        sexo = MagicMock()
        sexo.id_sexo = 1
        sexo.nombre = 'Otro'
        
        result = _serialize_sexo(sexo)
        
        assert result['valor'] == 'otro'


@pytest.mark.unit
class TestParametroEsTrue:
    """Tests para _parametro_es_true."""
    
    def test_parametro_es_true_true(self):
        """Test: Parámetro es True."""
        assert _parametro_es_true('true') is True
        assert _parametro_es_true('TRUE') is True
        assert _parametro_es_true('  True  ') is True
    
    def test_parametro_es_true_false(self):
        """Test: Parámetro es False."""
        assert _parametro_es_true('false') is False
        assert _parametro_es_true('False') is False
        assert _parametro_es_true('') is False
    
    def test_parametro_es_true_none(self):
        """Test: Parámetro es None."""
        assert _parametro_es_true(None) is False
        assert _parametro_es_true(None, default=True) is True


@pytest.mark.unit
class TestSerializeAcudiente:
    """Tests para _serialize_acudiente."""
    
    def test_serialize_acudiente_with_persona(self):
        """Test: Serializar acudiente con persona."""
        acudiente = MagicMock()
        acudiente.id_acudiente = 1
        acudiente.id_persona = 2
        acudiente.estado = True
        
        persona = MagicMock()
        persona.id_persona = 2
        persona.nombre_completo = 'Test Person'
        persona.documento = '1234567890'
        persona.correo_electronico = 'test@example.com'
        
        acudiente.persona = persona
        
        result = _serialize_acudiente(acudiente)
        
        assert result['id_acudiente'] == 1
        assert 'persona' in result
        assert result['persona']['nombre_completo'] == 'Test Person'
    
    def test_serialize_acudiente_without_persona(self):
        """Test: Serializar acudiente sin persona."""
        acudiente = MagicMock()
        acudiente.id_acudiente = 1
        acudiente.id_persona = 2
        acudiente.estado = True
        del acudiente.persona
        
        result = _serialize_acudiente(acudiente)
        
        assert result['id_acudiente'] == 1
        assert 'persona' not in result


@pytest.mark.unit
class TestSerializeDeportista:
    """Tests para _serialize_deportista."""
    
    def test_serialize_deportista_with_persona(self):
        """Test: Serializar deportista con persona."""
        deportista = MagicMock()
        deportista.id_deportista = 1
        deportista.id_persona = 2
        
        persona = MagicMock()
        persona.id_persona = 2
        persona.nombre_completo = 'Test Person'
        persona.primer_nombre = 'Test'
        persona.primer_apellido = 'Person'
        persona.segundo_nombre = None
        persona.segundo_apellido = None
        persona.documento = '1234567890'
        persona.correo_electronico = 'test@example.com'
        persona.telefono = '1234567890'
        
        deportista.persona = persona
        
        result = _serialize_deportista(deportista)
        
        assert result['id_deportista'] == 1
        assert 'persona' in result
        assert result['persona']['nombre_completo'] == 'Test Person'
    
    def test_serialize_deportista_without_persona(self):
        """Test: Serializar deportista sin persona."""
        deportista = MagicMock()
        deportista.id_deportista = 1
        deportista.id_persona = 2
        del deportista.persona
        
        result = _serialize_deportista(deportista)
        
        assert result['id_deportista'] == 1
        assert 'persona' not in result


@pytest.mark.unit
class TestHandleUnexpectedError:
    """Tests para _handle_unexpected_error."""
    
    def test_handle_unexpected_error_default_message(self, app):
        """Test: Manejar error con mensaje por defecto."""
        error = ValueError('Test error')
        
        with app.app_context():
            with patch('src.routes.catalogos_routes.logger') as mock_logger:
                response, status_code = _handle_unexpected_error('Test context', error)
                
                assert status_code == 500
                assert response.json['success'] is False
                mock_logger.error.assert_called_once()
    
    def test_handle_unexpected_error_custom_message(self, app):
        """Test: Manejar error con mensaje personalizado."""
        error = ValueError('Test error')
        
        with app.app_context():
            with patch('src.routes.catalogos_routes.logger'):
                response, status_code = _handle_unexpected_error('Test context', error, message='Custom error')
                
                assert status_code == 500
                assert response.json['error'] == 'Custom error'


@pytest.mark.unit
class TestFetchPersonaPorCedula:
    """Tests para _fetch_persona_por_cedula."""
    
    def test_fetch_persona_por_cedula_found(self, app):
        """Test: Buscar persona por cédula encontrada."""
        persona_mock = MagicMock()
        
        with app.app_context():
            with patch('src.models.personas.persona.Persona') as mock_persona:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = persona_mock
                mock_persona.query = mock_query
                
                result = _fetch_persona_por_cedula('1234567890')
                
                assert result == persona_mock
    
    def test_fetch_persona_por_cedula_not_found(self, app):
        """Test: Buscar persona por cédula no encontrada."""
        with app.app_context():
            with patch('src.models.personas.persona.Persona') as mock_persona:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_persona.query = mock_query
                
                result = _fetch_persona_por_cedula('1234567890')
                
                assert result is None


@pytest.mark.unit
class TestFetchAcudientePorPersona:
    """Tests para _fetch_acudiente_por_persona."""
    
    def test_fetch_acudiente_por_persona_found(self):
        """Test: Buscar acudiente por persona encontrado."""
        acudiente_mock = MagicMock()
        
        with patch('src.routes.catalogos_routes.Acudiente') as mock_acudiente:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = acudiente_mock
            mock_acudiente.query = mock_query
            
            result = _fetch_acudiente_por_persona(1)
            
            assert result == acudiente_mock


@pytest.mark.unit
class TestFetchDeportistaPorPersona:
    """Tests para _fetch_deportista_por_persona."""
    
    def test_fetch_deportista_por_persona_found(self, app):
        """Test: Buscar deportista por persona encontrado."""
        deportista_mock = MagicMock()
        
        with app.app_context():
            with patch('src.models.deportistas.deportista.Deportista') as mock_deportista:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = deportista_mock
                mock_deportista.query = mock_query
                
                result = _fetch_deportista_por_persona(1)
                
                assert result == deportista_mock


@pytest.mark.unit
class TestSerializeDebugFunctions:
    """Tests para funciones de serialización de debug."""
    
    def test_serialize_tipo_documento_debug(self):
        """Test: Serializar tipo documento para debug."""
        tipo = MagicMock()
        tipo.id_documento = 1
        tipo.nombre_documento = 'Test'
        
        result = _serialize_tipo_documento_debug(tipo)
        
        assert result == {'id': 1, 'nombre': 'Test'}
    
    def test_serialize_sexo_debug(self):
        """Test: Serializar sexo para debug."""
        sexo = MagicMock()
        sexo.id_sexo = 1
        sexo.nombre = 'Masculino'
        
        result = _serialize_sexo_debug(sexo)
        
        assert result == {'id': 1, 'nombre': 'Masculino'}
    
    def test_serialize_categoria_debug(self):
        """Test: Serializar categoría para debug."""
        categoria = MagicMock()
        categoria.id_categoria = 1
        categoria.nombre_categoria = 'Test'
        categoria.estado = True
        
        result = _serialize_categoria_debug(categoria)
        
        assert result == {'id': 1, 'nombre': 'Test', 'estado': True}


@pytest.mark.unit
class TestObtenerDebugInfo:
    """Tests para _obtener_debug_info."""
    
    def test_obtener_debug_info_basic(self):
        """Test: Obtener información de debug básica."""
        modelo = MagicMock()
        registro1 = MagicMock()
        registro2 = MagicMock()
        modelo.query.all.return_value = [registro1, registro2]
        modelo.__tablename__ = 'test_table'
        
        serializer = MagicMock(side_effect=lambda x: {'id': 1})
        
        result = _obtener_debug_info(modelo, serializer)
        
        assert result['count'] == 2
        assert result['tablename'] == 'test_table'
        assert len(result['data']) == 2


@pytest.mark.unit
class TestConsultarPragmaTable:
    """Tests para _consultar_pragma_table."""
    
    def test_consultar_pragma_table_basic(self, app):
        """Test: Consultar PRAGMA table_info."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_result.fetchall.return_value = [(0, 'col1', 'TEXT', 0, None, 0)]
                mock_db.session.execute.return_value = mock_result
                
                result = _consultar_pragma_table('test_table')
                
                assert isinstance(result, list)
                mock_db.session.execute.assert_called_once()


@pytest.mark.unit
class TestObtenerNombresColumnas:
    """Tests para _obtener_nombres_columnas."""
    
    def test_obtener_nombres_columnas_basic(self, app):
        """Test: Obtener nombres de columnas."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[(0, 'col1', 'TEXT', 0, None, 0), (1, 'col2', 'INTEGER', 0, None, 0)]):
                result = _obtener_nombres_columnas('test_table')
                
                assert 'col1' in result
                assert 'col2' in result


@pytest.mark.unit
class TestContarRegistros:
    """Tests para _contar_registros."""
    
    def test_contar_registros_basic(self, app):
        """Test: Contar registros en tabla."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_row = MagicMock()
                mock_row.__getitem__.return_value = 5
                mock_result.fetchone.return_value = (5,)
                mock_db.session.execute.return_value = mock_result
                
                result = _contar_registros('test_table')
                
                assert result == 5
    
    def test_contar_registros_empty(self, app):
        """Test: Contar registros cuando no hay fila."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_result.fetchone.return_value = None
                mock_db.session.execute.return_value = mock_result
                
                result = _contar_registros('test_table')
                
                assert result == 0


@pytest.mark.unit
class TestAgregarColumnaNombreSexo:
    """Tests para _agregar_columna_nombre_sexo."""
    
    def test_agregar_columna_nombre_sexo_when_not_exists(self, app):
        """Test: Agregar columna nombre cuando no existe."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._obtener_nombres_columnas', return_value=['id_sexo']), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _agregar_columna_nombre_sexo(cambios)
                
                assert len(cambios) == 1
                mock_db.session.execute.assert_called_once()
    
    def test_agregar_columna_nombre_sexo_when_exists(self, app):
        """Test: No agregar columna nombre cuando ya existe."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._obtener_nombres_columnas', return_value=['id_sexo', 'nombre']), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _agregar_columna_nombre_sexo(cambios)
                
                assert len(cambios) == 0
                mock_db.session.execute.assert_not_called()


@pytest.mark.unit
class TestPoblarTiposDocumentoSiVacio:
    """Tests para _poblar_tipos_documento_si_vacio."""
    
    def test_poblar_tipos_documento_when_empty(self, app):
        """Test: Poblar tipos de documento cuando está vacío."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_tipos_documento_si_vacio(cambios)
                
                assert len(cambios) == 1
                mock_db.session.execute.assert_called_once()
    
    def test_poblar_tipos_documento_when_not_empty(self, app):
        """Test: No poblar tipos de documento cuando ya hay datos."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=5), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_tipos_documento_si_vacio(cambios)
                
                assert len(cambios) == 0
                mock_db.session.execute.assert_not_called()


@pytest.mark.unit
class TestPoblarSexosSiVacio:
    """Tests para _poblar_sexos_si_vacio."""
    
    def test_poblar_sexos_when_empty_with_both_columns(self, app):
        """Test: Poblar sexos con columnas sexo y nombre."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[(0, 'id_sexo', 'INTEGER', 0, None, 0), (1, 'sexo', 'TEXT', 0, None, 0), (2, 'nombre', 'TEXT', 0, None, 0)]), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_sexos_si_vacio(cambios)
                
                assert len(cambios) == 1
                mock_db.session.execute.assert_called_once()
    
    def test_poblar_sexos_when_empty_with_nombre_only(self, app):
        """Test: Poblar sexos solo con columna nombre."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[(0, 'id_sexo', 'INTEGER', 0, None, 0), (1, 'nombre', 'TEXT', 0, None, 0)]), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_sexos_si_vacio(cambios)
                
                assert len(cambios) == 1
                mock_db.session.execute.assert_called_once()
    
    def test_poblar_sexos_when_empty_without_columns(self, app):
        """Test: Poblar sexos sin columnas sexo ni nombre."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0), \
                 patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[(0, 'id_sexo', 'INTEGER', 0, None, 0)]), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_sexos_si_vacio(cambios)
                
                assert len(cambios) == 1
                mock_db.session.execute.assert_called_once()
    
    def test_poblar_sexos_when_not_empty(self, app):
        """Test: No poblar sexos cuando ya hay datos."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=3), \
                 patch('src.routes.catalogos_routes.db') as mock_db:
                
                _poblar_sexos_si_vacio(cambios)
                
                assert len(cambios) == 0
                mock_db.session.execute.assert_not_called()


@pytest.mark.unit
class TestInsertarCategoriasIniciales:
    """Tests para _insertar_categorias_iniciales."""
    
    def test_insertar_categorias_iniciales_success(self, app):
        """Test: Insertar categorías iniciales exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_db.session.execute.return_value = None
                
                result = _insertar_categorias_iniciales()
                
                assert isinstance(result, list)
                assert len(result) == 5
                assert mock_db.session.execute.call_count == 5


@pytest.mark.unit
class TestSerializeMetodoPago:
    """Tests para _serialize_metodo_pago."""
    
    def test_serialize_metodo_pago_basic(self):
        """Test: Serializar método de pago."""
        metodo = MagicMock()
        metodo.id_metodo_pago = 1
        metodo.nombre_metodo = 'Efectivo'
        metodo.estado = True
        
        result = _serialize_metodo_pago(metodo)
        
        assert result['id_metodo_pago'] == 1
        assert result['nombre'] == 'Efectivo'
        assert result['estado'] is True


@pytest.mark.unit
class TestSerializeModelList:
    """Tests para _serialize_model_list."""
    
    def test_serialize_model_list_basic(self):
        """Test: Serializar lista de modelos."""
        registro1 = MagicMock()
        registro2 = MagicMock()
        
        def serializer(reg):
            return {'id': 1}
        
        result = _serialize_model_list([registro1, registro2], serializer)
        
        assert len(result) == 2
        assert all(isinstance(item, dict) for item in result)


@pytest.mark.unit
class TestConsultarPragmaTable:
    """Tests para _consultar_pragma_table."""
    
    def test_consultar_pragma_table_success(self, app):
        """Test: Consultar PRAGMA table_info exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_result.fetchall.return_value = [('1', 'columna1'), ('2', 'columna2')]
                mock_db.session.execute.return_value = mock_result
                
                result = _consultar_pragma_table('test_table')
                
                assert len(result) == 2
                mock_db.session.execute.assert_called_once()


@pytest.mark.unit
class TestObtenerNombresColumnas:
    """Tests para _obtener_nombres_columnas."""
    
    def test_obtener_nombres_columnas_success(self, app):
        """Test: Obtener nombres de columnas exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[('1', 'columna1'), ('2', 'columna2')]):
                result = _obtener_nombres_columnas('test_table')
                
                assert 'columna1' in result
                assert 'columna2' in result


@pytest.mark.unit
class TestContarRegistros:
    """Tests para _contar_registros."""
    
    def test_contar_registros_success(self, app):
        """Test: Contar registros exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_result.fetchone.return_value = (5,)
                mock_db.session.execute.return_value = mock_result
                
                result = _contar_registros('test_table')
                
                assert result == 5
    
    def test_contar_registros_no_fila(self, app):
        """Test: Contar registros cuando no hay fila."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                mock_result = MagicMock()
                mock_result.fetchone.return_value = None
                mock_db.session.execute.return_value = mock_result
                
                result = _contar_registros('test_table')
                
                assert result == 0


@pytest.mark.unit
class TestAgregarColumnaNombreSexo:
    """Tests para _agregar_columna_nombre_sexo."""
    
    def test_agregar_columna_nombre_sexo_columna_existe(self, app):
        """Test: No agregar columna si ya existe."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._obtener_nombres_columnas', return_value=['nombre', 'otra_columna']):
                with patch('src.routes.catalogos_routes.db') as mock_db:
                    _agregar_columna_nombre_sexo(cambios)
                    
                    assert len(cambios) == 0
                    mock_db.session.execute.assert_not_called()
    
    def test_agregar_columna_nombre_sexo_columna_no_existe(self, app):
        """Test: Agregar columna si no existe."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._obtener_nombres_columnas', return_value=['otra_columna']):
                with patch('src.routes.catalogos_routes.db') as mock_db:
                    _agregar_columna_nombre_sexo(cambios)
                    
                    assert len(cambios) == 1
                    assert "Agregada columna 'nombre' a tabla sexos" in cambios
                    mock_db.session.execute.assert_called_once()


@pytest.mark.unit
class TestPoblarTiposDocumentoSiVacio:
    """Tests para _poblar_tipos_documento_si_vacio."""
    
    def test_poblar_tipos_documento_si_vacio_tabla_no_vacia(self, app):
        """Test: No poblar si la tabla no está vacía."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=1):
                with patch('src.routes.catalogos_routes.db') as mock_db:
                    _poblar_tipos_documento_si_vacio(cambios)
                    
                    assert len(cambios) == 0
                    mock_db.session.execute.assert_not_called()
    
    def test_poblar_tipos_documento_si_vacio_tabla_vacia(self, app):
        """Test: Poblar si la tabla está vacía."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0):
                with patch('src.routes.catalogos_routes.db') as mock_db:
                    _poblar_tipos_documento_si_vacio(cambios)
                    
                    assert len(cambios) == 1
                    assert 'Poblados tipos de documento' in cambios
                    mock_db.session.execute.assert_called_once()


@pytest.mark.unit
class TestPoblarSexosSiVacio:
    """Tests para _poblar_sexos_si_vacio."""
    
    def test_poblar_sexos_si_vacio_tabla_no_vacia(self, app):
        """Test: No poblar si la tabla no está vacía."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=1):
                _poblar_sexos_si_vacio(cambios)
                
                assert len(cambios) == 0
    
    def test_poblar_sexos_si_vacio_con_sexo_y_nombre(self, app):
        """Test: Poblar sexos cuando tiene columnas sexo y nombre."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0):
                with patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[('1', 'sexo'), ('2', 'nombre')]):
                    with patch('src.routes.catalogos_routes.db') as mock_db:
                        _poblar_sexos_si_vacio(cambios)
                        
                        assert len(cambios) == 1
                        assert 'Poblados sexos' in cambios
                        mock_db.session.execute.assert_called_once()
                        # Verificar que el SQL incluye 'sexo' y 'nombre'
                        call_args = mock_db.session.execute.call_args[0][0]
                        assert 'sexo' in str(call_args).lower()
    
    def test_poblar_sexos_si_vacio_solo_nombre(self, app):
        """Test: Poblar sexos cuando solo tiene columna nombre."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0):
                with patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[('1', 'nombre')]):
                    with patch('src.routes.catalogos_routes.db') as mock_db:
                        _poblar_sexos_si_vacio(cambios)
                        
                        assert len(cambios) == 1
                        mock_db.session.execute.assert_called_once()
    
    def test_poblar_sexos_si_vacio_sin_columnas(self, app):
        """Test: Poblar sexos cuando no tiene columnas especiales."""
        cambios = []
        
        with app.app_context():
            with patch('src.routes.catalogos_routes._contar_registros', return_value=0):
                with patch('src.routes.catalogos_routes._consultar_pragma_table', return_value=[('1', 'id_sexo')]):
                    with patch('src.routes.catalogos_routes.db') as mock_db:
                        _poblar_sexos_si_vacio(cambios)
                        
                        assert len(cambios) == 1
                        mock_db.session.execute.assert_called_once()


@pytest.mark.unit
class TestInsertarCategoriasIniciales:
    """Tests para _insertar_categorias_iniciales."""
    
    def test_insertar_categorias_iniciales_success(self, app):
        """Test: Insertar categorías iniciales exitosamente."""
        with app.app_context():
            with patch('src.routes.catalogos_routes.db') as mock_db:
                result = _insertar_categorias_iniciales()
                
                assert len(result) == 5  # 5 categorías en CATEGORIAS_INICIALES
                assert mock_db.session.execute.call_count == 5

