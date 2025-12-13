"""
Módulo de modelos relacionados con roles y permisos.
"""

from .rol import Rol
from .permiso import Permiso
from .rol_permiso import RolPermiso
from .usuario_rol import UsuarioRol

__all__ = [
    'Rol',
    'Permiso',
    'RolPermiso',
    'UsuarioRol',
]
