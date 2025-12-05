"""
Rutas para la gestión de archivos e imágenes de la galería.

Responsabilidad:
- Subir imágenes respetando límites de peso y extensiones permitidas.
- Eliminar archivos físicos junto con su registro en base de datos.
- Reparar URLs relativas generadas previamente.

El módulo respeta principios SOLID, DRY y PEP8.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Tuple
import uuid

from flask import Blueprint, Flask, Response, current_app, jsonify, request
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..middleware.auth_decorator import token_required
from ..models.base import db
from ..models.categorias.categoria import Categoria
from ..models.eventos.tipo_evento import TipoEvento
from ..models.galeria.galeria import Galeria
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError
from ..utils.validations import ValidationError, sanitize_free_text

JsonResponse = Tuple[Response, int]

archivos_bp = Blueprint('archivos', __name__, url_prefix='/api/archivos')
logger = obtener_registrador('aplicacion')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
UPLOAD_PATH = Path('static') / 'uploads' / 'galeria'
BASE_IMAGE_URL_DEFAULT = 'http://localhost:5000'


# ============================================================================
# UTILIDADES
# ============================================================================

def _build_response(success: bool, status_code: int = 200, **payload: Any) -> JsonResponse:
    """Construye una respuesta JSON estandarizada."""
    body = {'success': success, **payload}
    return jsonify(body), status_code


def _allowed_file(filename: str) -> bool:
    """Verifica si el archivo tiene una extensión permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _generate_unique_filename(original_filename: str) -> str:
    """Genera un nombre de archivo único preservando la extensión."""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_id = uuid.uuid4().hex
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{timestamp}_{unique_id}.{ext}"


def _obtener_upload_folder() -> Path:
    """Obtiene la ruta absoluta donde se guardarán los archivos."""
    base_path = Path(current_app.root_path)
    upload_folder = base_path / UPLOAD_PATH
    upload_folder.mkdir(parents=True, exist_ok=True)
    return upload_folder


def _obtener_base_url() -> str:
    """Obtiene la URL base para servir imágenes estáticas (configurable)."""
    return current_app.config.get('BASE_STATIC_URL', BASE_IMAGE_URL_DEFAULT)


def _validar_y_obtener_archivo() -> Tuple[FileStorage, int]:
    """Valida la presencia y características del archivo enviado."""
    uploaded_file = request.files.get('file')
    if uploaded_file is None:
        raise RequestValidationError('No se envió ningún archivo', status_code=400)
    if uploaded_file.filename == '':
        raise RequestValidationError('No se seleccionó ningún archivo', status_code=400)
    if not _allowed_file(uploaded_file.filename):
        raise RequestValidationError(
            f'Tipo de archivo no permitido. Tipos permitidos: {", ".join(ALLOWED_EXTENSIONS)}',
            status_code=400,
        )

    uploaded_file.seek(0, 2)
    file_size = uploaded_file.tell()
    uploaded_file.seek(0)
    if file_size > MAX_FILE_SIZE:
        raise RequestValidationError(
            f'El archivo es demasiado grande. Tamaño máximo: {MAX_FILE_SIZE // (1024 * 1024)}MB',
            status_code=400,
        )

    return uploaded_file, file_size


def _validar_relaciones(
    id_tipo_evento: Optional[str],
    id_categoria: Optional[str],
) -> Tuple[Optional[int], Optional[int]]:
    """Valida IDs de tipo de evento y categoría si se proporcionan."""
    tipo_evento_id: Optional[int] = None
    categoria_id: Optional[int] = None

    if id_tipo_evento:
        try:
            tipo_evento_id = int(id_tipo_evento)
        except ValueError as exc:
            raise RequestValidationError('ID de tipo de evento inválido', status_code=400) from exc
        if not TipoEvento.query.get(tipo_evento_id):
            raise RequestValidationError(
                f'Tipo de evento con ID {tipo_evento_id} no encontrado',
                status_code=400,
            )

    if id_categoria:
        try:
            categoria_id = int(id_categoria)
        except ValueError as exc:
            raise RequestValidationError('ID de categoría inválido', status_code=400) from exc
        if not Categoria.query.get(categoria_id):
            raise RequestValidationError(
                f'Categoría con ID {categoria_id} no encontrada',
                status_code=400,
            )

    return tipo_evento_id, categoria_id


def _construir_url_imagen(filename: str) -> str:
    """Construye la URL pública de la imagen almacenada."""
    base_url = _obtener_base_url().rstrip('/')
    return f'{base_url}/static/uploads/galeria/{filename}'


