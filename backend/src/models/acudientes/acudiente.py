"""
Modelo para acudientes del sistema.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Acudiente(BaseModel):
    """
    Modelo para acudientes del sistema.

    Representa a los acudientes que están asociados con los deportistas,
    manteniendo información sobre su estado y relación con las personas.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_acudiente (int): Identificador único del acudiente (clave primaria).
        id_persona (int): Clave foránea a la tabla de personas.
        estado (bool): Estado activo/inactivo del acudiente.
        persona (Persona): Relación uno a uno con el modelo Persona.
        deportistas_acudientes (list): Relación muchos a muchos con Deportista a través de DeportistaAcudiente.
    """
    __tablename__ = 'puerta_orion_acudiente'
    
    id_acudiente = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False, unique=True)
    estado = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    persona = relationship('Persona', uselist=False)
    deportistas_acudientes = relationship('DeportistaAcudiente', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Acudiente.

        Returns:
            str: Una cadena que representa la instancia de Acudiente.
        """
        return f'<Acudiente {self.id_acudiente}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Acudiente.
        """
        return {
            'id_acudiente': self.id_acudiente,
            'id_persona': self.id_persona,
            'estado': self.estado
        }
