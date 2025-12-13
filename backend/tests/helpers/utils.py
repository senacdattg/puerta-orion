"""
Utilidades y helpers adicionales para tests.

Este módulo contiene funciones auxiliares que complementan
las funciones en assertions.py y requests.py.
"""

import os
from typing import Any
from flask import Response
import jwt
from datetime import datetime, timedelta, timezone


def assert_json_response(
    response: Response,
    expected_status: int = 200,
    has_success: bool = True
) -> dict[str, Any]:
    """
    Helper para validar respuestas JSON.
    
    Args:
        response: Respuesta del cliente de Flask
        expected_status: Código de estado HTTP esperado
        has_success: Si la respuesta debe tener success=True
    
    Returns:
        Datos JSON de la respuesta
    """
    assert response.status_code == expected_status
    assert response.is_json
    
    data = response.get_json()
    assert 'success' in data
    
    if has_success:
        assert data['success'] is True
    else:
        assert data['success'] is False
    
    return data


def create_auth_token(user_id: int, username: str) -> str:
    """
    Crea un token JWT de prueba.
    
    Args:
        user_id: ID del usuario
        username: Nombre de usuario
    
    Returns:
        Token JWT como string
    """
    payload = {
        'usuario_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1),
        'iat': datetime.now(timezone.utc)
    }
    
    secret = os.getenv('JWT_SECRET_KEY', 'test_secret_key')  # nosonar: S2068, S6418 - Test secret fallback only, never used in production
    return jwt.encode(payload, secret, algorithm='HS256')

