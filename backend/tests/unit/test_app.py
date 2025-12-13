"""
Tests unitarios para app.py.

Cubre la inicialización de la aplicación Flask, configuración CORS,
registro de blueprints y endpoints de estado.
"""

import pytest
import os
from unittest.mock import patch, MagicMock, call
from flask import Flask

from app import (
    create_app,
    _resolve_config_name,
    _build_flask_app,
    _load_configuration,
    _configure_cors,
    _register_preflight_handler,
    _select_origin_for_response,
    _initialize_extensions,
    _register_blueprints,
    _register_status_routes,
    _normalize_origins,
    _initialize_scheduler,
    shutdown_handler,
    _register_auth_blueprints,
    _register_domain_blueprints,
)


@pytest.mark.unit
class TestResolveConfigName:
    """Tests para _resolve_config_name."""
    
    def test_resolve_config_name_with_provided_name(self):
        """Test: Resolver nombre de configuración proporcionado."""
        result = _resolve_config_name('production')
        assert result == 'production'
    
    def test_resolve_config_name_with_none(self):
        """Test: Resolver nombre de configuración cuando es None."""
        with patch.dict(os.environ, {'FLASK_ENV': 'testing'}, clear=False):
            result = _resolve_config_name(None)
            assert result == 'testing'
    
    def test_resolve_config_name_without_env(self):
        """Test: Resolver nombre de configuración cuando no hay variable de entorno."""
        with patch.dict(os.environ, {}, clear=True):
            # Si no hay FLASK_ENV, debería usar 'development' como default
            result = _resolve_config_name(None)
            assert result == 'development'


@pytest.mark.unit
class TestBuildFlaskApp:
    """Tests para _build_flask_app."""
    
    def test_build_flask_app(self):
        """Test: Construir aplicación Flask base."""
        app = _build_flask_app()
        
        assert isinstance(app, Flask)
        assert app.static_folder is not None
        assert 'static' in app.static_folder or app.static_folder == 'static'
        assert app.static_url_path == '/static'


@pytest.mark.unit
class TestLoadConfiguration:
    """Tests para _load_configuration."""
    
    def test_load_configuration_success(self):
        """Test: Cargar configuración exitosamente."""
        app = Flask(__name__)
        mock_config = MagicMock()
        
        with patch('app.config') as mock_config_module:
            mock_config_module.__getitem__.return_value = mock_config
            with patch('app.validate_config', return_value=(True, [])):
                with patch.object(app.config, 'from_object') as mock_from_object:
                    _load_configuration(app, 'testing')
                    
                    mock_config_module.__getitem__.assert_called_once_with('testing')
                    mock_from_object.assert_called_once_with(mock_config)
    
    def test_load_configuration_with_errors(self):
        """Test: Cargar configuración con errores."""
        app = Flask(__name__)
        mock_config = MagicMock()
        app.logger = MagicMock()
        
        with patch('app.config') as mock_config_module:
            mock_config_module.__getitem__.return_value = mock_config
            with patch('app.validate_config', return_value=(False, ['Error 1', 'Error 2'])):
                _load_configuration(app, 'testing')
                
                app.logger.warning.assert_called_once()
                warning_call = app.logger.warning.call_args[0][0]
                assert 'Configuración con problemas' in warning_call


@pytest.mark.unit
class TestNormalizeOrigins:
    """Tests para _normalize_origins."""
    
    def test_normalize_origins_with_valid_origins(self):
        """Test: Normalizar orígenes válidos."""
        origins = ['http://localhost:3000', '  https://example.com  ', 'http://test.com']
        result = _normalize_origins(origins)
        
        assert result == ['http://localhost:3000', 'https://example.com', 'http://test.com']
    
    def test_normalize_origins_with_empty_strings(self):
        """Test: Normalizar orígenes con strings vacíos."""
        origins = ['http://localhost:3000', '', '  ', 'https://example.com']
        result = _normalize_origins(origins)
        
        assert result == ['http://localhost:3000', 'https://example.com']
    
    def test_normalize_origins_with_empty_list(self):
        """Test: Normalizar lista vacía."""
        result = _normalize_origins([])
        assert result == []


