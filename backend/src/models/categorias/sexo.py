"""
Modelo para tipos de sexo.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, Boolean
from ...database.database import db


class Sexo(BaseModel):
    """Modelo para tipos de sexo."""
    __tablename__ = 'puerta_orion_sexo'
    
    id_sexo = Column(Integer, primary_key=True)
    sexo = Column(Boolean, nullable=False)
    
    # Relaciones
    personas = db.relationship('Persona', backref='sexo', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Sexo.
        """
        return f'<Sexo {self.sexo}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_sexo': self.id_sexo,
            'sexo': self.sexo
        }
