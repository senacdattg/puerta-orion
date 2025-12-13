"""
Modelo para categorías de deportistas.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class Categoria(BaseModel):
    """
    Modelo para categorías de deportistas.

    Define las diferentes categorías en las que se agrupan los deportistas,
    basado en criterios como la edad mínima y máxima. También maneja el estado
    de la categoría (activa/inactiva) y sus relaciones con eventos y deportistas.
    Hereda de BaseModel para incluir campos de auditoría.
    """
    __tablename__ = 'puerta_orion_categoria'
    
    id_categoria = Column(Integer, primary_key=True)
    codigo_categoria = Column(Integer, nullable=False, unique=True)
    nombre_categoria = Column(String(150), nullable=False)
    edad_minima = Column(Integer, nullable=False)
    edad_maxima = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    eventos = relationship('Evento', lazy=True, overlaps="categoria")
    deportistas = relationship('Deportista', lazy=True, overlaps="categoria")
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Categoria.
        """
        return f'<Categoria {self.nombre_categoria}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Categoría.
        """
        return {
            'id_categoria': self.id_categoria,
            'codigo_categoria': self.codigo_categoria,
            'nombre_categoria': self.nombre_categoria,
            'edad_minima': self.edad_minima,
            'edad_maxima': self.edad_maxima,
            'estado': self.estado
        }
