"""
Modelo para grupos sanguíneos.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class GrupoSanguineo(BaseModel):
    """
    Modelo para grupos sanguíneos.

    Define los diferentes tipos de grupos sanguíneos disponibles en el sistema.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_tipo_sangre (int): Identificador único del tipo de sangre (clave primaria).
        tipo_sangre (str): Nombre del tipo de sangre (ej. "A+", "O-") (único).
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_grupo_sanguineo'
    
    id_tipo_sangre = Column(Integer, primary_key=True)
    tipo_sangre = Column(String(150), nullable=False, unique=True)
    
    # Relaciones
    deportistas = relationship('Deportista', lazy=True, overlaps="tipo_sanguineo")
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de GrupoSanguineo.

        Returns:
            str: Una cadena que representa la instancia de GrupoSanguineo.
        """
        return f'<GrupoSanguineo {self.tipo_sangre}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de GrupoSanguineo.
        """
        return {
            'id_tipo_sangre': self.id_tipo_sangre,
            'tipo_sangre': self.tipo_sangre
        }