@pytest.mark.unit
class TestConfigureCors:
    """Tests para _configure_cors."""
    
    def test_configure_cors_with_valid_origins(self):
        """Test: Configurar CORS con orígenes válidos."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['http://localhost:3000', 'https://example.com']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = True
        app.config['CORS_METHODS'] = ['GET', 'POST']
        app.config['CORS_HEADERS'] = ['Content-Type']
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            _configure_cors(app)
            
            mock_cors.assert_called_once()
            call_args = mock_cors.call_args
            assert call_args[1]['origins'] == ['http://localhost:3000', 'https://example.com']
            assert call_args[1]['supports_credentials'] is True
            assert 'EFFECTIVE_CORS_ORIGINS' in app.config
    
    def test_configure_cors_with_wildcard_and_credentials(self):
        """Test: Configurar CORS con wildcard y credenciales (debe deshabilitarse)."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['*']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = True
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            _configure_cors(app)
            
            call_args = mock_cors.call_args
            assert call_args[1]['origins'] == '*'
            assert call_args[1]['supports_credentials'] is False
            app.logger.warning.assert_called()
    
    def test_configure_cors_without_origins(self):
        """Test: Configurar CORS sin orígenes definidos."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = []
        app.config['CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            result = _configure_cors(app)
            
            call_args = mock_cors.call_args
            assert call_args[1]['origins'] == '*'
            assert call_args[1]['supports_credentials'] is False
            assert 'EFFECTIVE_CORS_ORIGINS' in app.config
            assert 'EFFECTIVE_CORS_SUPPORTS_CREDENTIALS' in app.config
            assert result == ('*',)
            app.logger.warning.assert_called()
    
    def test_configure_cors_with_supports_credentials_and_wildcard_in_list(self):
        """Test: Configurar CORS con credenciales y wildcard en lista de orígenes."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['http://localhost:3000', '*']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = True
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            _configure_cors(app)
            
            call_args = mock_cors.call_args
            # Cuando hay wildcard y credenciales, se elimina el wildcard de la lista
            # y se deshabilitan las credenciales, pero el origen se normaliza
            assert call_args[1]['supports_credentials'] is False
            # El wildcard se elimina de la lista, dejando solo los orígenes válidos
            origins_arg = call_args[1]['origins']
            # Puede ser '*' si solo queda wildcard, o lista sin wildcard
            assert origins_arg == '*' or (isinstance(origins_arg, list) and '*' not in origins_arg)
            app.logger.warning.assert_called()
    
    def test_configure_cors_with_default_methods_and_headers(self):
        """Test: Configurar CORS con métodos y headers por defecto."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['http://localhost:3000']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            _configure_cors(app)
            
            call_args = mock_cors.call_args
            assert call_args[1]['methods'] == ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']
            assert call_args[1]['allow_headers'] == ['Content-Type', 'Authorization']


@pytest.mark.unit
class TestSelectOriginForResponse:
    """Tests para _select_origin_for_response."""
    
    def test_select_origin_with_request_origin(self):
        """Test: Seleccionar origin cuando hay request origin."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://example.com']
        
        result = _select_origin_for_response(app, 'http://localhost:3000')
        assert result == 'http://localhost:3000'
    
    def test_select_origin_with_wildcard(self):
        """Test: Seleccionar origin cuando hay wildcard."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['*']
        
        result = _select_origin_for_response(app, None)
        assert result == '*'
    
    def test_select_origin_with_first_origin(self):
        """Test: Seleccionar primer origin de la lista."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://example.com', 'http://test.com']
        
        result = _select_origin_for_response(app, None)
        assert result == 'http://example.com'
    
    def test_select_origin_without_origins(self):
        """Test: Seleccionar origin cuando no hay orígenes configurados."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ()
        
        result = _select_origin_for_response(app, None)
        assert result is None


@pytest.mark.unit
class TestRegisterPreflightHandler:
    """Tests para _register_preflight_handler."""
    
    def test_preflight_handler_registered(self):
        """Test: Verificar que el handler de preflight está registrado."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET', 'POST', 'OPTIONS']
        app.config['CORS_HEADERS'] = ['Content-Type', 'Authorization']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://localhost:3000']
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        # Verificar que el before_request está registrado
        assert len(app.before_request_funcs.get(None, [])) > 0
    
    def test_preflight_handler_with_options_request(self):
        """Test: Handler preflight responde correctamente a petición OPTIONS."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET', 'POST', 'OPTIONS']
        app.config['CORS_HEADERS'] = ['Content-Type', 'Authorization']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://localhost:3000']
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        with app.test_client() as client:
            response = client.open(
                '/test',
                method='OPTIONS',
                headers={'Origin': 'http://localhost:3000'}
            )
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'
            assert 'GET, POST, OPTIONS' in response.headers.get('Access-Control-Allow-Methods', '')
            assert 'Content-Type, Authorization' in response.headers.get('Access-Control-Allow-Headers', '')
            assert response.headers.get('Access-Control-Max-Age') == '3600'
    
    def test_preflight_handler_with_options_request_with_credentials(self):
        """Test: Handler preflight con credenciales habilitadas."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET', 'POST']
        app.config['CORS_HEADERS'] = ['Content-Type']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://localhost:3000']
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = True
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        with app.test_client() as client:
            response = client.open(
                '/test',
                method='OPTIONS',
                headers={'Origin': 'http://localhost:3000'}
            )
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Credentials') == 'true'
    
    def test_preflight_handler_with_options_request_no_origin(self):
        """Test: Handler preflight sin origin en headers."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET', 'POST']
        app.config['CORS_HEADERS'] = ['Content-Type']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://example.com']
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        with app.test_client() as client:
            response = client.open(
                '/test',
                method='OPTIONS'
            )
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Origin') == 'http://example.com'
    
    def test_preflight_handler_with_options_request_wildcard_origin(self):
        """Test: Handler preflight con wildcard en orígenes efectivos."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET']
        app.config['CORS_HEADERS'] = ['Content-Type']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['*']
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        with app.test_client() as client:
            response = client.open(
                '/test',
                method='OPTIONS'
            )
            
            assert response.status_code == 200
            assert response.headers.get('Access-Control-Allow-Origin') == '*'
    
    def test_preflight_handler_with_non_options_request(self):
        """Test: Handler preflight no procesa peticiones no OPTIONS."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://localhost:3000']
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        @app.route('/test')
        def test_route():
            return {'message': 'success'}
        
        with app.test_client() as client:
            response = client.get('/test')
            
            assert response.status_code == 200
            assert response.get_json()['message'] == 'success'
    
    def test_preflight_handler_with_options_request_no_allowed_origin(self):
        """Test: Handler preflight sin origin permitido."""
        app = Flask(__name__)
        app.config['CORS_METHODS'] = ['GET']
        app.config['CORS_HEADERS'] = ['Content-Type']
        app.config['EFFECTIVE_CORS_ORIGINS'] = ()
        app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        _register_preflight_handler(app)
        
        with app.test_client() as client:
            response = client.open(
                '/test',
                method='OPTIONS'
            )
            
            assert response.status_code == 200
            assert 'Access-Control-Allow-Origin' not in response.headers


@pytest.mark.unit
class TestInitializeExtensions:
    """Tests para _initialize_extensions."""
    
    def test_initialize_extensions(self):
        """Test: Inicializar extensiones."""
        app = Flask(__name__)
        
        mock_gestor_logs = MagicMock()
        mock_db = MagicMock()
        mock_migrate = MagicMock()
        
        with patch('app.gestor_logs', mock_gestor_logs):
            with patch('app.db', mock_db):
                with patch('app.migrate', mock_migrate):
                    with patch('app._initialize_scheduler') as mock_scheduler:
                        _initialize_extensions(app)
                        
                        mock_gestor_logs.inicializar_aplicacion.assert_called_once_with(app)
                        mock_db.init_app.assert_called_once_with(app)
                        mock_migrate.init_app.assert_called_once_with(app, mock_db)
                        mock_scheduler.assert_called_once_with(app)


@pytest.mark.unit
class TestRegisterBlueprints:
    """Tests para _register_blueprints."""
    
    def test_register_blueprints(self):
        """Test: Registrar todos los blueprints."""
        app = Flask(__name__)
        
        with patch('app._register_auth_blueprints') as mock_auth:
            with patch('app._register_domain_blueprints') as mock_domain:
                _register_blueprints(app)
                
                mock_auth.assert_called_once_with(app)
                mock_domain.assert_called_once_with(app)


@pytest.mark.unit
class TestRegisterStatusRoutes:
    """Tests para _register_status_routes."""
    
    def test_register_status_routes_index(self):
        """Test: Verificar ruta index."""
        app = Flask(__name__)
        _register_status_routes(app, 'testing')
        
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
            assert 'API de Puerta Orion funcionando correctamente' in data['message']
    
    def test_register_status_routes_health(self):
        """Test: Verificar ruta health."""
        app = Flask(__name__)
        app.config['DEBUG'] = False
        with patch('app.db') as mock_db:
            mock_db.engine = MagicMock()
            _register_status_routes(app, 'testing')
            
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'healthy'
                assert data['environment'] == 'testing'
                assert 'database' in data
    
    def test_register_status_routes_config_debug_mode(self):
        """Test: Verificar ruta config en modo debug."""
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:pass@host/db'
        app.config['EFFECTIVE_CORS_ORIGINS'] = ('http://localhost:3000',)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
        app.config['LOG_LEVEL'] = 'INFO'
        
        _register_status_routes(app, 'testing')
        
        with app.test_client() as client:
            response = client.get('/config')
            assert response.status_code == 200
            data = response.get_json()
            assert data['environment'] == 'testing'
            assert data['debug'] is True
            assert 'database_uri' in data
            assert '@***' in data['database_uri']  # Debe estar enmascarado
    
    def test_register_status_routes_config_production_mode(self):
        """Test: Verificar ruta config en modo producción."""
        app = Flask(__name__)
        app.config['DEBUG'] = False
        
        _register_status_routes(app, 'production')
        
        with app.test_client() as client:
            response = client.get('/config')
            assert response.status_code == 200
            data = response.get_json()
            assert 'message' in data
            assert 'no disponible' in data['message']
    
    def test_register_status_routes_config_with_no_at_in_uri(self):
        """Test: Verificar ruta config con URI sin @."""
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['EFFECTIVE_CORS_ORIGINS'] = ('http://localhost:3000',)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
        app.config['LOG_LEVEL'] = 'INFO'
        
        _register_status_routes(app, 'testing')
        
        with app.test_client() as client:
            response = client.get('/config')
            assert response.status_code == 200
            data = response.get_json()
            assert data['database_uri'] == 'sqlite:///test.db'


@pytest.mark.unit
class TestCreateApp:
    """Tests para create_app."""
    
    def test_create_app_with_config_name(self):
        """Test: Crear app con nombre de configuración."""
        with patch('app._resolve_config_name', return_value='testing') as mock_resolve:
            with patch('app._build_flask_app') as mock_build:
                with patch('app._load_configuration') as mock_load:
                    with patch('app._configure_cors') as mock_cors:
                        with patch('app._register_preflight_handler') as mock_preflight:
                            with patch('app._initialize_extensions') as mock_ext:
                                with patch('app._register_blueprints') as mock_bp:
                                    with patch('app._register_status_routes') as mock_status:
                                        mock_app = Flask(__name__)
                                        mock_build.return_value = mock_app
                                        
                                        create_app('production')
                                        
                                        mock_resolve.assert_called_once_with('production')
                                        mock_build.assert_called_once()
                                        mock_load.assert_called_once_with(mock_app, 'testing')
                                        mock_cors.assert_called_once_with(mock_app)
                                        mock_preflight.assert_called_once_with(mock_app)
                                        mock_ext.assert_called_once_with(mock_app)
                                        mock_bp.assert_called_once_with(mock_app)
                                        mock_status.assert_called_once_with(mock_app, 'testing')
    
    def test_create_app_with_none_config_name(self):
        """Test: Crear app con config_name None usa FLASK_ENV."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}, clear=False):
            with patch('app._resolve_config_name', return_value='production') as mock_resolve:
                with patch('app._build_flask_app') as mock_build:
                    with patch('app._load_configuration'):
                        with patch('app._configure_cors'):
                            with patch('app._register_preflight_handler'):
                                with patch('app._initialize_extensions') as mock_ext:
                                    with patch('app._register_blueprints'):
                                        with patch('app._register_status_routes'):
                                            mock_app = Flask(__name__)
                                            mock_build.return_value = mock_app
                                            
                                            create_app(None)
                                            
                                            mock_resolve.assert_called_once_with(None)
                                            mock_ext.assert_called_once_with(mock_app)
    
    def test_create_app_returns_flask_instance(self):
        """Test: create_app retorna instancia de Flask."""
        app = create_app('testing')
        assert isinstance(app, Flask)
    
    def test_create_app_registers_status_routes(self):
        """Test: create_app registra rutas de estado."""
        app = create_app('testing')
        
        with app.test_client() as client:
            # Verificar ruta index
            response = client.get('/')
            assert response.status_code == 200
            
            # Verificar ruta health
            response = client.get('/health')
            assert response.status_code == 200


