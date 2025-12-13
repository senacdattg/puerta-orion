"""
Servicio para registro completo de deportistas.

Responsabilidad:
- Registrar deportista con toda su información relacionada
- Gestionar información deportiva
- Asociar diagnósticos al deportista
- Coordinar transacciones de base de datos

Este módulo sigue los principios SRP, KISS, DRY, POO y SOLID.
"""

from typing import Dict, Any, Optional, List, Tuple
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
from ..models.pagos.mensualidad import Mensualidad
from ..utils.logger import obtener_registrador
from ..utils.validations import sanitize_free_text


class RegistroDeportistaService:
    """Servicio para registro completo de deportistas."""

    @staticmethod
    def _obtener_logger():
        """Obtiene el logger configurado."""
        return obtener_registrador('aplicacion')
    
    @staticmethod
    def _procesar_fecha_nacimiento(fecha_nacimiento) -> Tuple[Optional[str], Optional[int]]:
        """
        Procesa la fecha de nacimiento y calcula la edad.
        
        Args:
            fecha_nacimiento: Puede ser date o int (año)
            
        Returns:
            tuple: (fecha_formateada, edad_aproximada)
        """
        if isinstance(fecha_nacimiento, date):
            fecha_formateada = fecha_nacimiento.isoformat()
            hoy = date.today()
            edad = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            return fecha_formateada, edad
        
        # Mantener compatibilidad con años antiguos (número)
        anio_actual = date.today().year
        edad = anio_actual - fecha_nacimiento
        return fecha_nacimiento, edad

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
                    anio = int(fecha_nacimiento)
                    fecha_nac = date(anio, 1, 1)  # Usar 1 de enero como fecha por defecto
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
                # Removed logger.info for performance
                # logger.info(f'Categoría calculada para edad {edad}: {categoria.nombre_categoria}')
                return categoria.id_categoria
            else:
                logger.warning(f'No se encontró categoría para edad {edad}')
                return None
                
        except Exception as e:
            logger.error(f'Error al calcular categoría por fecha de nacimiento: {str(e)}')
            return None

    @staticmethod
    def _validar_id_persona(datos_deportista: Dict[str, Any]) -> Optional[str]:
        """Valida que el ID de persona exista."""
        if datos_deportista.get('id_persona'):
            persona = Persona.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            if not persona:
                return 'La persona especificada no existe'
        return None

    @staticmethod
    def _validar_ids_deportista(datos_deportista: Dict[str, Any]) -> Optional[str]:
        """Valida IDs relacionados con datos del deportista."""
        from ..models.categorias.grupo_sanguineo import GrupoSanguineo
        from ..models.categorias.ciudad_residencia import CiudadResidencia
        from ..models.catalogos.eps import EPS
        
        if datos_deportista.get('id_tipo_sanguineo'):
            tipo_sangre = GrupoSanguineo.query.filter_by(id_tipo_sangre=datos_deportista['id_tipo_sanguineo']).first()
            if not tipo_sangre:
                return 'El tipo sanguíneo especificado no existe'
        
        if datos_deportista.get('id_ciudad_recidencia'):
            ciudad = CiudadResidencia.query.filter_by(id_ciudad=datos_deportista['id_ciudad_recidencia']).first()
            if not ciudad:
                return 'La ciudad de residencia especificada no existe'
        
        if datos_deportista.get('id_eps'):
            eps = EPS.query.filter_by(id_eps=datos_deportista['id_eps']).first()
            if not eps:
                return 'La EPS especificada no existe'
        
        return None

    @staticmethod
    def _validar_ids_informacion_deportiva(informacion_deportiva: Dict[str, Any]) -> Optional[str]:
        """Valida IDs relacionados con información deportiva."""
        from ..models.categorias.escuela import Escuela
        from ..models.categorias.deporte import Deporte
        from ..models.categorias.institucion_registro import InstitucionRegistro
        
        if informacion_deportiva.get('id_escuela'):
            escuela = Escuela.query.filter_by(id_escuela=informacion_deportiva['id_escuela']).first()
            if not escuela:
                return 'La escuela especificada no existe'
        
        if informacion_deportiva.get('id_deporte'):
            deporte = Deporte.query.filter_by(id_deporte=informacion_deportiva['id_deporte']).first()
            if not deporte:
                return 'El deporte especificado no existe'
        
        if informacion_deportiva.get('id_institucion_registro'):
            institucion = InstitucionRegistro.query.filter_by(id_institucion=informacion_deportiva['id_institucion_registro']).first()
            if not institucion:
                return 'La institución de registro especificada no existe'
        
        return None

    @staticmethod
    def _validar_ids_salud(datos: Dict[str, Any]) -> Optional[str]:
        """Valida IDs relacionados con salud (tipo de enfermedad y diagnósticos)."""
        from ..models.salud.tipo_enfermedad import TipoEnfermedad
        
        if datos.get('tipo_enfermedad'):
            tipo_enfermedad = TipoEnfermedad.query.filter_by(id_tipo_enfermedad=datos['tipo_enfermedad']).first()
            if not tipo_enfermedad:
                return 'El tipo de enfermedad especificado no existe'
        
        if datos.get('diagnostico'):
            for id_diagnostico in datos['diagnostico']:
                diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
                if not diagnostico:
                    return f'El diagnóstico con ID {id_diagnostico} no existe'
        
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
        datos_deportista = datos.get('datos_deportista', {})
        informacion_deportiva = datos.get('informacion_deportiva', {})
        
        error = RegistroDeportistaService._validar_id_persona(datos_deportista)
        if error:
            return False, error
        
        error = RegistroDeportistaService._validar_ids_deportista(datos_deportista)
        if error:
            return False, error
        
        error = RegistroDeportistaService._validar_ids_informacion_deportiva(informacion_deportiva)
        if error:
            return False, error
        
        error = RegistroDeportistaService._validar_ids_salud(datos)
        if error:
            return False, error
        
        return True, None

    @staticmethod
    def _validar_estructura_datos(datos: Dict[str, Any]) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Valida la estructura básica de los datos y retorna los diccionarios extraídos."""
        if 'datos_deportista' not in datos:
            return None, None
        
        datos_deportista = datos['datos_deportista']
        informacion_deportiva = datos.get('informacion_deportiva') or {}
        datos['informacion_deportiva'] = informacion_deportiva
        
        return datos_deportista, informacion_deportiva

    @staticmethod
    def _validar_campos_requeridos(datos_deportista: Dict[str, Any], informacion_deportiva: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Valida que todos los campos requeridos estén presentes."""
        campos_requeridos = ['id_persona', 'fecha_nacimiento', 'id_tipo_sanguineo', 'id_ciudad_recidencia', 'id_eps']
        campos_faltantes = [
            campo for campo in campos_requeridos
            if campo not in datos_deportista or datos_deportista[campo] in (None, '', [])
        ]
        
        if campos_faltantes:
            return {
                'success': False,
                'message': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}',
                'status_code': 400
            }
        
        campos_info_requeridos = ['id_deporte', 'id_institucion_registro']
        campos_info_faltantes = [
            campo for campo in campos_info_requeridos
            if campo not in informacion_deportiva or informacion_deportiva[campo] in (None, '', [])
        ]
        
        if campos_info_faltantes:
            return {
                'success': False,
                'message': f'Campos requeridos faltantes en informacion_deportiva: {", ".join(campos_info_faltantes)}',
                'status_code': 400
            }
        
        return None

    @staticmethod
    def _validar_persona_y_deportista_existente(id_persona: int) -> Optional[Dict[str, Any]]:
        """Valida que la persona exista y que no haya un deportista ya registrado."""
        persona = Persona.query.filter_by(id_persona=id_persona).first()
        if not persona:
            return {
                'success': False,
                'message': 'La persona especificada no existe',
                'status_code': 404
            }
        
        usuario = Usuario.query.filter_by(id_persona=id_persona).first()
        if usuario:
            roles_usuario = [rol.nombre_rol for rol in usuario.roles]
            if 'Deportista' in roles_usuario:
                return {
                    'success': False,
                    'message': 'El usuario ya tiene el rol de deportista. No puede realizar el registro nuevamente.',
                    'status_code': 409
                }
        
        deportista_existente = Deportista.query.filter_by(id_persona=id_persona).first()
        if deportista_existente:
            return {
                'success': False,
                'message': 'Ya existe un deportista para esta persona',
                'status_code': 409
            }
        
        return None

    @staticmethod
    def _validar_tipo_enfermedad_diagnosticos(tipo_enfermedad_id: Optional[int], diagnosticos: List[int]) -> Optional[Dict[str, Any]]:
        """Valida la relación entre tipo de enfermedad y diagnósticos."""
        if not tipo_enfermedad_id:
            return None
        
        if not diagnosticos or len(diagnosticos) == 0:
            return {
                'success': False,
                'message': 'Si selecciona un tipo de enfermedad, debe seleccionar al menos un diagnóstico',
                'status_code': 400
            }
        
        for id_diagnostico in diagnosticos:
            diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
            if diagnostico and diagnostico.id_tipo_enfermedad != tipo_enfermedad_id:
                return {
                    'success': False,
                    'message': f'El diagnóstico con ID {id_diagnostico} no corresponde al tipo de enfermedad seleccionado',
                    'status_code': 400
                }
        
        return None

    @staticmethod
    def _procesar_fecha_nacimiento_completa(fecha_nacimiento_raw: Any) -> tuple[Optional[date], Optional[Dict[str, Any]]]:
        """Procesa y convierte la fecha de nacimiento a objeto date."""
        if isinstance(fecha_nacimiento_raw, str):
            try:
                fecha_nacimiento_date = datetime.fromisoformat(fecha_nacimiento_raw).date()
                return fecha_nacimiento_date, None
            except ValueError:
                try:
                    anio = int(fecha_nacimiento_raw)
                    fecha_nacimiento_date = date(anio, 1, 1)
                    return fecha_nacimiento_date, None
                except ValueError:
                    return None, {
                        'success': False,
                        'message': f'Formato de fecha de nacimiento inválido: {fecha_nacimiento_raw}',
                        'status_code': 400
                    }
        elif isinstance(fecha_nacimiento_raw, int):
            fecha_nacimiento_date = date(fecha_nacimiento_raw, 1, 1)
            return fecha_nacimiento_date, None
        elif isinstance(fecha_nacimiento_raw, date):
            return fecha_nacimiento_raw, None
        else:
            return None, {
                'success': False,
                'message': f'Tipo de fecha de nacimiento no válido: {type(fecha_nacimiento_raw)}',
                'status_code': 400
            }

    @staticmethod
    def _crear_informacion_deportiva(datos_deportista: Dict[str, Any], informacion_deportiva: Dict[str, Any]) -> Optional[int]:
        """Crea la información deportiva y retorna su ID."""
        if not informacion_deportiva:
            return None
        
        recomendacion_medica = informacion_deportiva.get('recomendacion_medica', False)
        descripcion_recomendacion = None
        if recomendacion_medica:
            descripcion_recomendacion = sanitize_free_text(
                'descripcion_recomendacion',
                informacion_deportiva.get('descripcion_recomendacion'),
                max_length=500
            )
        
        informacion = InformacionDeportiva(
            id_persona=datos_deportista['id_persona'],
            practica_otro_deporte=informacion_deportiva.get('practica_otro_deporte', False),
            participa_escuela=informacion_deportiva.get('participa_escuela', False),
            recomendacion_medica=recomendacion_medica,
            descripcion_recomendacion=descripcion_recomendacion,
            id_escuela=informacion_deportiva.get('id_escuela'),
            id_deporte=informacion_deportiva.get('id_deporte'),
            id_institucion_registro=informacion_deportiva.get('id_institucion_registro')
        )
        
        db.session.add(informacion)
        db.session.flush()
        logger = RegistroDeportistaService._obtener_logger()
        # Removed logger.info for performance
        # logger.info(f'Información deportiva creada: ID {informacion.id_informacion_deportiva}')
        return informacion.id_informacion_deportiva

    @staticmethod
    def _asociar_diagnosticos(deportista: Deportista, diagnosticos: List[int]) -> None:
        """Asocia diagnósticos al deportista."""
        if not diagnosticos or len(diagnosticos) == 0:
            return
        
        for id_diagnostico in diagnosticos:
            diagnostico_deportista = DiagnosticoDeportista(
                id_deportista=deportista.id_deportista,
                id_diagnostico=id_diagnostico,
                fecha=date.today()
            )
            db.session.add(diagnostico_deportista)
        
        logger = RegistroDeportistaService._obtener_logger()
        # Removed logger.info for performance
        # logger.info(f'{len(diagnosticos)} diagnóstico(s) asociados al deportista {deportista.id_deportista}')

    @staticmethod
    def _asociar_acudientes(deportista: Deportista, acudientes_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Asocia acudientes al deportista con validaciones."""
        if not acudientes_data or len(acudientes_data) == 0:
            return None
        
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
        
        logger = RegistroDeportistaService._obtener_logger()
        for acudiente_data in acudientes_data:
            id_acudiente = acudiente_data.get('id_acudiente')
            id_parentesco = acudiente_data.get('id_parentesco')
            es_responsable = acudiente_data.get('es_responsable', False)
            
            acudiente = Acudiente.query.filter_by(id_acudiente=id_acudiente).first()
            if not acudiente:
                continue
            
            parentesco = Parentesco.query.filter_by(id_parentesco=id_parentesco).first()
            if not parentesco:
                continue
            
            relacion_existente = DeportistaAcudiente.query.filter_by(
                id_deportista=deportista.id_deportista,
                id_acudiente=id_acudiente
            ).first()
            
            if relacion_existente:
                logger.warning(f'Ya existe relación entre deportista {deportista.id_deportista} y acudiente {id_acudiente}')
                continue
            
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
        
        # Removed logger.info for performance
        # logger.info(f'{len(acudientes_data)} acudiente(s) asociados al deportista {deportista.id_deportista}')
        return None

    @staticmethod
    def _asignar_rol_deportista(id_persona: int) -> None:
        """Asigna el rol de deportista al usuario si existe."""
        usuario = Usuario.query.filter_by(id_persona=id_persona).first()
        if not usuario:
            return
        
        rol_deportista = Rol.query.filter_by(nombre_rol='Deportista').first()
        if not rol_deportista:
            return
        
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
            logger = RegistroDeportistaService._obtener_logger()
            # Removed logger.info for performance
        # logger.info(f'Rol de Deportista asignado al usuario ID: {usuario.id_usuario}')

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
            datos_deportista, informacion_deportiva = RegistroDeportistaService._validar_estructura_datos(datos)
            if not datos_deportista:
                return {
                    'success': False,
                    'message': 'Los datos del deportista son requeridos',
                    'status_code': 400
                }
            
            datos['informacion_deportiva'] = informacion_deportiva
            
            error_response = RegistroDeportistaService._validar_campos_requeridos(datos_deportista, informacion_deportiva)
            if error_response:
                return error_response
            
            es_valido, mensaje_error = RegistroDeportistaService._validar_ids(datos)
            if not es_valido:
                return {
                    'success': False,
                    'message': mensaje_error,
                    'status_code': 400
                }
            
            error_response = RegistroDeportistaService._validar_persona_y_deportista_existente(datos_deportista['id_persona'])
            if error_response:
                return error_response
            
            persona = Persona.query.filter_by(id_persona=datos_deportista['id_persona']).first()
            
            tipo_enfermedad_id = datos.get('tipo_enfermedad')
            diagnosticos = datos.get('diagnostico', [])
            error_response = RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos(tipo_enfermedad_id, diagnosticos)
            if error_response:
                return error_response
            
            fecha_nacimiento_date, error_response = RegistroDeportistaService._procesar_fecha_nacimiento_completa(
                datos_deportista['fecha_nacimiento']
            )
            if error_response:
                return error_response
            
            id_categoria = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento(fecha_nacimiento_date)
            if not id_categoria:
                return {
                    'success': False,
                    'message': f'No se pudo determinar la categoría para la fecha de nacimiento {fecha_nacimiento_date}',
                    'status_code': 400
                }
            
            id_informacion_deportiva = RegistroDeportistaService._crear_informacion_deportiva(
                datos_deportista, informacion_deportiva
            )
            
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
            
            RegistroDeportistaService._asociar_diagnosticos(deportista, diagnosticos)
            
            acudientes_data = datos.get('acudientes', [])
            error_response = RegistroDeportistaService._asociar_acudientes(deportista, acudientes_data)
            if error_response:
                return error_response
            
            RegistroDeportistaService._asignar_rol_deportista(datos_deportista['id_persona'])
            
            db.session.commit()
            
            deportista_completo = Deportista.query.filter_by(id_deportista=deportista.id_deportista).first()
            categoria_info = deportista_completo.categoria
            
            # Removed logger.info for performance
        # logger.info(f'Deportista registrado exitosamente: ID {deportista.id_deportista}')
            
            return {
                'success': True,
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
                'success': False,
                'message': 'Error de duplicación de datos',
                'status_code': 409
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error inesperado al registrar deportista: {str(e)}')
            return {
                'success': False,
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
    def _construir_datos_persona(deportista: Deportista) -> Dict[str, Any]:
        """Construye los datos de persona del deportista."""
        persona_data = {}
        if not deportista.persona:
            return persona_data
        
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
        
        if deportista.fecha_nacimiento:
            persona_data['fecha_nacimiento'], persona_data['edad_aproximada'] = (
                RegistroDeportistaService._procesar_fecha_nacimiento(deportista.fecha_nacimiento)
            )
        
        persona_data['id_tipo_sanguineo'] = deportista.id_tipo_sanguineo
        persona_data['id_ciudad_recidencia'] = deportista.id_ciudad_recidencia
        persona_data['id_eps'] = deportista.id_eps
        
        return persona_data

    @staticmethod
    def _construir_info_deportiva(deportista: Deportista) -> Dict[str, Any]:
        """Construye la información deportiva del deportista."""
        if deportista.informacion_deportiva:
            info = deportista.informacion_deportiva
            return {
                'id_informacion_deportiva': info.id_informacion_deportiva,
                'practica_otro_deporte': info.practica_otro_deporte,
                'participa_escuela': info.participa_escuela,
                'recomendacion_medica': info.recomendacion_medica,
                'descripcion_recomendacion': info.descripcion_recomendacion,
                'id_deporte': info.id_deporte,
                'id_escuela': info.id_escuela,
                'id_institucion_registro': info.id_institucion_registro,
                'id_categoria': deportista.id_categoria
            }
        
        return {
            'practica_otro_deporte': False,
            'participa_escuela': False,
            'recomendacion_medica': False,
            'descripcion_recomendacion': None,
            'id_deporte': None,
            'id_escuela': None,
            'id_institucion_registro': None,
            'id_categoria': deportista.id_categoria if deportista.id_categoria else None
        }

    @staticmethod
    def _construir_datos_salud(id_deportista: int) -> Dict[str, Any]:
        """Construye los datos de salud del deportista."""
        salud_data = {}
        diagnosticos_deportista = DiagnosticoDeportista.query.filter_by(id_deportista=id_deportista).all()
        
        if not diagnosticos_deportista:
            return salud_data
        
        diagnosticos_ids = []
        tipos_enfermedad_ids = set()
        
        for diagnostico_deportista in diagnosticos_deportista:
            if not diagnostico_deportista.diagnostico:
                continue
            
            diagnosticos_ids.append({
                'id_diagnostico': diagnostico_deportista.id_diagnostico,
                'id_tipo_enfermedad': diagnostico_deportista.diagnostico.id_tipo_enfermedad if diagnostico_deportista.diagnostico.tipo_enfermedad else None,
                'fecha': diagnostico_deportista.fecha.isoformat() if diagnostico_deportista.fecha else None
            })
            
            if diagnostico_deportista.diagnostico.tipo_enfermedad:
                tipos_enfermedad_ids.add(diagnostico_deportista.diagnostico.tipo_enfermedad.id_tipo_enfermedad)
        
        if diagnosticos_ids:
            salud_data['diagnosticos'] = diagnosticos_ids
            salud_data['cantidad_diagnosticos'] = len(diagnosticos_ids)
            salud_data['tipos_enfermedad_ids'] = list(tipos_enfermedad_ids)
        
        return salud_data

    @staticmethod
    def _construir_datos_adicionales(deportista: Deportista) -> Dict[str, Any]:
        """Construye los datos adicionales del deportista."""
        datos_adicionales = {}
        
        if deportista.peso:
            datos_adicionales['peso'] = deportista.peso
        if deportista.altura:
            datos_adicionales['altura'] = deportista.altura
        if deportista.imc:
            datos_adicionales['imc'] = deportista.imc
        if deportista.fecha_ingreso:
            datos_adicionales['fecha_ingreso'] = deportista.fecha_ingreso.isoformat()
        
        mensualidad = Mensualidad.query.filter_by(
            id_persona=deportista.id_persona,
            activo=True
        ).order_by(Mensualidad.created_at.desc()).first()
        
        if mensualidad:
            datos_adicionales['mensualidad'] = {
                'monto': float(mensualidad.monto_pago) if mensualidad.monto_pago else None,
                'fecha_pago': mensualidad.fecha_pago.isoformat() if mensualidad.fecha_pago else None,
                'estado': mensualidad.estado
            }
        
        return datos_adicionales

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
            
            # Buscar el deportista con todas sus relaciones - use eager loading to prevent N+1
            from sqlalchemy.orm import joinedload
            deportista = Deportista.query.options(
                joinedload(Deportista.categoria)
            ).filter_by(id_deportista=id_deportista).first()
            
            if not deportista:
                return {
                    'status': 'error',
                    'message': 'El deportista con el ID especificado no existe',
                    'status_code': 404
                }
            
            persona_data = RegistroDeportistaService._construir_datos_persona(deportista)
            info_deportiva = RegistroDeportistaService._construir_info_deportiva(deportista)
            salud_data = RegistroDeportistaService._construir_datos_salud(id_deportista)
            datos_deportista_adicionales = RegistroDeportistaService._construir_datos_adicionales(deportista)
            
            # Removed logger.info for performance
        # logger.info(f'Información completa obtenida para deportista ID {id_deportista}')
            
            return {
                'success': True,
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

