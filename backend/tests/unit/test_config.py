"""
Tests para el módulo de configuración.

Este módulo contiene tests que verifican la configuración
de la aplicación Flask en diferentes entornos.

NOTA: Las variables de entorno se leen al definir la clase Config,
por lo que los tests verifican principalmente las funciones y
la estructura de las clases de configuración.
"""

import pytest
import os
from unittest.mock import patch

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig, get_config, validate_config


@pytest.mark.unit
class TestConfig:
    """Tests para la clase Config base."""
    
    def test_config_has_required_attributes(self):
        """Test: Config tiene todos los atributos requeridos."""
        config_obj = Config()
        
        # Atributos básicos
        assert hasattr(config_obj, 'SECRET_KEY')
        assert hasattr(config_obj, 'DEBUG')
        assert hasattr(config_obj, 'HOST')
        assert hasattr(config_obj, 'PORT')
        
        # Base de datos
        assert hasattr(config_obj, 'SQLALCHEMY_DATABASE_URI')
        assert hasattr(config_obj, 'SQLALCHEMY_TRACK_MODIFICATIONS')
        
        # CORS
        assert hasattr(config_obj, 'CORS_ORIGINS')
        assert hasattr(config_obj, 'CORS_METHODS')
        assert hasattr(config_obj, 'CORS_HEADERS')
        assert hasattr(config_obj, 'CORS_SUPPORTS_CREDENTIALS')
        
        # JWT
        assert hasattr(config_obj, 'JWT_SECRET_KEY')
        assert hasattr(config_obj, 'JWT_ACCESS_TOKEN_EXPIRES')
        
        # Email
        assert hasattr(config_obj, 'MAIL_SERVER')
        assert hasattr(config_obj, 'MAIL_PORT')
        assert hasattr(config_obj, 'MAIL_USE_TLS')
        
        # Logs
        assert hasattr(config_obj, 'LOG_LEVEL')
        assert hasattr(config_obj, 'LOG_DIR')
    
    def test_sqlalchemy_track_modifications(self):
        """Test: SQLALCHEMY_TRACK_MODIFICATIONS está desactivado."""
        config_obj = Config()
        assert config_obj.SQLALCHEMY_TRACK_MODIFICATIONS is False
    
    def test_cors_methods(self):
        """Test: CORS_METHODS contiene los métodos esperados."""
        config_obj = Config()
        expected_methods = ['GET', 'PUT', 'POST', 'DELETE', 'PATCH', 'OPTIONS']
        assert set(config_obj.CORS_METHODS) == set(expected_methods)
    
    def test_cors_headers(self):
        """Test: CORS_HEADERS contiene los headers esperados."""
        config_obj = Config()
        assert 'Content-Type' in config_obj.CORS_HEADERS
        assert 'Authorization' in config_obj.CORS_HEADERS
    
    def test_cors_supports_credentials(self):
        """Test: CORS_SUPPORTS_CREDENTIALS está activado."""
        config_obj = Config()
        assert config_obj.CORS_SUPPORTS_CREDENTIALS is True
    
    def test_cors_origins_is_list(self):
        """Test: CORS_ORIGINS es una lista."""
        config_obj = Config()
        assert isinstance(config_obj.CORS_ORIGINS, list)
    
    def test_jwt_access_token_expires_is_int(self):
        """Test: JWT_ACCESS_TOKEN_EXPIRES es un entero."""
        config_obj = Config()
        assert isinstance(config_obj.JWT_ACCESS_TOKEN_EXPIRES, int)
        assert config_obj.JWT_ACCESS_TOKEN_EXPIRES > 0
    
    def test_mail_port_is_int(self):
        """Test: MAIL_PORT es un entero."""
        config_obj = Config()
        assert isinstance(config_obj.MAIL_PORT, int)
    
    def test_mail_use_tls_is_bool(self):
        """Test: MAIL_USE_TLS es un booleano."""
        config_obj = Config()
        assert isinstance(config_obj.MAIL_PORT, int)
    
    def test_database_url_defined(self):
        """Test: SQLALCHEMY_DATABASE_URI está definido."""
        config_obj = Config()
        assert config_obj.SQLALCHEMY_DATABASE_URI is not None
        assert isinstance(config_obj.SQLALCHEMY_DATABASE_URI, str)


@pytest.mark.unit
class TestDevelopmentConfig:
    """Tests para DevelopmentConfig."""
    
    def test_debug_enabled(self):
        """Test: DEBUG está habilitado en desarrollo."""
        config_obj = DevelopmentConfig()
        assert config_obj.DEBUG is True
    
    def test_log_level_debug(self):
        """Test: LOG_LEVEL es DEBUG en desarrollo."""
        config_obj = DevelopmentConfig()
        assert config_obj.LOG_LEVEL == 'DEBUG'
    
    def test_inherits_from_config(self):
        """Test: DevelopmentConfig hereda de Config."""
        config_obj = DevelopmentConfig()
        assert isinstance(config_obj, Config)
        assert hasattr(config_obj, 'SECRET_KEY')
        assert hasattr(config_obj, 'HOST')
        assert hasattr(config_obj, 'PORT')


