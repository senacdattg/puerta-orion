from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from datetime import date
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
from src.middleware.auth_decorator import permission_required, get_current_user, has_role
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


@mensualidades_bp.get('/')
@permission_required('ver_mensualidad')
def listar_mensualidades():
    try:
        persona_id = request.args.get('persona_id', type=int)
        # Restricción por rol: Deportista solo ve su persona; Acudiente debe indicar persona_id
        user = get_current_user()
        if has_role('Deportista') and user and user.get('persona'):
            persona_id = user['persona'].get('id_persona')
        if has_role('Acudiente'):
            # Requiere persona_id explícito
            if not persona_id:
                return jsonify({'success': False, 'error': 'persona_id requerido para acudiente'}), 400
        estado = request.args.get('estado')  # 'pagado' | 'pendiente' -> bool
        activo = request.args.get('activo', type=int)
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)

        query = Mensualidad.query

        if persona_id is not None:
            query = query.filter(Mensualidad.id_persona == persona_id)

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
            # Resolver nombre de persona de forma robusta
            persona_nombre = None
            try:
                pers = getattr(m, 'persona', None)
                if pers is not None:
                    persona_nombre = getattr(pers, 'nombre', None) or getattr(pers, 'nombres', None) or \
                                     getattr(pers, 'nombre_persona', None) or getattr(pers, 'nombre_completo', None)
                if not persona_nombre and Persona is not None and getattr(m, 'id_persona', None):
                    # Consulta directa si la relación no está materializada
                    p = db.session.get(Persona, m.id_persona)
                    if p is not None:
                        persona_nombre = getattr(p, 'nombre', None) or getattr(p, 'nombres', None) or \
                                         getattr(p, 'nombre_persona', None) or getattr(p, 'nombre_completo', None)
            except Exception:
                persona_nombre = None
            d['persona_nombre'] = persona_nombre
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
    persona_nombre = None
    try:
        pers = getattr(m, 'persona', None)
        if pers is not None:
            persona_nombre = getattr(pers, 'nombre', None) or getattr(pers, 'nombres', None) or \
                             getattr(pers, 'nombre_persona', None) or getattr(pers, 'nombre_completo', None)
        if not persona_nombre and Persona is not None and getattr(m, 'id_persona', None):
            p = db.session.get(Persona, m.id_persona)
            if p is not None:
                persona_nombre = getattr(p, 'nombre', None) or getattr(p, 'nombres', None) or \
                                 getattr(p, 'nombre_persona', None) or getattr(p, 'nombre_completo', None)
    except Exception:
        persona_nombre = None
    d['persona_nombre'] = persona_nombre
    return jsonify({'success': True, 'data': d}), 200


