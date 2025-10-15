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
    de la categoría (activa/inactiva) y sus relaciones con eventos y mensualidades.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_categoria (int): Identificador único de la categoría (clave primaria).
        codigo_categoria (int): Código único de la categoría.
        nombre_categoria (str): Nombre descriptivo de la categoría.
        edad_minima (int): Edad mínima para pertenecer a esta categoría.
        edad_maxima (int): Edad máxima para pertenecer a esta categoría.
        estado (bool): Indica si la categoría está activa o inactiva.
        eventos (list): Relación uno a muchos con el modelo Evento.
        mensualidades (list): Relación uno a muchos con el modelo Mensualidad.
    """
    __tablename__ = 'puerta_orion_categoria'
    
    id_categoria = Column(Integer, primary_key=True)
    codigo_categoria = Column(Integer, nullable=False, unique=True)
    nombre_categoria = Column(String(150), nullable=False)
    edad_minima = Column(Integer, nullable=False)
    edad_maxima = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    eventos = relationship('Evento', lazy=True)
    mensualidades = relationship('Mensualidad', lazy=True)
    deportistas = relationship('Deportista', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Categoría.

        Returns:
            str: Una cadena que representa la instancia de Categoría.
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
