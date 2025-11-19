"""
Rutas de catálogos para el sistema Puerta Orion.

Responsabilidad:
- Exponer endpoints para obtener datos de catálogos.
- Proporcionar acceso a tipos de documento, sexos, catálogos agregados y diferentes
  entidades auxiliares requeridas por el frontend.

El módulo respeta los principios SRP, KISS, DRY y SOLID.
"""

import os
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from flask_cors import cross_origin
from sqlalchemy import text

from ..models.base import db

from ..models.acudientes.acudiente import Acudiente
from ..models.acudientes.parentesco import Parentesco
from ..models.catalogos.tipo_documento import TipoDocumento
from ..models.categorias.categoria import Categoria
from ..models.categorias.sexo import Sexo
from ..models.pagos.metodo_pago import MetodoPago
from ..services.catalogos_service import catalogos_service
from ..utils.logger import obtener_registrador

JsonResponse = Tuple[Response, int]

# Crear Blueprint de catálogos
catalogos_bp = Blueprint('catalogos', __name__, url_prefix='/api/catalogos')
logger = obtener_registrador('aplicacion')

SUCCESS_STATUS = 200
ERROR_STATUS = 500
NOT_FOUND_STATUS = 404

ERROR_INTERNO = 'Error interno del servidor'
ERROR_SOLICITUD = 'Solicitud incorrecta'
ERROR_DEBUG = 'Error en debug: {detalle}'
ERROR_POBLANDO_CATEGORIAS = 'Error poblando categorías: {detalle}'
ERROR_CORRIGIENDO_ESTRUCTURA = 'Error corrigiendo estructura: {detalle}'
MENSAJE_TIPOS_DOCUMENTO = 'Tipos de documento obtenidos exitosamente'
MENSAJE_SEXOS = 'Sexos obtenidos exitosamente'
MENSAJE_METODOS_PAGO = 'Métodos de pago obtenidos exitosamente'
MENSAJE_CATALOGOS = 'Catálogos obtenidos exitosamente'
MENSAJE_TIPOS_ENFERMEDAD = 'Tipos de enfermedad obtenidos exitosamente'
MENSAJE_DIAGNOSTICOS = 'Diagnósticos obtenidos exitosamente'
MENSAJE_CATEGORIAS = 'Categorías obtenidas exitosamente'
MENSAJE_PARENTESCOS = 'Parentescos obtenidos exitosamente'
MENSAJE_PARENTESCOS_VACIO = 'No hay parentescos registrados'
MENSAJE_ACUDIENTES = 'Acudientes obtenidos exitosamente'
MENSAJE_ACUDIENTE_ENCONTRADO = 'Acudiente encontrado exitosamente'
MENSAJE_DEPOR = 'Deportistas obtenidos exitosamente'
MENSAJE_DEPOR_ENCONTRADO = 'Deportista encontrado exitosamente'
MENSAJE_FIX_STRUCTURE = 'Estructura de catálogos corregida exitosamente'
MENSAJE_POBLAR_CATEGORIAS = 'Categorías pobladas exitosamente: {cantidad}'

MAPEO_TIPOS_DOCUMENTO = {
            'Cédula de Ciudadanía': 'cc',
            'Cédula de Extranjería': 'ce',
            'Tarjeta de Identidad': 'ti',
    'Pasaporte': 'pasaporte',
}

MAPEO_SEXOS = {
    'Masculino': 'masculino',
    'Femenino': 'femenino',
    'Otro': 'otro',
}

# Configuración de CORS: En desarrollo local se permite HTTP (localhost)
# En producción, la variable de entorno CORS_ALLOWED_ORIGINS debe contener solo URLs HTTPS
# SonarQube Security Hotspot: HTTP es intencional solo para desarrollo local
# En producción, configure CORS_ALLOWED_ORIGINS con URLs HTTPS en variables de entorno
CORS_ALLOWED_ORIGINS = tuple(  # NOSONAR: python:S5332 - HTTP solo para desarrollo local
    origen.strip()
    for origen in os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://localhost:8080').split(',')
    if origen.strip()
)

