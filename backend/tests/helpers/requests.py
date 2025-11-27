"""
Utilidades para realizar requests HTTP en tests.

Funciones auxiliares para simplificar las peticiones HTTP
en los tests de integración.
"""

from typing import Dict, Any, Optional
from flask import Response
from flask.testing import FlaskClient


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
    
    method_upper = method.upper()
    if method_upper == 'GET':
        return client.get(url, headers=default_headers)
    elif method_upper == 'POST':
        return client.post(url, json=data or {}, headers=default_headers)
    elif method_upper == 'PUT':
        return client.put(url, json=data or {}, headers=default_headers)
    elif method_upper == 'PATCH':
        return client.patch(url, json=data or {}, headers=default_headers)
    elif method_upper == 'DELETE':
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

