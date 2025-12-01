"""
Modelo para tipos de sexo.
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import relationship


class Sexo(BaseModel):
    """
    Modelo para tipos de sexo.
    
    Representa el sexo biológico de las personas en el sistema.
    Almacena valores descriptivos como "Masculino", "Femenino", etc.
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_sexo (int): Identificador único del sexo (clave primaria).
        nombre (str): Nombre descriptivo del sexo.
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_sexo'
    
    id_sexo = Column(Integer, primary_key=True)
    nombre = Column(db.String(150), nullable=False)
    
    # Relaciones
    personas = relationship('Persona', lazy=True, overlaps="sexo")
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Sexo.
        """
        return f'<Sexo {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_sexo': self.id_sexo,
            'nombre': self.nombre
        }