@pytest.mark.unit
class TestInitializeScheduler:
    """Tests para _initialize_scheduler."""
    
    def test_initialize_scheduler_success(self):
        """Test: Inicializar scheduler exitosamente."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        mock_init_scheduler = MagicMock()
        
        with patch('src.utils.scheduler.init_scheduler', mock_init_scheduler):
            _initialize_scheduler(app)
            
            mock_init_scheduler.assert_called_once_with(app)
            app.logger.info.assert_called_once()
            assert 'Scheduler' in app.logger.info.call_args[0][0]
    
    def test_initialize_scheduler_import_error(self):
        """Test: Inicializar scheduler con ImportError."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        with patch('src.utils.scheduler.init_scheduler', side_effect=ImportError('Module not found')):
            _initialize_scheduler(app)
            
            app.logger.warning.assert_called_once()
            assert 'No se pudo inicializar el scheduler' in app.logger.warning.call_args[0][0]
    
    def test_initialize_scheduler_generic_exception(self):
        """Test: Inicializar scheduler con Exception genérica."""
        app = Flask(__name__)
        app.logger = MagicMock()
        
        with patch('src.utils.scheduler.init_scheduler', side_effect=Exception('Generic error')):
            _initialize_scheduler(app)
            
            app.logger.error.assert_called_once()
            assert 'Error inicializando scheduler' in app.logger.error.call_args[0][0]


