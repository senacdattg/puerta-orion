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

from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ..models.base import db
from ..models.deportistas.deportista import Deportista
from ..models.deportistas.informacion_deportiva import InformacionDeportiva
from ..models.personas.persona import Persona
from ..models.usuarios.usuario import Usuario
from ..utils.logger import obtener_registrador


class DeportistaService:
    """Servicio para gestión de deportistas con operaciones CRUD."""

    @staticmethod
    def _obtener_logger():
        """Obtiene el logger configurado."""
        return obtener_registrador('aplicacion')

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
            # Validar datos requeridos
            campos_requeridos = ['id_persona', 'id_categoria']
            campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or datos[campo] is None]
            
            if campos_faltantes:
                return {
                    'success': False,
                    'message': f'Campos requeridos faltantes: {", ".join(campos_faltantes)}',
                    'status_code': 400
                }

            # Verificar que la persona existe
            persona = Persona.query.filter_by(id_persona=datos['id_persona']).first()
            if not persona:
                return {
                    'success': False,
                    'message': 'La persona especificada no existe',
                    'status_code': 404
                }

            # Verificar que no existe ya un deportista para esa persona
            deportista_existente = Deportista.query.filter_by(id_persona=datos['id_persona']).first()
            if deportista_existente:
                return {
                    'success': False,
                    'message': 'Ya existe un deportista para esta persona',
                    'status_code': 409
                }

            # Procesar fecha de nacimiento - convertir string a date si es necesario
            fecha_nacimiento_date = None
            fecha_nacimiento_raw = datos.get('fecha_nacimiento')
            
            if fecha_nacimiento_raw:
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
            
            # Crear instancia de deportista
            # La fecha de ingreso se asigna automáticamente a la fecha actual
            deportista = Deportista(
                id_persona=datos['id_persona'],
                id_categoria=datos['id_categoria'],
                fecha_ingreso=datos.get('fecha_ingreso', date.today()),  # Automática por defecto
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
                'message': 'Error de duplicación de datos',
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
                    'message': 'Deportista no encontrado',
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
                    'message': 'Deportista no encontrado',
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
                'message': 'Error de duplicación de datos',
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
            # Validar que se proporcione al menos una sección de datos
            if not datos_deportista and not datos_informacion_deportiva:
                return {
                    'success': False,
                    'message': 'Debe proporcionar al menos datos_deportista o datos_informacion_deportiva',
                    'status_code': 400
                }
            
            # Obtener el deportista
            deportista = Deportista.query.filter_by(id_deportista=id_deportista).first()
            
            if not deportista:
                return {
                    'success': False,
                    'message': 'Deportista no encontrado',
                    'status_code': 404
                }
            
            # Actualizar campos del deportista
            if datos_deportista:
                # Validar permisos para actualizar peso y altura (solo Entrenador y Administrador)
                campos_restrictos = ['peso', 'altura']
                campos_intentados = [campo for campo in campos_restrictos if campo in datos_deportista]
                
                if campos_intentados and usuario_actual:
                    # Obtener roles del usuario
                    roles_usuario = []
                    if 'roles' in usuario_actual and usuario_actual['roles']:
                        # Extraer nombres de roles desde el diccionario
                        for rol in usuario_actual['roles']:
                            if isinstance(rol, dict):
                                nombre_rol = rol.get('nombre_rol', '') or rol.get('nombre', '') or str(rol)
                                if nombre_rol:
                                    roles_usuario.append(nombre_rol)
                            elif hasattr(rol, 'nombre_rol'):
                                roles_usuario.append(rol.nombre_rol)
                            elif isinstance(rol, str):
                                roles_usuario.append(rol)
                    
                    # Roles permitidos para actualizar peso y altura
                    roles_permitidos = ['Entrenador', 'Administrador', 'SuperAdmin']
                    tiene_permiso = any(rol in roles_permitidos for rol in roles_usuario)
                    
                    if not tiene_permiso:
                        return {
                            'success': False,
                            'message': f'No tiene permisos para actualizar los campos: {", ".join(campos_intentados)}. Solo Entrenador y Administrador pueden modificar peso y altura.',
                            'status_code': 403
                        }
                
                # Validar IDs relacionados si se proporcionan
                from ..models.categorias.grupo_sanguineo import GrupoSanguineo
                from ..models.categorias.ciudad_residencia import CiudadResidencia
                from ..models.catalogos.eps import EPS
                from ..models.categorias.categoria import Categoria
                from ..models.pagos.mensualidad import Mensualidad
                
                # Validar categoría
                if 'id_categoria' in datos_deportista and datos_deportista['id_categoria'] is not None:
                    categoria = Categoria.query.filter_by(id_categoria=datos_deportista['id_categoria']).first()
                    if not categoria:
                        return {
                            'success': False,
                            'message': 'La categoría especificada no existe',
                            'status_code': 400
                        }
                
                # Validar tipo sanguíneo
                if 'id_tipo_sanguineo' in datos_deportista and datos_deportista['id_tipo_sanguineo'] is not None:
                    tipo_sangre = GrupoSanguineo.query.filter_by(id_tipo_sangre=datos_deportista['id_tipo_sanguineo']).first()
                    if not tipo_sangre:
                        return {
                            'success': False,
                            'message': 'El tipo sanguíneo especificado no existe',
                            'status_code': 400
                        }
                
                # Validar ciudad de residencia
                if 'id_ciudad_recidencia' in datos_deportista and datos_deportista['id_ciudad_recidencia'] is not None:
                    ciudad = CiudadResidencia.query.filter_by(id_ciudad=datos_deportista['id_ciudad_recidencia']).first()
                    if not ciudad:
                        return {
                            'success': False,
                            'message': 'La ciudad de residencia especificada no existe',
                            'status_code': 400
                        }
                
                # Validar EPS
                if 'id_eps' in datos_deportista and datos_deportista['id_eps'] is not None:
                    eps = EPS.query.filter_by(id_eps=datos_deportista['id_eps']).first()
                    if not eps:
                        return {
                            'success': False,
                            'message': 'La EPS especificada no existe',
                            'status_code': 400
                        }
                
                # Campos actualizables del deportista
                campos_deportista_actualizables = [
                    'peso', 'altura', 'fecha_ingreso', 'fecha_nacimiento',
                    'id_tipo_sanguineo', 'id_ciudad_recidencia',
                    'id_informacion_deportiva', 'id_eps', 'id_categoria'
                ]
                
                for campo in campos_deportista_actualizables:
                    if campo in datos_deportista:
                        valor = datos_deportista[campo]
                        # Convertir fecha_nacimiento si viene como string
                        if campo == 'fecha_nacimiento' and isinstance(valor, str):
                            try:
                                valor = datetime.fromisoformat(valor).date()
                            except ValueError:
                                return {
                                    'success': False,
                                    'message': 'Formato de fecha_nacimiento inválido. Use YYYY-MM-DD',
                                    'status_code': 400
                                }
                        # Convertir fecha_ingreso si viene como string
                        if campo == 'fecha_ingreso' and isinstance(valor, str):
                            try:
                                valor = datetime.fromisoformat(valor).date()
                            except ValueError:
                                return {
                                    'success': False,
                                    'message': 'Formato de fecha_ingreso inválido. Use YYYY-MM-DD',
                                    'status_code': 400
                                }
                        setattr(deportista, campo, valor)
            
            # Actualizar campos de información deportiva
            if datos_informacion_deportiva:
                # Obtener o crear información deportiva
                if deportista.id_informacion_deportiva:
                    info_deportiva = InformacionDeportiva.query.filter_by(
                        id_informacion_deportiva=deportista.id_informacion_deportiva
                    ).first()
                    if not info_deportiva:
                        # Si el ID existe pero no se encuentra el registro, crear uno nuevo
                        info_deportiva = None
                else:
                    info_deportiva = None
                
                if not info_deportiva:
                    # Crear nueva información deportiva
                    info_deportiva = InformacionDeportiva(
                        id_persona=deportista.id_persona,
                        practica_otro_deporte=datos_informacion_deportiva.get('practica_otro_deporte', False),
                        participa_escuela=datos_informacion_deportiva.get('participa_escuela', False),
                        recomendacion_medica=datos_informacion_deportiva.get('recomendacion_medica', False),
                        descripcion_recomendacion=datos_informacion_deportiva.get('descripcion_recomendacion'),
                        id_escuela=datos_informacion_deportiva.get('id_escuela'),
                        id_deporte=datos_informacion_deportiva.get('id_deporte'),
                        id_institucion_registro=datos_informacion_deportiva.get('id_institucion_registro')
                    )
                    db.session.add(info_deportiva)
                    db.session.flush()  # Para obtener el ID
                    deportista.id_informacion_deportiva = info_deportiva.id_informacion_deportiva
                else:
                    # Validar IDs relacionados si se proporcionan
                    from ..models.categorias.escuela import Escuela
                    from ..models.categorias.deporte import Deporte
                    from ..models.categorias.institucion_registro import InstitucionRegistro
                    
                    # Validar escuela
                    if 'id_escuela' in datos_informacion_deportiva and datos_informacion_deportiva['id_escuela'] is not None:
                        escuela = Escuela.query.filter_by(id_escuela=datos_informacion_deportiva['id_escuela']).first()
                        if not escuela:
                            return {
                                'success': False,
                                'message': 'La escuela especificada no existe',
                                'status_code': 400
                            }
                    
                    # Validar deporte
                    if 'id_deporte' in datos_informacion_deportiva and datos_informacion_deportiva['id_deporte'] is not None:
                        deporte = Deporte.query.filter_by(id_deporte=datos_informacion_deportiva['id_deporte']).first()
                        if not deporte:
                            return {
                                'success': False,
                                'message': 'El deporte especificado no existe',
                                'status_code': 400
                            }
                    
                    # Validar institución de registro
                    if 'id_institucion_registro' in datos_informacion_deportiva and datos_informacion_deportiva['id_institucion_registro'] is not None:
                        institucion = InstitucionRegistro.query.filter_by(
                            id_institucion=datos_informacion_deportiva['id_institucion_registro']
                        ).first()
                        if not institucion:
                            return {
                                'success': False,
                                'message': 'La institución de registro especificada no existe',
                                'status_code': 400
                            }
                    
                    # Campos actualizables de información deportiva
                    campos_info_deportiva = [
                        'practica_otro_deporte', 'participa_escuela', 'recomendacion_medica',
                        'descripcion_recomendacion', 'id_escuela', 'id_deporte', 'id_institucion_registro'
                    ]
                    
                    for campo in campos_info_deportiva:
                        if campo in datos_informacion_deportiva:
                            setattr(info_deportiva, campo, datos_informacion_deportiva[campo])
            
            # Actualizar diagnósticos si se proporcionan
            if tipo_enfermedad is not None or diagnosticos is not None:
                from ..models.salud.diagnostico_deportista import DiagnosticoDeportista
                from ..models.salud.diagnostico import Diagnostico
                
                # Eliminar diagnósticos existentes del deportista
                DiagnosticoDeportista.query.filter_by(id_deportista=id_deportista).delete()
                
                # Si se proporcionan nuevos diagnósticos, validar y agregar
                if diagnosticos and len(diagnosticos) > 0:
                    # Validar tipo de enfermedad si se proporciona
                    if tipo_enfermedad:
                        # Validar que los diagnósticos pertenecen al tipo de enfermedad seleccionado
                        for id_diagnostico in diagnosticos:
                            diagnostico = Diagnostico.query.filter_by(id_diagnostico=id_diagnostico).first()
                            if not diagnostico:
                                db.session.rollback()
                                return {
                                    'success': False,
                                    'message': f'El diagnóstico con ID {id_diagnostico} no existe',
                                    'status_code': 400
                                }
                            if diagnostico.id_tipo_enfermedad != tipo_enfermedad:
                                db.session.rollback()
                                return {
                                    'success': False,
                                    'message': f'El diagnóstico con ID {id_diagnostico} no corresponde al tipo de enfermedad seleccionado',
                                    'status_code': 400
                                }
                    
                    # Agregar nuevos diagnósticos
                    from datetime import date
                    for id_diagnostico in diagnosticos:
                        diagnostico_deportista = DiagnosticoDeportista(
                            id_deportista=id_deportista,
                            id_diagnostico=id_diagnostico,
                            fecha=date.today()
                        )
                        db.session.add(diagnostico_deportista)
                    logger.info(f'{len(diagnosticos)} diagnóstico(s) actualizados para el deportista {id_deportista}')
            
            # Confirmar todos los cambios
            db.session.commit()
            
            logger.info(f'Deportista actualizado completamente: ID {id_deportista}')
            
            # Construir respuesta con datos actualizados
            respuesta = deportista.to_dict()
            if deportista.persona:
                respuesta['persona'] = deportista.persona.to_dict()
            if deportista.informacion_deportiva:
                respuesta['informacion_deportiva'] = deportista.informacion_deportiva.to_dict()
            
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
                'message': 'Error de duplicación de datos',
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

