"""
Configuración para passwords de seeders.

Este módulo centraliza la gestión de passwords para los seeders,
permitiendo usar variables de entorno en lugar de valores hardcodeados.

Variables de entorno soportadas:
- SEEDER_SUPERADMIN_PASSWORD: Password para el superadmin (default: 'SuperAdmin2024!')
- SEEDER_ADMIN2_PASSWORD: Password para admin2 (default: 'Admin2024!')
- SEEDER_ADMIN3_PASSWORD: Password para admin3 (default: 'Admin2024!')

⚠️ IMPORTANTE: En producción, siempre usar variables de entorno con passwords seguros.
"""

import os


def get_superadmin_password() -> str:
    """
    Obtiene la password del superadmin desde variables de entorno.
    
    Returns:
        str: Password del superadmin
    """
    return os.environ.get('SEEDER_SUPERADMIN_PASSWORD', 'SuperAdmin2024!')


def get_admin2_password() -> str:
    """
    Obtiene la password de admin2 desde variables de entorno.
    
    Returns:
        str: Password de admin2
    """
    return os.environ.get('SEEDER_ADMIN2_PASSWORD', 'Admin2024!')


def get_admin3_password() -> str:
    """
    Obtiene la password de admin3 desde variables de entorno.
    
    Returns:
        str: Password de admin3
    """
    return os.environ.get('SEEDER_ADMIN3_PASSWORD', 'Admin2024!')

