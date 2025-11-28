"""
Tests for http_responses utility module.

This module contains tests that verify HTTP response building functions,
including success, error, and convenience methods.
"""

import pytest
from flask import Flask

from src.utils.http_responses import (
    HttpResponseBuilder,
    build_response,
    handle_exception
)
from src.utils.error_messages import (
    ERROR_INTERNO_SERVIDOR,
    ERROR_CONTENT_TYPE_JSON,
    ERROR_USUARIO_NO_AUTENTICADO,
    ERROR_RECURSO_NO_ENCONTRADO,
)


@pytest.mark.unit
class TestHttpResponseBuilder:
    """Tests for HttpResponseBuilder class."""
    
    def test_success_with_data(self, app_context):
        """Test: Success response with data."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.success(
                data={'id': 1, 'name': 'Test'},
                message='Operation successful'
            )
            response_data = response.get_json()
            
            assert status_code == 200
            assert response_data['success'] is True
            assert response_data['data'] == {'id': 1, 'name': 'Test'}
            assert response_data['message'] == 'Operation successful'
    
    def test_success_without_data(self, app_context):
        """Test: Success response without data."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.success(
                message='Operation successful'
            )
            response_data = response.get_json()
            
            assert status_code == 200
            assert response_data['success'] is True
            assert 'data' not in response_data
            assert response_data['message'] == 'Operation successful'
    
    def test_success_with_custom_status_code(self, app_context):
        """Test: Success response with custom status code."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.success(
                data={'id': 1},
                status_code=201
            )
            response_data = response.get_json()
            
            assert status_code == 201
            assert response_data['success'] is True
            assert response_data['status_code'] == 201
    
    def test_success_with_kwargs(self, app_context):
        """Test: Success response with additional kwargs."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.success(
                data={'id': 1},
                extra_field='extra_value',
                count=5
            )
            response_data = response.get_json()
            
            assert status_code == 200
            assert response_data['extra_field'] == 'extra_value'
            assert response_data['count'] == 5
    
    def test_error_basic(self, app_context):
        """Test: Basic error response."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.error(
                error='Validation failed',
                message='Invalid input data'
            )
            response_data = response.get_json()
            
            assert status_code == 400
            assert response_data['success'] is False
            assert response_data['error'] == 'Validation failed'
            assert response_data['message'] == 'Invalid input data'
    
    def test_error_with_data(self, app_context):
        """Test: Error response with data."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.error(
                error='Validation failed',
                data={'field': 'email', 'reason': 'Invalid format'}
            )
            response_data = response.get_json()
            
            assert status_code == 400
            assert response_data['data'] == {'field': 'email', 'reason': 'Invalid format'}
    
    def test_error_with_custom_status_code(self, app_context):
        """Test: Error response with custom status code."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.error(
                error='Not found',
                status_code=404
            )
            response_data = response.get_json()
            
            assert status_code == 404
            assert response_data['status_code'] == 404
    
    def test_created(self, app_context):
        """Test: Created response (201)."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.created(
                data={'id': 1},
                message='Resource created'
            )
            response_data = response.get_json()
            
            assert status_code == 201
            assert response_data['success'] is True
            assert response_data['data'] == {'id': 1}
            assert response_data['message'] == 'Resource created'
    
    def test_created_default_message(self, app_context):
        """Test: Created response with default message."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.created(
                data={'id': 1}
            )
            response_data = response.get_json()
            
            assert status_code == 201
            assert response_data['message'] == 'Recurso creado exitosamente'
    
    def test_not_found_default(self, app_context):
        """Test: Not found response with default error."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.not_found()
            response_data = response.get_json()
            
            assert status_code == 404
            assert response_data['success'] is False
            assert response_data['error'] == ERROR_RECURSO_NO_ENCONTRADO
    
    def test_not_found_custom(self, app_context):
        """Test: Not found response with custom error."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.not_found(
                error='User not found',
                message='The requested user does not exist'
            )
            response_data = response.get_json()
            
            assert status_code == 404
            assert response_data['error'] == 'User not found'
            assert response_data['message'] == 'The requested user does not exist'
    
    def test_unauthorized_default(self, app_context):
        """Test: Unauthorized response with default error."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.unauthorized()
            response_data = response.get_json()
            
            assert status_code == 401
            assert response_data['success'] is False
            assert response_data['error'] == ERROR_USUARIO_NO_AUTENTICADO
    
    def test_unauthorized_custom(self, app_context):
        """Test: Unauthorized response with custom error."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.unauthorized(
                error='Token expired',
                message='Please login again'
            )
            response_data = response.get_json()
            
            assert status_code == 401
            assert response_data['error'] == 'Token expired'
            assert response_data['message'] == 'Please login again'
    
    def test_bad_request(self, app_context):
        """Test: Bad request response."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.bad_request(
                error='Invalid input',
                message='The provided data is invalid'
            )
            response_data = response.get_json()
            
            assert status_code == 400
            assert response_data['error'] == 'Invalid input'
            assert response_data['message'] == 'The provided data is invalid'
    
    def test_internal_server_error_default(self, app_context):
        """Test: Internal server error with default message."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.internal_server_error()
            response_data = response.get_json()
            
            assert status_code == 500
            assert response_data['success'] is False
            assert response_data['error'] == ERROR_INTERNO_SERVIDOR
            assert response_data['message'] == 'Contacte al administrador'
    
    def test_internal_server_error_custom(self, app_context):
        """Test: Internal server error with custom message."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.internal_server_error(
                error='Database error',
                message='Please try again later'
            )
            response_data = response.get_json()
            
            assert status_code == 500
            assert response_data['error'] == 'Database error'
            assert response_data['message'] == 'Please try again later'
    
    def test_json_required(self, app_context):
        """Test: JSON required response."""
        with app_context.app_context():
            response, status_code = HttpResponseBuilder.json_required()
            response_data = response.get_json()
            
            assert status_code == 400
            assert response_data['success'] is False
            assert response_data['error'] == ERROR_CONTENT_TYPE_JSON
            assert 'message' in response_data


