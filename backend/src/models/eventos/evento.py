"""
Modelo para eventos deportivos.
"""

from datetime import datetime, date, time
from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship


class Evento(BaseModel):
    """Modelo para eventos deportivos."""
    __tablename__ = 'puerta_orion_evento'
    
    id_evento = Column(Integer, primary_key=True)
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    id_tipo_evento = Column(Integer, ForeignKey('puerta_orion_tipo_evento.id_tipo_evento'), nullable=False)
    id_sesion = Column(Integer, ForeignKey('puerta_orion_sesiones.id_sesion'), nullable=False)
    nombre = Column(String(250), nullable=False)
    fecha_evento = Column(Date, nullable=False)
    duracion = Column(Time, nullable=False)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Evento.
        """
        return f'<Evento {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_evento': self.id_evento,
            'id_categoria': self.id_categoria,
            'id_tipo_evento': self.id_tipo_evento,
            'id_sesion': self.id_sesion,
            'nombre': self.nombre,
            'fecha_evento': self.fecha_evento.isoformat() if self.fecha_evento else None,
            'duracion': self.duracion.isoformat() if self.duracion else None
        }
