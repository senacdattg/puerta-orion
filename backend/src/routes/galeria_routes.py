"""
Rutas y lógica de negocio para la galería de imágenes del sistema.

Responsabilidad:
- Listar, crear, actualizar y eliminar imágenes de la galería.
- Proveer catálogos de apoyo (tipos de evento y categorías activas).

El módulo respeta principios SOLID, DRY y PEP8.
"""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

from flask import Blueprint, Flask, Response, jsonify, request

from ..middleware.auth_decorator import token_required
from ..models.base import db
from ..models.categorias.categoria import Categoria
from ..models.eventos.tipo_evento import TipoEvento
from ..models.galeria.galeria import Galeria
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido
from ..utils.validations import ValidationError, sanitize_free_text

JsonResponse = Tuple[Response, int]

DEFAULT_LIMIT = 50
DEFAULT_OFFSET = 0
MIN_LIMIT = 1
MAX_LIMIT = 200
STATIC_GALERIA_PATH = Path('static') / 'uploads' / 'galeria'

ERROR_LISTANDO = 'Error listando galería: {detalle}'
ERROR_OBTENIENDO = 'Error obteniendo imagen: {detalle}'
ERROR_CREANDO = 'Error creando imagen: {detalle}'
ERROR_ACTUALIZANDO = 'Error actualizando imagen: {detalle}'
ERROR_ELIMINANDO = 'Error eliminando imagen: {detalle}'

ERROR_IMAGEN_NO_ENCONTRADA = 'Imagen no encontrada'
ERROR_TITULO_REQUERIDO = 'El título es requerido'
ERROR_DESCRIPCION_REQUERIDA = 'La descripción es requerida'
ERROR_URL_REQUERIDA = 'La URL de la imagen es requerida'
ERROR_TIPO_EVENTO_REQUERIDO = 'El tipo de evento es requerido'
ERROR_TIPO_EVENTO_NO_ENCONTRADO = 'Tipo de evento no encontrado'
ERROR_CATEGORIA_NO_ENCONTRADA = 'Categoría no encontrada'
ERROR_ARCHIVO_NO_ENCONTRADO = 'Archivo físico no encontrado: {ruta}'

logger = obtener_registrador('aplicacion')

galeria_bp = Blueprint('galeria', __name__, url_prefix='/api/galeria')


def _normalizar_limite(limit_param: Optional[int]) -> int:
    """Normaliza el parámetro de límite de resultados."""
    if not isinstance(limit_param, int):
        return DEFAULT_LIMIT
    return max(MIN_LIMIT, min(limit_param, MAX_LIMIT))


def _normalizar_offset(offset_param: Optional[int]) -> int:
    """Normaliza el parámetro de desplazamiento."""
    if not isinstance(offset_param, int):
        return DEFAULT_OFFSET
    return max(DEFAULT_OFFSET, offset_param)


def _aplicar_filtros(
    query,
    id_tipo_evento: Optional[int],
    id_categoria: Optional[int],
):
    """Agrega filtros opcionales a la consulta base."""
    if id_tipo_evento:
        query = query.filter(Galeria.id_tipo_evento == id_tipo_evento)
    if id_categoria:
        query = query.filter(Galeria.id_categoria == id_categoria)
    return query


def _serializar_imagen(imagen: Galeria) -> Dict[str, Any]:
    """Serializa una imagen incluyendo relaciones relevantes."""
    imagen_dict = imagen.to_dict()
    if imagen.tipo_evento:
        imagen_dict['tipo_evento'] = imagen.tipo_evento.to_dict()
    if imagen.categoria:
        imagen_dict['categoria'] = imagen.categoria.to_dict()
    return imagen_dict


def _sanitizar_titulo(valor: Any) -> str:
    """Normaliza y valida el título."""
    try:
        titulo = sanitize_free_text('titulo', valor, max_length=120)
    except ValidationError as exc:
        raise RequestValidationError(str(exc), status_code=400) from exc
    if not titulo:
        raise RequestValidationError(ERROR_TITULO_REQUERIDO, status_code=400)
    return titulo


def _sanitizar_descripcion(valor: Any) -> str:
    """Normaliza y valida la descripción."""
    if not valor:
        raise RequestValidationError(ERROR_DESCRIPCION_REQUERIDA, status_code=400)
    try:
        return sanitize_free_text('descripcion', valor, max_length=500)
    except ValidationError as exc:
        raise RequestValidationError(str(exc), status_code=400) from exc


def _obtener_tipo_evento(tipo_evento_id: Any) -> TipoEvento:
    """Recupera el tipo de evento validando su existencia."""
    if not tipo_evento_id:
        raise RequestValidationError(ERROR_TIPO_EVENTO_REQUERIDO, status_code=400)
    tipo_evento = TipoEvento.query.get(tipo_evento_id)
    if not tipo_evento:
        raise RequestValidationError(ERROR_TIPO_EVENTO_NO_ENCONTRADO, status_code=400)
    return tipo_evento


