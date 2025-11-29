"""
Tests para el manejador de errores de autenticación.

Este módulo contiene tests que verifican el manejo
de errores relacionados con tokens JWT y autenticación.
"""

import pytest
from unittest.mock import patch, MagicMock
import jwt
from flask import Flask

from src.middleware.auth_error_handler import (
    handle_auth_errors,
    validate_token_format,
    get_token_from_request
)


@pytest.mark.unit
class TestAuthErrorHandler:
    """Tests para auth_error_handler."""
    
    @pytest.fixture
    def app(self):
        """Crea una aplicación Flask para testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    # Tests para handle_auth_errors
    def test_handle_auth_errors_success(self, app):
        """Test: Decorador permite ejecución exitosa."""
        @handle_auth_errors
        def test_function():
            return {'success': True, 'data': 'test'}
        
        with app.test_request_context():
            result = test_function()
            
            assert result['success'] is True
            assert result['data'] == 'test'
    
    def test_handle_auth_errors_expired_token(self, app):
        """Test: Manejo de token expirado."""
        @handle_auth_errors
        def test_function():
            raise jwt.ExpiredSignatureError("Token expired")
        
        with app.test_request_context():
            result = test_function()
            
            # El decorador retorna una tupla (response, status_code)
            response, status_code = result
            assert status_code == 401
            assert response.json['success'] is False
            assert response.json['error'] == 'Token expirado'
            assert 'Por favor inicia sesión nuevamente' in response.json['message']
    
    def test_handle_auth_errors_invalid_token(self, app):
        """Test: Manejo de token inválido."""
        @handle_auth_errors
        def test_function():
            raise jwt.InvalidTokenError("Invalid token")
        
        with app.test_request_context():
            result = test_function()
            
            response, status_code = result
            assert status_code == 401
            assert response.json['success'] is False
            assert response.json['error'] == 'Token inválido'
            assert 'Por favor inicia sesión nuevamente' in response.json['message']
    
    def test_handle_auth_errors_generic_exception(self, app):
        """Test: Manejo de excepción genérica."""
        @handle_auth_errors
        def test_function():
            raise ValueError("Generic error")
        
        with app.test_request_context():
            # El logger se importa dentro de la función, así que mockeamos el módulo logger
            with patch('src.utils.logger.obtener_registrador') as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log
                
                result = test_function()
                
                # El decorador siempre retorna una tupla
                response, status_code = result
                assert status_code == 500
                assert response.json['success'] is False
                assert response.json['error'] == 'Error interno del servidor'
                assert 'Por favor intenta nuevamente' in response.json['message']
                mock_log.error.assert_called_once()
    
    # Tests para validate_token_format
    def test_validate_token_format_valid(self):
        """Test: Validar formato de token válido."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        result = validate_token_format(token)
        
        assert result is True
    
    def test_validate_token_format_invalid_short(self):
        """Test: Token con formato inválido (muy corto)."""
        token = "invalid.token"
        
        result = validate_token_format(token)
        
        assert result is False
    
    def test_validate_token_format_invalid_long(self):
        """Test: Token con formato inválido (muy largo)."""
        token = "part1.part2.part3.part4"
        
        result = validate_token_format(token)
        
        assert result is False
    
    def test_validate_token_format_empty(self):
        """Test: Token vacío."""
        token = ""
        
        result = validate_token_format(token)
        
        assert result is False
    
    def test_validate_token_format_none(self):
        """Test: Token None."""
        token = None
        
        result = validate_token_format(token)
        
        assert result is False
    
    # Tests para get_token_from_request
    def test_get_token_from_request_valid(self, app):
        """Test: Obtener token válido del header."""
        with app.test_request_context('/', headers={'Authorization': 'Bearer valid.token.here'}):
            token = get_token_from_request()
            
            assert token == 'valid.token.here'
    
    def test_get_token_from_request_no_header(self, app):
        """Test: No hay header Authorization."""
        with app.test_request_context('/'):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_format(self, app):
        """Test: Formato de header inválido."""
        with app.test_request_context('/', headers={'Authorization': 'InvalidFormat token'}):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_no_bearer(self, app):
        """Test: Header sin prefijo Bearer."""
        with app.test_request_context('/', headers={'Authorization': 'token.only'}):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_token_format(self, app):
        """Test: Token con formato inválido."""
        with app.test_request_context('/', headers={'Authorization': 'Bearer invalid.token'}):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_multiple_spaces(self, app):
        """Test: Header con múltiples espacios."""
        with app.test_request_context('/', headers={'Authorization': 'Bearer  valid.token.here'}):
            token = get_token_from_request()
            
            # Debería extraer el token correctamente
            assert token is not None
