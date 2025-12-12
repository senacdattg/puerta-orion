
"""
Rutas de gestión de eventos, sesiones y tipos de evento para el sistema Puerta Orion.

Responsabilidad:
- Administrar el ciclo de vida de eventos deportivos.
- Gestionar catálogos asociados (sesiones y tipos de evento).
- Restringir accesos según roles e impedir inconsistencias de horario.

El módulo aplica principios SRP, DRY, KISS, POO y Clean Code.
"""

from datetime import date, datetime, time, timedelta
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple

from flask import Blueprint, Flask, Response, request
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, selectinload

from ..middleware.auth_decorator import get_current_user, token_required
from ..models.acudientes.acudiente import Acudiente
from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
from ..models.base import db
from ..models.categorias.categoria import Categoria
from ..models.deportistas.deportista import Deportista
from ..models.eventos.evento import Evento
from ..models.eventos.sesion import Sesion
from ..models.eventos.tipo_evento import TipoEvento
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido
from ..utils.validations import ValidationError, sanitize_address, sanitize_free_text
from ..utils.http_responses import HttpResponseBuilder, handle_exception, JsonResponse
from ..utils.error_messages import (
    ERROR_NO_SE_ENVIARON_DATOS,
    ERROR_NO_SE_PROPORCIONARON_DATOS,
    ERROR_NOMBRE_MINIMO_CARACTERES,
    ERROR_LUGAR_MINIMO_CARACTERES,
    ERROR_INTERNO_SERVIDOR,
)

ROLES_GENERALES = (
    'SuperAdmin',
    'Administrador',
    'Entrenador',
    'Deportista',
    'Acudiente',
    'usuario',
)
ROLES_ADMIN = ('SuperAdmin', 'Administrador', 'Entrenador')
ROLES_CATALOGOS = ('SuperAdmin', 'Administrador', 'Entrenador', 'Deportista', 'Acudiente')

# Tipos de evento públicos visibles para usuarios con solo rol "Usuario"
# 2: Competencia, 3: Exhibición, 4: Torneo
TIPOS_EVENTO_PUBLICOS = (2, 3, 4)

ERROR_EVENTO_NO_ENCONTRADO = 'Evento con ID {id} no encontrado'
ERROR_CATEGORIA_NO_ENCONTRADA = 'Categoría con ID {id} no encontrada'
ERROR_TIPO_EVENTO_NO_ENCONTRADO = 'Tipo de evento con ID {id} no encontrado'
ERROR_SESION_NO_ENCONTRADA = 'Sesión con ID {id} no encontrada'
ERROR_SIN_ACCESO_CATEGORIA = 'No tienes acceso a eventos de esta categoría'

logger = obtener_registrador('aplicacion')
eventos_bp = Blueprint('eventos', __name__, url_prefix='/api/eventos')


# ============================================================================
# UTILIDADES COMUNES
# ============================================================================

# Función de compatibilidad temporal (se reemplazará gradualmente)
def _build_response(success: bool, status_code: int = 200, **payload: Any) -> JsonResponse:
    """Construye una respuesta JSON con formato consistente (legacy)."""
    if success:
        return HttpResponseBuilder.success(status_code=status_code, **payload)
    else:
        error = payload.pop('error', 'Error desconocido')
        message = payload.pop('message', None)
        return HttpResponseBuilder.error(
            error=error,
            message=message,
            status_code=status_code,
            **payload
        )


def _parse_date(value: str) -> Optional[date]:
    """Convierte una cadena en fecha si cumple el formato esperado."""
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _parse_time(value: str) -> Optional[time]:
    """Convierte una cadena en hora admitiendo los formatos HH:MM y HH:MM:SS."""
    try:
        parts = value.split(':')
        if len(parts) == 2:
            return datetime.strptime(value, '%H:%M').time()
        if len(parts) == 3:
            return datetime.strptime(value, '%H:%M:%S').time()
        return None
    except (AttributeError, ValueError):
        return None


def _validar_lugar(value: str) -> bool:
    """Valida que el lugar tenga longitud suficiente."""
    return bool(value and len(value.strip()) >= 3)


def _obtener_categoria_todos() -> Optional[int]:
    """Recupera el identificador de la categoría global 'Todos', si existe."""
    categoria = Categoria.query.filter_by(nombre_categoria='Todos').first()
    return categoria.id_categoria if categoria else None