def _eliminar_archivo_fisico(url_imagen: str) -> None:
    """Elimina el archivo físico si la URL apunta a un recurso local."""
    if not url_imagen or not url_imagen.startswith('/static/uploads/'):
        return
    file_path = Path(current_app.root_path) / url_imagen.lstrip('/')
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError as exc:  # pragma: no cover
            logger.warning("No se pudo eliminar el archivo %s: %s", file_path, str(exc))


# ============================================================================
# ENDPOINTS
# ============================================================================

@archivos_bp.route('/upload', methods=['POST'])
@token_required(
    required_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
    required_active_roles=['SuperAdmin', 'Administrador', 'Entrenador'],
)
def subir_archivo() -> JsonResponse:
    """
    Sube un archivo de imagen y crea el registro asociado.

    Form data:
        - file: archivo de imagen (requerido)
        - titulo: título de la imagen (requerido)
        - descripcion: descripción (opcional)
        - id_tipo_evento: ID del tipo de evento (opcional)
        - id_categoria: ID de la categoría (opcional)
    """
    try:
        uploaded_file, _ = _validar_y_obtener_archivo()

        titulo_raw = request.form.get('titulo', '')
        descripcion_raw = request.form.get('descripcion', '')
        try:
            titulo = sanitize_free_text('titulo', titulo_raw, max_length=120)
        except ValidationError as exc:
            raise RequestValidationError(str(exc), status_code=400) from exc

        if not titulo:
            raise RequestValidationError('El título es requerido', status_code=400)

        descripcion = (
            sanitize_free_text('descripcion', descripcion_raw, max_length=500)
            if descripcion_raw
            else None
        )

        tipo_evento_id, categoria_id = _validar_relaciones(
            request.form.get('id_tipo_evento'),
            request.form.get('id_categoria'),
        )

        upload_folder = _obtener_upload_folder()
        filename = secure_filename(uploaded_file.filename)
        unique_filename = _generate_unique_filename(filename)
        file_path = upload_folder / unique_filename
        uploaded_file.save(file_path)

        image_url = _construir_url_imagen(unique_filename)

        nueva_imagen = Galeria(
            titulo=titulo,
            url_imagen=image_url,
            descripcion=descripcion,
            id_tipo_evento=tipo_evento_id,
            id_categoria=categoria_id,
        )

        db.session.add(nueva_imagen)
        db.session.commit()

        return _build_response(
            True,
            message='Imagen subida exitosamente',
            data=nueva_imagen.to_dict(),
            status_code=201,
        )
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error("Error al subir archivo: %s", str(exc))
        return _build_response(False, error=f'Error interno del servidor: {str(exc)}', status_code=500)


@archivos_bp.route('/delete/<int:id_galeria>', methods=['DELETE'])
@token_required()
def eliminar_archivo(id_galeria: int) -> JsonResponse:
    """Elimina una imagen y su archivo asociado."""
    try:
        imagen = Galeria.query.get(id_galeria)
        if not imagen:
            return _build_response(False, error='Imagen no encontrada', status_code=404)

        _eliminar_archivo_fisico(imagen.url_imagen)

        db.session.delete(imagen)
        db.session.commit()

        return _build_response(True, message='Imagen eliminada exitosamente')
    except RequestValidationError as exc:
        db.session.rollback()
        return _build_response(False, error=str(exc), status_code=exc.status_code)
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error("Error al eliminar archivo: %s", str(exc))
        return _build_response(False, error=f'Error interno del servidor: {str(exc)}', status_code=500)


@archivos_bp.route('/fix-urls', methods=['POST'])
@token_required()
def arreglar_urls() -> JsonResponse:
    """Convierte URLs relativas de imágenes a URLs absolutas."""
    try:
        imagenes_relativas = Galeria.query.filter(Galeria.url_imagen.like('/static/uploads/%')).all()

        actualizadas = 0
        base_url = _obtener_base_url().rstrip('/')
        for imagen in imagenes_relativas:
            imagen.url_imagen = f'{base_url}{imagen.url_imagen}'
            actualizadas += 1

        db.session.commit()

        return _build_response(
            True,
            message=f'Se actualizaron {actualizadas} URLs de imágenes',
            actualizadas=actualizadas,
        )
    except Exception as exc:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error("Error al arreglar URLs: %s", str(exc))
        return _build_response(False, error=f'Error interno del servidor: {str(exc)}', status_code=500)


# ============================================================================
# REGISTRO DEL BLUEPRINT
# ============================================================================

def registrar_archivos_routes(app: Flask) -> None:
    """Registra las rutas de archivos en la aplicación Flask."""
    app.register_blueprint(archivos_bp)
    logger.info('Rutas de archivos registradas exitosamente')

