"""
Tests for auth_error_handler middleware.

This module contains tests that verify error handling for authentication,
token format validation, and token extraction from requests.
"""

import pytest
from unittest.mock import patch, MagicMock
import jwt
from flask import Flask, request

from src.middleware.auth_error_handler import (
    handle_auth_errors,
    validate_token_format,
    get_token_from_request
)


@pytest.mark.unit
class TestAuthErrorHandler:
    """Tests for auth_error_handler middleware."""
    
    def test_handle_auth_errors_success(self):
        """Test: Successful function execution without errors."""
        @handle_auth_errors
        def test_function():
            return {'success': True, 'data': 'test'}
        
        result = test_function()
        
        assert result['success'] is True
        assert result['data'] == 'test'
    
    def test_handle_auth_errors_expired_token(self, app_context):
        """Test: Handle ExpiredSignatureError."""
        @handle_auth_errors
        def test_function():
            raise jwt.ExpiredSignatureError('Token expired')
        
        with app_context.app_context():
            response, status_code = test_function()
            response_data = response.get_json()
            
            assert status_code == 401
            assert response_data['success'] is False
            assert response_data['error'] == 'Token expirado'
            assert response_data['message'] == 'Por favor inicia sesión nuevamente'
    
    def test_handle_auth_errors_invalid_token(self, app_context):
        """Test: Handle InvalidTokenError."""
        @handle_auth_errors
        def test_function():
            raise jwt.InvalidTokenError('Invalid token')
        
        with app_context.app_context():
            response, status_code = test_function()
            response_data = response.get_json()
            
            assert status_code == 401
            assert response_data['success'] is False
            assert response_data['error'] == 'Token inválido'
            assert response_data['message'] == 'Por favor inicia sesión nuevamente'
    
    def test_handle_auth_errors_generic_exception(self, app_context):
        """Test: Handle generic exceptions."""
        @handle_auth_errors
        def test_function():
            raise ValueError('Generic error')
        
        with app_context.app_context():
            with patch('src.utils.logger.obtener_registrador') as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log
                
                response, status_code = test_function()
                response_data = response.get_json()
                
                assert status_code == 500
                assert response_data['success'] is False
                assert response_data['error'] == 'Error interno del servidor'
                assert response_data['message'] == 'Por favor intenta nuevamente'
                mock_log.error.assert_called_once()
    
    def test_validate_token_format_valid(self):
        """Test: Valid token format (3 parts separated by dots)."""
        valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        
        result = validate_token_format(valid_token)
        
        assert result is True
    
    def test_validate_token_format_invalid_no_token(self):
        """Test: Invalid token format - no token."""
        result = validate_token_format(None)
        
        assert result is False
    
    def test_validate_token_format_invalid_empty(self):
        """Test: Invalid token format - empty string."""
        result = validate_token_format("")
        
        assert result is False
    
    def test_validate_token_format_invalid_two_parts(self):
        """Test: Invalid token format - only 2 parts."""
        invalid_token = "part1.part2"
        
        result = validate_token_format(invalid_token)
        
        assert result is False
    
    def test_validate_token_format_invalid_four_parts(self):
        """Test: Invalid token format - 4 parts."""
        invalid_token = "part1.part2.part3.part4"
        
        result = validate_token_format(invalid_token)
        
        assert result is False
    
    def test_get_token_from_request_success(self, app_context):
        """Test: Successful token extraction from Authorization header."""
        with app_context.test_request_context(
            headers={'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'}
        ):
            token = get_token_from_request()
            
            assert token is not None
            assert token.startswith('eyJ')
    
    def test_get_token_from_request_no_header(self, app_context):
        """Test: No Authorization header."""
        with app_context.test_request_context():
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_format_no_bearer(self, app_context):
        """Test: Invalid format - no Bearer prefix."""
        with app_context.test_request_context(
            headers={'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'}
        ):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_format_wrong_prefix(self, app_context):
        """Test: Invalid format - wrong prefix."""
        with app_context.test_request_context(
            headers={'Authorization': 'Token eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U'}
        ):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_format_too_many_parts(self, app_context):
        """Test: Invalid format - too many parts in header."""
        with app_context.test_request_context(
            headers={'Authorization': 'Bearer token1 token2 token3'}
        ):
            token = get_token_from_request()
            
            assert token is None
    
    def test_get_token_from_request_invalid_token_format(self, app_context):
        """Test: Invalid token format in header."""
        with app_context.test_request_context(
            headers={'Authorization': 'Bearer invalid.token'}
        ):
            token = get_token_from_request()
            
            assert token is None

