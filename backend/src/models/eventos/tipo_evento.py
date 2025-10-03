"""
Modelo para tipos de eventos.
"""

from ..base import BaseModel, db
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class TipoEvento(BaseModel):
    """
    Modelo para tipos de eventos.
    
    Define los diferentes tipos de eventos que pueden ocurrir en el sistema
    (competencias, entrenamientos, exhibiciones, etc.).
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_tipo_evento (int): Identificador único del tipo de evento (clave primaria).
        nombre (str): Nombre del tipo de evento.
        descripcion (str): Descripción detallada del tipo de evento (opcional).
        eventos (list): Relación uno a muchos con el modelo Evento.
    """
    __tablename__ = 'puerta_orion_tipo_evento'
    
    id_tipo_evento = Column(Integer, primary_key=True)
    nombre = Column(String(250), nullable=False)
    descripcion = Column(String(300))
    
    # Relaciones
    eventos = relationship('Evento', backref='tipo_evento_obj', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de TipoEvento.
        """
        return f'<TipoEvento {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_tipo_evento': self.id_tipo_evento,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }
