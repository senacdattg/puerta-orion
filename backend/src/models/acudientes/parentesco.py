"""
Modelo para tipos de parentesco.
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Parentesco(BaseModel):
    """
    Modelo para tipos de parentesco.

    Define los diferentes tipos de parentesco que pueden existir
    entre deportistas y acudientes (padre, madre, hermano, etc.).
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_parentesco (int): Identificador único del parentesco (clave primaria).
        nombre (str): Nombre del tipo de parentesco.
        deportistas_acudientes (list): Relación uno a muchos con el modelo DeportistaAcudiente.
    """
    __tablename__ = 'puerta_orion_parentesco'
    
    id_parentesco = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False, unique=True)
    
    # Relaciones
    deportistas_acudientes = relationship('DeportistaAcudiente', lazy=True, overlaps="parentesco")
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Parentesco.

        Returns:
            str: Una cadena que representa la instancia de Parentesco.
        """
        return f'<Parentesco {self.nombre}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Parentesco.
        """
        return {
            'id_parentesco': self.id_parentesco,
            'nombre': self.nombre
        }
