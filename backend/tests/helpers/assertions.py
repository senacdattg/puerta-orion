"""
Assertions personalizadas para tests.

Funciones de validación reutilizables que mejoran la legibilidad
y mantienen consistencia en las aserciones de los tests.
"""

from typing import Dict, Any, Optional
from flask import Response


def assert_success_response(
    response: Response,
    expected_status: int = 200,
    expected_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Valida que una respuesta sea exitosa.
    
    Args:
        response: Respuesta HTTP de Flask
        expected_status: Código de estado esperado
        expected_message: Mensaje esperado (opcional)
    
    Returns:
        Datos JSON de la respuesta
    
    Raises:
        AssertionError: Si la respuesta no es exitosa
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    assert response.is_json, "Response should be JSON"
    
    data = response.get_json()
    assert 'success' in data, "Response should have 'success' field"
    assert data['success'] is True, f"Expected success=True, got {data.get('success')}"
    
    if expected_message:
        assert 'message' in data, "Response should have 'message' field"
        assert expected_message in data['message'], \
            f"Expected message containing '{expected_message}', got '{data.get('message')}'"
    
    return data


def assert_error_response(
    response: Response,
    expected_status: int = 400,
    expected_error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Valida que una respuesta sea de error.
    
    Args:
        response: Respuesta HTTP de Flask
        expected_status: Código de estado esperado
        expected_error: Mensaje de error esperado (opcional)
    
    Returns:
        Datos JSON de la respuesta
    
    Raises:
        AssertionError: Si la respuesta no es de error
    """
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}"
    assert response.is_json, "Response should be JSON"
    
    data = response.get_json()
    assert 'success' in data, "Response should have 'success' field"
    assert data['success'] is False, f"Expected success=False, got {data.get('success')}"
    assert 'error' in data, "Error response should have 'error' field"
    
    if expected_error:
        assert expected_error in data['error'], \
            f"Expected error containing '{expected_error}', got '{data.get('error')}'"
    
    return data

