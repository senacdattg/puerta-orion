import re

from flask import Blueprint, request, jsonify
from src.models.base import db
from src.models import (
    Parentesco,
    EPS,
    Escuela,
    Deporte,
    CiudadResidencia,
    InstitucionRegistro,
    TipoEvento,
    TipoEnfermedad,
    TipoDocumento,
    Sexo
)
from src.models.pagos.metodo_pago import MetodoPago
from src.models.roles_y_permisos.rol import Rol
from src.utils.validations import (
    ValidationError,
    validate_name,
    sanitize_free_text,
    normalize_upper,
)

dynamic_data_bp = Blueprint('dynamic_data', __name__)

# Mapeo de temas a modelos
TEMA_MODELOS = {
    'parentesco': Parentesco,
    'eps': EPS,
    'escuela': Escuela,
    'deporte': Deporte,
    'ciudad-residencia': CiudadResidencia,
    'institucion-registro': InstitucionRegistro,
    'tipo-evento': TipoEvento,
    'tipo-enfermedad': TipoEnfermedad,
    'roles': Rol,
    'metodo-pago': MetodoPago,
    'tipo-documento': TipoDocumento,
    'sexo': Sexo
}

# Mapeo de temas a nombres de campos
TEMA_CAMPOS = {
    'parentesco': 'nombre',
    'eps': 'nombre_eps',
    'escuela': 'nombre',
    'deporte': 'nombre',
    'ciudad-residencia': 'nombre_ciudad',
    'institucion-registro': 'nombre_institucion',
    'tipo-evento': 'nombre',
    'tipo-enfermedad': 'nombre',
    'roles': 'nombre_rol',
    'metodo-pago': 'nombre_metodo',
    'tipo-documento': 'nombre_documento',
    'sexo': 'nombre'
}

STRICT_NAME_TOPICS = {
    'tipo-documento',
    'sexo',
    'parentesco',
    'metodo-pago',
    'deporte',
    'escuela',
    'tipo-evento',
    'tipo-enfermedad',
    'roles',
}

FREE_TEXT_TOPICS = {
    'eps',
    'ciudad-residencia',
    'institucion-registro',
}

def normalizar_nombre_por_tema(tema, campo, valor):
    if tema in STRICT_NAME_TOPICS:
        return validate_name(campo, valor)
    # Usar texto libre para temas que podrían incluir caracteres especiales o números
    return sanitize_free_text(campo, valor, max_length=120)


def normalizar_codigo_eps(valor):
    if not valor:
        return None
    codigo = normalize_upper(str(valor))
    codigo = re.sub(r'[^A-Z0-9\-]', '', codigo)
    if len(codigo) < 2 or len(codigo) > 20:
        raise ValidationError('El código de la EPS debe tener entre 2 y 20 caracteres alfanuméricos (puede incluir guiones)')
    return codigo


def normalizar_descripcion(valor, max_length=500):
    if not valor:
        return ''
    return sanitize_free_text('descripcion', valor, max_length=max_length)


def normalizar_estado_bool(valor, default=True):
    if valor is None:
        return default
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, (int, float)):
        return bool(int(valor))
    if isinstance(valor, str):
        return valor.strip().lower() in {'1', 'true', 'activo', 'activa', 'sí', 'si', 'on'}
    return default

def validar_tema(tema):
    """Valida que el tema sea válido"""
    if tema not in TEMA_MODELOS:
        return False, f"Tema '{tema}' no válido. Temas disponibles: {', '.join(TEMA_MODELOS.keys())}"
    return True, None

def obtener_modelo_y_campo(tema):
    """Obtiene el modelo y campo correspondiente al tema"""
    modelo = TEMA_MODELOS[tema]
    campo_nombre = TEMA_CAMPOS[tema]
    return modelo, campo_nombre