def _obtener_categoria(categoria_id: Any) -> Optional[Categoria]:
    """Recupera la categoría si se proporciona y existe."""
    if not categoria_id:
        return None
    categoria = Categoria.query.get(categoria_id)
    if not categoria:
        raise RequestValidationError(ERROR_CATEGORIA_NO_ENCONTRADA, status_code=400)
    return categoria


def _extraer_nombre_archivo(url: str) -> Optional[str]:
    """Obtiene el nombre de archivo desde una URL."""
    if not url:
        return None
    parsed = urlparse(url)
    return Path(parsed.path).name or None


def _eliminar_archivo_fisico(nombre_archivo: str) -> None:
    """Elimina el archivo físico asociado si existe."""
    ruta_archivo = STATIC_GALERIA_PATH / nombre_archivo
    if not ruta_archivo.exists():
        logger.warning(ERROR_ARCHIVO_NO_ENCONTRADO.format(ruta=ruta_archivo))
        return
    try:
        ruta_archivo.unlink()
        # Removed logger.info for performance - uncomment for debugging if needed
        # logger.info("Archivo físico eliminado: %s", ruta_archivo)
    except Exception as exc:  # pragma: no cover
        logger.error("Error eliminando archivo físico %s: %s", ruta_archivo, str(exc))


def _build_response(success: bool, **payload) -> JsonResponse:
    """Construye una respuesta JSON estándar."""
    status_code = payload.get('status_code', 200 if success else 500)
    body = {'success': success, **payload}
    return jsonify(body), status_code


