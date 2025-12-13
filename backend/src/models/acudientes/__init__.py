"""
Módulo de acudientes.

Contiene los modelos relacionados con acudientes y sus relaciones.
"""

from .acudiente import Acudiente
from .deportista_acudiente import DeportistaAcudiente
from .parentesco import Parentesco

__all__ = [
    'Acudiente',
    'DeportistaAcudiente', 
    'Parentesco'
]
