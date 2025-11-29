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