CATEGORIAS_INICIALES = [
    {
        'nombre_categoria': 'Fútbol',
        'codigo_categoria': 101,
        'edad_minima': 6,
        'edad_maxima': 18,
    },
    {
        'nombre_categoria': 'Básquetbol',
        'codigo_categoria': 102,
        'edad_minima': 8,
        'edad_maxima': 18,
    },
    {
        'nombre_categoria': 'Voleibol',
        'codigo_categoria': 103,
        'edad_minima': 10,
        'edad_maxima': 18,
    },
    {
        'nombre_categoria': 'Tenis',
        'codigo_categoria': 104,
        'edad_minima': 6,
        'edad_maxima': 18,
    },
    {
        'nombre_categoria': 'Natación',
        'codigo_categoria': 105,
        'edad_minima': 4,
        'edad_maxima': 18,
    },
]


def _build_response(success: bool, status_code: int = SUCCESS_STATUS, **payload: Any) -> JsonResponse:
    """Construye una respuesta JSON estándar."""
    body = {'success': success, **payload}
    body.setdefault('status_code', status_code)
    return jsonify(body), status_code


def _serialize_model_list(registros: Iterable[Any], serializer) -> List[Dict[str, Any]]:
    """Serializa una lista de modelos con la función indicada."""
    return [serializer(registro) for registro in registros]


def _serialize_tipo_documento(tipo: TipoDocumento) -> Dict[str, Any]:
    """Serializa un tipo de documento respetando el mapeo de códigos."""
    codigo = MAPEO_TIPOS_DOCUMENTO.get(
        tipo.nombre_documento,
        tipo.nombre_documento.lower().replace(' ', '_'),
    )
    return {
                'id': tipo.id_documento,
                'codigo': codigo,
        'nombre': tipo.nombre_documento,
    }


def _serialize_sexo(sexo: Sexo) -> Dict[str, Any]:
    """Serializa un sexo aplicando sus valores normalizados."""
    valor = MAPEO_SEXOS.get(sexo.nombre, sexo.nombre.lower())
    return {
        'id': sexo.id_sexo,
        'valor': valor,
        'nombre': sexo.nombre,
    }


def _serialize_metodo_pago(metodo: MetodoPago) -> Dict[str, Any]:
    """Serializa un método de pago activo."""
    return {
        'id_metodo_pago': metodo.id_metodo_pago,
        'nombre': metodo.nombre_metodo,
        'estado': metodo.estado,
    }


def _serialize_categoria(categoria: Categoria) -> Dict[str, Any]:
    """Serializa una categoría activa."""
    return {
        'id_categoria': categoria.id_categoria,
        'nombre_categoria': categoria.nombre_categoria,
        'codigo_categoria': categoria.codigo_categoria,
        'edad_minima': categoria.edad_minima,
        'edad_maxima': categoria.edad_maxima,
    }


def _serialize_parentesco(parentesco: Parentesco) -> Dict[str, Any]:
    """Serializa un parentesco a dict."""
    return parentesco.to_dict()


def _serialize_acudiente(acudiente: Acudiente) -> Dict[str, Any]:
    """Serializa un acudiente con datos de persona si están disponibles."""
    acudiente_dict: Dict[str, Any] = {
        'id_acudiente': acudiente.id_acudiente,
        'id_persona': acudiente.id_persona,
        'estado': acudiente.estado,
    }
    persona = getattr(acudiente, 'persona', None)
    if persona:
        acudiente_dict['persona'] = {
            'id_persona': persona.id_persona,
            'nombre_completo': persona.nombre_completo,
            'documento': persona.documento,
            'correo_electronico': persona.correo_electronico,
        }
    return acudiente_dict


