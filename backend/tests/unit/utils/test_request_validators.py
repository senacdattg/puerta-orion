"""
Tests para utilidades de validación de requests.

Este módulo contiene tests que verifican las funciones
de validación de solicitudes HTTP.
"""

import pytest
from unittest.mock import MagicMock
from flask import Flask, Request
from src.utils.request_validators import (
    obtener_json_requerido,
    validar_campo_booleano,
    RequestValidationError
)


@pytest.mark.unit
class TestObtenerJsonRequerido:
    """Tests para obtener_json_requerido."""
    
    def test_obtener_json_requerido_success(self, app):
        """Test: Obtener JSON requerido exitosamente."""
        with app.test_request_context(
            json={'id': 1, 'name': 'Test'},
            content_type='application/json'
        ):
            from flask import request as flask_request
            
            result = obtener_json_requerido(
                req=flask_request,
                mensaje_tipo='Debe ser JSON',
                mensaje_vacio='No puede estar vacío'
            )
            
            assert result == {'id': 1, 'name': 'Test'}
    
    def test_obtener_json_requerido_not_json(self, app):
        """Test: Error cuando request no es JSON."""
        with app.test_request_context():
            request = MagicMock(spec=Request)
            request.is_json = False
            
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    req=request,
                    mensaje_tipo='Debe ser JSON',
                    mensaje_vacio='No puede estar vacío'
                )
            
            assert exc_info.value.status_code == 400
            assert str(exc_info.value) == 'Debe ser JSON'
    
    def test_obtener_json_requerido_empty(self, app):
        """Test: Error cuando JSON está vacío."""
        with app.test_request_context():
            request = MagicMock(spec=Request)
            request.is_json = True
            request.get_json = lambda: None
            
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    req=request,
                    mensaje_tipo='Debe ser JSON',
                    mensaje_vacio='No puede estar vacío'
                )
            
            assert exc_info.value.status_code == 400
            assert str(exc_info.value) == 'No puede estar vacío'
    
    def test_obtener_json_requerido_empty_dict(self, app):
        """Test: Error cuando JSON es diccionario vacío."""
        with app.test_request_context():
            request = MagicMock(spec=Request)
            request.is_json = True
            request.get_json = lambda: {}
            
            with pytest.raises(RequestValidationError) as exc_info:
                obtener_json_requerido(
                    req=request,
                    mensaje_tipo='Debe ser JSON',
                    mensaje_vacio='No puede estar vacío'
                )
            
            assert exc_info.value.status_code == 400


@pytest.mark.unit
class TestValidarCampoBooleano:
    """Tests para validar_campo_booleano."""
    
    def test_validar_campo_booleano_true(self):
        """Test: Validar campo booleano con valor True."""
        data = {'activo': True}
        
        result = validar_campo_booleano(
            data=data,
            campo='activo',
            mensaje_faltante='Campo faltante',
            mensaje_tipo='Debe ser booleano'
        )
        
        assert result is True
    
    def test_validar_campo_booleano_false(self):
        """Test: Validar campo booleano con valor False."""
        data = {'activo': False}
        
        result = validar_campo_booleano(
            data=data,
            campo='activo',
            mensaje_faltante='Campo faltante',
            mensaje_tipo='Debe ser booleano'
        )
        
        assert result is False
    
    def test_validar_campo_booleano_missing(self):
        """Test: Error cuando campo booleano está ausente."""
        data = {'otro_campo': 'valor'}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data=data,
                campo='activo',
                mensaje_faltante='Campo faltante',
                mensaje_tipo='Debe ser booleano'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Campo faltante'
    
    def test_validar_campo_booleano_wrong_type_string(self):
        """Test: Error cuando campo no es booleano (string)."""
        data = {'activo': 'true'}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data=data,
                campo='activo',
                mensaje_faltante='Campo faltante',
                mensaje_tipo='Debe ser booleano'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Debe ser booleano'
    
    def test_validar_campo_booleano_wrong_type_int(self):
        """Test: Error cuando campo no es booleano (int)."""
        data = {'activo': 1}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data=data,
                campo='activo',
                mensaje_faltante='Campo faltante',
                mensaje_tipo='Debe ser booleano'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Debe ser booleano'
    
    def test_validar_campo_booleano_wrong_type_none(self):
        """Test: Error cuando campo es None."""
        data = {'activo': None}
        
        with pytest.raises(RequestValidationError) as exc_info:
            validar_campo_booleano(
                data=data,
                campo='activo',
                mensaje_faltante='Campo faltante',
                mensaje_tipo='Debe ser booleano'
            )
        
        assert exc_info.value.status_code == 400
        assert str(exc_info.value) == 'Debe ser booleano'


@pytest.mark.unit
class TestRequestValidationError:
    """Tests para RequestValidationError."""
    
    def test_request_validation_error_basic(self):
        """Test: Crear RequestValidationError básico."""
        error = RequestValidationError("Error de validación")
        
        assert str(error) == "Error de validación"
        assert error.status_code == 400
    
    def test_request_validation_error_custom_status(self):
        """Test: Crear RequestValidationError con status code personalizado."""
        error = RequestValidationError("Error no encontrado", status_code=404)
        
        assert str(error) == "Error no encontrado"
        assert error.status_code == 404
    
    def test_request_validation_error_inheritance(self):
        """Test: RequestValidationError hereda de ValueError."""
        error = RequestValidationError("Error")
        
        assert isinstance(error, ValueError)
