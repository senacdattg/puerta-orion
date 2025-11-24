# ¿Las funciones de este archivo se usan?
#
# Respuesta técnica:
#
# Este archivo define el servicio `DeportistaService` que incluye las operaciones CRUD principales para el modelo "Deportista".
# Sin embargo, únicamente con este código no es posible saber si las funciones:
#   - crear_deportista
#   - obtener_deportista
#   - listar_deportistas
#   - actualizar_deportista
# se usan desde algún controlador, blueprint, endpoint Flask, o desde otras partes del backend.
#
# ¿Cómo verificar si se usan?
# 1. **Buscar imports y llamadas en el backend**: Revisa los archivos ubicados en `/backend/src/controllers/`, `/backend/src/routes/` o `/backend/src/api/` para ver si usan `DeportistaService`.
# 2. **Buscar en endpoints Flask (API)**: Busca si en alguna ruta (por ejemplo, `@app.route("/deportistas", ...)`) se invoca algún método de este servicio.
# 3. **Buscar en tests**: Verifica si hay tests automáticos que llamen a estos métodos.
#
# **Evidencia indirecta disponible:**
# - En la información proporcionada aquí, no están visibles los controladores ni endpoints que integren este servicio.
# - El archivo está bien estructurado, lo que sugiere que está pensado para ser usado en una arquitectura de backend moderna con separación de servicios, pero no podemos confirmar su uso real solo con este archivo.
#
# **Conclusión**:
# - Para saber si *de hecho* se usan, busca referencias a estos métodos (`DeportistaService.crear_deportista`, etc) en el código del proyecto backend fuera de este archivo.
# - Si no se encuentra ninguna referencia en views/controladores/rutas/tests, entonces actualmente NO se estarían usando explícitamente.
# - Si existen endpoints para crear, consultar, listar o actualizar deportistas, es altamente probable que estos métodos sean llamados desde allí.

# (El código original de las funciones se mantiene más abajo.)