def _serialize_deportista(deportista: Any) -> Dict[str, Any]:
    """Serializa un deportista con datos de persona si están disponibles."""
    deportista_dict: Dict[str, Any] = {
        'id_deportista': deportista.id_deportista,
        'id_persona': deportista.id_persona,
    }
    persona = getattr(deportista, 'persona', None)
    if persona:
        deportista_dict['persona'] = {
            'id_persona': persona.id_persona,
            'nombre_completo': persona.nombre_completo,
            'primer_nombre': persona.primer_nombre,
            'primer_apellido': persona.primer_apellido,
            'segundo_nombre': persona.segundo_nombre,
            'segundo_apellido': persona.segundo_apellido,
            'documento': persona.documento,
            'correo_electronico': persona.correo_electronico,
            'telefono': persona.telefono,
        }
    return deportista_dict


def _handle_unexpected_error(context: str, error: Exception, *, message: Optional[str] = None) -> JsonResponse:
    """Registra un error y retorna la respuesta HTTP correspondiente."""
    logger.error("%s: %s", context, str(error))
    response_message = message or ERROR_INTERNO
    return _build_response(False, status_code=ERROR_STATUS, error=response_message)


def _fetch_persona_por_cedula(cedula: str) -> Optional[Any]:
    """Obtiene una persona por documento si existe."""
    from ..models.personas.persona import Persona  # Importación diferida

    return Persona.query.filter_by(documento=cedula).first()


def _fetch_acudiente_por_persona(persona_id: int) -> Optional[Acudiente]:
    """Obtiene un acudiente activo por ID de persona."""
    return Acudiente.query.filter_by(id_persona=persona_id, estado=True).first()


def _fetch_deportista_por_persona(persona_id: int) -> Optional[Any]:
    """Obtiene un deportista asociado a la persona proporcionada."""
    from ..models.deportistas.deportista import Deportista  # Importación diferida

    return Deportista.query.filter_by(id_persona=persona_id).first()


def _parametro_es_true(valor: Optional[str], default: bool = False) -> bool:
    """Convierte un parámetro textual en booleano."""
    if valor is None:
        return default
    return valor.strip().lower() == 'true'


def _serialize_tipo_documento_debug(tipo: TipoDocumento) -> Dict[str, Any]:
    """Serializa un tipo de documento para el endpoint de debug."""
    return {'id': tipo.id_documento, 'nombre': tipo.nombre_documento}


def _serialize_sexo_debug(sexo: Sexo) -> Dict[str, Any]:
    """Serializa un sexo para el endpoint de debug."""
    return {'id': sexo.id_sexo, 'nombre': sexo.nombre}


def _serialize_categoria_debug(categoria: Categoria) -> Dict[str, Any]:
    """Serializa una categoría para el endpoint de debug."""
    return {
        'id': categoria.id_categoria,
        'nombre': categoria.nombre_categoria,
        'estado': categoria.estado,
    }


def _obtener_debug_info(modelo: Any, serializer) -> Dict[str, Any]:
    """Obtiene información de depuración para un modelo."""
    registros = modelo.query.all()
    return {
        'count': len(registros),
        'tablename': getattr(modelo, '__tablename__', ''),
        'data': [serializer(registro) for registro in registros],
    }


def _consultar_pragma_table(nombre_tabla: str) -> List[Tuple[Any, ...]]:
    """Consulta la metadata de una tabla utilizando PRAGMA."""
    resultado = db.session.execute(text(f'PRAGMA table_info({nombre_tabla})'))
    return resultado.fetchall()


def _obtener_nombres_columnas(nombre_tabla: str) -> List[str]:
    """Obtiene la lista de nombres de columnas de una tabla."""
    return [columna[1] for columna in _consultar_pragma_table(nombre_tabla)]


def _contar_registros(nombre_tabla: str) -> int:
    """Cuenta los registros existentes en una tabla."""
    resultado = db.session.execute(text(f'SELECT COUNT(*) FROM {nombre_tabla}'))
    fila = resultado.fetchone()
    return int(fila[0]) if fila else 0


def _agregar_columna_nombre_sexo(cambios_realizados: List[str]) -> None:
    """Agrega la columna nombre a la tabla de sexos si no existe."""
    columnas_sexo = _obtener_nombres_columnas('puerta_orion_sexo')
    if 'nombre' not in columnas_sexo:
            db.session.execute(text("ALTER TABLE puerta_orion_sexo ADD COLUMN nombre VARCHAR(150)"))
            cambios_realizados.append("Agregada columna 'nombre' a tabla sexos")