def _validar_solapamiento_horario(
    fecha_evento: date,
    hora_inicio: time,
    hora_fin: time,
    *,
    id_evento_excluir: Optional[int] = None,
    id_categoria: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """Garantiza que no existan colisiones horarias en la misma categoría."""
    try:
        query = Evento.query.filter_by(fecha_evento=fecha_evento)
        if id_categoria is not None:
            query = query.filter_by(id_categoria=id_categoria)

        eventos = query.all()
        if id_evento_excluir is not None:
            eventos = [ev for ev in eventos if ev.id_evento != id_evento_excluir]

        inicio_nuevo = datetime.combine(fecha_evento, hora_inicio)
        # Si hora_fin < hora_inicio, el evento cruza la medianoche (termina al día siguiente)
        if hora_fin < hora_inicio:
            fin_nuevo = datetime.combine(fecha_evento + timedelta(days=1), hora_fin)
        else:
            fin_nuevo = datetime.combine(fecha_evento, hora_fin)

        for evento_existente in eventos:
            inicio_existente = datetime.combine(fecha_evento, evento_existente.hora_inicio)
            # Considerar si el evento existente también cruza la medianoche
            if evento_existente.hora_fin < evento_existente.hora_inicio:
                fin_existente = datetime.combine(fecha_evento + timedelta(days=1), evento_existente.hora_fin)
            else:
                fin_existente = datetime.combine(fecha_evento, evento_existente.hora_fin)
            
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                mensaje = _construir_mensaje_solapamiento(
                    evento_existente=evento_existente,
                    hora_inicio_nueva=hora_inicio,
                    hora_fin_nueva=hora_fin,
                )
                return False, mensaje
        return True, None
    except Exception as exc:  # pragma: no cover
        logger.error('Error al validar solapamiento de horario: %s', str(exc))
        return True, None


def _construir_mensaje_solapamiento(
    *,
    evento_existente: Evento,
    hora_inicio_nueva: time,
    hora_fin_nueva: time,
) -> str:
    """Genera el mensaje de error cuando existe solapamiento horario."""
    inicio_existente = evento_existente.hora_inicio.strftime('%H:%M')
    fin_existente = evento_existente.hora_fin.strftime('%H:%M')
    inicio_nuevo = hora_inicio_nueva.strftime('%H:%M')
    fin_nuevo = hora_fin_nueva.strftime('%H:%M')

    if hora_inicio_nueva < evento_existente.hora_inicio:
        return (
            f"El horario de fin del nuevo evento ({fin_nuevo}) se solapa con el inicio del evento "
            f"'{evento_existente.nombre}' que inicia a las {inicio_existente}."
        )
    if hora_inicio_nueva >= evento_existente.hora_inicio and hora_fin_nueva <= evento_existente.hora_fin:
        return (
            f"El horario del nuevo evento ({inicio_nuevo} - {fin_nuevo}) está completamente dentro del evento "
            f"'{evento_existente.nombre}' ({inicio_existente} - {fin_existente})."
        )
    return (
        f"El horario de inicio del nuevo evento ({inicio_nuevo}) se solapa con el evento "
        f"'{evento_existente.nombre}' que está en curso de {inicio_existente} a {fin_existente}."
    )


# ============================================================================
# ACCESO SEGÚN ROLES
# ============================================================================

def _es_usuario_admin(roles: List[str]) -> bool:
    """Verifica si el usuario tiene rol de administrador."""
    return any(rol in ROLES_ADMIN for rol in roles) or 'SuperAdmin' in roles


def _obtener_categorias_deportista(id_persona: int) -> set:
    """Obtiene las categorías asociadas a un deportista."""
    categorias = set()
    deportista = Deportista.query.filter_by(id_persona=id_persona).first()
    if deportista and deportista.id_categoria:
        categorias.add(deportista.id_categoria)
    return categorias


def _obtener_categorias_acudiente(id_persona: int) -> set:
    """Obtiene las categorías asociadas a un acudiente a través de sus deportistas."""
    categorias = set()
    acudiente = Acudiente.query.filter_by(id_persona=id_persona).first()
    if not acudiente:
        return categorias

    relaciones = DeportistaAcudiente.query.filter_by(id_acudiente=acudiente.id_acudiente).all()
    for relacion in relaciones:
        deportista = Deportista.query.get(relacion.id_deportista)
        if deportista and deportista.id_categoria:
            categorias.add(deportista.id_categoria)
    return categorias


def obtener_categorias_permitidas_usuario() -> Optional[List[int]]:
    """Obtiene las categorías visibles para el usuario autenticado."""
    try:
        usuario_data = get_current_user()
        if not usuario_data:
            return []

        roles = [rol.get('nombre_rol', '') for rol in usuario_data.get('roles', [])]
        rol_activo = usuario_data.get('rol_activo', '')
        id_persona = usuario_data.get('persona', {}).get('id_persona')
        if not id_persona:
            return []

        # Si el rol activo es Deportista o Acudiente, SIEMPRE filtrar por categoría
        # aunque tenga otros roles administrativos
        if rol_activo in ['Deportista', 'Acudiente']:
            categorias = set()
            if rol_activo == 'Deportista':
                categorias.update(_obtener_categorias_deportista(id_persona))
            if rol_activo == 'Acudiente':
                categorias.update(_obtener_categorias_acudiente(id_persona))
            return list(categorias) if categorias else []
        
        # Si el rol activo es admin/entrenador, ver todos los eventos
        if _es_usuario_admin(roles) and rol_activo in ['SuperAdmin', 'Administrador', 'Entrenador']:
            return None

        categorias = set()

        if 'Deportista' in roles:
            categorias.update(_obtener_categorias_deportista(id_persona))

        if 'Acudiente' in roles:
            categorias.update(_obtener_categorias_acudiente(id_persona))

        return list(categorias) if categorias else []
    except Exception as exc:  # pragma: no cover
        logger.error('Error al obtener categorías permitidas: %s', str(exc))
        return []


def _es_usuario_solo_deportista_o_acudiente() -> bool:
    """Verifica si el usuario tiene solo roles Deportista o Acudiente sin roles admin."""
    try:
        usuario_data = get_current_user()
        if not usuario_data:
            return False

        roles = [rol.get('nombre_rol', '') for rol in usuario_data.get('roles', [])]
        
        # Roles administrativos
        roles_admin = ['SuperAdmin', 'Administrador', 'Entrenador']
        tiene_rol_admin = any(rol in roles_admin for rol in roles)
        
        # Tiene rol deportista o acudiente
        tiene_rol_deportista_acudiente = any(rol in ['Deportista', 'Acudiente'] for rol in roles)
        
        # Es solo deportista/acudiente si tiene ese rol pero NO tiene roles admin
        return tiene_rol_deportista_acudiente and not tiene_rol_admin
    except Exception as exc:  # pragma: no cover
        logger.error('Error al verificar si es solo deportista/acudiente: %s', str(exc))
        return False


def _es_usuario_solo_rol_usuario() -> bool:
    """Verifica si el usuario tiene solo el rol 'Usuario' sin otros roles principales."""
    try:
        usuario_data = get_current_user()
        if not usuario_data:
            return False

        roles = [rol.get('nombre_rol', '') for rol in usuario_data.get('roles', [])]
        
        # Verificar si tiene solo rol 'usuario' o 'Usuario'
        roles_principales = ['SuperAdmin', 'Administrador', 'Entrenador', 'Deportista', 'Acudiente']
        tiene_rol_principal = any(rol in roles_principales for rol in roles)
        
        # Tiene rol usuario (case insensitive)
        tiene_rol_usuario = any(
            rol.lower() == 'usuario' or rol.lower() == 'user' 
            for rol in roles
        )
        
        # Es usuario solo si tiene rol usuario pero NO tiene roles principales
        return tiene_rol_usuario and not tiene_rol_principal
    except Exception as exc:  # pragma: no cover
        logger.error('Error al verificar si es usuario solo rol usuario: %s', str(exc))
        return False


# ============================================================================
# VALIDADORES DE CAMPOS
# ============================================================================

def validar_fecha(fecha_str: str) -> Optional[date]:
    """Valida y convierte una cadena a fecha."""
    return _parse_date(fecha_str)


def validar_hora(hora_str: str) -> Optional[time]:
    """Valida y convierte una cadena a hora."""
    return _parse_time(hora_str)


def validar_lugar(lugar_str: str) -> bool:
    """Valida que un lugar sea suficientemente descriptivo."""
    return _validar_lugar(lugar_str)


def validar_solapamiento_horario(
    fecha_evento: date,
    hora_inicio: time,
    hora_fin: time,
    id_evento_excluir: Optional[int] = None,
    id_categoria: Optional[int] = None,
) -> Tuple[bool, Optional[str]]:
    """Proxy para mantener compatibilidad con código existente."""
    return _validar_solapamiento_horario(
        fecha_evento,
        hora_inicio,
        hora_fin,
        id_evento_excluir=id_evento_excluir,
        id_categoria=id_categoria,
    )


# ============================================================================
# SERIALIZADORES
# ============================================================================

def _agregar_categoria_serializada(evento: Evento, evento_dict: Dict[str, Any]) -> None:
    """Agrega la categoría serializada al diccionario del evento."""
    if not (hasattr(evento, 'categoria') and evento.categoria):
        return
    try:
        evento_dict['categoria'] = evento.categoria.to_dict()
    except Exception as e:
        logger.warning('Error al serializar categoría del evento %s: %s', evento.id_evento, str(e))


def _agregar_sesion_serializada(evento: Evento, evento_dict: Dict[str, Any]) -> None:
    """Agrega la sesión serializada al diccionario del evento."""
    if not (hasattr(evento, 'sesion') and evento.sesion):
        return
    try:
        evento_dict['sesion'] = evento.sesion.to_dict()
    except Exception as e:
        logger.warning('Error al serializar sesión del evento %s: %s', evento.id_evento, str(e))


def _agregar_tipo_evento_serializado(evento: Evento, evento_dict: Dict[str, Any]) -> None:
    """Agrega el tipo de evento serializado al diccionario del evento."""
    if not evento.id_tipo_evento:
        return
    try:
        # Use pre-loaded relationship instead of query.get() to avoid N+1
        if hasattr(evento, 'tipo_evento') and evento.tipo_evento:
            evento_dict['tipo_evento'] = evento.tipo_evento.to_dict()
        else:
            # Fallback only if relationship wasn't loaded
            tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
            if tipo_evento:
                evento_dict['tipo_evento'] = tipo_evento.to_dict()
    except Exception as e:
        logger.warning('Error al obtener tipo_evento del evento %s: %s', evento.id_evento, str(e))


def _serializar_evento(evento: Evento) -> Dict[str, Any]:
    """Serializa un evento incluyendo relaciones asociadas."""
    try:
        evento_dict = evento.to_dict()
        _agregar_categoria_serializada(evento, evento_dict)
        _agregar_sesion_serializada(evento, evento_dict)
        _agregar_tipo_evento_serializado(evento, evento_dict)
        return evento_dict
    except Exception as e:
        logger.error('Error al serializar evento %s: %s', evento.id_evento if evento else 'desconocido', str(e))
        logger.error('Traceback: %s', traceback.format_exc())
        raise


# ============================================================================
# VALIDADORES GENERALES DE NOMBRES
# ============================================================================

def _obtener_nombre_requerido(data: Dict[str, Any]) -> str:
    """Obtiene y valida el nombre dentro de un payload."""
    if 'nombre' not in data or not str(data['nombre']).strip():
        raise RequestValidationError('El campo nombre es requerido', status_code=400)
    nombre = str(data['nombre']).strip()
    if len(nombre) < 3:
        raise RequestValidationError(ERROR_NOMBRE_MINIMO_CARACTERES, status_code=400)
    return nombre


# ============================================================================
# FUNCIONES AUXILIARES PARA ACTUALIZACIÓN DE EVENTOS
# ============================================================================

def _actualizar_nombre_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza el nombre del evento si está presente en los datos."""
    if 'nombre' not in data:
        return None
    try:
        nombre = sanitize_free_text('nombre', data['nombre'], max_length=120)
    except ValidationError as exc:
        return HttpResponseBuilder.bad_request(error=str(exc))
    if len(nombre) < 3:
        return HttpResponseBuilder.bad_request(error=ERROR_NOMBRE_MINIMO_CARACTERES)
    evento.nombre = nombre
    return None


def _actualizar_fecha_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza la fecha del evento si está presente en los datos."""
    if 'fecha_evento' not in data:
        return None
    fecha_evento = _parse_date(data['fecha_evento'])
    if not fecha_evento:
        return HttpResponseBuilder.bad_request(error='Formato de fecha inválido. Use YYYY-MM-DD')
    evento.fecha_evento = fecha_evento
    return None


def _actualizar_horas_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza las horas de inicio y fin del evento si están presentes."""
    if 'hora_inicio' in data:
        hora_inicio = _parse_time(data['hora_inicio'])
        if not hora_inicio:
            return HttpResponseBuilder.bad_request(
                error='Formato de hora de inicio inválido. Use HH:MM o HH:MM:SS'
            )
        evento.hora_inicio = hora_inicio

    if 'hora_fin' in data:
        hora_fin = _parse_time(data['hora_fin'])
        if not hora_fin:
            return HttpResponseBuilder.bad_request(
                error='Formato de hora de fin inválido. Use HH:MM o HH:MM:SS'
            )
        evento.hora_fin = hora_fin

    # Permitir eventos que cruzan la medianoche (hora_fin < hora_inicio es válido)
    # Solo rechazar si las horas son iguales (duración cero)
    if evento.hora_fin == evento.hora_inicio:
        return HttpResponseBuilder.bad_request(
            error='La hora de fin debe ser diferente a la hora de inicio'
        )
    return None


def _actualizar_lugar_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza el lugar del evento si está presente en los datos."""
    if 'lugar' not in data:
        return None
    try:
        lugar = sanitize_address('lugar', data['lugar'], max_length=120)
    except ValidationError as exc:
        return HttpResponseBuilder.bad_request(error=str(exc))
    if not _validar_lugar(lugar):
        return HttpResponseBuilder.bad_request(error=ERROR_LUGAR_MINIMO_CARACTERES)
    evento.lugar = lugar
    return None


def _actualizar_descripcion_evento(evento: Evento, data: Dict[str, Any]) -> None:
    """Actualiza la descripción del evento si está presente en los datos."""
    if 'descripcion' in data:
        evento.descripcion = (
            sanitize_free_text('descripcion', data['descripcion'], max_length=500)
            if data['descripcion']
            else None
        )


def _actualizar_categoria_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza la categoría del evento si está presente en los datos."""
    if 'id_categoria' not in data:
        return None
    categoria = Categoria.query.get(data['id_categoria'])
    if not categoria:
        return HttpResponseBuilder.not_found(
            error=ERROR_CATEGORIA_NO_ENCONTRADA.format(id=data['id_categoria'])
        )
    evento.id_categoria = data['id_categoria']
    return None


def _actualizar_tipo_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza el tipo de evento si está presente en los datos."""
    if 'id_tipo_evento' not in data:
        return None
    tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
    if not tipo_evento:
        return HttpResponseBuilder.not_found(
            error=ERROR_TIPO_EVENTO_NO_ENCONTRADO.format(id=data['id_tipo_evento'])
        )
    evento.id_tipo_evento = data['id_tipo_evento']
    return None


def _actualizar_sesion_evento(evento: Evento, data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Actualiza la sesión del evento si está presente en los datos."""
    if 'id_sesion' not in data:
        return None
    sesion = Sesion.query.get(data['id_sesion'])
    if not sesion:
        return HttpResponseBuilder.not_found(
            error=ERROR_SESION_NO_ENCONTRADA.format(id=data['id_sesion'])
        )
    evento.id_sesion = data['id_sesion']
    return None


def _validar_solapamiento_evento_actualizado(
    evento: Evento,
    evento_id: int,
    data: Dict[str, Any]
) -> Optional[JsonResponse]:
    """Valida solapamiento de horario si se actualizaron campos relevantes."""
    campos_relevantes = ('fecha_evento', 'hora_inicio', 'hora_fin', 'id_categoria')
    if not any(key in data for key in campos_relevantes):
        return None

    valido, mensaje_error = validar_solapamiento_horario(
        evento.fecha_evento,
        evento.hora_inicio,
        evento.hora_fin,
        id_evento_excluir=evento_id,
        id_categoria=evento.id_categoria,
    )
    if not valido:
        return HttpResponseBuilder.bad_request(error=mensaje_error)
    return None


# ============================================================================
# FUNCIONES AUXILIARES PARA FILTRADO DE EVENTOS
# ============================================================================

def _aplicar_filtro_categorias(
    query: Any,
    categorias_permitidas: Optional[List[int]],
    id_categoria_todos: Optional[int]
) -> Any:
    """Aplica filtro de categorías a la consulta de eventos."""
    # Si es None, es admin/entrenador - ver todos los eventos (sin filtrar)
    if categorias_permitidas is None:
        return query

    # Si es lista vacía, no hay categorías permitidas - retornar consulta vacía
    if not categorias_permitidas:
        return query.filter(Evento.id_evento == -1)

    # Si se incluye la categoría "Todos", agregarla al filtro
    if id_categoria_todos:
        return query.filter(
            or_(
                Evento.id_categoria.in_(categorias_permitidas),
                Evento.id_categoria == id_categoria_todos,
            )
        )
    
    # Filtrar SOLO por las categorías permitidas (sin "Todos")
    # Asegurar que id_categoria NO sea NULL y esté en la lista exacta
    return query.filter(
        Evento.id_categoria.isnot(None),
        Evento.id_categoria.in_(categorias_permitidas)
    )


def _aplicar_filtro_categoria_especifica(
    query: Any,
    categoria_id: int,
    categorias_permitidas: Optional[List[int]],
    id_categoria_todos: Optional[int]
) -> Tuple[Any, Optional[JsonResponse]]:
    """Aplica filtro de categoría específica y valida permisos."""
    categoria_permitida = (
        categorias_permitidas is None
        or categoria_id in categorias_permitidas
        or categoria_id == id_categoria_todos
    )

    if not categoria_permitida:
        return query, HttpResponseBuilder.success(
            message=ERROR_SIN_ACCESO_CATEGORIA,
            data=[],
            pagination={'page': 1, 'per_page': 10, 'total': 0, 'pages': 0}
        )

    return query.filter_by(id_categoria=categoria_id), None


def _aplicar_filtros_basicos(
    query: Any,
    search: Optional[str],
    tipo_evento_id: Optional[int],
    fecha_desde: Optional[str],
    fecha_hasta: Optional[str]
) -> Any:
    """Aplica filtros básicos a la consulta de eventos."""
    if search:
        query = query.filter(Evento.nombre.ilike(f"%{search}%"))
    
    if tipo_evento_id:
        query = query.filter_by(id_tipo_evento=tipo_evento_id)
    
    if fecha_desde:
        fecha_desde_obj = _parse_date(fecha_desde)
        if fecha_desde_obj:
            query = query.filter(Evento.fecha_evento >= fecha_desde_obj)
    
    if fecha_hasta:
        fecha_hasta_obj = _parse_date(fecha_hasta)
        if fecha_hasta_obj:
            query = query.filter(Evento.fecha_evento <= fecha_hasta_obj)
    
    return query


def _aplicar_filtro_usuario_solo(query: Any, tipo_evento_id: Optional[int]) -> Tuple[Any, Optional[JsonResponse]]:
    """Aplica filtro para usuarios con solo rol 'Usuario'."""
    # Removed excessive logging for performance
    query = query.filter(Evento.id_tipo_evento.in_(TIPOS_EVENTO_PUBLICOS))
    if tipo_evento_id and tipo_evento_id not in TIPOS_EVENTO_PUBLICOS:
        return query, HttpResponseBuilder.success(
            message='No tienes acceso a este tipo de evento',
            data=[],
            pagination={'page': 1, 'per_page': 10, 'total': 0, 'pages': 0}
        )
    return query, None


def _aplicar_filtro_admin_entrenador(query: Any, categoria_id: Optional[int]) -> Any:
    """Aplica filtro para administradores y entrenadores."""
    # Removed excessive logging for performance
    if categoria_id:
        query = query.filter_by(id_categoria=categoria_id)
    return query


def _aplicar_filtro_deportista_acudiente(
    query: Any,
    categorias_permitidas: List[int],
    categoria_id: Optional[int]
) -> Tuple[Any, Optional[JsonResponse]]:
    """Aplica filtro para deportistas y acudientes."""
    # Removed excessive logging for performance
    if not categorias_permitidas:
        return query.filter(Evento.id_evento == -1), None
    query = query.filter(
        Evento.id_categoria.isnot(None),
        Evento.id_categoria.in_(categorias_permitidas)
    )
    
    if categoria_id:
        if categoria_id not in categorias_permitidas:
            # Removed excessive logging for performance
            return query, HttpResponseBuilder.success(
                message=ERROR_SIN_ACCESO_CATEGORIA,
                data=[],
                pagination={'page': 1, 'per_page': 10, 'total': 0, 'pages': 0}
            )
        query = query.filter_by(id_categoria=categoria_id)
    
    return query, None


def _serializar_eventos_paginados(
    query: Any,
    page: int,
    per_page: int,
    categorias_permitidas: Optional[List[int]]
) -> Tuple[List[Dict[str, Any]], Any]:
    """Serializa eventos paginados aplicando validaciones adicionales."""
    # Optimize: Let paginate() handle count() internally - avoid double counting
    # paginate() is optimized and will only count if needed
    pagination = query.order_by(Evento.fecha_evento.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )
    
    eventos_data = []
    # Removed excessive logging inside loop - only log if DEBUG mode
    for evento in pagination.items:
        try:
            # Filter by allowed categories only if needed (already filtered in query, but double-check for safety)
            if categorias_permitidas is not None and categorias_permitidas:
                if evento.id_categoria is None or evento.id_categoria not in categorias_permitidas:
                    # Skip events not in allowed categories (shouldn't happen if query is correct, but safety check)
                    continue
            
            evento_serializado = _serializar_evento(evento)
            eventos_data.append(evento_serializado)
        except Exception as exc_serializar:
            logger.error('Error al serializar evento %s: %s', evento.id_evento, str(exc_serializar))
            logger.error('Traceback: %s', traceback.format_exc())
            continue
    
    return eventos_data, pagination


def _aplicar_filtro_deportista_acudiente_proximos(
    query: Any,
    categorias_permitidas: List[int],
    categoria_id: Optional[int]
) -> Tuple[Any, Optional[JsonResponse]]:
    """Aplica filtro para deportistas y acudientes en eventos próximos."""
    if not categorias_permitidas:
        return query.filter(Evento.id_evento == -1), None
    
    query = query.filter(
        Evento.id_categoria.isnot(None),
        Evento.id_categoria.in_(categorias_permitidas)
    )
    
    if categoria_id:
        if categoria_id not in categorias_permitidas:
            return query, HttpResponseBuilder.success(
                data=[],
                total=0,
                message=ERROR_SIN_ACCESO_CATEGORIA
            )
        query = query.filter_by(id_categoria=categoria_id)
    
    return query, None


# ============================================================================
# CRUD DE EVENTOS
# ============================================================================

@eventos_bp.route('/calendario', methods=['GET'])
@token_required(required_roles=ROLES_GENERALES, required_active_roles=ROLES_GENERALES)
def listar_eventos() -> JsonResponse:
    """
    Lista eventos aplicando filtros y restricciones por rol.

    GET /api/eventos/calendario?page=1&per_page=10&search=texto&categoria_id=1&tipo_evento_id=1&fecha_desde=2024-01-01&fecha_hasta=2024-12-31

    Query params:
        page (int, opcional): Número de página
        per_page (int, opcional): Elementos por página
        search (str, opcional): Búsqueda por nombre
        categoria_id (int, opcional): Filtrar por categoría
        tipo_evento_id (int, opcional): Filtrar por tipo de evento
        fecha_desde (str, opcional): Fecha desde (YYYY-MM-DD)
        fecha_hasta (str, opcional): Fecha hasta (YYYY-MM-DD)

    Returns:
        Lista paginada de eventos o error.
    """
    try:
        # Verificar si el usuario tiene solo rol "Usuario"
        es_usuario_solo = _es_usuario_solo_rol_usuario()
        
        categorias_permitidas = obtener_categorias_permitidas_usuario()
        
        # Reduced logging - only log in DEBUG mode to improve performance
        # usuario_data = get_current_user()
        # rol_activo = usuario_data.get('rol_activo', '') if usuario_data else ''
        # logger.info('🔍 FILTRO EVENTOS - Rol activo: %s, es_usuario_solo: %s, categorias_permitidas: %s', 
        #            rol_activo, es_usuario_solo, categorias_permitidas)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = (request.args.get('search') or '').strip()
        categoria_id = request.args.get('categoria_id', type=int)
        tipo_evento_id = request.args.get('tipo_evento_id', type=int)
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')

        # Use eager loading to prevent N+1 queries
        query = Evento.query.options(
            joinedload(Evento.categoria),
            joinedload(Evento.tipo_evento)
        )
        
        # Aplicar filtros según el rol del usuario
        if es_usuario_solo:
            query, error_response = _aplicar_filtro_usuario_solo(query, tipo_evento_id)
            if error_response:
                return error_response
        elif categorias_permitidas is None:
            query = _aplicar_filtro_admin_entrenador(query, categoria_id)
        else:
            query, error_response = _aplicar_filtro_deportista_acudiente(query, categorias_permitidas, categoria_id)
            if error_response:
                return error_response

        query = _aplicar_filtros_basicos(query, search, tipo_evento_id, fecha_desde, fecha_hasta)
        eventos_data, pagination = _serializar_eventos_paginados(query, page, per_page, categorias_permitidas)
        
        return HttpResponseBuilder.success(
            data=eventos_data,
            pagination={
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
            }
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error('Error completo en listar_eventos: %s', str(exc))
        logger.error('Traceback completo: %s', traceback.format_exc())
        return handle_exception(exc, logger, "listar eventos")


@eventos_bp.route('/calendario/<int:evento_id>', methods=['GET'])
@token_required(required_roles=ROLES_GENERALES, required_active_roles=ROLES_GENERALES)
def obtener_evento(evento_id: int) -> JsonResponse:
    """
    Obtiene un evento específico por identificador.

    GET /api/eventos/calendario/<evento_id>

    Returns:
        Datos del evento o error.
    """
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return _build_response(
                False,
                error=ERROR_EVENTO_NO_ENCONTRADO.format(id=evento_id),
                status_code=404,
            )
        
        evento_dict = evento.to_dict()
        if evento.categoria:
            evento_dict['categoria'] = evento.categoria.to_dict()
        if evento.sesion:
            evento_dict['sesion'] = evento.sesion.to_dict()
        tipo_evento = TipoEvento.query.get(evento.id_tipo_evento)
        if tipo_evento:
            evento_dict['tipo_evento'] = tipo_evento.to_dict()
        
        return _build_response(True, data=evento_dict)
    except Exception as exc:  # pylint: disable=broad-except
        return handle_exception(exc, logger, "obtener evento")


def _validar_campos_requeridos_evento(data: Dict[str, Any]) -> Optional[JsonResponse]:
    """Valida que todos los campos requeridos estén presentes."""
    campos_requeridos = [
        'nombre',
        'fecha_evento',
        'hora_inicio',
        'hora_fin',
        'lugar',
        'id_categoria',
        'id_tipo_evento',
    ]
    campos_faltantes = [campo for campo in campos_requeridos if not data.get(campo)]
    if campos_faltantes:
        return _build_response(
            False,
            error='Campos requeridos faltantes',
            message=f'Los siguientes campos son obligatorios: {", ".join(campos_faltantes)}',
            campos_faltantes=campos_faltantes,
            status_code=400,
        )
    return None


def _validar_y_sanitizar_nombre(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[JsonResponse]]:
    """Valida y sanitiza el nombre del evento."""
    try:
        nombre = sanitize_free_text('nombre', data['nombre'], max_length=120)
        if len(nombre) < 3:
            return None, HttpResponseBuilder.bad_request(error=ERROR_NOMBRE_MINIMO_CARACTERES)
        return nombre, None
    except ValidationError as exc:
        return None, _build_response(False, error=str(exc), status_code=400)


def _validar_fecha_y_horas(data: Dict[str, Any]) -> Tuple[Optional[date], Optional[time], Optional[time], Optional[JsonResponse]]:
    """Valida fecha y horas del evento."""
    fecha_evento = _parse_date(data['fecha_evento'])
    if not fecha_evento:
        return None, None, None, _build_response(False, error='Formato de fecha inválido. Use YYYY-MM-DD', status_code=400)
    
    # Validar que la fecha no sea pasada (solo para creación de eventos)
    fecha_actual = date.today()
    if fecha_evento < fecha_actual:
        return None, None, None, _build_response(
            False,
            error='No se pueden crear eventos en fechas pasadas. La fecha debe ser hoy o una fecha futura.',
            status_code=400,
        )
    
    hora_inicio = _parse_time(data['hora_inicio'])
    if not hora_inicio:
        return None, None, None, _build_response(
            False,
            error='Formato de hora de inicio inválido. Use HH:MM o HH:MM:SS',
            status_code=400,
        )

    hora_fin = _parse_time(data['hora_fin'])
    if not hora_fin:
        return None, None, None, _build_response(
            False,
            error='Formato de hora de fin inválido. Use HH:MM o HH:MM:SS',
            status_code=400,
        )
    
    # Permitir eventos que cruzan la medianoche (hora_fin < hora_inicio es válido)
    # Solo rechazar si las horas son iguales (duración cero)
    if hora_fin == hora_inicio:
        return None, None, None, _build_response(False, error='La hora de fin debe ser diferente a la hora de inicio', status_code=400)
    
    return fecha_evento, hora_inicio, hora_fin, None


def _validar_y_sanitizar_lugar(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[JsonResponse]]:
    """Valida y sanitiza el lugar del evento."""
    try:
        lugar = sanitize_address('lugar', data['lugar'], max_length=120)
        return lugar, None
    except ValidationError as exc:
        return None, _build_response(False, error=str(exc), status_code=400)


def _validar_entidades_evento(data: Dict[str, Any]) -> Tuple[Optional[Categoria], Optional[TipoEvento], Optional[JsonResponse]]:
    """Valida que la categoría y tipo de evento existan."""
    categoria = Categoria.query.get(data['id_categoria'])
    if not categoria:
        return None, None, _build_response(
            False,
            error=ERROR_CATEGORIA_NO_ENCONTRADA.format(id=data['id_categoria']),
            status_code=404,
        )
    
    tipo_evento = TipoEvento.query.get(data['id_tipo_evento'])
    if not tipo_evento:
        return None, None, _build_response(
            False,
            error=ERROR_TIPO_EVENTO_NO_ENCONTRADO.format(id=data['id_tipo_evento']),
            status_code=404,
        )
    
    return categoria, tipo_evento, None


@eventos_bp.route('/calendario', methods=['POST'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def crear_evento() -> JsonResponse:
    """
    Crea un nuevo evento con validaciones de negocio.

    POST /api/eventos/calendario

    Body JSON requerido:
    {
        "nombre": "Nombre del evento",
        "fecha_evento": "2024-12-31",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
        "lugar": "Lugar del evento",
        "id_categoria": 1,
        "id_tipo_evento": 1,
        "descripcion": "Descripción opcional"
    }

    Returns:
        Evento creado o error.
    """
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_NO_SE_ENVIARON_DATOS,
            mensaje_vacio='El cuerpo de la petición debe contener datos JSON',
        )

        error_response = _validar_campos_requeridos_evento(data)
        if error_response:
            return error_response

        nombre, error_response = _validar_y_sanitizar_nombre(data)
        if error_response:
            return error_response

        fecha_evento, hora_inicio, hora_fin, error_response = _validar_fecha_y_horas(data)
        if error_response:
            return error_response

        lugar, error_response = _validar_y_sanitizar_lugar(data)
        if error_response:
            return error_response

        validacion_horario, mensaje_error = validar_solapamiento_horario(
            fecha_evento,
            hora_inicio,
            hora_fin,
            id_categoria=data.get('id_categoria'),
        )
        if not validacion_horario:
            return _build_response(False, error=mensaje_error, status_code=400)

        _, _, error_response = _validar_entidades_evento(data)
        if error_response:
            return error_response

        descripcion = (
            sanitize_free_text('descripcion', data.get('descripcion'), max_length=500)
            if data.get('descripcion')
            else None
        )

        nuevo_evento = Evento(
            nombre=nombre,
            fecha_evento=fecha_evento,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            lugar=lugar,
            descripcion=descripcion,
            id_categoria=data['id_categoria'],
            id_tipo_evento=data['id_tipo_evento'],
        )
        
        db.session.add(nuevo_evento)
        db.session.commit()
        
        return _build_response(
            True,
            message='Evento creado exitosamente',
            data=nuevo_evento.to_dict(),
            status_code=201,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return HttpResponseBuilder.bad_request(error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return handle_exception(exc, logger, "crear evento")


@eventos_bp.route('/calendario/<int:evento_id>', methods=['PUT'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def actualizar_evento(evento_id: int) -> JsonResponse:
    """
    Actualiza los datos de un evento existente.

    PUT /api/eventos/calendario/<evento_id>

    Body JSON (todos los campos son opcionales):
    {
        "nombre": "Nuevo nombre",
        "fecha_evento": "2024-12-31",
        "hora_inicio": "10:00",
        "hora_fin": "12:00",
        "lugar": "Nuevo lugar",
        "descripcion": "Nueva descripción",
        "id_categoria": 1,
        "id_tipo_evento": 1,
        "id_sesion": 1
    }

    Returns:
        Evento actualizado o error.
    """
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return HttpResponseBuilder.not_found(
                error=ERROR_EVENTO_NO_ENCONTRADO.format(id=evento_id)
            )

        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_NO_SE_ENVIARON_DATOS,
            mensaje_vacio=ERROR_NO_SE_PROPORCIONARON_DATOS,
        )

        # Actualizar cada campo usando funciones auxiliares (reduce complejidad cognitiva)
        error_response = _actualizar_nombre_evento(evento, data)
        if error_response:
            return error_response

        error_response = _actualizar_fecha_evento(evento, data)
        if error_response:
            return error_response

        error_response = _actualizar_horas_evento(evento, data)
        if error_response:
            return error_response

        error_response = _actualizar_lugar_evento(evento, data)
        if error_response:
            return error_response

        _actualizar_descripcion_evento(evento, data)

        error_response = _actualizar_categoria_evento(evento, data)
        if error_response:
            return error_response

        error_response = _actualizar_tipo_evento(evento, data)
        if error_response:
            return error_response

        error_response = _actualizar_sesion_evento(evento, data)
        if error_response:
            return error_response

        error_response = _validar_solapamiento_evento_actualizado(evento, evento_id, data)
        if error_response:
            return error_response
        
        db.session.commit()
        return HttpResponseBuilder.success(
            message='Evento actualizado exitosamente',
            data=evento.to_dict()
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return HttpResponseBuilder.bad_request(error=str(exc))
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return handle_exception(exc, logger, "actualizar evento")


@eventos_bp.route('/calendario/<int:evento_id>', methods=['DELETE'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def eliminar_evento(evento_id: int) -> JsonResponse:
    """Elimina un evento existente."""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return _build_response(
                False,
                error=ERROR_EVENTO_NO_ENCONTRADO.format(id=evento_id),
                status_code=404,
            )
        
        nombre_evento = evento.nombre
        
        db.session.delete(evento)
        db.session.commit()
        
        return _build_response(
            True,
            message=f'Evento "{nombre_evento}" eliminado exitosamente',
        )
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return _build_response(False, error=f'Error al eliminar evento: {str(exc)}', status_code=500)


# ============================================================================
# CRUD DE SESIONES
# ============================================================================

@eventos_bp.route('/sesiones', methods=['GET'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def listar_sesiones() -> JsonResponse:
    """Lista las sesiones disponibles con paginación opcional."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = (request.args.get('search') or '').strip()
        
        query = Sesion.query
        if search:
            query = query.filter(Sesion.nombre.ilike(f"%{search}%"))

        pagination = query.order_by(Sesion.nombre.asc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        return _build_response(
            True,
            data=[sesion.to_dict() for sesion in pagination.items],
            pagination={
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
            },
        )
    except Exception as exc:  # pylint: disable=broad-except
        return _build_response(False, error=f'Error al listar sesiones: {str(exc)}', status_code=500)


@eventos_bp.route('/sesiones/<int:sesion_id>', methods=['GET'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def obtener_sesion(sesion_id: int) -> JsonResponse:
    """Obtiene una sesión específica por identificador."""
    try:
        sesion = Sesion.query.get(sesion_id)
        if not sesion:
            return _build_response(
                False,
                error=ERROR_SESION_NO_ENCONTRADA.format(id=sesion_id),
                status_code=404,
            )

        return _build_response(True, data=sesion.to_dict())
    except Exception as exc:  # pylint: disable=broad-except
        return _build_response(False, error=f'Error al obtener sesión: {str(exc)}', status_code=500)


@eventos_bp.route('/sesiones', methods=['POST'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def crear_sesion() -> JsonResponse:
    """Crea una nueva sesión."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_NO_SE_ENVIARON_DATOS,
            mensaje_vacio=ERROR_NO_SE_PROPORCIONARON_DATOS,
        )
        try:
            nombre = _obtener_nombre_requerido(data)
        except RequestValidationError as exc:
            return _build_response(False, error=str(exc), status_code=exc.status_code)

        if Sesion.query.filter_by(nombre=nombre).first():
            return _build_response(
                False,
                error=f'Ya existe una sesión con el nombre "{nombre}"',
                status_code=400,
            )

        descripcion = (data.get('descripcion') or '').strip()
        nueva_sesion = Sesion(nombre=nombre, descripcion=descripcion)

        db.session.add(nueva_sesion)
        db.session.commit()
        
        return _build_response(
            True,
            message='Sesión creada exitosamente',
            data=nueva_sesion.to_dict(),
            status_code=201,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return _build_response(False, error=f'Error al crear sesión: {str(exc)}', status_code=500)




@eventos_bp.route('/sesiones/<int:sesion_id>', methods=['PUT'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def actualizar_sesion(sesion_id: int) -> JsonResponse:
    """Actualiza una sesión existente."""
    try:
        sesion = Sesion.query.get(sesion_id)
        if not sesion:
            return _build_response(
                False,
                error=ERROR_SESION_NO_ENCONTRADA.format(id=sesion_id),
                status_code=404,
            )

        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_NO_SE_ENVIARON_DATOS,
            mensaje_vacio=ERROR_NO_SE_PROPORCIONARON_DATOS,
        )
        
        if 'nombre' in data:
            nombre = str(data['nombre']).strip()
            if len(nombre) < 3:
                return _build_response(False, error='El nombre debe tener al menos 3 caracteres', status_code=400)
            existe = (
                Sesion.query.filter(Sesion.nombre == nombre, Sesion.id_sesion != sesion_id).first()
            )
            if existe:
                return _build_response(
                    False,
                    error=f'Ya existe otra sesión con el nombre "{nombre}"',
                    status_code=400,
                )
            sesion.nombre = nombre
        
        if 'descripcion' in data:
            sesion.descripcion = (data['descripcion'] or '').strip()
        
        db.session.commit()
        
        return _build_response(
            True,
            message='Sesión actualizada exitosamente',
            data=sesion.to_dict(),
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return _build_response(False, error=f'Error al actualizar sesión: {str(exc)}', status_code=500)


@eventos_bp.route('/sesiones/<int:sesion_id>', methods=['DELETE'])
@token_required(required_roles=ROLES_ADMIN, required_active_roles=ROLES_ADMIN)
def eliminar_sesion(sesion_id: int) -> JsonResponse:
    """Elimina una sesión si no tiene eventos asociados."""
    try:
        sesion = Sesion.query.get(sesion_id)
        if not sesion:
            return _build_response(
                False,
                error=ERROR_SESION_NO_ENCONTRADA.format(id=sesion_id),
                status_code=404,
            )

        eventos_count = Evento.query.filter_by(id_sesion=sesion_id).count()
        if eventos_count > 0:
            return _build_response(
                False,
                error=f'No se puede eliminar la sesión porque tiene {eventos_count} evento(s) asociado(s)',
                status_code=400,
            )
        
        nombre_sesion = sesion.nombre
        
        db.session.delete(sesion)
        db.session.commit()
        
        return _build_response(
            True,
            message=f'Sesión "{nombre_sesion}" eliminada exitosamente',
        )
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        return _build_response(False, error=f'Error al eliminar sesión: {str(exc)}', status_code=500)


# ============================================================================
# CRUD DE TIPOS DE EVENTO
# ============================================================================



# ============================================================================
# ENDPOINTS ADICIONALES
# ============================================================================

@eventos_bp.route('/proximos', methods=['GET'])
@token_required(required_roles=ROLES_GENERALES, required_active_roles=ROLES_GENERALES)
def eventos_proximos() -> JsonResponse:
    """
    Lista eventos futuros aplicando restricciones de rol.

    GET /api/eventos/proximos?limit=10&categoria_id=1

    Query params:
        limit (int, opcional): Número máximo de eventos a retornar (default: 10)
        categoria_id (int, opcional): Filtrar por categoría

    Returns:
        Lista de eventos próximos o error.
    """
    try:
        # Verificar si el usuario tiene solo rol "Usuario"
        es_usuario_solo = _es_usuario_solo_rol_usuario()
        
        categorias_permitidas = obtener_categorias_permitidas_usuario()
        
        limit = request.args.get('limit', 10, type=int)
        categoria_id = request.args.get('categoria_id', type=int)
        
        query = Evento.query.filter(Evento.fecha_evento >= date.today())
        
        # Aplicar filtros según el rol del usuario
        if es_usuario_solo:
            query = query.filter(Evento.id_tipo_evento.in_(TIPOS_EVENTO_PUBLICOS))
        elif categorias_permitidas is None:
            if categoria_id:
                query = query.filter_by(id_categoria=categoria_id)
        else:
            query, error_response = _aplicar_filtro_deportista_acudiente_proximos(
                query, categorias_permitidas, categoria_id
            )
            if error_response:
                return error_response

        eventos = query.order_by(Evento.fecha_evento.asc()).limit(limit).all()
        eventos_data = []
        for evento in eventos:
            try:
                eventos_data.append(_serializar_evento(evento))
            except Exception as exc:  # pragma: no cover
                logger.warning('Error procesando evento %s: %s', evento.id_evento, str(exc))
                continue

        return HttpResponseBuilder.success(data=eventos_data, total=len(eventos_data))
    except Exception as exc:  # pylint: disable=broad-except
        return handle_exception(exc, logger, "obtener eventos próximos")


@eventos_bp.route('/categoria/<int:categoria_id>', methods=['GET'])
@token_required(required_roles=ROLES_GENERALES, required_active_roles=ROLES_GENERALES)
def eventos_por_categoria(categoria_id: int) -> JsonResponse:
    """
    Lista los eventos de una categoría específica.

    GET /api/eventos/categoria/<categoria_id>

    Args:
        categoria_id: ID de la categoría

    Returns:
        Lista de eventos de la categoría o error.
    """
    try:
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return _build_response(
                False,
                error=ERROR_CATEGORIA_NO_ENCONTRADA.format(id=categoria_id),
                status_code=404,
            )
        
        eventos = Evento.query.filter_by(id_categoria=categoria_id).order_by(Evento.fecha_evento.desc()).all()
        eventos_data = [_serializar_evento(evento) for evento in eventos]

        return _build_response(
            True,
            data=eventos_data,
            categoria=categoria.to_dict(),
            total=len(eventos_data),
        )
    except Exception as exc:  # pylint: disable=broad-except
        return _build_response(
            False,
            error=f'Error al obtener eventos por categoría: {str(exc)}',
            status_code=500,
        )

