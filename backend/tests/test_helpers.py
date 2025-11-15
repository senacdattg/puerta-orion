"""
Utilidades y helpers para tests.

Este módulo contiene funciones auxiliares que se pueden usar en todos los tests
para mantener el código DRY y seguir el principio AAA (Arrange-Act-Assert).
"""

from typing import Dict, Any, Optional
from flask import Response
from flask.testing import FlaskClient


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


def make_json_request(
    client: FlaskClient,
    method: str,
    url: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Response:
    """
    Realiza una petición JSON de forma conveniente.
    
    Args:
        client: Cliente de Flask
        method: Método HTTP (GET, POST, PUT, DELETE, etc.)
        url: URL del endpoint
        data: Datos JSON a enviar (opcional)
        headers: Headers HTTP adicionales (opcional)
    
    Returns:
        Respuesta HTTP
    """
    default_headers = {'Content-Type': 'application/json'}
    if headers:
        default_headers.update(headers)
    
    if method.upper() == 'GET':
        return client.get(url, headers=default_headers)
    elif method.upper() == 'POST':
        return client.post(url, json=data or {}, headers=default_headers)
    elif method.upper() == 'PUT':
        return client.put(url, json=data or {}, headers=default_headers)
    elif method.upper() == 'PATCH':
        return client.patch(url, json=data or {}, headers=default_headers)
    elif method.upper() == 'DELETE':
        return client.delete(url, headers=default_headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


def create_auth_headers(token: str) -> Dict[str, str]:
    """
    Crea headers de autenticación.
    
    Args:
        token: Token JWT
    
    Returns:
        Diccionario con headers de autenticación
    """
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