@pytest.mark.unit
class TestShutdownHandler:
    """Tests para shutdown_handler."""
    
    def test_shutdown_handler_success(self):
        """Test: shutdown_handler exitoso."""
        mock_shutdown_scheduler = MagicMock()
        
        with patch('src.utils.scheduler.shutdown_scheduler', mock_shutdown_scheduler):
            shutdown_handler()
            
            mock_shutdown_scheduler.assert_called_once()
    
    def test_shutdown_handler_with_exception(self):
        """Test: shutdown_handler con Exception (debe manejarse silenciosamente)."""
        with patch('src.utils.scheduler.shutdown_scheduler', side_effect=Exception('Error')):
            # No debe lanzar excepción
            shutdown_handler()


@pytest.mark.unit
class TestRegisterAuthBlueprints:
    """Tests para _register_auth_blueprints."""
    
    def test_register_auth_blueprints(self):
        """Test: Registrar blueprints de autenticación."""
        app = Flask(__name__)
        
        mock_registrar_auth_routes = MagicMock()
        mock_registrar_auth_reset_routes = MagicMock()
        
        with patch('src.routes.auth_routes.registrar_auth_routes', mock_registrar_auth_routes):
            with patch('src.routes.auth_reset.registrar_auth_reset_routes', mock_registrar_auth_reset_routes):
                _register_auth_blueprints(app)
                
                mock_registrar_auth_routes.assert_called_once_with(app)
                mock_registrar_auth_reset_routes.assert_called_once_with(app)


