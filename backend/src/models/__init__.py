"""
Módulo principal de modelos.
Importa todos los modelos organizados por módulos.
"""
from .base import db, BaseModel

# Importar módulos completos
from . import personas
from . import categorias
from . import usuarios
from . import eventos
from . import pagos
from . import roles_y_permisos
from . import salud
from . import acudientes
from . import deportistas
from . import catalogos
from . import galeria

# Importar modelos específicos para acceso directo 
from .personas.persona import Persona
from .categorias.categoria import Categoria
from .categorias.ciudad_residencia import CiudadResidencia
from .categorias.grupo_sanguineo import GrupoSanguineo
from .categorias.institucion_registro import InstitucionRegistro
from .categorias.sexo import Sexo
from .categorias.deporte import Deporte
from .categorias.escuela import Escuela

from .eventos.sesion import Sesion
from .eventos.evento import Evento
from .eventos.tipo_evento import TipoEvento
from .pagos.cuota import Cuota
from .pagos.mensualidad import Mensualidad
from .pagos.metodo_pago import MetodoPago
from .pagos.transaccion_mercadopago import TransaccionMercadoPago
from .roles_y_permisos.rol import Rol
from .roles_y_permisos.permiso import Permiso
from .roles_y_permisos.rol_permiso import RolPermiso
from .roles_y_permisos.usuario_rol import UsuarioRol
from .salud.tipo_enfermedad import TipoEnfermedad
from .usuarios.usuario import Usuario
from .acudientes.acudiente import Acudiente
from .acudientes.deportista_acudiente import DeportistaAcudiente
from .acudientes.parentesco import Parentesco
from .deportistas.deportista import Deportista
from .catalogos.tipo_documento import TipoDocumento
from .catalogos.eps import EPS
from .categorias.escuela import Escuela
from .categorias.deporte import Deporte

# Nuevas tablas agregadas
from .deportistas.informacion_deportiva import InformacionDeportiva
from .roles_y_permisos.personas_rol import PersonasRol
from .eventos.sesionAuth import SesionAuth
from .salud.diagnostico import Diagnostico
from .salud.diagnostico_deportista import DiagnosticoDeportista
from .galeria.galeria import Galeria

__all__ = [
    # Base y utilidades
    'db',
    'BaseModel',
    
    # Módulos
    'personas',
    'categorias', 
    'usuarios',
    'eventos',
    'pagos',
    'roles_y_permisos',
    'salud',
    'acudientes',
    'deportistas',
    'catalogos',
    'galeria',
    
    # Modelos principales
    'Persona',
    'Usuario',
    'Deportista',
    'Acudiente',
    'DeportistaAcudiente',
    'Parentesco',
    
    # Modelos de categorías
    'Categoria',
    'CiudadResidencia',
    'GrupoSanguineo',
    'InstitucionRegistro',
    'Sexo',
    'Escuela',
    'Deporte',
    'TipoDocumento',
    'EPS',
    
    # Modelos de eventos
    'Evento',
    'TipoEvento',
    'Sesion',
    'SesionAuth',  # Nueva tabla
    
    # Modelos de pagos
    'Cuota',
    'Mensualidad',
    'MetodoPago',
    'TransaccionMercadoPago',
    
    # Modelos de roles y permisos
    'Rol',
    'Permiso',
    'RolPermiso',
    'UsuarioRol',
    
    # Modelos de salud
    'TipoEnfermedad',
    'Diagnostico',
    'DiagnosticoDeportista',

    # Modelos de deportistas
    'InformacionDeportiva',
    
    # Nuevas tablas agregadas
    'PersonasRol',
    'Galeria',
]