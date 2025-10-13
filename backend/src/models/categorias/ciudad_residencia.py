"""
Modelo para ciudades de residencia.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class CiudadResidencia(BaseModel):
    """
    Modelo para ciudades de residencia.

    Representa las diferentes ciudades donde pueden residir las personas 
    registradas en el sistema. Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_ciudad (int): Identificador único de la ciudad (clave primaria).
        nombre_ciudad (str): Nombre de la ciudad (único).
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_ciudad_residencia'
    
    id_ciudad = Column(Integer, primary_key=True)
    nombre_ciudad = Column(String(150), nullable=False, unique=True)
    
    # Relaciones
    deportistas = relationship('Deportista', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de CiudadResidencia.

        Returns:
            str: Una cadena que representa la instancia de CiudadResidencia.
        """
        return f'<CiudadResidencia {self.nombre_ciudad}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de CiudadResidencia.
        """
        return {
            'id_ciudad': self.id_ciudad,
            'nombre_ciudad': self.nombre_ciudad
        }