"""
Servicio para gestión de deportistas.

Responsabilidad:
- Gestionar operaciones CRUD de deportistas
- Validar datos de deportistas
- Coordinar transacciones de base de datos
- Mantener consistencia de datos

Este módulo sigue los principios SRP, KISS, DRY, POO y SOLID.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ..models.base import db
from ..models.deportistas.deportista import Deportista
from ..models.deportistas.informacion_deportiva import InformacionDeportiva
from ..models.personas.persona import Persona
from ..models.usuarios.usuario import Usuario
from ..utils.logger import obtener_registrador
from ..utils.validations import sanitize_free_text


# Constants for error messages
ERROR_DUPLICACION_DATOS = 'Error de duplicación de datos'
ERROR_DEPORTISTA_NO_ENCONTRADO = 'Deportista no encontrado'


class DeportistaService:
    """Servicio para gestión de deportistas con operaciones CRUD."""

    @staticmethod
    def _obtener_logger():
        """Obtiene el logger configurado."""
        return obtener_registrador('aplicacion')

    @staticmethod
    def _validar_campos_requeridos(datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Valida que los campos requeridos estén presentes."""
        campos_requeridos = ['id_persona', 'id_categoria']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or datos[campo] is None]
        
        if campos_faltantes:
            return {
                'success': False,
                'message': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_persona_existente(id_persona: int) -> Optional[Dict[str, Any]]:
        """Valida que la persona existe."""
        persona = Persona.query.filter_by(id_persona=id_persona).first()
        if not persona:
            return {
                'success': False,
                'message': 'La persona especificada no existe',
                'status_code': 404
            }
        return None

    @staticmethod
    def _validar_deportista_no_existente(id_persona: int) -> Optional[Dict[str, Any]]:
        """Valida que no existe ya un deportista para esa persona."""
        deportista_existente = Deportista.query.filter_by(id_persona=id_persona).first()
        if deportista_existente:
            return {
                'success': False,
                'message': 'Ya existe un deportista para esta persona',
                'status_code': 409
            }
        return None

    @staticmethod
    def _procesar_fecha_nacimiento(fecha_nacimiento_raw: Any) -> Tuple[Optional[date], Optional[Dict[str, Any]]]:
        """Procesa y convierte la fecha de nacimiento a date."""
        if not fecha_nacimiento_raw:
            return None, None
        
        if isinstance(fecha_nacimiento_raw, date):
            return fecha_nacimiento_raw, None
        
        if isinstance(fecha_nacimiento_raw, int):
            return date(fecha_nacimiento_raw, 1, 1), None
        
        if isinstance(fecha_nacimiento_raw, str):
            try:
                return datetime.fromisoformat(fecha_nacimiento_raw).date(), None
            except ValueError:
                try:
                    anio = int(fecha_nacimiento_raw)
                    return date(anio, 1, 1), None
                except ValueError:
                    error = {
                        'success': False,
                        'message': f'Formato de fecha de nacimiento inválido: {fecha_nacimiento_raw}',
                        'status_code': 400
                    }
                    return None, error
        
        return None, None

    @staticmethod
    def crear_deportista(datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo deportista.
        
        La fecha de ingreso se asigna automáticamente a la fecha actual.

        Args:
            datos: Diccionario con los datos del deportista
                - id_persona (int): Obligatorio. ID de la persona
                - id_categoria (int): Obligatorio. ID de la categoría deportiva
                - fecha_ingreso (date, opcional): Si no se proporciona, usa la fecha actual
                - peso (float, opcional): Peso en kilogramos
                - altura (float, opcional): Altura en metros
                - fecha_nacimiento (int, opcional): Año de nacimiento
                - id_tipo_sanguineo (int, opcional): ID del grupo sanguíneo
                - id_ciudad_recidencia (int, opcional): ID de la ciudad de residencia
                - id_informacion_deportiva (int, opcional): ID de información deportiva
                - id_eps (int, opcional): ID de la EPS

        Returns:
            Dict: Respuesta con el resultado de la operación
        """
        logger = DeportistaService._obtener_logger()
        
        try:
            error_validacion = DeportistaService._validar_campos_requeridos(datos)
            if error_validacion:
                return error_validacion

            error_persona = DeportistaService._validar_persona_existente(datos['id_persona'])
            if error_persona:
                return error_persona

            error_deportista = DeportistaService._validar_deportista_no_existente(datos['id_persona'])
            if error_deportista:
                return error_deportista

            fecha_nacimiento_date, error_fecha = DeportistaService._procesar_fecha_nacimiento(
                datos.get('fecha_nacimiento')
            )
            if error_fecha:
                return error_fecha

            deportista = Deportista(
                id_persona=datos['id_persona'],
                id_categoria=datos['id_categoria'],
                fecha_ingreso=datos.get('fecha_ingreso', date.today()),
                peso=datos.get('peso'),
                altura=datos.get('altura'),
                fecha_nacimiento=fecha_nacimiento_date,
                id_tipo_sanguineo=datos.get('id_tipo_sanguineo'),
                id_ciudad_recidencia=datos.get('id_ciudad_recidencia'),
                id_informacion_deportiva=datos.get('id_informacion_deportiva'),
                id_eps=datos.get('id_eps')
            )

            db.session.add(deportista)
            db.session.commit()

            logger.info(f'Deportista creado exitosamente: ID {deportista.id_deportista}')

            return {
                'success': True,
                'message': 'Deportista creado exitosamente',
                'data': deportista.to_dict(),
                'status_code': 201
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Error de integridad al crear deportista: {str(e)}')
            return {
                'success': False,
                'message': ERROR_DUPLICACION_DATOS,
                'status_code': 409
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error inesperado al crear deportista: {str(e)}')
            return {
                'success': False,
                'message': f'Error al crear deportista: {str(e)}',
                'status_code': 500
            }

    @staticmethod
    def obtener_deportista(id_deportista: int) -> Dict[str, Any]:
        """
        Obtiene un deportista por su ID.

        Args:
            id_deportista: ID del deportista

        Returns:
            Dict: Respuesta con los datos del deportista
        """
        logger = DeportistaService._obtener_logger()

        try:
            deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()

            if not deportista:
                return {
                    'success': False,
                    'message': ERROR_DEPORTISTA_NO_ENCONTRADO,
                    'status_code': 404
                }

            # Serializar con relaciones
            datos = deportista.to_dict()
            
            # Agregar datos de la persona si existe la relación
            if deportista.persona:
                datos['persona'] = deportista.persona.to_dict()

            return {
                'success': True,
                'data': datos,
                'status_code': 200
            }

        except Exception as e:
            logger.error(f'Error al obtener deportista {id_deportista}: {str(e)}')
            return {
                'success': False,
                'message': 'Error interno del servidor',
                'status_code': 500
            }

    @staticmethod
    def listar_deportistas(page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Lista deportistas con paginación.

        Args:
            page: Número de página
            per_page: Cantidad de elementos por página

        Returns:
            Dict: Respuesta con la lista de deportistas
        """
        logger = DeportistaService._obtener_logger()

        try:
            paginacion = Deportista.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            # Enriquecer datos con información de persona y categoría
            deportistas = []
            for deportista in paginacion.items:
                datos = deportista.to_dict()
                
                # Agregar datos de la persona si existe la relación
                if deportista.persona:
                    datos['persona'] = deportista.persona.to_dict()
                    # Agregar nombre completo para facilitar el uso en frontend
                    datos['nombre'] = deportista.persona.nombre_completo
                    datos['nombre1'] = deportista.persona.primer_nombre
                    datos['nombre2'] = deportista.persona.segundo_nombre
                    datos['apellido1'] = deportista.persona.primer_apellido
                    datos['apellido2'] = deportista.persona.segundo_apellido
                    datos['correo'] = deportista.persona.correo_electronico
                    datos['telefono'] = deportista.persona.telefono
                    datos['direccion'] = deportista.persona.direccion
                    datos['documento'] = deportista.persona.documento
                    
                    # Determinar el estado: priorizar el estado del usuario si existe
                    # Si la persona tiene un usuario asociado, usar el estado del usuario
                    # Si no tiene usuario, usar el estado de la persona
                    estado_final = deportista.persona.estado
                    
                    # Buscar si existe un usuario asociado a esta persona
                    usuario = Usuario.query.filter_by(id_persona=deportista.persona.id_persona).first()
                    if usuario:
                        # Si existe usuario, usar su estado (tiene prioridad)
                        estado_final = usuario.estado
                        # Agregar id_usuario para que el frontend pueda cambiar el estado
                        datos['id_usuario'] = usuario.id_usuario
                    else:
                        datos['id_usuario'] = None
                    
                    datos['estado'] = 'activo' if estado_final else 'inactivo'
                
                # Agregar datos de la categoría si existe la relación
                if deportista.categoria:
                    datos['categoria'] = deportista.categoria.nombre_categoria.lower()
                    datos['categoria_info'] = {
                        'id_categoria': deportista.categoria.id_categoria,
                        'nombre_categoria': deportista.categoria.nombre_categoria,
                        'edad_minima': deportista.categoria.edad_minima,
                        'edad_maxima': deportista.categoria.edad_maxima
                    }
                
                deportistas.append(datos)

            return {
                'success': True,
                'data': deportistas,
                'pagination': {
                    'page': paginacion.page,
                    'pages': paginacion.pages,
                    'per_page': paginacion.per_page,
                    'total': paginacion.total
                },
                'status_code': 200
            }

        except Exception as e:
            logger.error(f'Error al listar deportistas: {str(e)}')
            return {
                'success': False,
                'message': 'Error interno del servidor',
                'status_code': 500
            }

    @staticmethod
    def actualizar_deportista(id_deportista: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza un deportista existente.

        Args:
            id_deportista: ID del deportista
            datos: Diccionario con los datos a actualizar

        Returns:
            Dict: Respuesta con el resultado de la operación
        """
        logger = DeportistaService._obtener_logger()

        try:
            deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()

            if not deportista:
                return {
                    'success': False,
                    'message': ERROR_DEPORTISTA_NO_ENCONTRADO,
                    'status_code': 404
                }

            # Actualizar campos permitidos
            campos_permitidos = [
                'peso', 'altura', 'fecha_ingreso', 'fecha_nacimiento',
                'id_tipo_sanguineo', 'id_ciudad_recidencia',
                'id_informacion_deportiva', 'id_eps', 'id_categoria'
            ]

            for campo in campos_permitidos:
                if campo in datos:
                    setattr(deportista, campo, datos[campo])

            db.session.commit()

            logger.info(f'Deportista actualizado exitosamente: ID {id_deportista}')

            return {
                'success': True,
                'message': 'Deportista actualizado exitosamente',
                'data': deportista.to_dict(),
                'status_code': 200
            }

        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Error de integridad al actualizar deportista: {str(e)}')
            return {
                'success': False,
                'message': ERROR_DUPLICACION_DATOS,
                'status_code': 409
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error inesperado al actualizar deportista: {str(e)}')
            return {
                'success': False,
                'message': f'Error al actualizar deportista: {str(e)}',
                'status_code': 500
            }

    @staticmethod
    def _validar_datos_entrada(datos_deportista: Optional[Dict[str, Any]], datos_informacion_deportiva: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Valida que se proporcione al menos una sección de datos."""
        if not datos_deportista and not datos_informacion_deportiva:
            return {
                'success': False,
                'message': 'Debe proporcionar al menos datos_deportista o datos_informacion_deportiva',
                'status_code': 400
            }
        return None

    @staticmethod
    def _extraer_roles_usuario(usuario_actual: Dict[str, Any]) -> List[str]:
        """Extrae los nombres de roles del usuario."""
        roles_usuario = []
        if 'roles' in usuario_actual and usuario_actual['roles']:
            for rol in usuario_actual['roles']:
                if isinstance(rol, dict):
                    nombre_rol = rol.get('nombre_rol', '') or rol.get('nombre', '') or str(rol)
                    if nombre_rol:
                        roles_usuario.append(nombre_rol)
                elif hasattr(rol, 'nombre_rol'):
                    roles_usuario.append(rol.nombre_rol)
                elif isinstance(rol, str):
                    roles_usuario.append(rol)
        return roles_usuario

    @staticmethod
    def _validar_permisos_campos_restrictos(
        datos_deportista: Dict[str, Any],
        usuario_actual: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Valida permisos para actualizar campos restrictos (peso, altura)."""
        campos_restrictos = ['peso', 'altura']
        campos_intentados = [campo for campo in campos_restrictos if campo in datos_deportista]
        
        if not campos_intentados or not usuario_actual:
            return None
        
        roles_usuario = DeportistaService._extraer_roles_usuario(usuario_actual)
        roles_permitidos = ['Acudiente', 'Entrenador', 'Administrador', 'SuperAdmin']
        tiene_permiso = any(rol in roles_permitidos for rol in roles_usuario)
        
        if not tiene_permiso:
            return {
                'success': False,
                'message': f'No tiene permisos para actualizar los campos: {", ".join(campos_intentados)}. Solo Acudiente, Entrenador y Administrador pueden modificar peso y altura.',
                'status_code': 403
            }
        return None

    @staticmethod
    def _validar_id_categoria(id_categoria: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que la categoría existe."""
        if id_categoria is None:
            return None
        from ..models.categorias.categoria import Categoria
        categoria = Categoria.query.filter_by(id_categoria=id_categoria).first()
        if not categoria:
            return {
                'success': False,
                'message': 'La categoría especificada no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_id_tipo_sanguineo(id_tipo_sanguineo: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que el tipo sanguíneo existe."""
        if id_tipo_sanguineo is None:
            return None
        from ..models.categorias.grupo_sanguineo import GrupoSanguineo
        tipo_sangre = GrupoSanguineo.query.filter_by(id_tipo_sangre=id_tipo_sanguineo).first()
        if not tipo_sangre:
            return {
                'success': False,
                'message': 'El tipo sanguíneo especificado no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_id_ciudad_residencia(id_ciudad: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que la ciudad de residencia existe."""
        if id_ciudad is None:
            return None
        from ..models.categorias.ciudad_residencia import CiudadResidencia
        ciudad = CiudadResidencia.query.filter_by(id_ciudad=id_ciudad).first()
        if not ciudad:
            return {
                'success': False,
                'message': 'La ciudad de residencia especificada no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_id_eps(id_eps: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que la EPS existe."""
        if id_eps is None:
            return None
        from ..models.catalogos.eps import EPS
        eps = EPS.query.filter_by(id_eps=id_eps).first()
        if not eps:
            return {
                'success': False,
                'message': 'La EPS especificada no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_ids_deportista(datos_deportista: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Valida todos los IDs relacionados del deportista."""
        error = DeportistaService._validar_id_categoria(datos_deportista.get('id_categoria'))
        if error:
            return error
        
        error = DeportistaService._validar_id_tipo_sanguineo(datos_deportista.get('id_tipo_sanguineo'))
        if error:
            return error
        
        error = DeportistaService._validar_id_ciudad_residencia(datos_deportista.get('id_ciudad_recidencia'))
        if error:
            return error
        
        error = DeportistaService._validar_id_eps(datos_deportista.get('id_eps'))
        if error:
            return error
        
        return None

    @staticmethod
    def _convertir_fecha_string(valor: str, nombre_campo: str) -> Tuple[Optional[date], Optional[Dict[str, Any]]]:
        """Convierte una fecha desde string a date."""
        try:
            return datetime.fromisoformat(valor).date(), None
        except ValueError:
            error = {
                'success': False,
                'message': f'Formato de {nombre_campo} inválido. Use YYYY-MM-DD',
                'status_code': 400
            }
            return None, error

    @staticmethod
    def _validar_edad_minima(fecha_nacimiento: date) -> Optional[Dict[str, Any]]:
        """Valida que el deportista tenga mínimo 5 años de edad."""
        hoy = date.today()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        
        if edad < 5:
            return {
                'success': False,
                'message': 'El deportista debe tener mínimo 5 años de edad. La edad mínima de la categoría Pre-infantil es 5 años.',
                'status_code': 400
            }
        return None

    @staticmethod
    def _procesar_campo_fecha(campo: str, valor: Any) -> Tuple[Optional[date], Optional[Dict[str, Any]]]:
        """Procesa y valida un campo de fecha."""
        if campo == 'fecha_nacimiento' and isinstance(valor, str):
            fecha_date, error = DeportistaService._convertir_fecha_string(valor, 'fecha_nacimiento')
            if error:
                return None, error
            error_edad = DeportistaService._validar_edad_minima(fecha_date)
            if error_edad:
                return None, error_edad
            return fecha_date, None
        
        if campo == 'fecha_ingreso' and isinstance(valor, str):
            return DeportistaService._convertir_fecha_string(valor, 'fecha_ingreso')
        
        return valor, None

    @staticmethod
    def _actualizar_campos_deportista(deportista: Deportista, datos_deportista: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Actualiza los campos del deportista."""
        campos_deportista_actualizables = [
            'peso', 'altura', 'fecha_ingreso', 'fecha_nacimiento',
            'id_tipo_sanguineo', 'id_ciudad_recidencia',
            'id_informacion_deportiva', 'id_eps', 'id_categoria'
        ]
        
        for campo in campos_deportista_actualizables:
            if campo in datos_deportista:
                valor = datos_deportista[campo]
                
                if campo in ['fecha_nacimiento', 'fecha_ingreso']:
                    valor_procesado, error = DeportistaService._procesar_campo_fecha(campo, valor)
                    if error:
                        return error
                    valor = valor_procesado
                
                setattr(deportista, campo, valor)
        
        return None

    @staticmethod
    def _obtener_o_crear_info_deportiva(deportista: Deportista, datos_informacion_deportiva: Dict[str, Any]) -> InformacionDeportiva:
        """Obtiene o crea información deportiva."""
        if deportista.id_informacion_deportiva:
            info_deportiva = InformacionDeportiva.query.filter_by(
                id_informacion_deportiva=deportista.id_informacion_deportiva
            ).first()
            if info_deportiva:
                return info_deportiva
        
        recomendacion_medica = datos_informacion_deportiva.get('recomendacion_medica', False)
        descripcion_recomendacion = None
        if recomendacion_medica:
            descripcion_recomendacion = sanitize_free_text(
                'descripcion_recomendacion',
                datos_informacion_deportiva.get('descripcion_recomendacion'),
                max_length=500
            )

        info_deportiva = InformacionDeportiva(
            id_persona=deportista.id_persona,
            practica_otro_deporte=datos_informacion_deportiva.get('practica_otro_deporte', False),
            participa_escuela=datos_informacion_deportiva.get('participa_escuela', False),
            recomendacion_medica=recomendacion_medica,
            descripcion_recomendacion=descripcion_recomendacion,
            id_escuela=datos_informacion_deportiva.get('id_escuela'),
            id_deporte=datos_informacion_deportiva.get('id_deporte'),
            id_institucion_registro=datos_informacion_deportiva.get('id_institucion_registro')
        )
        db.session.add(info_deportiva)
        db.session.flush()
        deportista.id_informacion_deportiva = info_deportiva.id_informacion_deportiva
        return info_deportiva

    @staticmethod
    def _validar_id_escuela(id_escuela: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que la escuela existe."""
        if id_escuela is None:
            return None
        from ..models.categorias.escuela import Escuela
        escuela = Escuela.query.filter_by(id_escuela=id_escuela).first()
        if not escuela:
            return {
                'success': False,
                'message': 'La escuela especificada no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_id_deporte(id_deporte: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que el deporte existe."""
        if id_deporte is None:
            return None
        from ..models.categorias.deporte import Deporte
        deporte = Deporte.query.filter_by(id_deporte=id_deporte).first()
        if not deporte:
            return {
                'success': False,
                'message': 'El deporte especificado no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_id_institucion_registro(id_institucion: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que la institución de registro existe."""
        if id_institucion is None:
            return None
        from ..models.categorias.institucion_registro import InstitucionRegistro
        institucion = InstitucionRegistro.query.filter_by(id_institucion=id_institucion).first()
        if not institucion:
            return {
                'success': False,
                'message': 'La institución de registro especificada no existe',
                'status_code': 400
            }
        return None

    @staticmethod
    def _validar_ids_info_deportiva(datos_informacion_deportiva: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Valida todos los IDs relacionados de información deportiva."""
        error = DeportistaService._validar_id_escuela(datos_informacion_deportiva.get('id_escuela'))
        if error:
            return error
        
        error = DeportistaService._validar_id_deporte(datos_informacion_deportiva.get('id_deporte'))
        if error:
            return error
        
        error = DeportistaService._validar_id_institucion_registro(datos_informacion_deportiva.get('id_institucion_registro'))
        if error:
            return error
        
        return None

    @staticmethod
    def _actualizar_info_deportiva(info_deportiva: InformacionDeportiva, datos_informacion_deportiva: Dict[str, Any]) -> None:
        """Actualiza los campos de información deportiva."""
        campos_info_deportiva = [
            'practica_otro_deporte', 'participa_escuela', 'recomendacion_medica',
            'descripcion_recomendacion', 'id_escuela', 'id_deporte', 'id_institucion_registro'
        ]
        
        for campo in campos_info_deportiva:
            if campo in datos_informacion_deportiva:
                valor = datos_informacion_deportiva[campo]

                if campo == 'descripcion_recomendacion':
                    recom_med = datos_informacion_deportiva.get(
                        'recomendacion_medica', info_deportiva.recomendacion_medica
                    )
                    if not recom_med:
                        valor = None
                    elif valor:
                        valor = sanitize_free_text('descripcion_recomendacion', valor, max_length=500)

                setattr(info_deportiva, campo, valor)

        if 'recomendacion_medica' in datos_informacion_deportiva and not datos_informacion_deportiva['recomendacion_medica']:
            info_deportiva.descripcion_recomendacion = None

    @staticmethod
    def _validar_diagnosticos(diagnosticos: List[int], tipo_enfermedad: Optional[int]) -> Optional[Dict[str, Any]]:
        """Valida que los diagnósticos existen y corresponden al tipo de enfermedad."""
        if not tipo_enfermedad:
            return None
        
        from ..models.salud.diagnostico import Diagnostico
        for id_diagnostico in diagnosticos:
            diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
            if not diagnostico:
                return {
                    'success': False,
                    'message': f'El diagnóstico con ID {id_diagnostico} no existe',
                    'status_code': 400
                }
            if diagnostico.id_tipo_enfermedad != tipo_enfermedad:
                return {
                    'success': False,
                    'message': f'El diagnóstico con ID {id_diagnostico} no corresponde al tipo de enfermedad seleccionado',
                    'status_code': 400
                }
        return None

    @staticmethod
    def _actualizar_diagnosticos(id_deportista: int, diagnosticos: Optional[List[int]], tipo_enfermedad: Optional[int], logger) -> Optional[Dict[str, Any]]:
        """Actualiza los diagnósticos del deportista."""
        if tipo_enfermedad is None and diagnosticos is None:
            return None
        
        from ..models.salud.diagnostico_deportista import DiagnosticoDeportista
        from ..models.salud.diagnostico import Diagnostico
        from datetime import date
        
        DiagnosticoDeportista.query.filter_by(id_deportista=id_deportista).delete()
        
        if diagnosticos and len(diagnosticos) > 0:
            error = DeportistaService._validar_diagnosticos(diagnosticos, tipo_enfermedad)
            if error:
                return error
            
            for id_diagnostico in diagnosticos:
                diagnostico_deportista = DiagnosticoDeportista(
                    id_deportista=id_deportista,
                    id_diagnostico=id_diagnostico,
                    fecha=date.today()
                )
                db.session.add(diagnostico_deportista)
            logger.info(f'{len(diagnosticos)} diagnóstico(s) actualizados para el deportista {id_deportista}')
        
        return None

    @staticmethod
    def _construir_respuesta_actualizacion(deportista: Deportista) -> Dict[str, Any]:
        """Construye la respuesta con los datos actualizados del deportista."""
        respuesta = deportista.to_dict()
        if deportista.persona:
            respuesta['persona'] = deportista.persona.to_dict()
        if deportista.informacion_deportiva:
            respuesta['informacion_deportiva'] = deportista.informacion_deportiva.to_dict()
        return respuesta

    @staticmethod
    def _procesar_actualizacion_deportista(
        deportista: Deportista,
        datos_deportista: Optional[Dict[str, Any]],
        usuario_actual: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Procesa la actualización de campos del deportista."""
        if not datos_deportista:
            return None
        
        error_permisos = DeportistaService._validar_permisos_campos_restrictos(datos_deportista, usuario_actual)
        if error_permisos:
            return error_permisos
        
        error_ids = DeportistaService._validar_ids_deportista(datos_deportista)
        if error_ids:
            return error_ids
        
        return DeportistaService._actualizar_campos_deportista(deportista, datos_deportista)

    @staticmethod
    def _procesar_actualizacion_info_deportiva(
        deportista: Deportista,
        datos_informacion_deportiva: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Procesa la actualización de información deportiva."""
        if not datos_informacion_deportiva:
            return None
        
        info_deportiva = DeportistaService._obtener_o_crear_info_deportiva(deportista, datos_informacion_deportiva)
        
        if deportista.id_informacion_deportiva:
            error_ids = DeportistaService._validar_ids_info_deportiva(datos_informacion_deportiva)
            if error_ids:
                return error_ids
            DeportistaService._actualizar_info_deportiva(info_deportiva, datos_informacion_deportiva)
        
        return None

    @staticmethod
    def _ejecutar_actualizaciones(
        deportista: Deportista,
        datos_deportista: Optional[Dict[str, Any]],
        datos_informacion_deportiva: Optional[Dict[str, Any]],
        usuario_actual: Optional[Dict[str, Any]],
        id_deportista: int,
        diagnosticos: Optional[List[int]],
        tipo_enfermedad: Optional[int],
        logger
    ) -> Optional[Dict[str, Any]]:
        """Ejecuta todas las actualizaciones necesarias."""
        error_deportista = DeportistaService._procesar_actualizacion_deportista(deportista, datos_deportista, usuario_actual)
        if error_deportista:
            return error_deportista
        
        error_info = DeportistaService._procesar_actualizacion_info_deportiva(deportista, datos_informacion_deportiva)
        if error_info:
            return error_info
        
        return DeportistaService._actualizar_diagnosticos(id_deportista, diagnosticos, tipo_enfermedad, logger)

    @staticmethod
    def actualizar_deportista_completo(
        id_deportista: int,
        datos_deportista: Optional[Dict[str, Any]] = None,
        datos_informacion_deportiva: Optional[Dict[str, Any]] = None,
        usuario_actual: Optional[Dict[str, Any]] = None,
        tipo_enfermedad: Optional[int] = None,
        diagnosticos: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Actualiza completamente un deportista con todos sus campos relacionados.
        
        Permite actualizar:
        - Campos del deportista (peso, altura, fecha_ingreso, fecha_nacimiento, etc.)
        - Campos de información deportiva (deporte, escuela, recomendaciones, etc.)
        
        NOTA: Los campos de persona se actualizan a través del endpoint de personas (/personas/<id>).
        
        Args:
            id_deportista: ID del deportista a actualizar
            datos_deportista: Diccionario con campos del deportista a actualizar (opcional)
            datos_informacion_deportiva: Diccionario con campos de información deportiva (opcional)
            usuario_actual: Diccionario con información del usuario autenticado (opcional)
            
        Returns:
            Dict: Respuesta con el resultado de la operación
        """
        logger = DeportistaService._obtener_logger()
        
        try:
            error_validacion = DeportistaService._validar_datos_entrada(datos_deportista, datos_informacion_deportiva)
            if error_validacion:
                return error_validacion
            
            deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
            if not deportista:
                return {
                    'success': False,
                    'message': ERROR_DEPORTISTA_NO_ENCONTRADO,
                    'status_code': 404
                }
            
            error_actualizacion = DeportistaService._ejecutar_actualizaciones(
                deportista, datos_deportista, datos_informacion_deportiva,
                usuario_actual, id_deportista, diagnosticos, tipo_enfermedad, logger
            )
            if error_actualizacion:
                return error_actualizacion
            
            db.session.commit()
            logger.info(f'Deportista actualizado completamente: ID {id_deportista}')
            
            respuesta = DeportistaService._construir_respuesta_actualizacion(deportista)
            return {
                'success': True,
                'message': 'Deportista actualizado exitosamente',
                'data': respuesta,
                'status_code': 200
            }
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'Error de integridad al actualizar deportista completo: {str(e)}')
            return {
                'success': False,
                'message': ERROR_DUPLICACION_DATOS,
                'status_code': 409
            }
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error inesperado al actualizar deportista completo: {str(e)}')
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'message': f'Error al actualizar deportista: {str(e)}',
                'status_code': 500
            }