@galeria_bp.route('/', methods=['GET'])
@token_required(
    required_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
    required_active_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
)
def listar_galeria() -> JsonResponse:
    """Lista las imágenes de la galería aplicando filtros opcionales."""
    try:
        id_tipo_evento = request.args.get('id_tipo_evento', type=int)
        id_categoria = request.args.get('id_categoria', type=int)
        limit = _normalizar_limite(request.args.get('limit', type=int))
        offset = _normalizar_offset(request.args.get('offset', type=int))

        query = _aplicar_filtros(Galeria.query, id_tipo_evento, id_categoria)
        imagenes = query.offset(offset).limit(limit).all()
        imagenes_data = [_serializar_imagen(imagen) for imagen in imagenes]

        return _build_response(
            True,
            data=imagenes_data,
            total=len(imagenes_data),
            status_code=200,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(ERROR_LISTANDO.format(detalle=str(exc)))
        return _build_response(False, error=ERROR_LISTANDO.format(detalle=str(exc)), status_code=500)


@galeria_bp.route('/<int:id_galeria>', methods=['GET'])
@token_required(
    required_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
    required_active_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
)
def obtener_imagen(id_galeria: int) -> JsonResponse:
    """Obtiene una imagen específica por su identificador."""
    try:
        imagen = Galeria.query.get(id_galeria)
        if not imagen:
            return _build_response(False, error=ERROR_IMAGEN_NO_ENCONTRADA, status_code=404)

        return _build_response(True, data=_serializar_imagen(imagen), status_code=200)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(ERROR_OBTENIENDO.format(detalle=str(exc)))
        return _build_response(False, error=ERROR_OBTENIENDO.format(detalle=str(exc)), status_code=500)


@galeria_bp.route('/', methods=['POST'])
@token_required(
    required_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
    required_active_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
)
def crear_imagen() -> JsonResponse:
    """Crea una nueva imagen en la galería."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo='Content-Type debe ser application/json',
            mensaje_vacio='No se proporcionaron datos',
        )

        titulo = _sanitizar_titulo(data.get('titulo'))
        descripcion = _sanitizar_descripcion(data.get('descripcion'))

        if not data.get('url_imagen'):
            raise RequestValidationError(ERROR_URL_REQUERIDA, status_code=400)

        tipo_evento = _obtener_tipo_evento(data.get('id_tipo_evento'))
        categoria = _obtener_categoria(data.get('id_categoria'))

        nueva_imagen = Galeria(
            titulo=titulo,
            url_imagen=data['url_imagen'],
            descripcion=descripcion,
            id_tipo_evento=tipo_evento.id_tipo_evento,
            id_categoria=categoria.id_categoria if categoria else None,
        )

        db.session.add(nueva_imagen)
        db.session.commit()

        # Removed logger.info for performance - uncomment for debugging if needed
        # logger.info("Imagen creada: %s - %s", nueva_imagen.id_galeria, nueva_imagen.titulo)
        return _build_response(
            True,
            data=_serializar_imagen(nueva_imagen),
            message='Imagen creada exitosamente',
            status_code=201,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except ValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=400)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error(ERROR_CREANDO.format(detalle=str(exc)))
        return _build_response(False, error=ERROR_CREANDO.format(detalle=str(exc)), status_code=500)


@galeria_bp.route('/<int:id_galeria>', methods=['PUT'])
@token_required(
    required_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
    required_active_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
)
def actualizar_imagen(id_galeria: int) -> JsonResponse:
    """Actualiza los datos de una imagen existente."""
    try:
        imagen = Galeria.query.get(id_galeria)
        if not imagen:
            return _build_response(False, error=ERROR_IMAGEN_NO_ENCONTRADA, status_code=404)

        data = obtener_json_requerido(
            request,
            mensaje_tipo='Content-Type debe ser application/json',
            mensaje_vacio='No se proporcionaron datos',
        )

        _obtener_tipo_evento(data.get('id_tipo_evento'))
        _obtener_categoria(data.get('id_categoria'))

        if 'titulo' in data:
            imagen.titulo = _sanitizar_titulo(data.get('titulo'))

        if 'url_imagen' in data:
            if not data['url_imagen']:
                raise RequestValidationError(ERROR_URL_REQUERIDA, status_code=400)
            imagen.url_imagen = data['url_imagen']

        if 'descripcion' in data:
            imagen.descripcion = _sanitizar_descripcion(data['descripcion'])

        if 'id_tipo_evento' in data:
            imagen.id_tipo_evento = data['id_tipo_evento']

        if 'id_categoria' in data:
            imagen.id_categoria = data['id_categoria']

        db.session.commit()

        # Removed logger.info for performance - uncomment for debugging if needed
        # logger.info("Imagen actualizada: %s - %s", imagen.id_galeria, imagen.titulo)
        return _build_response(
            True,
            data=_serializar_imagen(imagen),
            message='Imagen actualizada exitosamente',
            status_code=200,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except ValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=400)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error(ERROR_ACTUALIZANDO.format(detalle=str(exc)))
        return _build_response(False, error=ERROR_ACTUALIZANDO.format(detalle=str(exc)), status_code=500)


@galeria_bp.route('/<int:id_galeria>', methods=['DELETE'])
@token_required(
    required_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
    required_active_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
)
def eliminar_imagen(id_galeria: int) -> JsonResponse:
    """Elimina una imagen y su archivo físico asociado."""
    try:
        imagen = Galeria.query.get(id_galeria)
        if not imagen:
            return _build_response(False, error=ERROR_IMAGEN_NO_ENCONTRADA, status_code=404)

        nombre_archivo = _extraer_nombre_archivo(imagen.url_imagen)
        if nombre_archivo:
            _eliminar_archivo_fisico(nombre_archivo)

        db.session.delete(imagen)
        db.session.commit()

        # Removed logger.info for performance - uncomment for debugging if needed
        # logger.info("Imagen eliminada: %s - %s", id_galeria, imagen.titulo)
        return _build_response(
            True,
            message='Imagen y archivo eliminados exitosamente',
            status_code=200,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error(ERROR_ELIMINANDO.format(detalle=str(exc)))
        return _build_response(False, error=ERROR_ELIMINANDO.format(detalle=str(exc)), status_code=500)


@galeria_bp.route('/catalogos', methods=['GET'])
@token_required(
    required_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
    required_active_roles=[
        'SuperAdmin',
        'Administrador',
        'Entrenador',
        'Deportista',
        'Acudiente',
        'usuario',
    ],
)
def obtener_catalogos() -> JsonResponse:
    """Obtiene catálogos necesarios para la galería."""
    try:
        from ..utils.cache import get_or_set
        
        # Use cache for static catalog data (1 hour TTL)
        tipos_evento = get_or_set(
            'galeria_tipos_evento',
            lambda: [tipo.to_dict() for tipo in TipoEvento.query.all()],
            max_age_seconds=3600
        )
        categorias = get_or_set(
            'galeria_categorias',
            lambda: [cat.to_dict() for cat in Categoria.query.filter_by(estado=True).all()],
            max_age_seconds=3600
        )

        return _build_response(
            True,
            data={
                'tipos_evento': tipos_evento,
                'categorias': categorias,
            },
            status_code=200,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Error obteniendo catálogos de galería: %s", str(exc))
        return _build_response(
            False,
            error=f'Error obteniendo catálogos: {str(exc)}',
            status_code=500,
        )


def registrar_galeria_routes(app: Flask) -> None:
    """Registra las rutas de galería en la aplicación Flask."""
    app.register_blueprint(galeria_bp)
    # Removed logger.info for performance
    # logger.info("Rutas de galería registradas exitosamente")
