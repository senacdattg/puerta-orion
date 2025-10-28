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
from datetime import date
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_

from ..models.base import db
from ..models.deportistas.deportista import Deportista
from ..models.personas.persona import Persona
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
                - id_mensualidad (int, opcional): ID de la mensualidad
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

            # Crear instancia de deportista
            # La fecha de ingreso se asigna automáticamente a la fecha actual
            deportista = Deportista(
                id_persona=datos['id_persona'],
                id_categoria=datos['id_categoria'],
                fecha_ingreso=datos.get('fecha_ingreso', date.today()),  # Automática por defecto
                peso=datos.get('peso'),
                altura=datos.get('altura'),
                fecha_nacimiento=datos.get('fecha_nacimiento'),
                id_tipo_sanguineo=datos.get('id_tipo_sanguineo'),
                id_ciudad_recidencia=datos.get('id_ciudad_recidencia'),
                id_mensualidad=datos.get('id_mensualidad'),
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

            deportistas = [deportista.to_dict() for deportista in paginacion.items]

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
                'id_tipo_sanguineo', 'id_ciudad_recidencia', 'id_mensualidad',
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

