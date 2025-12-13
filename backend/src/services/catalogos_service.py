"""
Servicio de catálogos para el sistema Puerta Orion.

Responsabilidad:
- Obtener datos de catálogos desde la base de datos
- Proporcionar acceso a tipos de documento, sexos, categorías, etc.
- Manejar consultas optimizadas para formularios

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from typing import Dict, Any, List
from ..models.catalogos.tipo_documento import TipoDocumento
from ..models.categorias.sexo import Sexo
from ..models.categorias.categoria import Categoria
from ..models.salud.diagnostico import Diagnostico
from ..models.salud.tipo_enfermedad import TipoEnfermedad
from ..models.categorias.grupo_sanguineo import GrupoSanguineo
from ..models.categorias.ciudad_residencia import CiudadResidencia
from ..models.categorias.deporte import Deporte
from ..models.categorias.escuela import Escuela
from ..models.categorias.institucion_registro import InstitucionRegistro
from ..models.catalogos.eps import EPS
from ..utils.logger import obtener_registrador


class CatalogosService:
    """
    Servicio para gestión de catálogos.

    Encapsula toda la lógica de negocio relacionada con la obtención
    de datos de catálogos para formularios y consultas.
    """

    # Mapeos de códigos para consistencia con las rutas
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

    def __init__(self):
        """Inicializa el servicio con el logger configurado."""
        self.logger = obtener_registrador('aplicacion')

    def obtener_catalogos_completos(self) -> Dict[str, Any]:
        """
        Obtiene todos los catálogos necesarios para los formularios.

        Returns:
            Dict: Diccionario con todos los catálogos

        Raises:
            Exception: Si hay errores al consultar la base de datos
        """
        try:
            # Obtener tipos de documento
            tipos_documento = self._obtener_tipos_documento()

            # Obtener sexos
            sexos = self._obtener_sexos()

            # Obtener categorías
            categorias = self._obtener_categorias()

            return {
                'tipos_documento': tipos_documento,
                'sexos': sexos,
                'categorias': categorias
            }

        except Exception as e:
            self.logger.error(f"Error al obtener catálogos completos: {str(e)}")
            raise

    def _obtener_tipos_documento(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los tipos de documento.

        Returns:
            List[Dict]: Lista de tipos de documento
        """
        try:
            tipos = TipoDocumento.query.all()
            # Removed logger.info for performance

            return [
                {
                    'id': tipo.id_documento,
                    'codigo': self.MAPEO_TIPOS_DOCUMENTO.get(
                        tipo.nombre_documento,
                        tipo.nombre_documento.lower().replace(' ', '_')
                    ),
                    'nombre': tipo.nombre_documento
                }
                for tipo in tipos
            ]
        except Exception as e:
            self.logger.error(f"Error al obtener tipos de documento: {str(e)}")
            return []

    def _obtener_sexos(self) -> List[Dict[str, Any]]:
        """
        Obtiene todos los sexos.

        Returns:
            List[Dict]: Lista de sexos
        """
        try:
            sexos = Sexo.query.all()
            # Removed logger.info for performance

            return [
                {
                    'id': sexo.id_sexo,
                    'valor': self.MAPEO_SEXOS.get(sexo.nombre, sexo.nombre.lower()),
                    'nombre': sexo.nombre
                }
                for sexo in sexos
            ]
        except Exception as e:
            self.logger.error(f"Error al obtener sexos: {str(e)}")
            return []

    def _obtener_categorias(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las categorías.

        Returns:
            List[Dict]: Lista de categorías
        """
        try:
            categorias = Categoria.query.filter_by(estado=True).all()
            # Removed logger.info for performance

            return [
                {
                    'id': categoria.id_categoria,
                    'codigo': str(categoria.codigo_categoria),
                    'nombre': categoria.nombre_categoria
                }
                for categoria in categorias
            ]
        except Exception as e:
            self.logger.error(f"Error al obtener categorías: {str(e)}")
            return []

    def obtener_diagnosticos(self, id_tipo_enfermedad: int = None) -> Dict[str, Any]:
        """
        Obtiene los diagnósticos disponibles.
        
        Args:
            id_tipo_enfermedad: Opcional. Filtra diagnósticos por tipo de enfermedad.
        """
        try:
            if id_tipo_enfermedad:
                diagnosticos = Diagnostico.query.filter_by(id_tipo_enfermedad=id_tipo_enfermedad).all()
                # Removed logger.info for performance
            # self.logger.info(f"Diagnósticos encontrados para tipo enfermedad {id_tipo_enfermedad}: {len(diagnosticos)}")
            else:
                diagnosticos = Diagnostico.query.all()
                # Removed logger.info for performance
            # self.logger.info(f"Diagnósticos encontrados: {len(diagnosticos)}")
            
            return {
                'success': True,
                'data': [diagnostico.to_dict() for diagnostico in diagnosticos],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener diagnósticos: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener diagnósticos: {str(e)}',
                'status_code': 500
            }

    def obtener_tipos_enfermedad(self, incluir_diagnosticos: bool = False) -> Dict[str, Any]:
        """
        Obtiene todos los tipos de enfermedad disponibles.
        
        Args:
            incluir_diagnosticos: Si es True, incluye los diagnósticos relacionados en la respuesta.
        """
        try:
            tipos = TipoEnfermedad.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Tipos de enfermedad encontrados: {len(tipos)}")
            
            tipos_data = []
            for tipo in tipos:
                tipo_dict = tipo.to_dict()
                if incluir_diagnosticos:
                    # Cargar diagnósticos relacionados
                    diagnosticos = Diagnostico.query.filter_by(id_tipo_enfermedad=tipo.id_tipo_enfermedad).all()
                    tipo_dict['diagnosticos'] = [diagnostico.to_dict() for diagnostico in diagnosticos]
                tipos_data.append(tipo_dict)
            
            return {
                'success': True,
                'data': tipos_data,
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener tipos de enfermedad: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener tipos de enfermedad: {str(e)}',
                'status_code': 500
            }

    def obtener_grupos_sanguineos(self) -> Dict[str, Any]:
        """Obtiene todos los grupos sanguíneos disponibles."""
        try:
            grupos = GrupoSanguineo.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Grupos sanguíneos encontrados: {len(grupos)}")
            
            return {
                'success': True,
                'data': [grupo.to_dict() for grupo in grupos],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener grupos sanguíneos: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener grupos sanguíneos: {str(e)}',
                'status_code': 500
            }

    def obtener_ciudades_residencia(self) -> Dict[str, Any]:
        """Obtiene todas las ciudades de residencia disponibles."""
        try:
            ciudades = CiudadResidencia.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Ciudades de residencia encontradas: {len(ciudades)}")
            
            return {
                'success': True,
                'data': [ciudad.to_dict() for ciudad in ciudades],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener ciudades de residencia: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener ciudades de residencia: {str(e)}',
                'status_code': 500
            }

    def obtener_eps(self) -> Dict[str, Any]:
        """Obtiene todas las EPS disponibles."""
        try:
            eps_list = EPS.query.filter_by(estado=True).all()
            # Removed logger.info for performance
            # self.logger.info(f"EPS encontradas: {len(eps_list)}")
            
            return {
                'success': True,
                'data': [eps.to_dict() for eps in eps_list],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener EPS: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener EPS: {str(e)}',
                'status_code': 500
            }

    def obtener_deportes(self) -> Dict[str, Any]:
        """Obtiene todos los deportes disponibles."""
        try:
            deportes = Deporte.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Deportes encontrados: {len(deportes)}")
            
            return {
                'success': True,
                'data': [deporte.to_dict() for deporte in deportes],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener deportes: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener deportes: {str(e)}',
                'status_code': 500
            }

    def obtener_escuelas(self) -> Dict[str, Any]:
        """Obtiene todas las escuelas deportivas disponibles."""
        try:
            escuelas = Escuela.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Escuelas encontradas: {len(escuelas)}")
            
            return {
                'success': True,
                'data': [escuela.to_dict() for escuela in escuelas],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener escuelas: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener escuelas: {str(e)}',
                'status_code': 500
            }

    def obtener_instituciones_registro(self) -> Dict[str, Any]:
        """Obtiene todas las instituciones de registro disponibles."""
        try:
            instituciones = InstitucionRegistro.query.all()
            # Removed logger.info for performance
            # self.logger.info(f"Instituciones de registro encontradas: {len(instituciones)}")
            
            return {
                'success': True,
                'data': [institucion.to_dict() for institucion in instituciones],
                'status_code': 200
            }
        except Exception as e:
            self.logger.error(f"Error al obtener instituciones de registro: {str(e)}")
            return {
                'success': False,
                'message': f'Error al obtener instituciones de registro: {str(e)}',
                'status_code': 500
            }


# Instancia global del servicio para uso en la aplicación
catalogos_service = CatalogosService()





