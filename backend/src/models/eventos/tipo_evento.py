"""
Modelo para tipos de eventos.
"""

from ..base import BaseModel
from ...database.database import db
from sqlalchemy import Column, Integer, String


class TipoEvento(BaseModel):
    """Modelo para tipos de eventos."""
    __tablename__ = 'puerta_orion_tipo_evento'
    
    id_tipo_evento = Column(Integer, primary_key=True)
    nombre = Column(String(250), nullable=False)
    descripcion = Column(String(300))
    
    # Relaciones
    eventos = db.relationship('Evento', backref='tipo_evento', lazy=True)
    
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