def _poblar_tipos_documento_si_vacio(cambios_realizados: List[str]) -> None:
    """Puebla la tabla de tipos de documento si no hay registros."""
    if _contar_registros('puerta_orion_tipo_documento') == 0:
        db.session.execute(
            text(
                """
                INSERT INTO puerta_orion_tipo_documento (
                    id_documento,
                    nombre_documento,
                    created_at,
                    updated_at
                ) VALUES
            (1, 'Cédula de Ciudadanía', datetime('now'), datetime('now')),
            (2, 'Tarjeta de Identidad', datetime('now'), datetime('now')),
            (3, 'Cédula de Extranjería', datetime('now'), datetime('now')),
            (4, 'Pasaporte', datetime('now'), datetime('now')),
            (5, 'Registro Civil', datetime('now'), datetime('now'))
                """
            )
        )
        cambios_realizados.append('Poblados tipos de documento')


def _poblar_sexos_si_vacio(cambios_realizados: List[str]) -> None:
    """Puebla la tabla de sexos si se encuentra vacía."""
    if _contar_registros('puerta_orion_sexo') != 0:
        return

    columnas_info = _consultar_pragma_table('puerta_orion_sexo')
    columnas = [columna[1] for columna in columnas_info]

    if {'sexo', 'nombre'}.issubset(columnas):
        sexos_sql = (
            "INSERT INTO puerta_orion_sexo (id_sexo, sexo, nombre, created_at, updated_at) VALUES "
            "(1, 'M', 'Masculino', datetime('now'), datetime('now')), "
            "(2, 'F', 'Femenino', datetime('now'), datetime('now')), "
            "(3, 'O', 'Otro', datetime('now'), datetime('now'))"
        )
    elif 'nombre' in columnas:
        sexos_sql = (
            "INSERT INTO puerta_orion_sexo (id_sexo, nombre, created_at, updated_at) VALUES "
            "(1, 'Masculino', datetime('now'), datetime('now')), "
            "(2, 'Femenino', datetime('now'), datetime('now')), "
            "(3, 'Otro', datetime('now'), datetime('now'))"
        )
    else:
        sexos_sql = (
            "INSERT INTO puerta_orion_sexo (id_sexo, created_at, updated_at) VALUES "
            "(1, datetime('now'), datetime('now')), "
            "(2, datetime('now'), datetime('now')), "
            "(3, datetime('now'), datetime('now'))"
        )

    db.session.execute(text(sexos_sql))
    cambios_realizados.append('Poblados sexos')


def _insertar_categorias_iniciales() -> List[str]:
    """Inserta las categorías iniciales y retorna sus nombres."""
    categorias_insertadas: List[str] = []
    insert_sql = text(
        """
        INSERT INTO puerta_orion_categoria (
            nombre_categoria,
            codigo_categoria,
            edad_minima,
            edad_maxima,
            estado,
            created_at,
            updated_at
        ) VALUES (
            :nombre_categoria,
            :codigo_categoria,
            :edad_minima,
            :edad_maxima,
            1,
            datetime('now'),
            datetime('now')
        )
        """
    )
    for categoria in CATEGORIAS_INICIALES:
        db.session.execute(insert_sql, categoria)
        categorias_insertadas.append(categoria['nombre_categoria'])
    return categorias_insertadas


