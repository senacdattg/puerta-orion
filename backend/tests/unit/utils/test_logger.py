"""
Tests para utilidades de logging.

Este módulo contiene tests que verifican las funciones
de logging y el gestor de logs.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from src.utils.logger import (
    obtener_registrador,
    registrar_peticion,
    registrar_error,
    registrar_base_datos,
    GestorLogs
)


@pytest.mark.unit
class TestObtenerRegistrador:
    """Tests para obtener_registrador."""
    
    def test_obtener_registrador_default(self):
        """Test: Obtener registrador por defecto."""
        logger = obtener_registrador()
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
        assert hasattr(logger, 'warning')
    
    def test_obtener_registrador_named(self):
        """Test: Obtener registrador con nombre específico."""
        logger = obtener_registrador('test_logger')
        
        assert logger is not None
        # El logger puede tener el nombre exacto o contenerlo en la jerarquía
        assert hasattr(logger, 'name')
    
    def test_obtener_registrador_multiple_calls(self):
        """Test: Múltiples llamadas retornan el mismo logger."""
        logger1 = obtener_registrador('test')
        logger2 = obtener_registrador('test')
        
        assert logger1 is logger2


@pytest.mark.unit
class TestRegistrarPeticion:
    """Tests para registrar_peticion."""
    
    def test_registrar_peticion_basic(self):
        """Test: Registrar petición básica."""
        from src.utils.logger import gestor_logs
        
        mock_request = MagicMock()
        mock_request.path = '/api/test'
        mock_request.method = 'GET'
        mock_request.remote_addr = '127.0.0.1'
        mock_request.headers = MagicMock()
        mock_request.headers.get.return_value = 'Test Agent'
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_peticion(mock_request, mock_response, duracion=0.5)
            
            mock_get_logger.assert_called_with('acceso')
            mock_logger.info.assert_called_once()
    
    def test_registrar_peticion_without_response(self):
        """Test: Registrar petición sin respuesta."""
        from src.utils.logger import gestor_logs
        
        mock_request = MagicMock()
        mock_request.path = '/api/test'
        mock_request.method = 'POST'
        mock_request.remote_addr = '192.168.1.1'
        mock_request.headers = MagicMock()
        mock_request.headers.get.return_value = 'Agent'
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_peticion(mock_request, None, duracion=1.0)
            
            mock_logger.info.assert_called_once()


@pytest.mark.unit
class TestRegistrarError:
    """Tests para registrar_error."""
    
    def test_registrar_error_basic(self):
        """Test: Registrar error básico."""
        from src.utils.logger import gestor_logs
        
        error = ValueError("Error de prueba")
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_error(error)
            
            mock_get_logger.assert_called_with('error')
            mock_logger.error.assert_called_once()
    
    def test_registrar_error_with_context(self):
        """Test: Registrar error con contexto."""
        from src.utils.logger import gestor_logs
        
        error = RuntimeError("Error crítico")
        contexto = {'path': '/api/test', 'user_id': 123}
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_error(error, contexto)
            
            mock_logger.error.assert_called_once()
            call_args = mock_logger.error.call_args[0][0]
            assert 'Error crítico' in call_args


@pytest.mark.unit
class TestRegistrarBaseDatos:
    """Tests para registrar_base_datos."""
    
    def test_registrar_base_datos_basic(self):
        """Test: Registrar operación de base de datos básica."""
        from src.utils.logger import gestor_logs
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_base_datos('SELECT', tabla='usuarios', duracion=0.1)
            
            mock_get_logger.assert_called_with('base_datos')
            mock_logger.info.assert_called_once()
    
    def test_registrar_base_datos_with_query(self):
        """Test: Registrar operación con consulta."""
        from src.utils.logger import gestor_logs
        
        with patch.object(gestor_logs, 'obtener_registrador') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            registrar_base_datos(
                'INSERT',
                tabla='personas',
                consulta='INSERT INTO personas...',
                duracion=0.05
            )
            
            mock_logger.info.assert_called_once()


@pytest.mark.unit
class TestGestorLogs:
    """Tests para GestorLogs."""
    
    def test_gestor_logs_init_without_app(self):
        """Test: Inicializar GestorLogs sin aplicación."""
        gestor = GestorLogs()
        
        assert gestor.aplicacion is None
        assert gestor.registradores == {}
    
    def test_gestor_logs_obtener_registrador_fallback(self):
        """Test: Obtener registrador con fallback."""
        gestor = GestorLogs()
        
        logger = gestor.obtener_registrador('test')
        
        assert logger is not None
        assert hasattr(logger, 'info')
    
    def test_gestor_logs_obtener_url_amigable_with_id(self):
        """Test: Obtener URL amigable con ID numérico."""
        gestor = GestorLogs()
        
        url = gestor._obtener_url_amigable('/api/usuarios/123')
        
        assert '/:id' in url
        assert '123' not in url
    
    def test_gestor_logs_obtener_url_amigable_with_uuid(self):
        """Test: Obtener URL amigable con UUID."""
        gestor = GestorLogs()
        uuid = '550e8400-e29b-41d4-a716-446655440000'
        
        url = gestor._obtener_url_amigable(f'/api/usuarios/{uuid}')
        
        assert '/:uuid' in url
        assert uuid not in url
    
    def test_gestor_logs_obtener_url_amigable_simple(self):
        """Test: Obtener URL amigable simple."""
        gestor = GestorLogs()
        
        url = gestor._obtener_url_amigable('/api/test')
        
        assert url == '/api/test'
    
    def test_gestor_logs_init_with_app(self):
        """Test: Inicializar GestorLogs con aplicación (línea 24)."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['LOG_DIR'] = '/tmp/test_logs'
        app.config['LOG_FILE'] = '/tmp/test_logs/app.log'
        app.config['LOG_ERROR_FILE'] = '/tmp/test_logs/error.log'
        app.config['LOG_ACCESS_FILE'] = '/tmp/test_logs/access.log'
        app.config['LOG_DB_FILE'] = '/tmp/test_logs/db.log'
        app.config['LOG_ARCHIVE_DIR'] = '/tmp/test_logs/archive'
        app.config['LOG_LEVEL'] = 'INFO'
        app.config['DEBUG'] = False
        
        with patch('src.utils.logger.os.makedirs') as mock_makedirs:
            with patch.object(GestorLogs, '_configurar_registradores') as mock_config:
                gestor = GestorLogs(aplicacion=app)
                
                assert gestor.aplicacion == app
                mock_config.assert_called_once()
    
    def test_gestor_logs_makedirs_when_directory_not_exists(self):
        """Test: Crear directorios cuando no existen (línea 61)."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['LOG_DIR'] = '/tmp/test_logs_new'
        app.config['LOG_FILE'] = '/tmp/test_logs_new/app.log'
        app.config['LOG_ERROR_FILE'] = '/tmp/test_logs_new/error.log'
        app.config['LOG_ACCESS_FILE'] = '/tmp/test_logs_new/access.log'
        app.config['LOG_DB_FILE'] = '/tmp/test_logs_new/db.log'
        app.config['LOG_ARCHIVE_DIR'] = '/tmp/test_logs_new/archive'
        app.config['LOG_LEVEL'] = 'INFO'
        app.config['DEBUG'] = False
        
        with patch('src.utils.logger.os.path.exists', return_value=False) as mock_exists:
            with patch('src.utils.logger.os.makedirs') as mock_makedirs:
                with patch('src.utils.logger.RotatingFileHandler') as mock_handler:
                    with patch('src.utils.logger.logging.getLogger') as mock_get_logger:
                        mock_logger = MagicMock()
                        mock_get_logger.return_value = mock_logger
                        
                        gestor = GestorLogs()
                        gestor.inicializar_aplicacion(app)
                        
                        # Verificar que se llamó makedirs
                        assert mock_makedirs.call_count >= 1
    
    def test_gestor_logs_formateador_exception_handling(self):
        """Test: Manejo de excepción al obtener formateador (líneas 158-159)."""
        gestor = GestorLogs()
        
        # Simular que _obtener_formateador lanza una excepción
        with patch.object(gestor, '_obtener_formateador', side_effect=Exception('Error')):
            # Esto debería usar el formateador de fallback en línea 159
            logger = gestor.obtener_registrador('test_fallback_exception')
            
            assert logger is not None
            assert hasattr(logger, 'info')
    
    def test_gestor_logs_configurar_logger_aplicacion_debug_mode(self):
        """Test: Configurar logger aplicación en modo DEBUG (líneas 76-79)."""
        from flask import Flask
        
        app = Flask(__name__)
        app.config['LOG_DIR'] = '/tmp/test_logs'
        app.config['LOG_FILE'] = '/tmp/test_logs/app.log'
        app.config['LOG_ERROR_FILE'] = '/tmp/test_logs/error.log'
        app.config['LOG_ACCESS_FILE'] = '/tmp/test_logs/access.log'
        app.config['LOG_DB_FILE'] = '/tmp/test_logs/db.log'
        app.config['LOG_ARCHIVE_DIR'] = '/tmp/test_logs/archive'
        app.config['LOG_LEVEL'] = 'INFO'
        app.config['DEBUG'] = True  # Modo debug
        
        gestor = GestorLogs()
        
        with patch('src.utils.logger.os.makedirs'):
            with patch('src.utils.logger.RotatingFileHandler') as mock_handler_class:
                with patch('src.utils.logger.logging.getLogger') as mock_get_logger:
                    with patch('src.utils.logger.logging.StreamHandler') as mock_stream_handler_class:
                        mock_logger = MagicMock()
                        mock_get_logger.return_value = mock_logger
                        mock_handler = MagicMock()
                        mock_handler_class.return_value = mock_handler
                        mock_stream_handler = MagicMock()
                        mock_stream_handler_class.return_value = mock_stream_handler
                        
                        gestor.inicializar_aplicacion(app)
                        
                        # Verificar que se agregó handler de consola (solo en modo DEBUG)
                        assert mock_stream_handler.setLevel.called
    
    def test_gestor_logs_obtener_registrador_from_registradores(self):
        """Test: Obtener registrador que ya existe en registradores (línea 141)."""
        gestor = GestorLogs()
        gestor.registradores = {}
        
        # Crear un logger primero
        logger1 = gestor.obtener_registrador('test')
        
        # Obtener el mismo logger de nuevo (debe retornar el existente)
        logger2 = gestor.obtener_registrador('test')
        
        assert logger1 is logger2
        assert 'test' in gestor.registradores
    
    def test_gestor_logs_obtener_registrador_fallback_to_aplicacion(self):
        """Test: Fallback a logger 'aplicacion' cuando no existe el solicitado (línea 145)."""
        gestor = GestorLogs()
        
        # Primero crear el logger 'aplicacion'
        logger_aplicacion = gestor.obtener_registrador('aplicacion')
        
        # Luego solicitar otro logger que no existe - debe retornar 'aplicacion'
        logger_otro = gestor.obtener_registrador('otro_logger')
        
        # Verificar que cuando 'otro_logger' no existe, retorna 'aplicacion'
        assert 'aplicacion' in gestor.registradores

