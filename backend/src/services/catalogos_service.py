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
from ..utils.logger import obtener_registrador


class CatalogosService:
    """
    Servicio para gestión de catálogos.
    
    Encapsula toda la lógica de negocio relacionada con la obtención
    de datos de catálogos para formularios y consultas.
    """
    
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
            self.logger.info(f"Tipos de documento encontrados: {len(tipos)}")
            for tipo in tipos:
                self.logger.info(f"  - ID: {tipo.id_documento}, Nombre: {tipo.nombre_documento}")
            
            return [
                {
                    'id': tipo.id_documento,
                    'codigo': tipo.nombre_documento.lower().replace(' ', '_'),
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
            self.logger.info(f"Sexos encontrados: {len(sexos)}")
            for sexo in sexos:
                self.logger.info(f"  - ID: {sexo.id_sexo}, Nombre: {sexo.nombre}")
            
            return [
                {
                    'id': sexo.id_sexo,
                    'valor': sexo.nombre.lower(),
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
            self.logger.info(f"Categorías encontradas: {len(categorias)}")
            for categoria in categorias:
                self.logger.info(f"  - ID: {categoria.id_categoria}, Nombre: {categoria.nombre_categoria}, Estado: {categoria.estado}")
            
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


# Instancia global del servicio para uso en la aplicación
catalogos_service = CatalogosService()





