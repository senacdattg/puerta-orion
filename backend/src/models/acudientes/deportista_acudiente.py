"""
Modelo para la relación muchos a muchos entre deportistas y acudientes.
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship


class DeportistaAcudiente(BaseModel):
    """
    Modelo para la relación muchos a muchos entre deportistas y acudientes.

    Esta tabla de unión maneja la relación entre deportistas y acudientes,
    incluyendo información sobre si el acudiente es responsable y la fecha de registro.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_deportista_acudiente (int): Identificador único de la relación (clave primaria).
        id_deportista (int): Clave foránea al deportista.
        id_acudiente (int): Clave foránea al acudiente.
        id_parentesco (int): Clave foránea al tipo de parentesco.
        es_responsable (bool): Indica si el acudiente es el responsable principal.
        fecha_registro (date): Fecha de registro de la relación.
        deportista (Deportista): Relación muchos a uno con el modelo Deportista.
        acudiente (Acudiente): Relación muchos a uno con el modelo Acudiente.
        parentesco (Parentesco): Relación muchos a uno con el modelo Parentesco.
    """
    __tablename__ = 'puerta_orion_deportista_acudiente'
    
    id_deportista_acudiente = Column(Integer, primary_key=True)
    id_deportista = Column(Integer, ForeignKey('puerta_orion_deportista.id_deportista'), nullable=False)
    id_acudiente = Column(Integer, ForeignKey('puerta_orion_acudiente.id_acudiente'), nullable=False)
    id_parentesco = Column(Integer, ForeignKey('puerta_orion_parentesco.id_parentesco'), nullable=False)
    es_responsable = Column(Boolean, default=False, nullable=False)
    fecha_registro = Column(Date, nullable=False)
    
    # Relaciones
    deportista = relationship('Deportista', backref='deportistas_acudientes', lazy=True)
    acudiente = relationship('Acudiente', backref='deportistas_acudientes', lazy=True)
    parentesco = relationship('Parentesco', backref='deportistas_acudientes', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de DeportistaAcudiente.

        Returns:
            str: Una cadena que representa la instancia de DeportistaAcudiente.
        """
        return f'<DeportistaAcudiente {self.id_deportista}-{self.id_acudiente}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de DeportistaAcudiente.
        """
        return {
            'id_deportista_acudiente': self.id_deportista_acudiente,
            'id_deportista': self.id_deportista,
            'id_acudiente': self.id_acudiente,
            'id_parentesco': self.id_parentesco,
            'es_responsable': self.es_responsable,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
