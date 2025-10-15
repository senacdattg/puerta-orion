"""
Modelo para instituciones de registro.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class InstitucionRegistro(BaseModel):
    """
    Modelo para instituciones de registro.

    Representa las diferentes instituciones donde las personas pueden registrarse.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_institucion (int): Identificador único de la institución (clave primaria).
        nombre_institucion (str): Nombre de la institución (único).
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_institucion_registro'
    
    id_institucion = Column(Integer, primary_key=True)
    nombre_institucion = Column(String(200), nullable=False, unique=True)
    
    # Relaciones
    informaciones_deportivas = relationship('InformacionDeportiva', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de InstitucionRegistro.

        Returns:
            str: Una cadena que representa la instancia de InstitucionRegistro.
        """
        return f'<InstitucionRegistro {self.nombre_institucion}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de InstitucionRegistro.
        """
        return {
            'id_institucion': self.id_institucion,
            'nombre_institucion': self.nombre_institucion
        }
