"""
Tests for request_validators utility module.

This module contains tests that verify request validation functions,
including JSON extraction and field validation.
"""

import pytest
from flask import Flask, Request

from src.utils.request_validators import (
    RequestValidationError,
    obtener_json_requerido,
    validar_campo_booleano
)


@pytest.mark.unit
class TestRequestValidationError:
    """Tests for RequestValidationError exception."""
    
    def test_request_validation_error_default_status(self):
        """Test: RequestValidationError with default status code."""
        error = RequestValidationError('Test error')
        
        assert str(error) == 'Test error'
        assert error.status_code == 400
    
    def test_request_validation_error_custom_status(self):
        """Test: RequestValidationError with custom status code."""
        error = RequestValidationError('Test error', status_code=404)
        
        assert str(error) == 'Test error'
        assert error.status_code == 404


@pytest.mark.unit
class TestObtenerJsonRequerido:
    """Tests for obtener_json_requerido function."""
    
    def test_obtener_json_requerido_success(self, app_context):
        """Test: Successful JSON extraction."""
        from flask import request
        with app_context.test_request_context(
            json={'id': 1, 'name': 'Test'},
            content_type='application/json'
        ):
            data = obtener_json_requerido(
                request,
                mensaje_tipo='Invalid content type',
                mensaje_vacio='Empty body'
            )
            
            assert data == {'id': 1, 'name': 'Test'}
    
    def test_obtener_json_requerido_not_json(self, app_context):
        """Test: Request is not JSON."""
        from flask import request
        with app_context.test_request_context(
            data='not json',
            content_type='text/plain'
        ):
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    request,
                    mensaje_tipo='Invalid content type',
                    mensaje_vacio='Empty body'
                )
            
            assert exc_info.value.status_code == 400
            assert str(exc_info.value) == 'Invalid content type'
    
    def test_obtener_json_requerido_empty_body(self, app_context):
        """Test: Empty JSON body."""
        from flask import request
        with app_context.test_request_context(
            data='{}',
            content_type='application/json'
        ):
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    request,
                    mensaje_tipo='Invalid content type',
                    mensaje_vacio='Empty body'
                )
            
            assert exc_info.value.status_code == 400
            assert str(exc_info.value) == 'Empty body'
    
    def test_obtener_json_requerido_empty_dict(self, app_context):
        """Test: Empty JSON dict."""
        from flask import request
        with app_context.test_request_context(
            json={},
            content_type='application/json'
        ):
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    request,
                    mensaje_tipo='Invalid content type',
                    mensaje_vacio='Empty body'
                )
            
            assert exc_info.value.status_code == 400
            assert str(exc_info.value) == 'Empty body'


@pytest.mark.unit
class TestValidarCampoBooleano:
    """Tests for validar_campo_booleano function."""
    
    def test_validar_campo_booleano_success_true(self):
        """Test: Valid boolean field with True value."""
        data = {'active': True}
        
        result = validar_campo_booleano(
            data,
            'active',
            mensaje_faltante='Field missing',
            mensaje_tipo='Invalid type'
        )
        
        assert result is True
    
    def test_validar_campo_booleano_success_false(self):
        """Test: Valid boolean field with False value."""
        data = {'active': False}
        
        result = validar_campo_booleano(
            data,
            'active',
            mensaje_faltante='Field missing',
            mensaje_tipo='Invalid type'
        )
        
        assert result is False
    
    def test_validar_campo_booleano_missing_field(self):
        """Test: Missing boolean field."""
        data = {'other_field': 'value'}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data,
                'active',
                mensaje_faltante='Field missing',
                mensaje_tipo='Invalid type'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Field missing'
    
    def test_validar_campo_booleano_invalid_type_string(self):
        """Test: Invalid type - string instead of boolean."""
        data = {'active': 'true'}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data,
                'active',
                mensaje_faltante='Field missing',
                mensaje_tipo='Invalid type'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Invalid type'
    
    def test_validar_campo_booleano_invalid_type_int(self):
        """Test: Invalid type - integer instead of boolean."""
        data = {'active': 1}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data,
                'active',
                mensaje_faltante='Field missing',
                mensaje_tipo='Invalid type'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Invalid type'
    
    def test_validar_campo_booleano_invalid_type_none(self):
        """Test: Invalid type - None instead of boolean."""
        data = {'active': None}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data,
                'active',
                mensaje_faltante='Field missing',
                mensaje_tipo='Invalid type'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Invalid type'

