"""
Módulo de modelos relacionados con categorías.
"""

from .categoria import Categoria
from .ciudad_residencia import CiudadResidencia
from .grupo_sanguineo import GrupoSanguineo
from .institucion_registro import InstitucionRegistro
from .sexo import Sexo
from .escuela import Escuela
from .deporte import Deporte

__all__ = [
    'Categoria',
    'CiudadResidencia',
    'GrupoSanguineo',
    'InstitucionRegistro',
    'Sexo',
    'Escuela',
    'Deporte',
]
