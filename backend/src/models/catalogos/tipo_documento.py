"""
Modelo para tipos de documento de identificación.
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class TipoDocumento(BaseModel):
    """
    Modelo para tipos de documento de identificación.

    Define los diferentes tipos de documentos de identificación
    que pueden tener las personas (cédula, pasaporte, etc.).
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_documento (int): Identificador único del tipo de documento (clave primaria).
        nombre_documento (str): Nombre del tipo de documento.
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_tipo_documento'
    
    id_documento = Column(Integer, primary_key=True)
    nombre_documento = Column(String(50), nullable=False, unique=True)
    
    # Relaciones
    personas = relationship('Persona', lazy=True, overlaps="tipo_documento")
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de TipoDocumento.

        Returns:
            str: Una cadena que representa la instancia de TipoDocumento.
        """
        return f'<TipoDocumento {self.nombre_documento}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de TipoDocumento.
        """
        return {
            'id_documento': self.id_documento,
            'nombre_documento': self.nombre_documento
        }