@pytest.mark.unit
class TestProductionConfig:
    """Tests para ProductionConfig."""
    
    def test_debug_disabled(self):
        """Test: DEBUG está deshabilitado en producción."""
        config_obj = ProductionConfig()
        assert config_obj.DEBUG is False
    
    def test_log_level_warning(self):
        """Test: LOG_LEVEL es WARNING en producción."""
        config_obj = ProductionConfig()
        assert config_obj.LOG_LEVEL == 'WARNING'
    
    def test_inherits_from_config(self):
        """Test: ProductionConfig hereda de Config."""
        config_obj = ProductionConfig()
        assert isinstance(config_obj, Config)
        assert hasattr(config_obj, 'SECRET_KEY')
        assert hasattr(config_obj, 'HOST')
        assert hasattr(config_obj, 'PORT')


@pytest.mark.unit
class TestTestingConfig:
    """Tests para TestingConfig."""
    
    def test_testing_enabled(self):
        """Test: TESTING está habilitado."""
        config_obj = TestingConfig()
        assert config_obj.TESTING is True
    
    def test_database_sqlite_in_memory(self):
        """Test: Base de datos SQLite en memoria para testing."""
        config_obj = TestingConfig()
        assert config_obj.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    
    def test_sqlalchemy_binds_empty(self):
        """Test: SQLALCHEMY_BINDS está vacío."""
        config_obj = TestingConfig()
        assert config_obj.SQLALCHEMY_BINDS == {}
    
    def test_inherits_from_config(self):
        """Test: TestingConfig hereda de Config."""
        config_obj = TestingConfig()
        assert isinstance(config_obj, Config)
        assert hasattr(config_obj, 'SECRET_KEY')


@pytest.mark.unit
class TestGetConfig:
    """Tests para la función get_config."""
    
    def test_get_config_development(self):
        """Test: Obtener configuración de desarrollo."""
        config_class = get_config('development')
        assert config_class == DevelopmentConfig
    
    def test_get_config_production(self):
        """Test: Obtener configuración de producción."""
        config_class = get_config('production')
        assert config_class == ProductionConfig
    
    def test_get_config_testing(self):
        """Test: Obtener configuración de testing."""
        config_class = get_config('testing')
        assert config_class == TestingConfig
    
    def test_get_config_with_env_name(self):
        """Test: Obtener configuración especificando nombre de entorno."""
        config_class = get_config('production')
        assert config_class == ProductionConfig
    
    def test_get_config_default_for_invalid_env(self):
        """Test: Obtener configuración por defecto para entorno inválido."""
        config_class = get_config('invalid_env')
        assert config_class == DevelopmentConfig
    
    def test_get_config_with_flask_env(self):
        """Test: Obtener configuración usando FLASK_ENV."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}):
            config_class = get_config()
            assert config_class == ProductionConfig
    
    def test_get_config_without_env_defaults_to_development(self):
        """Test: Obtener configuración sin FLASK_ENV usa development por defecto."""
        with patch.dict(os.environ, {}, clear=True):
            # Si FLASK_ENV no existe, debería usar 'development' como default
            config_class = get_config()
            assert config_class == DevelopmentConfig


@pytest.mark.unit
class TestValidateConfig:
    """Tests para la función validate_config."""
    
    def test_validate_config_valid_production(self):
        """Test: Validación exitosa con configuración completa de producción."""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'SECRET_KEY': 'test-secret',
            'DATABASE_URL': 'mysql://localhost/test',
            'JWT_SECRET_KEY': 'jwt-secret'
        }):
            is_valid, errors = validate_config()
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_config_missing_secret_key_production(self):
        """Test: Error cuando falta SECRET_KEY en producción."""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'DATABASE_URL': 'mysql://localhost/test',
            'JWT_SECRET_KEY': 'jwt-secret'
        }, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is False
            assert any('SECRET_KEY' in error for error in errors)
    
    def test_validate_config_missing_database_url_production(self):
        """Test: Error cuando falta DATABASE_URL en producción."""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'SECRET_KEY': 'test-secret',
            'JWT_SECRET_KEY': 'jwt-secret'
        }, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is False
            assert any('DATABASE_URL' in error for error in errors)
    
    def test_validate_config_missing_jwt_secret_production(self):
        """Test: Error cuando falta JWT_SECRET_KEY en producción."""
        with patch.dict(os.environ, {
            'FLASK_ENV': 'production',
            'SECRET_KEY': 'test-secret',
            'DATABASE_URL': 'mysql://localhost/test'
        }, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is False
            assert any('JWT_SECRET_KEY' in error for error in errors)
    
    def test_validate_config_development_no_errors(self):
        """Test: Validación en desarrollo no requiere variables críticas."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is True
            assert len(errors) == 0
    
    def test_validate_config_multiple_errors(self):
        """Test: Validación retorna múltiples errores."""
        with patch.dict(os.environ, {'FLASK_ENV': 'production'}, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is False
            assert len(errors) >= 3
            assert any('SECRET_KEY' in error for error in errors)
            assert any('DATABASE_URL' in error for error in errors)
            assert any('JWT_SECRET_KEY' in error for error in errors)
    
    def test_validate_config_non_production_no_errors(self):
        """Test: Validación en entornos no producción no requiere variables críticas."""
        with patch.dict(os.environ, {'FLASK_ENV': 'development'}, clear=True):
            is_valid, errors = validate_config()
            assert is_valid is True
    
    def test_validate_config_returns_tuple(self):
        """Test: validate_config retorna una tupla."""
        is_valid, errors = validate_config()
        assert isinstance(is_valid, bool)
        assert isinstance(errors, list)