@pytest.mark.unit
class TestRegisterDomainBlueprints:
    """Tests para _register_domain_blueprints."""
    
    def test_register_domain_blueprints(self):
        """Test: Registrar blueprints del dominio."""
        app = Flask(__name__)
        
        # Mock de app.register_blueprint
        mock_register_blueprint = MagicMock()
        app.register_blueprint = mock_register_blueprint
        
        # Mock de blueprints (solo necesitamos que sean objetos Blueprint)
        from flask import Blueprint
        
        mock_pagos_bp = Blueprint('pagos', __name__)
        mock_catalogos_bp = Blueprint('catalogos', __name__)
        mock_dynamic_data_bp = Blueprint('dynamic_data', __name__)
        mock_personas_bp = Blueprint('personas', __name__)
        mock_eventos_bp = Blueprint('eventos', __name__)
        mock_usuarios_bp = Blueprint('usuarios', __name__)
        mock_deportistas_bp = Blueprint('deportistas', __name__)
        mock_galeria_bp = Blueprint('galeria', __name__)
        mock_archivos_bp = Blueprint('archivos', __name__)
        mock_mensualidades_bp = Blueprint('mensualidades', __name__)
        
        with patch('src.routes.pagos_routes.pagos_bp', mock_pagos_bp):
            with patch('src.routes.catalogos_routes.catalogos_bp', mock_catalogos_bp):
                with patch('src.routes.dynamic_data_routes.dynamic_data_bp', mock_dynamic_data_bp):
                    with patch('src.routes.personas_routes.personas_bp', mock_personas_bp):
                        with patch('src.routes.eventos_routes.eventos_bp', mock_eventos_bp):
                            with patch('src.routes.usuarios_routes.usuarios_bp', mock_usuarios_bp):
                                with patch('src.routes.deportistas_routes.deportistas_bp', mock_deportistas_bp):
                                    with patch('src.routes.galeria_routes.galeria_bp', mock_galeria_bp):
                                        with patch('src.routes.archivos_routes.archivos_bp', mock_archivos_bp):
                                            with patch('src.routes.mensualidades_routes.mensualidades_bp', mock_mensualidades_bp):
                                                _register_domain_blueprints(app)
                                                
                                                # Verificar que se registraron los blueprints
                                                assert mock_register_blueprint.call_count == 10
                                                
                                                # Verificar que algunos se llamaron con url_prefix
                                                calls_with_prefix = [
                                                    c for c in mock_register_blueprint.call_args_list 
                                                    if len(c) > 1 and c[1] and 'url_prefix' in c[1]
                                                ]
                                                assert len(calls_with_prefix) > 0
    
    def test_register_domain_blueprints_with_prefix(self):
        """Test: Registrar blueprints del dominio con prefijos."""
        app = Flask(__name__)
        app.register_blueprint = MagicMock()
        
        from flask import Blueprint
        
        mock_pagos_bp = Blueprint('pagos', __name__)
        mock_catalogos_bp = Blueprint('catalogos', __name__)
        
        with patch('src.routes.pagos_routes.pagos_bp', mock_pagos_bp):
            with patch('src.routes.catalogos_routes.catalogos_bp', mock_catalogos_bp):
                with patch('src.routes.dynamic_data_routes.dynamic_data_bp', mock_catalogos_bp):
                    with patch('src.routes.personas_routes.personas_bp', mock_catalogos_bp):
                        with patch('src.routes.eventos_routes.eventos_bp', mock_catalogos_bp):
                            with patch('src.routes.usuarios_routes.usuarios_bp', mock_catalogos_bp):
                                with patch('src.routes.deportistas_routes.deportistas_bp', mock_pagos_bp):
                                    with patch('src.routes.galeria_routes.galeria_bp', mock_catalogos_bp):
                                        with patch('src.routes.archivos_routes.archivos_bp', mock_catalogos_bp):
                                            with patch('src.routes.mensualidades_routes.mensualidades_bp', mock_catalogos_bp):
                                                _register_domain_blueprints(app)
                                                
                                                # Verificar que se registraron todos los blueprints
                                                assert app.register_blueprint.call_count == 10
                                                
                                                # Verificar que todos los blueprints se registraron
                                                assert app.register_blueprint.call_count == 10


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests para el endpoint /health."""
    
    def test_health_endpoint_with_connected_database(self):
        """Test: Health endpoint con base de datos conectada."""
        app = create_app('testing')
        
        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
            assert 'database' in data
            assert data['environment'] == 'testing'
    
    def test_health_endpoint_with_disconnected_database(self):
        """Test: Health endpoint sin base de datos."""
        app = Flask(__name__)
        app.config['DEBUG'] = False
        
        with patch('app.db') as mock_db:
            mock_db.engine = None
            _register_status_routes(app, 'testing')
            
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['database'] == 'disconnected'


@pytest.mark.unit
class TestSelectOriginForResponse:
    """Tests adicionales para _select_origin_for_response."""
    
    def test_select_origin_with_empty_tuple_origins(self):
        """Test: Seleccionar origin con tupla vacía."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ()
        
        result = _select_origin_for_response(app, None)
        assert result is None
    
    def test_select_origin_with_first_origin_string(self):
        """Test: Seleccionar primer origin cuando hay múltiples."""
        app = Flask(__name__)
        app.config['EFFECTIVE_CORS_ORIGINS'] = ['http://example.com', 'http://test.com']
        
        result = _select_origin_for_response(app, None)
        assert result == 'http://example.com'


