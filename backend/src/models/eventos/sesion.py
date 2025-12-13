"""
Modelo para sesiones de entrenamiento.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String


class Sesion(BaseModel):
    """Modelo para sesiones de entrenamiento."""
    __tablename__ = 'puerta_orion_sesiones'
    
    id_sesion = Column(Integer, primary_key=True)
    nombre = Column(String(250), nullable=False)
    descripcion = Column(String(250))
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Sesion.
        """
        return f'<Sesion {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_sesion': self.id_sesion,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
