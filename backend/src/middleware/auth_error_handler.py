"""
Middleware para manejo de errores de autenticación y tokens.
"""

from flask import request, jsonify, g
from functools import wraps
import jwt
from datetime import datetime

def handle_auth_errors(f):
    """
    Decorador para manejar errores de autenticación de forma consistente.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error': 'Token expirado',
                'message': 'Por favor inicia sesión nuevamente',
                'status_code': 401
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error': 'Token inválido',
                'message': 'Por favor inicia sesión nuevamente',
                'status_code': 401
            }), 401
        except Exception as e:
            # Log del error
            from src.utils.logger import obtener_registrador
            logger = obtener_registrador('aplicacion')
            logger.error(f'Error inesperado en autenticación: {str(e)}')
            
            return jsonify({
                'success': False,
                'error': 'Error interno del servidor',
                'message': 'Por favor intenta nuevamente',
                'status_code': 500
            }), 500
    
    return decorated_function


def validate_token_format(token):
    """
    Valida que el token tenga el formato correcto.
    """
    if not token:
        return False
    
    # Un JWT válido debe tener 3 partes separadas por puntos
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    return True


def get_token_from_request():
    """
    Extrae el token JWT del header Authorization de la request.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # Verificar formato "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    token = parts[1]
    if not validate_token_format(token):
        return None
    
    return token
