"""
Módulo de modelos para la aplicación Puerta Orion.
Importa todos los modelos de la base de datos de manera organizada.
Cada tabla tiene su propio archivo de modelo siguiendo el principio SRP.
"""

# Importar configuración de base de datos
from ..database.database import db, init_database, create_tables, drop_tables

# Importar modelos individuales - Catálogos
from .tipo_documento import TipoDocumento
from .ciudad_residencia import CiudadResidencia
from .grupo_sanguineo import GrupoSanguineo
from .institucion_registro import InstitucionRegistro
from .eps import EPS
from .sexo import Sexo
from .tipo_enfermedad import TipoEnfermedad
from .enfermedad import Enfermedad
from .metodo_pago import MetodoPago
from .categoria import Categoria
from .tipo_evento import TipoEvento
from .sesion import Sesion

# Importar modelos individuales - Usuarios
from .permiso import Permiso
from .rol import Rol
from .usuario import Usuario
from .rol_usuario import RolUsuario

# Importar modelo principal
from .Personas import Persona

# Importar modelos individuales - Pagos
from .cuota import Cuota
from .mensualidad import Mensualidad

# Importar modelos individuales - Eventos
from .evento import Evento

# Importar tablas de asociación
from .rol_permiso import rol_permiso
from .usuario_rol import usuario_rol

# Lista de todos los modelos para facilitar la importación
__all__ = [
    # Configuración de base de datos
    'db',
    'init_database',
    'create_tables',
    'drop_tables',
    
    # Modelos de catálogos
    'TipoDocumento',
    'CiudadResidencia',
    'GrupoSanguineo',
    'InstitucionRegistro',
    'EPS',
    'Sexo',
    'TipoEnfermedad',
    'Enfermedad',
    'MetodoPago',
    'Categoria',
    'TipoEvento',
    'Sesion',
    
    # Modelos de usuarios
    'Permiso',
    'Rol',
    'Usuario',
    'RolUsuario',
    
    # Modelo principal
    'Persona',
    
    # Modelos de pagos
    'Cuota',
    'Mensualidad',
    
    # Modelos de eventos
    'Evento',
    
    # Tablas de asociación
    'rol_permiso',
    'usuario_rol'
]