@catalogos_bp.route('/tipos-documento', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_tipos_documento() -> JsonResponse:
    """Obtiene todos los tipos de documento disponibles."""
    try:
        tipos_documento = TipoDocumento.query.all()
        datos_tipos = _serialize_model_list(tipos_documento, _serialize_tipo_documento)
        return _build_response(
            True,
            message=MENSAJE_TIPOS_DOCUMENTO,
            data=datos_tipos,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener tipos de documento', error)


@catalogos_bp.route('/sexos', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_sexos() -> JsonResponse:
    """Obtiene todos los sexos disponibles."""
    try:
        sexos = Sexo.query.all()
        datos_sexos = _serialize_model_list(sexos, _serialize_sexo)
        return _build_response(
            True,
            message=MENSAJE_SEXOS,
            data=datos_sexos,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener sexos', error)


@catalogos_bp.route('/metodos-pago', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_metodos_pago() -> JsonResponse:
    """Obtiene los métodos de pago activos."""
    try:
        metodos = MetodoPago.query.filter_by(estado=True).all()
        datos = _serialize_model_list(metodos, _serialize_metodo_pago)
        return _build_response(
            True,
            message=MENSAJE_METODOS_PAGO,
            data=datos,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener métodos de pago', error)


@catalogos_bp.route('/catalogos-completos', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_catalogos_completos() -> JsonResponse:
    """Obtiene todos los catálogos necesarios para inicializar la aplicación."""
    try:
        catalogos = catalogos_service.obtener_catalogos_completos()
        return _build_response(
            True,
            message=MENSAJE_CATALOGOS,
            data=catalogos,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener catálogos', error)


@catalogos_bp.route('/fix-structure', methods=['POST'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('POST',))
def fix_catalogos_structure() -> JsonResponse:
    """
    Corrige la estructura de catálogos asegurando columnas y datos mínimos.
    Este endpoint acepta solo el método POST para mayor seguridad.
    """
    cambios_realizados: List[str] = []
    try:
        _agregar_columna_nombre_sexo(cambios_realizados)
        _poblar_tipos_documento_si_vacio(cambios_realizados)
        _poblar_sexos_si_vacio(cambios_realizados)
        db.session.commit()
        return _build_response(
            True,
            message=MENSAJE_FIX_STRUCTURE,
            cambios=cambios_realizados,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error('Error corrigiendo estructura de catálogos: %s', str(error))
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=ERROR_CORRIGIENDO_ESTRUCTURA.format(detalle=str(error)),
        )


@catalogos_bp.route('/tipos-enfermedad', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_tipos_enfermedad() -> JsonResponse:
    """Lista los tipos de enfermedad disponibles con la opción de incluir diagnósticos."""
    try:
        incluir_diagnosticos = _parametro_es_true(request.args.get('incluir_diagnosticos'), default=False)
        resultado = catalogos_service.obtener_tipos_enfermedad(incluir_diagnosticos=incluir_diagnosticos)
        return _build_response(
            True,
            message=MENSAJE_TIPOS_ENFERMEDAD,
            data=resultado.get('data', []),
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener tipos de enfermedad', error)


@catalogos_bp.route('/diagnosticos', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_diagnosticos() -> JsonResponse:
    """Obtiene diagnósticos opcionalmente filtrados por tipo de enfermedad."""
    try:
        id_tipo_enfermedad = request.args.get('id_tipo_enfermedad', type=int)
        resultado = catalogos_service.obtener_diagnosticos(id_tipo_enfermedad=id_tipo_enfermedad)
        return _build_response(
            True,
            message=MENSAJE_DIAGNOSTICOS,
            data=resultado.get('data', []),
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        return _handle_unexpected_error('Error inesperado al obtener diagnósticos', error)


@catalogos_bp.route('/debug', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def debug_catalogos() -> JsonResponse:
    """Endpoint de depuración para verificar las consultas de catálogos."""
    debug_info: Dict[str, Any] = {}
    entradas_debug = [
        ('tipos_documento', TipoDocumento, _serialize_tipo_documento_debug),
        ('sexos', Sexo, _serialize_sexo_debug),
        ('categorias', Categoria, _serialize_categoria_debug),
    ]

    try:
        for clave, modelo, serializador in entradas_debug:
            try:
                debug_info[clave] = _obtener_debug_info(modelo, serializador)
            except Exception as error:  # pylint: disable=broad-except
                debug_info[clave] = {'error': str(error)}

        return _build_response(True, debug_info=debug_info, status_code=SUCCESS_STATUS)
    except Exception as error:  # pylint: disable=broad-except
        logger.error('Error en debug de catálogos: %s', str(error))
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=ERROR_DEBUG.format(detalle=str(error)),
        )


@catalogos_bp.route('/poblar-categorias', methods=['POST'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('POST', 'OPTIONS'))
def poblar_categorias() -> JsonResponse:
    """Puebla la tabla de categorías con datos iniciales si está vacía."""
    try:
        categorias_existentes = _contar_registros('puerta_orion_categoria')
        if categorias_existentes > 0:
            return _build_response(
                True,
                message=f'Ya existen {categorias_existentes} categorías en la base de datos',
                status_code=SUCCESS_STATUS,
            )

        categorias_insertadas = _insertar_categorias_iniciales()
        db.session.commit()

        return _build_response(
            True,
            message=MENSAJE_POBLAR_CATEGORIAS.format(cantidad=len(categorias_insertadas)),
            categorias_insertadas=categorias_insertadas,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        db.session.rollback()
        logger.error('Error poblando categorías: %s', str(error))
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=ERROR_POBLANDO_CATEGORIAS.format(detalle=str(error)),
        )


@catalogos_bp.route('/categorias', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_categorias() -> JsonResponse:
    """Obtiene todas las categorías activas."""
    try:
        categorias = Categoria.query.filter_by(estado=True).all()
        categorias_data = _serialize_model_list(categorias, _serialize_categoria)
        return _build_response(
            True,
            data=categorias_data,
            message=MENSAJE_CATEGORIAS,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error('Error inesperado al obtener categorías: %s', str(error))
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=f'Error al obtener categorías: {str(error)}',
        )


@catalogos_bp.route('/parentescos', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_parentescos() -> JsonResponse:
    """Obtiene todos los parentescos disponibles."""
    try:
        logger.info('Solicitando lista de parentescos...')
        try:
            parentescos = Parentesco.query.all()
        except Exception as db_error:  # pylint: disable=broad-except
            logger.error('Error al consultar parentescos: %s', str(db_error))
            return _build_response(
                False,
                status_code=ERROR_STATUS,
                data=[],
                error=f'Error al consultar parentescos: {str(db_error)}',
            )

        logger.info('Parentescos encontrados: %s', len(parentescos))
        parentescos_data = _serialize_model_list(parentescos, _serialize_parentesco)
        if not parentescos_data:
            logger.warning('No hay parentescos en la base de datos')
            return _build_response(
                True,
                data=[],
                message=MENSAJE_PARENTESCOS_VACIO,
                status_code=SUCCESS_STATUS,
            )

        return _build_response(
            True,
            data=parentescos_data,
            message=MENSAJE_PARENTESCOS,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error('Error inesperado al obtener parentescos: %s', str(error))
        logger.error(traceback.format_exc())
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=f'Error al obtener parentescos: {str(error)}',
        )


@catalogos_bp.route('/acudientes', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_acudientes() -> JsonResponse:
    """Obtiene acudientes activos o permite buscarlos por cédula."""
    try:
        cedula = request.args.get('cedula', '').strip()
        
        if cedula:
            persona = _fetch_persona_por_cedula(cedula)
            if not persona:
                return _build_response(
                    False,
                    status_code=NOT_FOUND_STATUS,
                    data=None,
                    message='No se encontró ninguna persona con ese documento',
                    sugerencia='El acudiente debe registrarse primero en el sistema',
                )

            acudiente = _fetch_acudiente_por_persona(persona.id_persona)
            if not acudiente:
                return _build_response(
                    False,
                    status_code=NOT_FOUND_STATUS,
                    data=None,
                    message='La persona encontrada no está registrada como acudiente',
                    sugerencia='El acudiente debe completar su registro en el sistema',
                )

            acudiente_dict = _serialize_acudiente(acudiente)
            acudiente_dict['persona'] = {
                'id_persona': persona.id_persona,
                'nombre_completo': persona.nombre_completo,
                'documento': persona.documento,
                'correo_electronico': persona.correo_electronico,
            }

            return _build_response(
                True,
                data=acudiente_dict,
                message=MENSAJE_ACUDIENTE_ENCONTRADO,
                status_code=SUCCESS_STATUS,
            )

        logger.info('Solicitando lista de acudientes...')
        acudientes = Acudiente.query.filter_by(estado=True).all()
        logger.info('Acudientes encontrados: %s', len(acudientes))
        acudientes_data = _serialize_model_list(acudientes, _serialize_acudiente)

        return _build_response(
            True,
            data=acudientes_data,
            message=MENSAJE_ACUDIENTES,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error('Error inesperado al obtener acudientes: %s', str(error))
        logger.error(traceback.format_exc())
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=f'Error al obtener acudientes: {str(error)}',
        )


@catalogos_bp.route('/deportistas', methods=['GET', 'OPTIONS'])
@cross_origin(origins=CORS_ALLOWED_ORIGINS, methods=('GET', 'OPTIONS'))
def obtener_deportistas() -> JsonResponse:
    """Obtiene deportistas o los busca por documento."""
    try:
        cedula = request.args.get('cedula', '').strip()
        
        if cedula:
            persona = _fetch_persona_por_cedula(cedula)
            if not persona:
                return _build_response(
                    False,
                    status_code=NOT_FOUND_STATUS,
                    data=None,
                    message='No se encontró ninguna persona con ese documento',
                    sugerencia='El deportista debe registrarse primero en el sistema',
                )

            deportista = _fetch_deportista_por_persona(persona.id_persona)
            if not deportista:
                return _build_response(
                    False,
                    status_code=NOT_FOUND_STATUS,
                    data=None,
                    message='La persona encontrada no está registrada como deportista',
                    sugerencia='El deportista debe completar su registro en el sistema',
                )

            deportista_dict = _serialize_deportista(deportista)
            deportista_dict.setdefault('persona', {})
            deportista_dict['persona'].update(
                {
                    'id_persona': persona.id_persona,
                    'nombre_completo': persona.nombre_completo,
                    'primer_nombre': persona.primer_nombre,
                    'primer_apellido': persona.primer_apellido,
                    'segundo_nombre': persona.segundo_nombre,
                    'segundo_apellido': persona.segundo_apellido,
                    'documento': persona.documento,
                    'correo_electronico': persona.correo_electronico,
                    'telefono': persona.telefono,
                }
            )

            return _build_response(
                True,
                data=deportista_dict,
                message=MENSAJE_DEPOR_ENCONTRADO,
                status_code=SUCCESS_STATUS,
            )

        logger.info('Solicitando lista de deportistas...')
        from ..models.deportistas.deportista import Deportista  # Importación diferida

        deportistas = Deportista.query.all()
        logger.info('Deportistas encontrados: %s', len(deportistas))
        deportistas_data = _serialize_model_list(deportistas, _serialize_deportista)

        return _build_response(
            True,
            data=deportistas_data,
            message=MENSAJE_DEPOR,
            status_code=SUCCESS_STATUS,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error('Error inesperado al obtener deportistas: %s', str(error))
        logger.error(traceback.format_exc())
        return _build_response(
            False,
            status_code=ERROR_STATUS,
            error=f'Error al obtener deportistas: {str(error)}',
        )


# Manejadores de errores específicos del Blueprint
@catalogos_bp.errorhandler(400)
def bad_request(error: Exception) -> JsonResponse:
    """Manejador para errores 400 (Bad Request)."""
    return _build_response(
        False,
        status_code=400,
        error=ERROR_SOLICITUD,
        message='Verifique los datos enviados',
    )


@catalogos_bp.errorhandler(500)
def internal_error(error: Exception) -> JsonResponse:
    """Manejador para errores 500 (Error interno del servidor)."""
    return _build_response(
        False,
        status_code=ERROR_STATUS,
        error=ERROR_INTERNO,
        message='Contacte al administrador',
    )


# Función para registrar el Blueprint en la aplicación
def registrar_catalogos_routes(app: Flask) -> None:
    """Registra las rutas de catálogos en la aplicación Flask.

    Args:
        app (Flask): Instancia de la aplicación Flask donde se registrarán las rutas.
    """
    app.register_blueprint(catalogos_bp)
    logger.info('Rutas de catálogos registradas exitosamente')