@mensualidades_bp.post('/')
@permission_required('crear_mensualidad')
def crear_mensualidad():
    try:
        data = request.get_json() or {}
        required = ['id_persona', 'id_metodo_pago', 'monto_pago']
        for field in required:
            if data.get(field) in (None, ''):
                return jsonify({'success': False, 'error': f'{field} es requerido'}), 400

        monto_pago = parse_decimal(data.get('monto_pago'))
        if monto_pago is None or monto_pago <= 0:
            return jsonify({'success': False, 'error': 'monto_pago debe ser > 0'}), 400

        fecha_vencimiento = data.get('fecha_vencimiento')  # ISO date opcional
        # Permitir definir saldo inicial/estado desde el payload (e.g., estado_ui = 'Pagado')
        saldo_inicial = data.get('saldo_pendiente')
        try:
            saldo_inicial = float(saldo_inicial) if saldo_inicial is not None and saldo_inicial != '' else None
        except Exception:
            saldo_inicial = None
        estado_ui = (str(data.get('estado_ui') or '')).strip().lower()
        # Aceptar también 'estado' boolean/string como alternativa
        estado_bool_raw = data.get('estado')
        estado_bool_norm = None
        if isinstance(estado_bool_raw, bool):
            estado_bool_norm = estado_bool_raw
        elif isinstance(estado_bool_raw, (int, float)):
            estado_bool_norm = bool(int(estado_bool_raw))
        elif isinstance(estado_bool_raw, str):
            estado_bool_norm = estado_bool_raw.strip().lower() in ('1', 'true', 'pagado', 'si', 'sí')

        is_pagado_inicial = (estado_ui == 'pagado') or (estado_bool_norm is True) or (saldo_inicial is not None and float(saldo_inicial) == 0)
        saldo_pendiente = 0 if is_pagado_inicial else (saldo_inicial if saldo_inicial is not None else float(monto_pago))

        mensualidad = Mensualidad(
            id_persona=int(data['id_persona']),
            id_metodo_pago=int(data['id_metodo_pago']),
            monto_pago=monto_pago,
            estado=bool(is_pagado_inicial),
            fecha_pago=date.today() if is_pagado_inicial else None,
            saldo_pendiente=saldo_pendiente,
            fecha_vencimiento=date.fromisoformat(fecha_vencimiento) if fecha_vencimiento else None,
            activo=True,
        )

        db.session.add(mensualidad)
        # Necesitamos el id para registrar abono inicial si ya está pagado
        db.session.flush()

        # Si se creó como pagado, registrar abono equivalente con método y monto
        if is_pagado_inicial and mensualidad.id_mensualidad:
            try:
                abono_inicial = AbonoMensualidad(
                    id_mensualidad=mensualidad.id_mensualidad,
                    monto=monto_pago,
                    fecha_abono=mensualidad.fecha_pago or date.today(),
                    id_metodo_pago=mensualidad.id_metodo_pago
                )
                db.session.add(abono_inicial)
            except Exception as _:
                # No bloquear la creación si falla el abono inicial
                pass

        db.session.commit()
        return jsonify({'success': True, 'data': mensualidad.to_dict()}), 201
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

        # Permitir actualizar ciertos campos
        if 'id_metodo_pago' in data:
            m.id_metodo_pago = int(data['id_metodo_pago'])
        if 'monto_pago' in data:
            monto_pago = parse_decimal(data['monto_pago'])
            if monto_pago is None or monto_pago <= 0:
                return jsonify({'success': False, 'error': 'monto_pago debe ser > 0'}), 400
            m.monto_pago = monto_pago
        if 'fecha_vencimiento' in data:
            m.fecha_vencimiento = date.fromisoformat(data['fecha_vencimiento']) if data['fecha_vencimiento'] else None
        if 'saldo_pendiente' in data:
            saldo = parse_decimal(data['saldo_pendiente'])
            if saldo is None or saldo < 0:
                return jsonify({'success': False, 'error': 'saldo_pendiente inválido'}), 400
            m.saldo_pendiente = saldo
        if 'activo' in data:
            m.activo = bool(int(data['activo'])) if isinstance(data['activo'], str) else bool(data['activo'])

        # Recalcular estado/fecha_pago si aplica
        if m.saldo_pendiente == 0:
            m.estado = True
            m.fecha_pago = date.today()
        else:
            m.estado = False
            m.fecha_pago = None

        db.session.commit()
        return jsonify({'success': True, 'data': m.to_dict()}), 200
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
        id_metodo_pago = data.get('id_metodo_pago')
        if monto_abonado is None or monto_abonado <= 0:
            return jsonify({'success': False, 'error': 'monto_abonado debe ser > 0'}), 400

        # Calcular meses cubiertos y sobrante
        meses_cubiertos = int(monto_abonado // float(m.monto_pago))
        sobrante = monto_abonado - (meses_cubiertos * float(m.monto_pago))

        # Actualizar fecha_vencimiento sumando meses cubiertos
        if meses_cubiertos > 0:
            base = m.fecha_vencimiento if m.fecha_vencimiento and m.fecha_vencimiento > date.today() else date.today()
            m.fecha_vencimiento = _add_months(base, meses_cubiertos)

        # Recalcular saldo_pendiente del período actual
        if meses_cubiertos >= 1:
            m.saldo_pendiente = float(m.monto_pago) - sobrante if sobrante > 0 else 0
        else:
            m.saldo_pendiente = max(0, float(m.saldo_pendiente) - sobrante)

        # Registrar abono en histórico
        fecha_abono = date.fromisoformat(fecha_abono_str) if fecha_abono_str else date.today()
        abono = AbonoMensualidad(
            id_mensualidad=mensualidad_id,
            monto=monto_abonado,
            fecha_abono=fecha_abono,
            id_metodo_pago=int(id_metodo_pago) if id_metodo_pago is not None else None
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