@pytest.mark.unit
class TestConfigureCorsAdditionalCases:
    """Tests adicionales para _configure_cors."""
    
    def test_configure_cors_with_custom_methods_and_headers(self):
        """Test: Configurar CORS con métodos y headers personalizados."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['http://localhost:3000']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = False
        app.config['CORS_METHODS'] = ['GET', 'POST']
        app.config['CORS_HEADERS'] = ['Content-Type', 'X-Custom-Header']
        app.logger = MagicMock()
        
        with patch('app.CORS') as mock_cors:
            _configure_cors(app)
            
            call_args = mock_cors.call_args
            assert call_args[1]['methods'] == ['GET', 'POST']
            assert call_args[1]['allow_headers'] == ['Content-Type', 'X-Custom-Header']
    
    def test_configure_cors_sets_effective_origins(self):
        """Test: Configurar CORS establece EFFECTIVE_CORS_ORIGINS."""
        app = Flask(__name__)
        app.config['CORS_ORIGINS'] = ['http://localhost:3000', 'http://example.com']
        app.config['CORS_SUPPORTS_CREDENTIALS'] = False
        app.logger = MagicMock()
        
        with patch('app.CORS'):
            result = _configure_cors(app)
            
            assert 'EFFECTIVE_CORS_ORIGINS' in app.config
            assert 'EFFECTIVE_CORS_SUPPORTS_CREDENTIALS' in app.config
            assert app.config['EFFECTIVE_CORS_ORIGINS'] == ('http://localhost:3000', 'http://example.com')
            assert isinstance(result, tuple)


@pytest.mark.unit
class TestNormalizeOriginsAdditionalCases:
    """Tests adicionales para _normalize_origins."""
    
    def test_normalize_origins_with_none_values(self):
        """Test: Normalizar orígenes con valores None."""
        origins = ['http://localhost:3000', None, 'http://example.com']
        result = _normalize_origins(origins)
        
        assert result == ['http://localhost:3000', 'http://example.com']
    
    def test_normalize_origins_removes_whitespace(self):
        """Test: Normalizar orígenes elimina espacios."""
        origins = ['  http://localhost:3000  ', '\thttps://example.com\n']
        result = _normalize_origins(origins)
        
        assert result == ['http://localhost:3000', 'https://example.com']


@pytest.mark.unit  
class TestLoadConfiguration:
    """Tests adicionales para _load_configuration."""
    
    def test_load_configuration_calls_from_object(self):
        """Test: Cargar configuración llama from_object."""
        app = Flask(__name__)
        mock_config = MagicMock()
        app.logger = MagicMock()
        
        with patch('app.config') as mock_config_module:
            mock_config_module.__getitem__.return_value = mock_config
            with patch('app.validate_config', return_value=(True, [])):
                with patch.object(app.config, 'from_object') as mock_from_object:
                    _load_configuration(app, 'development')
                    
                    mock_config_module.__getitem__.assert_called_once_with('development')
                    mock_from_object.assert_called_once_with(mock_config)

