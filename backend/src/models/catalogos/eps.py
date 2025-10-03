"""
Modelo para Entidades Promotoras de Salud (EPS).
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class EPS(BaseModel):
    """
    Modelo para Entidades Promotoras de Salud (EPS).

    Representa las diferentes EPS donde las personas pueden estar afiliadas.
    Incluye información como nombre, estado y código de la EPS.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_eps (int): Identificador único de la EPS (clave primaria).
        nombre_eps (str): Nombre de la EPS.
        estado (bool): Estado activo/inactivo de la EPS.
        codigo_eps (int): Código único de la EPS.
        personas (list): Relación uno a muchos con el modelo Persona.
    """
    __tablename__ = 'puerta_orion_eps'
    
    id_eps = Column(Integer, primary_key=True)
    nombre_eps = Column(String(150), nullable=False, unique=True)
    estado = Column(Boolean, default=True, nullable=False)
    codigo_eps = Column(Integer, nullable=True)
    
    # Relaciones
    personas = relationship('Persona', backref='eps_obj', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de EPS.

        Returns:
            str: Una cadena que representa la instancia de EPS.
        """
        return f'<EPS {self.nombre_eps}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de EPS.
        """
        return {
            'id_eps': self.id_eps,
            'nombre_eps': self.nombre_eps,
            'estado': self.estado,
            'codigo_eps': self.codigo_eps
        }
