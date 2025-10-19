"""
Módulo de rutas de la aplicación.
"""

from .pagos_routes import pagos_bp
from .catalogos_routes import catalogos_bp
from .dynamic_data_routes import dynamic_data_bp
from .personas_routes import personas_bp
from .eventos_routes import eventos_bp

__all__ = [
    'pagos_bp',
    'catalogos_bp',
    'dynamic_data_bp',
    'personas_bp',
    'eventos_bp',
]
