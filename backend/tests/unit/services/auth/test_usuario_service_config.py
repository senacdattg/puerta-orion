"""
Tests para usuario_service_config.py.
"""

import pytest
from src.services.Auth.usuario_service_config import UsuarioServiceConfig, config


@pytest.mark.unit
class TestUsuarioServiceConfig:
    """Tests para la clase UsuarioServiceConfig."""
    
    def test_min_length_clave(self):
        """Test: Verificar longitud mínima de clave."""
        assert UsuarioServiceConfig.MIN_LENGTH_CLAVE == 6
    
    def test_min_length_username(self):
        """Test: Verificar longitud mínima de username."""
        assert UsuarioServiceConfig.MIN_LENGTH_USERNAME == 3
    
    def test_max_length_username(self):
        """Test: Verificar longitud máxima de username."""
        assert UsuarioServiceConfig.MAX_LENGTH_USERNAME == 200
    
    def test_max_length_primer_nombre(self):
        """Test: Verificar longitud máxima de primer nombre."""
        assert UsuarioServiceConfig.MAX_LENGTH_PRIMER_NOMBRE == 50
    
    def test_max_length_primer_apellido(self):
        """Test: Verificar longitud máxima de primer apellido."""
        assert UsuarioServiceConfig.MAX_LENGTH_PRIMER_APELLIDO == 50
    
    def test_max_length_direccion(self):
        """Test: Verificar longitud máxima de dirección."""
        assert UsuarioServiceConfig.MAX_LENGTH_DIRECCION == 50
    
    def test_max_length_email(self):
        """Test: Verificar longitud máxima de email."""
        assert UsuarioServiceConfig.MAX_LENGTH_EMAIL == 50
    
    def test_hash_method(self):
        """Test: Verificar método de hash."""
        assert UsuarioServiceConfig.HASH_METHOD == 'pbkdf2:sha256'
    
    def test_salt_length(self):
        """Test: Verificar longitud de salt."""
        assert UsuarioServiceConfig.SALT_LENGTH == 16
    
    def test_log_configuration(self):
        """Test: Verificar configuración de logging."""
        assert UsuarioServiceConfig.LOG_SUCCESSFUL_REGISTRATIONS is True
        assert UsuarioServiceConfig.LOG_FAILED_ATTEMPTS is True
        assert UsuarioServiceConfig.LOG_VALIDATION_ERRORS is True
    
    def test_database_configuration(self):
        """Test: Verificar configuración de base de datos."""
        assert UsuarioServiceConfig.USE_TRANSACTIONS is True
        assert UsuarioServiceConfig.AUTO_COMMIT is False
    
    def test_response_configuration(self):
        """Test: Verificar configuración de respuesta."""
        assert UsuarioServiceConfig.INCLUDE_PERSONA_DATA is True
        assert UsuarioServiceConfig.INCLUDE_CREATION_DATE is True
        assert UsuarioServiceConfig.EXCLUDE_PASSWORD is True
    
    def test_error_messages_structure(self):
        """Test: Verificar estructura de mensajes de error."""
        error_messages = UsuarioServiceConfig.ERROR_MESSAGES
        
        assert isinstance(error_messages, dict)
        assert 'campos_faltantes' in error_messages
        assert 'email_invalido' in error_messages
        assert 'clave_corta' in error_messages
        assert 'username_corto' in error_messages
        assert 'username_largo' in error_messages
        assert 'nombre_largo' in error_messages
        assert 'apellido_largo' in error_messages
        assert 'documento_duplicado' in error_messages
        assert 'email_duplicado' in error_messages
        assert 'username_duplicado' in error_messages
        assert 'error_integridad' in error_messages
        assert 'error_creacion' in error_messages
        assert 'error_interno' in error_messages
    
    def test_error_messages_content(self):
        """Test: Verificar contenido de mensajes de error."""
        error_messages = UsuarioServiceConfig.ERROR_MESSAGES
        
        assert 'Campos requeridos faltantes' in error_messages['campos_faltantes']
        assert 'Formato de email inválido' in error_messages['email_invalido']
        assert 'La contraseña debe tener' in error_messages['clave_corta']
    
    def test_campos_persona_requeridos(self):
        """Test: Verificar campos requeridos de persona."""
        campos = UsuarioServiceConfig.CAMPOS_PERSONA_REQUERIDOS
        
        assert isinstance(campos, list)
        assert 'primer_nombre' in campos
        assert 'primer_apellido' in campos
        assert 'documento' in campos
        assert 'correo_electronico' in campos
        assert 'direccion' in campos
        assert 'telefono' in campos
        assert 'id_tipo_documento' in campos
        assert 'id_sexo' in campos
    
    def test_campos_usuario_requeridos(self):
        """Test: Verificar campos requeridos de usuario."""
        campos = UsuarioServiceConfig.CAMPOS_USUARIO_REQUERIDOS
        
        assert isinstance(campos, list)
        assert 'usuario' in campos
        assert 'clave' in campos
    
    def test_campos_persona_opcionales(self):
        """Test: Verificar campos opcionales de persona."""
        campos = UsuarioServiceConfig.CAMPOS_PERSONA_OPCIONALES
        
        assert isinstance(campos, list)
        assert 'segundo_nombre' in campos
        assert 'segundo_apellido' in campos
    
    def test_config_instance(self):
        """Test: Verificar que existe instancia global de configuración."""
        assert config is not None
        assert isinstance(config, UsuarioServiceConfig)
    
    def test_config_instance_has_attributes(self):
        """Test: Verificar que la instancia tiene todos los atributos."""
        assert hasattr(config, 'MIN_LENGTH_CLAVE')
        assert hasattr(config, 'MIN_LENGTH_USERNAME')
        assert hasattr(config, 'MAX_LENGTH_USERNAME')
        assert hasattr(config, 'ERROR_MESSAGES')
        assert hasattr(config, 'CAMPOS_PERSONA_REQUERIDOS')
        assert hasattr(config, 'CAMPOS_USUARIO_REQUERIDOS')

