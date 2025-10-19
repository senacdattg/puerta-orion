from flask import Blueprint, request, jsonify
from src.models.base import db
from src.models import Persona, TipoDocumento, Sexo
from datetime import date
import re

personas_bp = Blueprint('personas', __name__)

def validar_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_telefono(telefono):
    """Valida formato de teléfono (solo números)"""
    telefono_str = str(telefono).strip()
    return telefono_str.isdigit() and len(telefono_str) >= 7 and len(telefono_str) <= 15

def validar_documento(documento):
    """Valida formato de documento (solo números)"""
    return str(documento).isdigit() and len(str(documento)) >= 6

@personas_bp.route('/personas', methods=['GET'])
def listar_personas():
    """Listar todas las personas con filtros opcionales"""
    try:
        # Parámetros de consulta opcionales
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').strip()
        estado = request.args.get('estado', None)
        
        # Construir consulta base
        query = Persona.query
        
        # Filtro por estado
        if estado is not None:
            estado_bool = estado.lower() == 'true'
            query = query.filter_by(estado=estado_bool)
        
        # Filtro de búsqueda
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Persona.primer_nombre.ilike(search_filter),
                    Persona.segundo_nombre.ilike(search_filter),
                    Persona.primer_apellido.ilike(search_filter),
                    Persona.segundo_apellido.ilike(search_filter),
                    Persona.documento.cast(db.String).ilike(search_filter),
                    Persona.correo_electronico.ilike(search_filter)
                )
            )
        
        # Paginación
        personas = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [persona.to_dict() for persona in personas.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': personas.total,
                'pages': personas.pages,
                'has_next': personas.has_next,
                'has_prev': personas.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@personas_bp.route('/personas/<int:id>', methods=['GET'])
def obtener_persona(id):
    """Obtener una persona específica por ID"""
    try:
        persona = Persona.query.get(id)
        if not persona:
            return jsonify({
                'success': False,
                'error': f'Persona con ID {id} no encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': persona.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@personas_bp.route('/personas/<int:id>', methods=['PUT'])
def actualizar_persona(id):
    """Actualizar una persona específica"""
    try:
        # Validar que la petición sea JSON
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type debe ser application/json'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se proporcionaron datos'
            }), 400
        
        # Buscar persona
        persona = Persona.query.get(id)
        if not persona:
            return jsonify({
                'success': False,
                'error': f'Persona con ID {id} no encontrada'
            }), 404
        
        # Validaciones específicas si se proporcionan
        if 'correo_electronico' in data:
            if not validar_email(data['correo_electronico']):
                return jsonify({
                    'success': False,
                    'error': 'Formato de email inválido'
                }), 400
            
            # Verificar que el email no exista en otra persona
            email_existente = Persona.query.filter_by(correo_electronico=data['correo_electronico']).filter(Persona.id_persona != id).first()
            if email_existente:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe otra persona con el email: {data["correo_electronico"]}'
                }), 400
        
        if 'telefono' in data:
            if not validar_telefono(data['telefono']):
                return jsonify({
                    'success': False,
                    'error': 'Formato de teléfono inválido (solo números, mínimo 7 dígitos)'
                }), 400
        
        if 'documento' in data:
            if not validar_documento(data['documento']):
                return jsonify({
                    'success': False,
                    'error': 'Formato de documento inválido (solo números, mínimo 6 dígitos)'
                }), 400
            
            # Verificar que el documento no exista en otra persona
            documento_existente = Persona.query.filter_by(documento=data['documento']).filter(Persona.id_persona != id).first()
            if documento_existente:
                return jsonify({
                    'success': False,
                    'error': f'Ya existe otra persona con el documento: {data["documento"]}'
                }), 400
        
        # Verificar relaciones si se proporcionan
        if 'id_tipo_documento' in data:
            tipo_doc = TipoDocumento.query.get(data['id_tipo_documento'])
            if not tipo_doc:
                return jsonify({
                    'success': False,
                    'error': f'Tipo de documento con ID {data["id_tipo_documento"]} no encontrado'
                }), 400
        
        if 'id_sexo' in data:
            sexo = Sexo.query.get(data['id_sexo'])
            if not sexo:
                return jsonify({
                    'success': False,
                    'error': f'Sexo con ID {data["id_sexo"]} no encontrado'
                }), 400
        
        # Actualizar campos
        campos_actualizables = [
            'primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
            'documento', 'correo_electronico', 'direccion', 'telefono',
            'id_tipo_documento', 'id_sexo', 'estado'
        ]
        
        for campo in campos_actualizables:
            if campo in data:
                if campo in ['correo_electronico']:
                    setattr(persona, campo, data[campo].strip().lower())
                elif campo in ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido', 'direccion']:
                    valor = data[campo].strip() if data[campo] else None
                    setattr(persona, campo, valor)
                else:
                    setattr(persona, campo, data[campo])
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona actualizada exitosamente',
            'data': persona.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@personas_bp.route('/personas/<int:id>', methods=['DELETE'])
def eliminar_persona(id):
    """Eliminar (desactivar) una persona específica"""
    try:
        persona = Persona.query.get(id)
        if not persona:
            return jsonify({
                'success': False,
                'error': f'Persona con ID {id} no encontrada'
            }), 404
        
        # Verificar si tiene relaciones (opcional - puedes implementar esta validación)
        # Por ahora solo desactivamos
        
        # Desactivar persona (soft delete)
        persona.estado = False
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona eliminada exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@personas_bp.route('/personas/<int:id>/activar', methods=['PUT'])
def activar_persona(id):
    """Activar una persona previamente desactivada"""
    try:
        persona = Persona.query.get(id)
        if not persona:
            return jsonify({
                'success': False,
                'error': f'Persona con ID {id} no encontrada'
            }), 404
        
        # Activar persona
        persona.estado = True
        
        # Guardar cambios
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Persona activada exitosamente',
            'data': persona.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
