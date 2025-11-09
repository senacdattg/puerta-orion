"""
Servicio centralizado para la gestión de roles, permisos y visibilidad de paneles.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union

from flask import current_app

from src.models.deportistas.deportista import Deportista
from src.models.roles_y_permisos.rol import Rol
from src.models.usuarios.usuario import Usuario
from src.utils.logger import obtener_registrador


class RoleNames:
    SUPERADMIN = 'SuperAdmin'
    ADMINISTRADOR = 'Administrador'
    ENTRENADOR = 'Entrenador'
    DEPORTISTA = 'Deportista'
    ACUDIENTE = 'Acudiente'
    USUARIO = 'usuario'


ROLE_PRIORITY: Tuple[str, ...] = (
    RoleNames.SUPERADMIN,
    RoleNames.ADMINISTRADOR,
    RoleNames.ENTRENADOR,
    RoleNames.ACUDIENTE,
    RoleNames.DEPORTISTA,
    RoleNames.USUARIO,
)


# Módulos disponibles en el dashboard y roles que pueden visualizarlos
MODULE_ACCESS: Dict[str, Set[str]] = {
    'perfil': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
        RoleNames.ACUDIENTE,
        RoleNames.DEPORTISTA,
        RoleNames.USUARIO,
    },
    'calendario': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
        RoleNames.ACUDIENTE,
        RoleNames.DEPORTISTA,
        RoleNames.USUARIO,
    },
    'galeria': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
        RoleNames.ACUDIENTE,
        RoleNames.DEPORTISTA,
        RoleNames.USUARIO,
    },
    'mensualidades': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
        RoleNames.ACUDIENTE,
    },
    'deportistas': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
    },
    'eventos': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
        RoleNames.DEPORTISTA,
        RoleNames.ACUDIENTE,
    },
    'galeria_admin': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
        RoleNames.ENTRENADOR,
    },
    'panel_admin': {
        RoleNames.SUPERADMIN,
        RoleNames.ADMINISTRADOR,
    },
}


# Reglas para ocultar el rol "usuario" del selector cuando existan roles principales
HIDE_USUARIO_IF_HAS: Set[str] = {
    RoleNames.ACUDIENTE,
    RoleNames.DEPORTISTA,
    RoleNames.ENTRENADOR,
    RoleNames.ADMINISTRADOR,
    RoleNames.SUPERADMIN,
}


@dataclass(frozen=True)
class PanelVisibility:
    module: str
    allowed: bool


def _get_logger():
    return obtener_registrador('aplicacion')


def normalizar_nombre_rol(nombre: str) -> str:
    if not nombre:
        return ''
    return nombre.strip()


def obtener_roles_usuario(usuario: Usuario) -> Set[str]:
    if not usuario or not getattr(usuario, 'roles', None):
        return set()
    return {normalizar_nombre_rol(rol.nombre_rol) for rol in usuario.roles}


def calcular_edad(fecha_nacimiento: Union[date, datetime, int, None]) -> Optional[int]:
    if not fecha_nacimiento:
        return None
    if isinstance(fecha_nacimiento, int):
        fecha_nacimiento = date(fecha_nacimiento, 1, 1)
    elif isinstance(fecha_nacimiento, datetime):
        fecha_nacimiento = fecha_nacimiento.date()
    if not isinstance(fecha_nacimiento, date):
        return None
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year - (
        (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
    )
    return edad


def es_deportista_menor(usuario: Usuario) -> bool:
    if not usuario or not getattr(usuario, 'persona', None):
        return False
    deportista: Optional[Deportista] = Deportista.query.filter_by(
        id_persona=usuario.persona.id_persona
    ).first()
    if not deportista or not deportista.fecha_nacimiento:
        return False
    edad = calcular_edad(deportista.fecha_nacimiento)
    if edad is None:
        return False
    return edad < 18


def filtrar_roles_visibles(usuario: Usuario) -> List[str]:
    roles = obtener_roles_usuario(usuario)
    if not roles:
        return []

    roles_visibles = set(roles)
    if RoleNames.USUARIO in roles_visibles:
        if roles & HIDE_USUARIO_IF_HAS:
            roles_visibles.discard(RoleNames.USUARIO)

        if es_deportista_menor(usuario):
            roles_visibles.discard(RoleNames.USUARIO)

    # Mantener orden por prioridad
    ordered = [role for role in ROLE_PRIORITY if role in roles_visibles]
    if not ordered:
        ordered = list(roles_visibles)
    return ordered


def asegurar_rol_activo_valido(usuario: Usuario, commit: bool = False) -> Optional[Rol]:
    """
    Garantiza que el rol activo del usuario cumpla las reglas de visibilidad.
    Si el rol activo actual no es válido, selecciona otro según prioridad.
    """
    logger = _get_logger()
    roles_visibles = filtrar_roles_visibles(usuario)
    if not roles_visibles:
        usuario.set_rol_activo(None)
        if commit:
            from src.models.base import db
            db.session.commit()
        return None

    active_role_name = usuario.rol_activo.nombre_rol if usuario.rol_activo else None
    if active_role_name in roles_visibles:
        return usuario.rol_activo

    target_role_name = roles_visibles[0]
    nuevo_rol = next(
        (rol for rol in usuario.roles if rol.nombre_rol == target_role_name),
        None
    )
    usuario.set_rol_activo(nuevo_rol)
    logger.info(
        f"Rol activo ajustado automáticamente para usuario {usuario.id_usuario}: {target_role_name}"
    )
    if commit:
        from src.models.base import db
        db.session.commit()
    return nuevo_rol


def obtener_paneles_autorizados(usuario: Usuario) -> List[PanelVisibility]:
    roles_visibles = filtrar_roles_visibles(usuario)
    roles_con_permiso: Set[str] = set()

    rol_activo = usuario.rol_activo.nombre_rol if getattr(usuario, 'rol_activo', None) else None
    if rol_activo and rol_activo in roles_visibles:
        roles_con_permiso.add(rol_activo)
    elif roles_visibles:
        roles_con_permiso.add(roles_visibles[0])

    if RoleNames.USUARIO in obtener_roles_usuario(usuario):
        roles_con_permiso.add(RoleNames.USUARIO)

    paneles: List[PanelVisibility] = []
    for module, roles in MODULE_ACCESS.items():
        permitido = bool(roles_con_permiso & roles)
        paneles.append(PanelVisibility(module=module, allowed=permitido))
    return paneles


def puede_registrarse_como_acudiente(usuario: Usuario, edad_minima: int = 18) -> bool:
    if not usuario or not getattr(usuario, 'persona', None):
        return False

    deportista = Deportista.query.filter_by(id_persona=usuario.persona.id_persona).first()
    if not deportista or not deportista.fecha_nacimiento:
        # Si no es deportista, no hay restricción por edad
        return True

    if es_deportista_menor(usuario):
        return False

    return True


def validar_mayoria_de_edad(fecha_nacimiento: Optional[date], edad_minima: int = 18) -> bool:
    edad = calcular_edad(fecha_nacimiento)
    if edad is None:
        return True
    return edad >= edad_minima


def obtener_roles_para_selector(usuario: Usuario) -> Dict[str, bool]:
    """
    Devuelve un diccionario {rol: visible} para poblar menús de cambio de rol.
    """
    roles_asignados = obtener_roles_usuario(usuario)
    visibles = set(filtrar_roles_visibles(usuario))
    resultado: Dict[str, bool] = {}
    for rol in roles_asignados:
        resultado[rol] = rol in visibles
    return resultado


def cambiar_rol_activo(usuario: Usuario, rol_objetivo: str, commit: bool = True) -> Rol:
    """
    Cambia el rol activo del usuario validando reglas y visibilidad.
    """
    logger = _get_logger()
    roles_selector = obtener_roles_para_selector(usuario)
    rol_objetivo = normalizar_nombre_rol(rol_objetivo)

    if rol_objetivo not in roles_selector:
        raise ValueError(f"El usuario no tiene asignado el rol '{rol_objetivo}'")

    if not roles_selector[rol_objetivo]:
        raise PermissionError(f"El rol '{rol_objetivo}' no está disponible como rol activo para este usuario")

    nuevo_rol = next(
        (rol for rol in usuario.roles if rol.nombre_rol == rol_objetivo),
        None
    )
    if not nuevo_rol:
        raise ValueError(f"No se encontró la definición del rol '{rol_objetivo}'")

    usuario.set_rol_activo(nuevo_rol)
    logger.info(
        f"Usuario {usuario.id_usuario} cambió rol activo a {rol_objetivo}"
    )
    if commit:
        from src.models.base import db
        db.session.commit()
    return nuevo_rol