@dynamic_data_bp.route('/dynamic-data/<tema>', methods=['GET'])
def listar_datos_dinamicos(tema):
    """Listar todos los registros de un tema específico"""
    try:
        # Validar tema
        es_valido, error = validar_tema(tema)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Obtener modelo
        modelo, _ = obtener_modelo_y_campo(tema)
        
        # Consultar registros (filtrar por estado si existe el campo)
        if hasattr(modelo, 'estado'):
            registros = modelo.query.filter_by(estado=True).all()
        else:
            registros = modelo.query.all()
        
        return jsonify({
            'success': True,
            'data': [registro.to_dict() for registro in registros],
            'total': len(registros),
            'tema': tema
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_data_bp.route('/dynamic-data/<tema>', methods=['POST'])
def crear_dato_dinamico(tema):
    """Crear un nuevo registro en un tema específico"""
    try:
        # Validar tema
        es_valido, error = validar_tema(tema)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Obtener modelo y campo
        modelo, campo_nombre = obtener_modelo_y_campo(tema)
        
        # Validar campo requerido
        if campo_nombre not in data:
            return jsonify({
                'success': False,
                'error': f'Campo requerido: {campo_nombre}'
            }), 400
        
        try:
            nombre = normalizar_nombre_por_tema(tema, campo_nombre, data[campo_nombre])
        except ValidationError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        # Verificar si ya existe
        if hasattr(modelo, 'estado'):
            filtro = {campo_nombre: nombre, 'estado': True}
        else:
            filtro = {campo_nombre: nombre}
        existe = modelo.query.filter_by(**filtro).first()
        if existe:
            return jsonify({
                'success': False,
                'error': f'Ya existe un registro con {campo_nombre}: {nombre}'
            }), 400
        
        # Crear nuevo registro
        nuevo_registro = modelo()
        setattr(nuevo_registro, campo_nombre, nombre)
        if hasattr(nuevo_registro, 'estado'):
            nuevo_registro.estado = normalizar_estado_bool(data.get('estado'), True)
        
        # Manejar campos adicionales específicos por modelo
        if tema == 'eps':
            codigo_raw = data.get('codigo_eps') or data.get('codigo')
            if codigo_raw:
                try:
                    nuevo_registro.codigo_eps = normalizar_codigo_eps(codigo_raw)
                except ValidationError as e:
                    return jsonify({'success': False, 'error': str(e)}), 400
        elif tema == 'tipo-evento' and 'descripcion' in data:
            nuevo_registro.descripcion = normalizar_descripcion(data.get('descripcion'))
        elif tema == 'roles' and 'descripcion' in data:
            nuevo_registro.descripcion = normalizar_descripcion(data.get('descripcion'), max_length=300)
        
        # Guardar en base de datos
        db.session.add(nuevo_registro)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Registro creado exitosamente',
            'data': nuevo_registro.to_dict(),
            'tema': tema
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_data_bp.route('/dynamic-data/<tema>/<int:id>', methods=['PUT'])
def actualizar_dato_dinamico(tema, id):
    """Actualizar un registro específico de un tema"""
    try:
        # Validar tema
        es_valido, error = validar_tema(tema)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Obtener datos del request
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Obtener modelo y campo
        modelo, campo_nombre = obtener_modelo_y_campo(tema)
        
        # Buscar registro
        registro = modelo.query.get(id)
        if not registro:
            return jsonify({
                'success': False,
                'error': f'Registro con ID {id} no encontrado'
            }), 404
        
        # Validar campo requerido
        if campo_nombre not in data:
            return jsonify({
                'success': False,
                'error': f'Campo requerido: {campo_nombre}'
            }), 400
        
        try:
            nuevo_nombre = normalizar_nombre_por_tema(tema, campo_nombre, data[campo_nombre])
        except ValidationError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        
        # Verificar si el nuevo nombre ya existe en otro registro
        if hasattr(modelo, 'estado'):
            filtro = {campo_nombre: nuevo_nombre, 'estado': True}
        else:
            filtro = {campo_nombre: nuevo_nombre}
        
        # Obtener la clave primaria del modelo
        pk_column = modelo.__table__.primary_key.columns.values()[0]
        pk_name = pk_column.name
        
        existe = modelo.query.filter_by(**filtro).filter(getattr(modelo, pk_name) != id).first()
        if existe:
            return jsonify({
                'success': False,
                'error': f'Ya existe otro registro con {campo_nombre}: {nuevo_nombre}'
            }), 400
        
        # Actualizar registro
        setattr(registro, campo_nombre, nuevo_nombre)
        
        # Manejar campos adicionales específicos por modelo
        if tema == 'eps':
            codigo_raw = data.get('codigo_eps') or data.get('codigo')
            if codigo_raw is not None:
                if codigo_raw == '':
                    registro.codigo_eps = None
                else:
                    try:
                        registro.codigo_eps = normalizar_codigo_eps(codigo_raw)
                    except ValidationError as e:
                        return jsonify({'success': False, 'error': str(e)}), 400
            if 'estado' in data:
                registro.estado = normalizar_estado_bool(data.get('estado'), registro.estado)
        elif tema == 'metodo-pago' and 'estado' in data:
            registro.estado = normalizar_estado_bool(data.get('estado'), registro.estado)
        elif tema == 'tipo-evento' and 'descripcion' in data:
            registro.descripcion = normalizar_descripcion(data.get('descripcion'))
        elif tema == 'roles' and 'descripcion' in data:
            registro.descripcion = normalizar_descripcion(data.get('descripcion'), max_length=300)
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Registro actualizado exitosamente',
            'data': registro.to_dict(),
            'tema': tema
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_data_bp.route('/dynamic-data/<tema>/<int:id>', methods=['DELETE'])
def eliminar_dato_dinamico(tema, id):
    """Eliminar (desactivar) un registro específico de un tema"""
    try:
        # Validar tema
        es_valido, error = validar_tema(tema)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Obtener modelo
        modelo, _ = obtener_modelo_y_campo(tema)
        
        # Buscar registro
        registro = modelo.query.get(id)
        if not registro:
            return jsonify({
                'success': False,
                'error': f'Registro con ID {id} no encontrado'
            }), 404
        
        # Verificar si está siendo usado (opcional - puedes implementar esta validación)
        # Por ahora solo desactivamos o eliminamos
        
        # Desactivar registro (soft delete) si tiene campo estado, sino eliminar físicamente
        if hasattr(registro, 'estado'):
            registro.estado = False
        else:
            db.session.delete(registro)
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Registro eliminado exitosamente',
            'tema': tema
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@dynamic_data_bp.route('/dynamic-data/<tema>/<int:id>', methods=['GET'])
def obtener_dato_dinamico(tema, id):
    """Obtener un registro específico de un tema"""
    try:
        # Validar tema
        es_valido, error = validar_tema(tema)
        if not es_valido:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Obtener modelo
        modelo, _ = obtener_modelo_y_campo(tema)
        
        # Buscar registro
        registro = modelo.query.get(id)
        if not registro:
            return jsonify({
                'success': False,
                'error': f'Registro con ID {id} no encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': registro.to_dict(),
            'tema': tema
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
