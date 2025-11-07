from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import date
from sqlalchemy import or_, cast, String, extract
import re
# Implementación simple para sumar meses sin dependencias externas

def _add_months(base: date, months: int) -> date:
    month = base.month - 1 + months
    year = base.year + month // 12
    month = month % 12 + 1
    day = min(base.day, [31,
                         29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                         31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)

from src.models.base import db
from src.models.pagos.mensualidad import Mensualidad
from src.utils.logger import logger
from src.models.pagos.abono_mensualidad import AbonoMensualidad
from src.middleware.auth_decorator import permission_required, get_current_user, has_role, token_required
from src.utils.validations import validate_document, ValidationError
from src.models.usuarios.usuario import Usuario
from src.models.pagos.metodo_pago import MetodoPago
try:
    # Import defensivo: la ruta del modelo de Persona puede variar
    from src.models.personas.persona import Persona  # type: ignore
except Exception:
    Persona = None  # fallback si no existe o cambia la ruta
def _recalcular_estado_mensualidad(m: Mensualidad):
    # Recalcular saldo pendiente y estado a partir de los abonos
    total_abonos = db.session.query(db.func.coalesce(db.func.sum(AbonoMensualidad.monto), 0)).filter(
        AbonoMensualidad.id_mensualidad == m.id_mensualidad
    ).scalar() or 0
    try:
        total_abonos = float(total_abonos)
    except Exception:
        total_abonos = 0.0

    try:
        monto = float(m.monto_pago)
    except Exception:
        monto = 0.0

    restante = max(0.0, monto - total_abonos)
    m.saldo_pendiente = restante
    if restante == 0:
        m.estado = True
        m.fecha_pago = date.today()
    else:
        m.estado = False
        m.fecha_pago = None


def _estado_texto(m: Mensualidad) -> str:
    try:
        if not m.activo:
            return 'Inactiva'
        if float(m.saldo_pendiente or 0) == 0:
            return 'Pagado'
        # Considerar vencido cuando la fecha de vencimiento es hoy o ya pasó
        if m.fecha_vencimiento and m.fecha_vencimiento <= date.today():
            return 'Vencido'
        return 'Pendiente'
    except Exception:
        return 'Pendiente'


mensualidades_bp = Blueprint('mensualidades', __name__, url_prefix='/api/mensualidades')


def parse_decimal(value):
    try:
        return float(value) if value is not None else None
    except Exception:
        return None


def _buscar_persona_por_documento(numero_documento):
    if Persona is None or not numero_documento:
        return None

    doc_str = str(numero_documento).strip()
    columnas = []
    for nombre in ('numero_documento', 'documento', 'num_documento', 'dni', 'cedula'):
        try:
            col = getattr(Persona, nombre, None)
            if col is not None:
                columnas.append(col)
        except Exception:
            continue

    if not columnas:
        return None

    try:
        condiciones = [cast(columna, String) == doc_str for columna in columnas]
        return db.session.query(Persona).filter(or_(*condiciones)).first()
    except Exception:
        return None


def _persona_tiene_rol_deportista(id_persona):
    if id_persona is None:
        return False

    try:
        usuario = Usuario.query.filter_by(id_persona=id_persona).first()
        if not usuario or not getattr(usuario, 'estado', True):
            return False

        for rol in getattr(usuario, 'roles', []) or []:
            nombre = getattr(rol, 'nombre_rol', None) or getattr(rol, 'nombre', None)
            if nombre and nombre.lower() == 'deportista':
                return True
    except Exception:
        return False

    return False


def _adjuntar_info_persona_dict(mensualidad_obj, destino_dict):
    persona_nombre = None
    persona_documento = None

    try:
        persona_rel = getattr(mensualidad_obj, 'persona', None)
        if persona_rel is not None:
            persona_nombre = getattr(persona_rel, 'nombre', None) or getattr(persona_rel, 'nombres', None) or \
                             getattr(persona_rel, 'nombre_persona', None) or getattr(persona_rel, 'nombre_completo', None)
            persona_documento = getattr(persona_rel, 'documento', None)

        if (persona_nombre is None or persona_documento is None) and Persona is not None and getattr(mensualidad_obj, 'id_persona', None):
            persona_db = db.session.get(Persona, mensualidad_obj.id_persona)
            if persona_db is not None:
                if persona_nombre is None:
                    persona_nombre = getattr(persona_db, 'nombre', None) or getattr(persona_db, 'nombres', None) or \
                                     getattr(persona_db, 'nombre_persona', None) or getattr(persona_db, 'nombre_completo', None)
                if persona_documento is None:
                    persona_documento = getattr(persona_db, 'documento', None)
    except Exception:
        pass

    if persona_documento is not None:
        try:
            persona_documento = re.sub(r'\D', '', str(persona_documento)) or None
        except Exception:
            persona_documento = str(persona_documento)

    destino_dict['persona_nombre'] = persona_nombre
    destino_dict['numero_documento'] = persona_documento
    return destino_dict


@mensualidades_bp.get('/buscar-persona')
@permission_required('crear_mensualidad')
def buscar_persona_por_documento():
    documento_raw = (request.args.get('documento') or '').strip()

    if not documento_raw:
        return jsonify({
            'success': False,
            'error': 'Debes proporcionar un número de documento'
        }), 200

    try:
        documento = validate_document('numero_documento', documento_raw)
    except ValidationError as error:
        return jsonify({
            'success': False,
            'error': str(error)
        }), 200

    persona = _buscar_persona_por_documento(documento)
    if not persona:
        return jsonify({
            'success': True,
            'encontrado': False,
            'message': 'No encontramos una persona registrada con ese número de documento.'
        }), 200

    data = {
        'id_persona': getattr(persona, 'id_persona', None) or getattr(persona, 'id', None),
        'documento': getattr(persona, 'documento', documento),
        'nombre_completo': getattr(persona, 'nombre', None) or getattr(persona, 'nombres', None) or \
                           getattr(persona, 'nombre_persona', None) or getattr(persona, 'nombre_completo', None),
        'estado': bool(getattr(persona, 'estado', True))
    }

    mensaje = 'Persona encontrada y activa.' if data['estado'] else 'Persona encontrada, pero se encuentra inactiva.'
    data['rol_deportista'] = _persona_tiene_rol_deportista(data['id_persona'])

    return jsonify({
        'success': True,
        'encontrado': True,
        'message': mensaje,
        'data': data
    }), 200


@mensualidades_bp.get('/')
@permission_required('ver_mensualidad')
def listar_mensualidades():
    try:
        persona_id = request.args.get('persona_id', type=int)
        # Restricción por rol: Deportista solo ve su persona; Acudiente puede ver sus acudidos
        user = get_current_user()
        if has_role('Deportista') and user and user.get('persona'):
            persona_id = user['persona'].get('id_persona')
        
        # Para acudiente, si no se proporciona persona_id, mostrar todas las de sus acudidos
        acudido_persona_ids = None
        if has_role('Acudiente') and not persona_id:
            # Obtener los deportistas asociados a este acudiente
            from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
            from src.models.acudientes.acudiente import Acudiente
            from src.models.deportistas.deportista import Deportista
            
            # Buscar el acudiente por persona
            if user and user.get('persona'):
                id_persona = user['persona'].get('id_persona')
                acudiente = Acudiente.query.filter_by(id_persona=id_persona).first()
                if acudiente:
                    # Obtener los deportistas asociados
                    relaciones = DeportistaAcudiente.query.filter_by(id_acudiente=acudiente.id_acudiente).all()
                    if relaciones:
                        # Obtener los id_persona de los deportistas asociados
                        deportista_ids = [rel.id_deportista for rel in relaciones]
                        deportistas = Deportista.query.filter(Deportista.id_deportista.in_(deportista_ids)).all()
                        acudido_persona_ids = [dep.id_persona for dep in deportistas if dep.id_persona]
                        if not acudido_persona_ids:
                            # Si no hay acudidos, retornar lista vacía
                            return jsonify({
                                'success': True,
                                'data': [],
                                'page': request.args.get('page', default=1, type=int),
                                'per_page': request.args.get('per_page', default=20, type=int),
                                'total': 0
                            }), 200
                else:
                    # Si no se encuentra el acudiente, retornar lista vacía
                    return jsonify({
                        'success': True,
                        'data': [],
                        'page': request.args.get('page', default=1, type=int),
                        'per_page': request.args.get('per_page', default=20, type=int),
                        'total': 0
                    }), 200
        
        estado = request.args.get('estado')  # 'pagado' | 'pendiente' -> bool
        activo = request.args.get('activo', type=int)
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)

        query = Mensualidad.query

        if persona_id is not None:
            query = query.filter(Mensualidad.id_persona == persona_id)
        elif acudido_persona_ids is not None:
            # Filtrar por los id_persona de los acudidos
            query = query.filter(Mensualidad.id_persona.in_(acudido_persona_ids))

        if estado in ('pagado', 'pendiente'):
            query = query.filter(Mensualidad.estado == (estado == 'pagado'))

        if activo in (0, 1):
            query = query.filter(Mensualidad.activo == bool(activo))

        query = query.order_by(Mensualidad.id_mensualidad.desc())

        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        items = []
        for m in paginated.items:
            d = m.to_dict()
            d['estado_texto'] = _estado_texto(m)
            # Campos adicionales para frontend
            try:
                d['created_at'] = getattr(m, 'created_at', None).isoformat() if getattr(m, 'created_at', None) else None
            except Exception:
                d['created_at'] = None
            d['id_metodo_pago'] = getattr(m, 'id_metodo_pago', None)
            d = _adjuntar_info_persona_dict(m, d)
            items.append(d)
        return jsonify({
            'success': True,
            'data': items,
            'page': page,
            'per_page': per_page,
            'total': paginated.total
        }), 200
    except Exception as e:
        logger.error(f"Error listando mensualidades: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Evitar redirecciones en preflight/solicitudes sin barra final
@mensualidades_bp.route('', methods=['GET'])
@permission_required('ver_mensualidad')
def listar_mensualidades_sin_slash():
    return listar_mensualidades()


@mensualidades_bp.get('/<int:mensualidad_id>')
@permission_required('ver_mensualidad')
def obtener_mensualidad(mensualidad_id: int):
    m = Mensualidad.query.get(mensualidad_id)
    if not m:
        return jsonify({'success': False, 'error': 'Mensualidad no encontrada'}), 404
    # Restringir acceso a Deportista/Acudiente
    user = get_current_user()
    if has_role('Deportista') and user and user.get('persona'):
        if m.id_persona != user['persona'].get('id_persona'):
            return jsonify({'success': False, 'error': 'No autorizado ver esta mensualidad'}), 403
    if has_role('Acudiente'):
        # Para acudiente, permitir solo si coincide con persona_id query param (si viene)
        req_pid = request.args.get('persona_id', type=int)
        if req_pid and m.id_persona != req_pid:
            return jsonify({'success': False, 'error': 'No autorizado ver esta mensualidad'}), 403
    d = m.to_dict()
    d['estado_texto'] = _estado_texto(m)
    # Campos adicionales para frontend
    try:
        d['created_at'] = getattr(m, 'created_at', None).isoformat() if getattr(m, 'created_at', None) else None
    except Exception:
        d['created_at'] = None
    d['id_metodo_pago'] = getattr(m, 'id_metodo_pago', None)
    d = _adjuntar_info_persona_dict(m, d)
    return jsonify({'success': True, 'data': d}), 200


@mensualidades_bp.post('/')
@permission_required('crear_mensualidad')
def crear_mensualidad():
    try:
        data = request.get_json() or {}
        # Validar identificador de persona por id o número de documento
        id_persona = data.get('id_persona')
        numero_documento_raw = data.get('numero_documento') or data.get('documento')
        if isinstance(numero_documento_raw, str):
            numero_documento_raw = numero_documento_raw.strip()

        try:
            numero_documento = validate_document('numero_documento', numero_documento_raw) if numero_documento_raw else None
        except ValidationError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        if not id_persona and not numero_documento:
            return jsonify({'success': False, 'error': 'Debe proporcionar id_persona o numero_documento'}), 400

        estado_ui_raw = data.get('estado_ui')
        if estado_ui_raw is None:
            return jsonify({'success': False, 'error': 'El estado inicial es requerido'}), 400
        estado_ui = str(estado_ui_raw).strip().lower()
        if estado_ui not in ('pagado', 'pendiente'):
            return jsonify({'success': False, 'error': 'El estado inicial debe ser "Pagado" o "Pendiente"'}), 400
        is_pagado_inicial = estado_ui == 'pagado'

        if not data.get('id_metodo_pago') and data.get('id_metodo_pago') not in (0, '0'):
            return jsonify({'success': False, 'error': 'El método de pago es requerido'}), 400

        # Resolver persona por número de documento si aplica
        persona_obj = None
        if not id_persona and numero_documento:
            persona_obj = _buscar_persona_por_documento(numero_documento)
            if not persona_obj:
                return jsonify({'success': False, 'error': 'Persona no encontrada por numero_documento'}), 404
            id_persona = getattr(persona_obj, 'id_persona', None) or getattr(persona_obj, 'id', None)
            if not id_persona:
                return jsonify({'success': False, 'error': 'No se pudo determinar id_persona de la persona encontrada'}), 400

        if id_persona is None:
            return jsonify({'success': False, 'error': 'No se pudo determinar id_persona'}), 400
        try:
            id_persona = int(id_persona)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'id_persona debe ser numérico'}), 400

        if not _persona_tiene_rol_deportista(id_persona):
            return jsonify({'success': False, 'error': 'La persona especificada no tiene el rol "Deportista". No se puede crear la mensualidad.'}), 400

        monto_pago = parse_decimal(data.get('monto_pago'))
        if monto_pago is None or monto_pago <= 0:
            return jsonify({'success': False, 'error': 'monto_pago debe ser > 0'}), 400

        fecha_vencimiento_raw = data.get('fecha_vencimiento')
        if not fecha_vencimiento_raw:
            return jsonify({'success': False, 'error': 'La fecha de vencimiento es requerida'}), 400
        try:
            fecha_vencimiento = date.fromisoformat(str(fecha_vencimiento_raw))
        except ValueError:
            return jsonify({'success': False, 'error': 'fecha_vencimiento no tiene un formato válido (YYYY-MM-DD)'}), 400

        # Saldo pendiente requerido (0 para pagado)
        saldo_bruto = data.get('saldo_pendiente')
        if saldo_bruto in (None, ''):
            if is_pagado_inicial:
                saldo_inicial = 0.0
            else:
                return jsonify({'success': False, 'error': 'El saldo pendiente es requerido'}), 400
        else:
            saldo_inicial = parse_decimal(saldo_bruto)
            if saldo_inicial is None or saldo_inicial < 0:
                return jsonify({'success': False, 'error': 'El saldo pendiente debe ser un número mayor o igual a 0'}), 400
        if saldo_inicial > monto_pago:
            saldo_inicial = monto_pago

        if is_pagado_inicial:
            saldo_inicial = 0.0

        id_metodo_pago_raw = data.get('id_metodo_pago')
        try:
            id_metodo_pago_val = int(id_metodo_pago_raw)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'id_metodo_pago debe ser numérico'}), 400
        metodo_pago_obj = MetodoPago.query.get(id_metodo_pago_val)
        if not metodo_pago_obj:
            return jsonify({'success': False, 'error': f'Método de pago con ID {id_metodo_pago_val} no encontrado'}), 404

        # Validar duplicado mes/año
        existente_mes = Mensualidad.query.filter(
            Mensualidad.id_persona == id_persona,
            extract('year', Mensualidad.fecha_vencimiento) == fecha_vencimiento.year,
            extract('month', Mensualidad.fecha_vencimiento) == fecha_vencimiento.month
        ).first()
        if existente_mes:
            return jsonify({'success': False, 'error': 'Ya existe una mensualidad para este deportista en el mismo mes y año'}), 400

        mensualidad = Mensualidad(
            id_persona=id_persona,
            id_metodo_pago=id_metodo_pago_val,
            monto_pago=monto_pago,
            estado=is_pagado_inicial,
            fecha_pago=date.today() if is_pagado_inicial else None,
            saldo_pendiente=saldo_inicial,
            fecha_vencimiento=fecha_vencimiento,
            activo=True,
        )

        db.session.add(mensualidad)
        db.session.flush()

        if is_pagado_inicial and mensualidad.id_mensualidad:
            try:
                abono_inicial = AbonoMensualidad(
                    id_mensualidad=mensualidad.id_mensualidad,
                    monto=monto_pago,
                    fecha_abono=mensualidad.fecha_pago or date.today(),
                    id_metodo_pago=id_metodo_pago_val
                )
                db.session.add(abono_inicial)
            except Exception as _:
                pass

        db.session.commit()
        data_resp = _adjuntar_info_persona_dict(mensualidad, mensualidad.to_dict())
        return jsonify({'success': True, 'data': data_resp}), 201
    except Exception as e:
        logger.error(f"Error creando mensualidad: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Evitar redirecciones en POST sin barra final
@mensualidades_bp.route('', methods=['POST'])
@permission_required('crear_mensualidad')
def crear_mensualidad_sin_slash():
    return crear_mensualidad()


@mensualidades_bp.put('/<int:mensualidad_id>')
@permission_required('editar_mensualidad')
def actualizar_mensualidad(mensualidad_id: int):
    try:
        m = Mensualidad.query.get(mensualidad_id)
        if not m:
            return jsonify({'success': False, 'error': 'Mensualidad no encontrada'}), 404

        data = request.get_json() or {}

        numero_documento_actualizado = None
        if 'numero_documento' in data:
            try:
                nuevo_documento = validate_document('numero_documento', data['numero_documento'])
            except ValidationError as e:
                return jsonify({'success': False, 'error': str(e)}), 400

            persona_destino = _buscar_persona_por_documento(nuevo_documento)
            if not persona_destino:
                return jsonify({'success': False, 'error': 'Persona no encontrada por numero_documento'}), 404

            nuevo_id_persona = getattr(persona_destino, 'id_persona', None) or getattr(persona_destino, 'id', None)
            if not nuevo_id_persona:
                return jsonify({'success': False, 'error': 'No se pudo determinar id_persona de la persona encontrada'}), 400

            try:
                nuevo_id_persona = int(nuevo_id_persona)
            except (TypeError, ValueError):
                return jsonify({'success': False, 'error': 'id_persona asociado al documento es inválido'}), 400

            if not _persona_tiene_rol_deportista(nuevo_id_persona):
                return jsonify({'success': False, 'error': 'La persona asociada al documento no tiene el rol "Deportista".'}), 400

            if m.id_persona != nuevo_id_persona:
                m.id_persona = nuevo_id_persona
            numero_documento_actualizado = nuevo_documento

        # Permitir actualizar ciertos campos
        if 'id_metodo_pago' in data:
            if data['id_metodo_pago'] in (None, '',):
                return jsonify({'success': False, 'error': 'El método de pago es requerido'}), 400
            else:
                try:
                    nuevo_metodo = int(data['id_metodo_pago'])
                except (TypeError, ValueError):
                    return jsonify({'success': False, 'error': 'id_metodo_pago debe ser numérico'}), 400
                if not MetodoPago.query.get(nuevo_metodo):
                    return jsonify({'success': False, 'error': f'Método de pago con ID {nuevo_metodo} no encontrado'}), 404
                m.id_metodo_pago = nuevo_metodo
        if 'monto_pago' in data:
            monto_pago = parse_decimal(data['monto_pago'])
            if monto_pago is None or monto_pago <= 0:
                return jsonify({'success': False, 'error': 'monto_pago debe ser > 0'}), 400
            m.monto_pago = monto_pago
            if m.saldo_pendiente is not None and m.saldo_pendiente > monto_pago:
                m.saldo_pendiente = monto_pago
        if 'fecha_vencimiento' in data:
            if data['fecha_vencimiento']:
                try:
                    m.fecha_vencimiento = date.fromisoformat(str(data['fecha_vencimiento']))
                except ValueError:
                    return jsonify({'success': False, 'error': 'fecha_vencimiento no tiene un formato válido (YYYY-MM-DD)'}), 400
            else:
                return jsonify({'success': False, 'error': 'La fecha de vencimiento es requerida'}), 400
        if 'saldo_pendiente' in data:
            saldo = parse_decimal(data['saldo_pendiente'])
            if saldo is None or saldo < 0:
                return jsonify({'success': False, 'error': 'saldo_pendiente inválido'}), 400
            if m.monto_pago is not None and saldo > m.monto_pago:
                return jsonify({'success': False, 'error': 'saldo_pendiente no puede ser mayor al monto de la mensualidad'}), 400
            m.saldo_pendiente = saldo
        if 'activo' in data:
            m.activo = bool(int(data['activo'])) if isinstance(data['activo'], str) else bool(data['activo'])

        if not m.fecha_vencimiento:
            return jsonify({'success': False, 'error': 'La fecha de vencimiento es requerida'}), 400

        duplicada_mes = Mensualidad.query.filter(
            Mensualidad.id_persona == m.id_persona,
            extract('year', Mensualidad.fecha_vencimiento) == m.fecha_vencimiento.year,
            extract('month', Mensualidad.fecha_vencimiento) == m.fecha_vencimiento.month,
            Mensualidad.id_mensualidad != mensualidad_id
        ).first()
        if duplicada_mes:
            return jsonify({'success': False, 'error': 'Ya existe una mensualidad para este deportista en el mismo mes y año'}), 400

        # Recalcular estado/fecha_pago si aplica
        if m.saldo_pendiente == 0:
            m.estado = True
            m.fecha_pago = date.today()
        else:
            m.estado = False
            m.fecha_pago = None

        db.session.commit()
        data_resp = _adjuntar_info_persona_dict(m, m.to_dict())
        if numero_documento_actualizado is not None:
            data_resp['numero_documento'] = numero_documento_actualizado
        return jsonify({'success': True, 'data': data_resp}), 200
    except Exception as e:
        logger.error(f"Error actualizando mensualidad: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@mensualidades_bp.patch('/<int:mensualidad_id>/desactivar')
@cross_origin(methods=['PATCH', 'OPTIONS'])
@permission_required('desactivar_mensualidad')
def desactivar_mensualidad(mensualidad_id: int):
    m = Mensualidad.query.get(mensualidad_id)
    if not m:
        return jsonify({'success': False, 'error': 'Mensualidad no encontrada'}), 404
    m.activo = False
    db.session.commit()
    return jsonify({'success': True, 'data': m.to_dict()}), 200


@mensualidades_bp.patch('/<int:mensualidad_id>/reactivar')
@cross_origin(methods=['PATCH', 'OPTIONS'])
@permission_required('reactivar_mensualidad')
def reactivar_mensualidad(mensualidad_id: int):
    m = Mensualidad.query.get(mensualidad_id)
    if not m:
        return jsonify({'success': False, 'error': 'Mensualidad no encontrada'}), 404
    m.activo = True
    db.session.commit()
    return jsonify({'success': True, 'data': m.to_dict()}), 200


@mensualidades_bp.post('/<int:mensualidad_id>/abonar')
@permission_required('abonar_mensualidad')
def abonar_mensualidad(mensualidad_id: int):
    try:
        m = Mensualidad.query.get(mensualidad_id)
        if not m:
            return jsonify({'success': False, 'error': 'Mensualidad no encontrada'}), 404

        data = request.get_json() or {}
        monto_abonado = parse_decimal(data.get('monto_abonado'))
        fecha_abono_str = data.get('fecha_abono')  # opcional; ISO date
        id_metodo_pago_raw = data.get('id_metodo_pago')
        if monto_abonado is None or monto_abonado <= 0:
            return jsonify({'success': False, 'error': 'monto_abonado debe ser > 0'}), 400

        try:
            monto_base = float(m.monto_pago)
        except Exception:
            return jsonify({'success': False, 'error': 'La mensualidad tiene un monto inválido'}), 400
        try:
            saldo_actual = float(m.saldo_pendiente if m.saldo_pendiente is not None else monto_base)
        except Exception:
            saldo_actual = monto_base

        if saldo_actual >= 0 and monto_abonado > saldo_actual + 1e-6:
            return jsonify({'success': False, 'error': 'El monto abonado no puede superar el saldo pendiente'}), 400

        if fecha_abono_str:
            try:
                fecha_abono = date.fromisoformat(str(fecha_abono_str))
            except ValueError:
                return jsonify({'success': False, 'error': 'fecha_abono no tiene un formato válido (YYYY-MM-DD)'}), 400
        else:
            fecha_abono = date.today()

        if id_metodo_pago_raw in (None, '',):
            id_metodo_pago = None
        else:
            try:
                id_metodo_pago = int(id_metodo_pago_raw)
            except (TypeError, ValueError):
                return jsonify({'success': False, 'error': 'id_metodo_pago debe ser numérico'}), 400

        # Calcular meses cubiertos y sobrante
        meses_cubiertos = int(monto_abonado // monto_base) if monto_base > 0 else 0
        sobrante = monto_abonado - (meses_cubiertos * monto_base) if monto_base > 0 else 0

        # Actualizar fecha_vencimiento sumando meses cubiertos
        if meses_cubiertos > 0:
            base = m.fecha_vencimiento if m.fecha_vencimiento and m.fecha_vencimiento > date.today() else date.today()
            m.fecha_vencimiento = _add_months(base, meses_cubiertos)

        # Recalcular saldo_pendiente del período actual
        if meses_cubiertos >= 1:
            m.saldo_pendiente = max(0, monto_base - sobrante) if monto_base > 0 else 0
        else:
            try:
                saldo_float = float(m.saldo_pendiente)
            except Exception:
                saldo_float = saldo_actual
            m.saldo_pendiente = max(0, saldo_float - monto_abonado)

        # Registrar abono en histórico
        abono = AbonoMensualidad(
            id_mensualidad=mensualidad_id,
            monto=monto_abonado,
            fecha_abono=fecha_abono,
            id_metodo_pago=id_metodo_pago
        )
        db.session.add(abono)

        # Estado y fecha de pago (agregado en mensualidad)
        if m.saldo_pendiente == 0:
            m.estado = True
            m.fecha_pago = date.today()
        else:
            m.estado = False
            m.fecha_pago = None

        db.session.commit()
        return jsonify({
            'success': True,
            'data': m.to_dict(),
            'meses_cubiertos': meses_cubiertos,
            'sobrante': sobrante,
            'abono': abono.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error abonando mensualidad: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
@mensualidades_bp.get('/<int:mensualidad_id>/abonos')
@permission_required('ver_mensualidad')
def listar_abonos(mensualidad_id: int):
    try:
        abonos = AbonoMensualidad.query.filter_by(id_mensualidad=mensualidad_id).order_by(AbonoMensualidad.id_abono.desc()).all()
        m = Mensualidad.query.get(mensualidad_id)
        fecha_pago = getattr(m, 'fecha_pago', None)
        fecha_pago_iso = fecha_pago.isoformat() if fecha_pago else None
        data = []
        for a in abonos:
            d = a.to_dict()
            d['es_pago_final'] = (fecha_pago_iso is not None and d.get('fecha_abono') == fecha_pago_iso)
            data.append(d)
        # Si no hay abono registrado para la fecha de pago pero la mensualidad está pagada,
        # agregar un item sintético para que el front muestre monto y método del pago final
        if (m and m.estado and fecha_pago_iso) and not any(x.get('fecha_abono') == fecha_pago_iso for x in data):
            try:
                data.append({
                    'id_abono': None,
                    'id_mensualidad': mensualidad_id,
                    'monto': float(m.monto_pago) if m.monto_pago is not None else 0,
                    'fecha_abono': fecha_pago_iso,
                    'id_metodo_pago': m.id_metodo_pago,
                    'es_pago_final': True,
                })
            except Exception:
                pass
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        logger.error(f"Error listando abonos: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@mensualidades_bp.put('/<int:mensualidad_id>/abonos/<int:abono_id>')
@permission_required('editar_abono_mensualidad')
def actualizar_abono(mensualidad_id: int, abono_id: int):
    try:
        abono = AbonoMensualidad.query.get(abono_id)
        if not abono or abono.id_mensualidad != mensualidad_id:
            return jsonify({'success': False, 'error': 'Abono no encontrado'}), 404

        data = request.get_json() or {}
        if 'monto' in data:
            monto = parse_decimal(data.get('monto'))
            if monto is None or monto <= 0:
                return jsonify({'success': False, 'error': 'monto debe ser > 0'}), 400
            abono.monto = monto
        if 'fecha_abono' in data:
            abono.fecha_abono = date.fromisoformat(data['fecha_abono'])
        if 'id_metodo_pago' in data:
            abono.id_metodo_pago = int(data['id_metodo_pago']) if data['id_metodo_pago'] is not None else None
        _recalcular_estado_mensualidad(Mensualidad.query.get(mensualidad_id))
        db.session.commit()
        return jsonify({'success': True, 'data': abono.to_dict()}), 200
    except Exception as e:
        logger.error(f"Error actualizando abono: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@mensualidades_bp.delete('/<int:mensualidad_id>/abonos/<int:abono_id>')
@permission_required('eliminar_abono_mensualidad')
def eliminar_abono(mensualidad_id: int, abono_id: int):
    try:
        abono = AbonoMensualidad.query.get(abono_id)
        if not abono or abono.id_mensualidad != mensualidad_id:
            return jsonify({'success': False, 'error': 'Abono no encontrado'}), 404
        db.session.delete(abono)
        m = Mensualidad.query.get(mensualidad_id)
        _recalcular_estado_mensualidad(m)
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error eliminando abono: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500



