"""
Servicio para registro completo de deportistas.

Responsabilidad:
- Registrar deportista con toda su información relacionada
- Gestionar información deportiva
- Asociar diagnósticos al deportista
- Coordinar transacciones de base de datos

Este módulo sigue los principios SRP, KISS, DRY, POO y SOLID.
"""

from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from ..models.base import db
from ..models.deportistas.deportista import Deportista
from ..models.deportistas.informacion_deportiva import InformacionDeportiva
from ..models.salud.diagnostico_deportista import DiagnosticoDeportista
from ..models.salud.diagnostico import Diagnostico
from ..models.salud.tipo_enfermedad import TipoEnfermedad
from ..models.personas.persona import Persona
from ..models.categorias.categoria import Categoria
from ..models.acudientes.deportista_acudiente import DeportistaAcudiente
from ..models.acudientes.acudiente import Acudiente
from ..models.acudientes.parentesco import Parentesco
from ..models.roles_y_permisos.usuario_rol import UsuarioRol
from ..models.roles_y_permisos.rol import Rol
from ..models.usuarios.usuario import Usuario
from ..utils.logger import obtener_registrador


class RegistroDeportistaService:
    """Servicio para registro completo de deportistas."""

    @staticmethod
    def _obtener_logger():
        """Obtiene el logger configurado."""
        return obtener_registrador('aplicacion')

    @staticmethod
    def _calcular_categoria_por_fecha_nacimiento(fecha_nacimiento) -> Optional[int]:
        """
        Calcula la categoría del deportista basándose en su fecha de nacimiento.
        
        Args:
            fecha_nacimiento: Puede ser:
                - int: Año de nacimiento (para compatibilidad)
                - str: Fecha en formato ISO (YYYY-MM-DD)
                - date: Objeto date de Python
            
        Returns:
            int: ID de la categoría correspondiente o None si no se encuentra
        """
        logger = RegistroDeportistaService._obtener_logger()
        
        try:
            from datetime import date, datetime
            
            # Calcular la edad actual
            hoy = date.today()
            
            # Convertir fecha_nacimiento a objeto date
            if isinstance(fecha_nacimiento, date):
                fecha_nac = fecha_nacimiento
            elif isinstance(fecha_nacimiento, str):
                # Intentar parsear fecha ISO (YYYY-MM-DD)
                try:
                    fecha_nac = datetime.fromisoformat(fecha_nacimiento).date()
                except ValueError:
                    # Si falla, intentar parsear como año solo
                    año = int(fecha_nacimiento)
                    fecha_nac = date(año, 1, 1)  # Usar 1 de enero como fecha por defecto
            elif isinstance(fecha_nacimiento, int):
                # Compatibilidad con años antiguos
                fecha_nac = date(fecha_nacimiento, 1, 1)
            else:
                logger.error(f'Tipo de fecha_nacimiento no reconocido: {type(fecha_nacimiento)}')
                return None
            
            # Calcular edad exacta
            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            
            # Buscar la categoría que corresponde a esta edad
            categoria = Categoria.query.filter(
                Categoria.edad_minima <= edad,
                Categoria.edad_maxima >= edad,
                Categoria.estado == True
            ).first()
            
            if categoria:
                logger.info(f'Categoría calculada para edad {edad}: {categoria.nombre_categoria}')
                return categoria.id_categoria
            else:
                logger.warning(f'No se encontró categoría para edad {edad}')
                return None
                
        except Exception as e:
            logger.error(f'Error al calcular categoría por fecha de nacimiento: {str(e)}')
            return None

    @staticmethod
    def _validar_ids(datos: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Valida que todos los IDs proporcionados existan en sus respectivas tablas.
        
        Args:
            datos: Diccionario con los datos del deportista
            
        Returns:
            tuple: (True, None) si todo es válido, (False, mensaje_error) si hay error
        """
        logger = RegistroDeportistaService._obtener_logger()
        
        # Importar modelos necesarios
        from ..models.categorias.grupo_sanguineo import GrupoSanguineo
        from ..models.categorias.ciudad_residencia import CiudadResidencia
        from ..models.catalogos.eps import EPS
        from ..models.categorias.escuela import Escuela
        from ..models.categorias.deporte import Deporte
        from ..models.categorias.institucion_registro import InstitucionRegistro
        from ..models.salud.tipo_enfermedad import TipoEnfermedad
        
        datos_deportista = datos.get('datos_deportista', {})
        informacion_deportiva = datos.get('informacion_deportiva', {})
        
        # Validar ID de persona
        if datos_deportista.get('id_persona'):
            persona = Persona.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if not persona:
                return False, 'La persona especificada no existe'
        
        # Validar tipo sanguíneo
        if datos_deportista.get('id_tipo_sanguineo'):
            tipo_sangre = GrupoSanguineo.query.filter_by(id_tipo_sangre=datos_deportista['id_tipo_sanguineo']).first()
            if not tipo_sangre:
                return False, 'El tipo sanguíneo especificado no existe'
        
        # Validar ciudad de residencia
        if datos_deportista.get('id_ciudad_recidencia'):
            ciudad = CiudadResidencia.query.filter_by(id_ciudad=datos_deportista['id_ciudad_recidencia']).first()
            if not ciudad:
                return False, 'La ciudad de residencia especificada no existe'
        
        # Validar EPS
        if datos_deportista.get('id_eps'):
            eps = EPS.query.filter_by(id_eps=datos_deportista['id_eps']).first()
            if not eps:
                return False, 'La EPS especificada no existe'
        
        # Validar escuela
        if informacion_deportiva.get('id_escuela'):
            escuela = Escuela.query.filter_by(id_escuela=informacion_deportiva['id_escuela']).first()
            if not escuela:
                return False, 'La escuela especificada no existe'
        
        # Validar deporte
        if informacion_deportiva.get('id_deporte'):
            deporte = Deporte.query.filter_by(id_deporte=informacion_deportiva['id_deporte']).first()
            if not deporte:
                return False, 'El deporte especificado no existe'
        
        # Validar institución de registro
        if informacion_deportiva.get('id_institucion_registro'):
            institucion = InstitucionRegistro.query.filter_by(id_institucion=informacion_deportiva['id_institucion_registro']).first()
            if not institucion:
                return False, 'La institución de registro especificada no existe'
        
        # Validar tipo de enfermedad
        if datos.get('tipo_enfermedad'):
            tipo_enfermedad = TipoEnfermedad.query.filter_by(id_tipo_enfermedad=datos['tipo_enfermedad']).first()
            if not tipo_enfermedad:
                return False, 'El tipo de enfermedad especificado no existe'
        
        # Validar diagnósticos
        if datos.get('diagnostico'):
            for id_diagnostico in datos['diagnostico']:
                diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
                if not diagnostico:
                    return False, f'El diagnóstico con ID {id_diagnostico} no existe'
        
        return True, None

    @staticmethod
    def registrar_deportista_nuevo(datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra un nuevo deportista con validaciones completas y cálculo automático de categoría.
        
        Args:
            datos: Diccionario con todos los datos del deportista
                - datos_deportista (dict): Datos básicos del deportista
                - informacion_deportiva (dict): Información deportiva
                - tipo_enfermedad (int): ID del tipo de enfermedad seleccionado
                - diagnostico (list): Lista de IDs de diagnósticos
                
        Returns:
            Dict: Respuesta con el resultado de la operación
        """
        logger = RegistroDeportistaService._obtener_logger()
        
        try:
            # Validar estructura de datos
            if 'datos_deportista' not in datos:
                return {
                    'success': False,
                    'message': 'Los datos del deportista son requeridos',
                    'status_code': 400
                }
            
            datos_deportista = datos['datos_deportista']
            
            # Validar campos obligatorios
            campos_requeridos = ['id_persona', 'fecha_nacimiento']
            campos_faltantes = [
                campo for campo in campos_requeridos
                if campo not in datos_deportista or datos_deportista[campo] is None
            ]
            
            if campos_faltantes:
                return {
                    'success': False,
                    'message': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}',
                    'status_code': 400
                }
            
            # Validar que todos los IDs existen
            es_valido, mensaje_error = RegistroDeportistaService._validar_ids(datos)
            if not es_valido:
                return {
                    'success': False,
                    'message': mensaje_error,
                    'status_code': 400
                }
            
            # Validar persona existe
            persona = Persona.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if not persona:
                return {
                    'success': False,
                    'message': 'La persona especificada no existe',
                    'status_code': 404
                }
            
            # Verificar que el usuario no tenga ya el rol "Deportista"
            usuario = Usuario.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if usuario:
                roles_usuario = [rol.nombre_rol for rol in usuario.roles]
                if 'Deportista' in roles_usuario:
                    return {
                        'success': False,
                        'message': 'El usuario ya tiene el rol de deportista. No puede realizar el registro nuevamente.',
                        'status_code': 409
                    }
            
            # Verificar que no existe ya un deportista
            deportista_existente = Deportista.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if deportista_existente:
                return {
                    'success': False,
                    'message': 'Ya existe un deportista para esta persona',
                    'status_code': 409
                }
            
            # Validar tipo de enfermedad y diagnósticos
            tipo_enfermedad_id = datos.get('tipo_enfermedad')
            diagnosticos = datos.get('diagnostico', [])
            
            if tipo_enfermedad_id:
                # Si se selecciona tipo de enfermedad, debe haber diagnósticos
                if not diagnosticos or len(diagnosticos) == 0:
                    return {
                        'success': False,
                        'message': 'Si selecciona un tipo de enfermedad, debe seleccionar al menos un diagnóstico',
                        'status_code': 400
                    }
                
                # Validar que los diagnósticos pertenecen al tipo de enfermedad seleccionado
                for id_diagnostico in diagnosticos:
                    diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
                    if diagnostico and diagnostico.id_tipo_enfermedad != tipo_enfermedad_id:
                        return {
                            'success': False,
                            'message': f'El diagnóstico con ID {id_diagnostico} no corresponde al tipo de enfermedad seleccionado',
                            'status_code': 400
                        }
            
            # Procesar fecha de nacimiento
            fecha_nacimiento_raw = datos_deportista['fecha_nacimiento']
            
            # Convertir fecha de nacimiento a objeto date si viene como string
            fecha_nacimiento_date = None
            if isinstance(fecha_nacimiento_raw, str):
                # Intentar parsear fecha ISO (YYYY-MM-DD)
                try:
                    fecha_nacimiento_date = datetime.fromisoformat(fecha_nacimiento_raw).date()
                except ValueError:
                    # Si falla, tratar como año solo (compatibilidad)
                    try:
                        año = int(fecha_nacimiento_raw)
                        fecha_nacimiento_date = date(año, 1, 1)
                    except ValueError:
                        return {
                            'success': False,
                            'message': f'Formato de fecha de nacimiento inválido: {fecha_nacimiento_raw}',
                            'status_code': 400
                        }
            elif isinstance(fecha_nacimiento_raw, int):
                # Compatibilidad con años antiguos
                fecha_nacimiento_date = date(fecha_nacimiento_raw, 1, 1)
            elif isinstance(fecha_nacimiento_raw, date):
                fecha_nacimiento_date = fecha_nacimiento_raw
            else:
                return {
                    'success': False,
                    'message': f'Tipo de fecha de nacimiento no válido: {type(fecha_nacimiento_raw)}',
                    'status_code': 400
                }
            
            # Calcular categoría automáticamente
            id_categoria = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento(fecha_nacimiento_date)
            
            if not id_categoria:
                return {
                    'success': False,
                    'message': f'No se pudo determinar la categoría para la fecha de nacimiento {fecha_nacimiento_date}',
                    'status_code': 400
                }
            
            # Procesar información deportiva si existe
            id_informacion_deportiva = None
            if 'informacion_deportiva' in datos and datos['informacion_deportiva']:
                info_deportiva = datos['informacion_deportiva']
                
                # Si recomendacion_medica es false, descripcion_recomendacion debe ser null
                recomendacion_medica = info_deportiva.get('recomendacion_medica', False)
                descripcion_recomendacion = None if not recomendacion_medica else info_deportiva.get('descripcion_recomendacion')
                
                informacion = InformacionDeportiva(
                    id_persona=datos_deportista['id_persona'],
                    practica_otro_deporte=info_deportiva.get('practica_otro_deporte', False),
                    participa_escuela=info_deportiva.get('participa_escuela', False),
                    recomendacion_medica=recomendacion_medica,
                    descripcion_recomendacion=descripcion_recomendacion,
                    id_escuela=info_deportiva.get('id_escuela'),
                    id_deporte=info_deportiva.get('id_deporte'),
                    id_institucion_registro=info_deportiva.get('id_institucion_registro')
                )
                
                db.session.add(informacion)
                db.session.flush()
                id_informacion_deportiva = informacion.id_informacion_deportiva
                logger.info(f'Información deportiva creada: ID {id_informacion_deportiva}')
            
            # Crear el deportista
            deportista = Deportista(
                id_persona=datos_deportista['id_persona'],
                id_categoria=id_categoria,
                fecha_ingreso=date.today(),
                fecha_nacimiento=fecha_nacimiento_date,
                id_tipo_sanguineo=datos_deportista.get('id_tipo_sanguineo'),
                id_ciudad_recidencia=datos_deportista.get('id_ciudad_recidencia'),
                id_informacion_deportiva=id_informacion_deportiva,
                id_eps=datos_deportista.get('id_eps')
            )
            
            db.session.add(deportista)
            db.session.flush()
            
            # Asociar diagnósticos si existen
            if diagnosticos and len(diagnosticos) > 0:
                for id_diagnostico in diagnosticos:
                    diagnostico_deportista = DiagnosticoDeportista(
                        id_deportista=deportista.id_deportista,
                        id_diagnostico=id_diagnostico,
                        fecha=date.today()
                    )
                    db.session.add(diagnostico_deportista)
                logger.info(f'{len(diagnosticos)} diagnóstico(s) asociados al deportista {deportista.id_deportista}')
            
            # Asociar acudientes si se proporcionan
            acudientes_data = datos.get('acudientes', [])
            if acudientes_data and len(acudientes_data) > 0:
                # Validar que no se intenten asociar más de 3 acudientes al deportista
                acudientes_existentes = DeportistaAcudiente.query.filter_by(
                    id_deportista=deportista.id_deportista
                ).count()
                
                if acudientes_existentes + len(acudientes_data) > 3:
                    return {
                        'success': False,
                        'message': f'Un deportista solo puede tener máximo 3 acudientes. '
                                   f'Actualmente tiene {acudientes_existentes} acudiente(s) y se intentan asociar {len(acudientes_data)} más.',
                        'status_code': 400
                    }
                
                for acudiente_data in acudientes_data:
                    id_acudiente = acudiente_data.get('id_acudiente')
                    id_parentesco = acudiente_data.get('id_parentesco')
                    es_responsable = acudiente_data.get('es_responsable', False)
                    
                    # Validar que el acudiente existe
                    acudiente = Acudiente.query.filter_by(id_acudiente=id_acudiente).first()
                    if not acudiente:
                        continue
                    
                    # Validar que el parentesco existe
                    parentesco = Parentesco.query.filter_by(id_parentesco=id_parentesco).first()
                    if not parentesco:
                        continue
                    
                    # Validar que no exista ya esta relación
                    relacion_existente = DeportistaAcudiente.query.filter_by(
                        id_deportista=deportista.id_deportista,
                        id_acudiente=id_acudiente
                    ).first()
                    
                    if relacion_existente:
                        logger.warning(f'Ya existe relación entre deportista {deportista.id_deportista} y acudiente {id_acudiente}')
                        continue
                    
                    # Validar que el acudiente no tenga más de 5 deportistas asociados
                    deportistas_acudiente = DeportistaAcudiente.query.filter_by(
                        id_acudiente=id_acudiente
                    ).count()
                    
                    if deportistas_acudiente >= 5:
                        logger.warning(
                            f'Acudiente {id_acudiente} ya tiene {deportistas_acudiente} deportista(s). '
                            'No se puede asociar más (máximo 5).'
                        )
                        continue
                    
                    deportista_acudiente = DeportistaAcudiente(
                        id_deportista=deportista.id_deportista,
                        id_acudiente=id_acudiente,
                        id_parentesco=id_parentesco,
                        es_responsable=es_responsable,
                        fecha_registro=date.today()
                    )
                    db.session.add(deportista_acudiente)
                logger.info(f'{len(acudientes_data)} acudiente(s) asociados al deportista {deportista.id_deportista}')
            
            # Asignar rol de deportista al usuario
            usuario = Usuario.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if usuario:
                rol_deportista = Rol.query.filter_by(nombre_rol='Deportista').first()
                if rol_deportista:
                    # Verificar si ya tiene el rol
                    rol_existente = UsuarioRol.query.filter_by(
                        id_usuario=usuario.id_usuario,
                        id_rol=rol_deportista.id_rol
                    ).first()
                    
                    if not rol_existente:
                        usuario_rol = UsuarioRol(
                            id_usuario=usuario.id_usuario,
                            id_rol=rol_deportista.id_rol
                        )
                        db.session.add(usuario_rol)
                        logger.info(f'Rol de Deportista asignado al usuario ID: {usuario.id_usuario}')
            
            # Commit de toda la transacción
            db.session.commit()
            
            # Obtener el deportista completo con relaciones
            deportista_completo = Deportista.query.filter_by(id_deportista=deportista.id_deportista).first()
            categoria_info = deportista_completo.categoria
            
            logger.info(f'Deportista registrado exitosamente: ID {deportista.id_deportista}')
            
            return {
                'status': 'success',
                'message': 'Deportista registrado correctamente',
                'data': {
                    'id_deportista': deportista.id_deportista,
                    'categoria': categoria_info.nombre_categoria if categoria_info else 'Desconocida',
                    'nombre_persona': persona.nombre_completo
                },
                'status_code': 201
            }
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Error de integridad al registrar deportista: {str(e)}')
            return {
                'status': 'error',
                'message': 'Error de duplicación de datos',
                'status_code': 409
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error inesperado al registrar deportista: {str(e)}')
            return {
                'status': 'error',
                'message': f'Error al registrar deportista: {str(e)}',
                'status_code': 500
            }

    @staticmethod
    def obtener_diagnosticos_por_tipo_enfermedad(id_tipo_enfermedad: int) -> Dict[str, Any]:
        """
        Obtiene los diagnósticos filtrados por tipo de enfermedad.
        
        Args:
            id_tipo_enfermedad: ID del tipo de enfermedad
            
        Returns:
            Dict: Respuesta con los diagnósticos
        """
        logger = RegistroDeportistaService._obtener_logger()
        
        try:
            # Verificar que el tipo de enfermedad existe
            tipo_enfermedad = TipoEnfermedad.query.filter_by(id_tipo_enfermedad=id_tipo_enfermedad).first()
            if not tipo_enfermedad:
                return {
                    'success': False,
                    'message': 'Tipo de enfermedad no encontrado',
                    'status_code': 404
                }
            
            # Obtener diagnósticos por tipo de enfermedad
            diagnosticos = Diagnostico.query.filter_by(id_tipo_enfermedad=id_tipo_enfermedad).all()
            
            return {
                'success': True,
                'data': [diagnostico.to_dict() for diagnostico in diagnosticos],
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f'Error al obtener diagnósticos por tipo de enfermedad: {str(e)}')
            return {
                'success': False,
                'message': f'Error al obtener diagnósticos: {str(e)}',
                'status_code': 500
            }

    @staticmethod
    def obtener_informacion_completa_deportista(id_deportista: int) -> Dict[str, Any]:
        """
        Obtiene la información completa de un deportista por su ID.
        
        Incluye:
        - Datos personales (nombre, documento, tipo sanguíneo, ciudad, EPS)
        - Información deportiva (deporte, escuela, institución, categoría)
        - Diagnósticos médicos asociados
        
        Args:
            id_deportista: ID del deportista
            
        Returns:
            Dict: Respuesta con toda la información del deportista
        """
        logger = RegistroDeportistaService._obtener_logger()
        
        try:
            # Validar que el ID es numérico
            if not isinstance(id_deportista, int) or id_deportista <= 0:
                return {
                    'status': 'error',
                    'message': 'El ID del deportista debe ser un número entero positivo',
                    'status_code': 400
                }
            
            # Buscar el deportista con todas sus relaciones
            deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
            
            if not deportista:
                return {
                    'status': 'error',
                    'message': 'El deportista con el ID especificado no existe',
                    'status_code': 404
                }
            
            # Construir datos de persona
            persona_data = {}
            if deportista.persona:
                persona = deportista.persona
                persona_data = {
                    'id_persona': persona.id_persona,
                    'nombre_completo': persona.nombre_completo,
                    'primer_nombre': persona.primer_nombre,
                    'segundo_nombre': persona.segundo_nombre,
                    'primer_apellido': persona.primer_apellido,
                    'segundo_apellido': persona.segundo_apellido,
                    'documento': persona.documento,
                    'correo_electronico': persona.correo_electronico,
                    'telefono': persona.telefono,
                    'direccion': persona.direccion,
                    'id_tipo_documento': persona.id_tipo_documento
                }
                
                # Agregar fecha de nacimiento si existe
                if deportista.fecha_nacimiento:
                    # Si es Date, convertir a ISO format
                    if isinstance(deportista.fecha_nacimiento, date):
                        persona_data['fecha_nacimiento'] = deportista.fecha_nacimiento.isoformat()
                        # Calcular edad exacta
                        hoy = date.today()
                        edad = hoy.year - deportista.fecha_nacimiento.year - ((hoy.month, hoy.day) < (deportista.fecha_nacimiento.month, deportista.fecha_nacimiento.day))
                        persona_data['edad_aproximada'] = edad
                    else:
                        # Mantener compatibilidad con años antiguos (número)
                        persona_data['fecha_nacimiento'] = deportista.fecha_nacimiento
                        año_actual = date.today().year
                        persona_data['edad_aproximada'] = año_actual - deportista.fecha_nacimiento
                
                # Solo IDs de catálogos (el frontend mapeará los nombres)
                persona_data['id_tipo_sanguineo'] = deportista.id_tipo_sanguineo
                persona_data['id_ciudad_recidencia'] = deportista.id_ciudad_recidencia
                persona_data['id_eps'] = deportista.id_eps
            
            # Construir información deportiva (solo IDs de catálogos)
            info_deportiva = {}
            if deportista.informacion_deportiva:
                info = deportista.informacion_deportiva
                info_deportiva = {
                    'id_informacion_deportiva': info.id_informacion_deportiva,
                    'practica_otro_deporte': info.practica_otro_deporte,
                    'participa_escuela': info.participa_escuela,
                    'recomendacion_medica': info.recomendacion_medica,
                    'descripcion_recomendacion': info.descripcion_recomendacion,
                    # Solo IDs de catálogos (el frontend mapeará los nombres)
                    'id_deporte': info.id_deporte,
                    'id_escuela': info.id_escuela,
                    'id_institucion_registro': info.id_institucion_registro,
                    'id_categoria': deportista.id_categoria
                }
            else:
                info_deportiva = {
                    'practica_otro_deporte': False,
                    'participa_escuela': False,
                    'recomendacion_medica': False,
                    'descripcion_recomendacion': None,
                    'id_deporte': None,
                    'id_escuela': None,
                    'id_institucion_registro': None,
                    'id_categoria': deportista.id_categoria if deportista.id_categoria else None
                }
            
            # Construir información de salud (solo IDs de diagnósticos)
            salud_data = {}
            diagnósticos_deportista = DiagnosticoDeportista.query.filter_by(id_deportista=id_deportista).all()
            
            if diagnósticos_deportista:
                diagnosticos_ids = []
                tipos_enfermedad_ids = set()
                
                for diagnostico_deportista in diagnósticos_deportista:
                    if diagnostico_deportista.diagnostico:
                        diagnosticos_ids.append({
                            'id_diagnostico': diagnostico_deportista.id_diagnostico,
                            'id_tipo_enfermedad': diagnostico_deportista.diagnostico.id_tipo_enfermedad if diagnostico_deportista.diagnostico.tipo_enfermedad else None,
                            'fecha': diagnostico_deportista.fecha.isoformat() if diagnostico_deportista.fecha else None
                        })
                        
                        # Agregar ID de tipo de enfermedad
                        if diagnostico_deportista.diagnostico.tipo_enfermedad:
                            tipos_enfermedad_ids.add(diagnostico_deportista.diagnostico.tipo_enfermedad.id_tipo_enfermedad)
                
                if diagnosticos_ids:
                    salud_data['diagnosticos'] = diagnosticos_ids
                    salud_data['cantidad_diagnosticos'] = len(diagnosticos_ids)
                    salud_data['tipos_enfermedad_ids'] = list(tipos_enfermedad_ids)
            
            # Agregar información adicional del deportista
            datos_deportista_adicionales = {}
            if deportista.peso:
                datos_deportista_adicionales['peso'] = deportista.peso
            if deportista.altura:
                datos_deportista_adicionales['altura'] = deportista.altura
            if deportista.imc:
                datos_deportista_adicionales['imc'] = deportista.imc
            if deportista.fecha_ingreso:
                datos_deportista_adicionales['fecha_ingreso'] = deportista.fecha_ingreso.isoformat()
            
            # Información de mensualidad
            if deportista.mensualidad:
                datos_deportista_adicionales['mensualidad'] = {
                    'monto': float(deportista.mensualidad.monto_pago) if deportista.mensualidad.monto_pago else None,
                    'fecha_pago': deportista.mensualidad.fecha_pago.isoformat() if deportista.mensualidad.fecha_pago else None,
                    'estado': deportista.mensualidad.estado
                }
            
            logger.info(f'Información completa obtenida para deportista ID {id_deportista}')
            
            return {
                'status': 'success',
                'data': {
                    'id': deportista.id_deportista,
                    'persona': persona_data,
                    'informacion_deportiva': info_deportiva,
                    'salud': salud_data,
                    'datos_deportista': datos_deportista_adicionales,
                    'fecha_registro': deportista.created_at.isoformat() if deportista.created_at else None,
                    'ultima_actualizacion': deportista.updated_at.isoformat() if deportista.updated_at else None
                },
                'status_code': 200
            }
            
        except Exception as e:
            logger.error(f'Error al obtener información completa del deportista {id_deportista}: {str(e)}')
            return {
                'status': 'error',
                'message': f'Error al obtener información del deportista: {str(e)}',
                'status_code': 500
            }