@pytest.mark.unit
class TestBuildResponse:
    """Tests for build_response convenience function."""
    
    def test_build_response_success(self, app_context):
        """Test: Build success response."""
        with app_context.app_context():
            response, status_code = build_response(
                success=True,
                status_code=200,
                data={'id': 1},
                message='Success'
            )
            response_data = response.get_json()
            
            assert status_code == 200
            assert response_data['success'] is True
            assert response_data['data'] == {'id': 1}
            assert response_data['message'] == 'Success'
            assert response_data['status_code'] == 200
    
    def test_build_response_error(self, app_context):
        """Test: Build error response."""
        with app_context.app_context():
            response, status_code = build_response(
                success=False,
                status_code=400,
                error='Validation failed'
            )
            response_data = response.get_json()
            
            assert status_code == 400
            assert response_data['success'] is False
            assert response_data['error'] == 'Validation failed'
            assert response_data['status_code'] == 400


@pytest.mark.unit
class TestHandleException:
    """Tests for handle_exception function."""
    
    def test_handle_exception(self, app_context):
        """Test: Handle exception and return error response."""
        with app_context.app_context():
            mock_logger = MagicMock()
            exception = ValueError('Test error')
            
            response, status_code = handle_exception(
                exception=exception,
                logger=mock_logger,
                context='test operation'
            )
            response_data = response.get_json()
            
            assert status_code == 500
            assert response_data['success'] is False
            assert response_data['error'] == ERROR_INTERNO_SERVIDOR
            mock_logger.error.assert_called_once()
            assert 'test operation' in mock_logger.error.call_args[0][0]
    
    def test_handle_exception_custom_message(self, app_context):
        """Test: Handle exception with custom message."""
        with app_context.app_context():
            mock_logger = MagicMock()
            exception = ValueError('Test error')
            
            response, status_code = handle_exception(
                exception=exception,
                logger=mock_logger,
                context='test operation',
                custom_message='Custom error message'
            )
            response_data = response.get_json()
            
            assert status_code == 500
            assert response_data['message'] == 'Custom error message'

