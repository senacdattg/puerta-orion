"""
Módulo de modelos relacionados con salud.
"""

from .tipo_enfermedad import TipoEnfermedad
from .diagnostico import Diagnostico
from .diagnostico_deportista import DiagnosticoDeportista

__all__ = [
    'TipoEnfermedad',
    'Diagnostico',
    'DiagnosticoDeportista',
]
