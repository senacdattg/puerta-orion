"""
Modelo para eventos deportivos.
"""

from datetime import datetime, date, time
from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey
from sqlalchemy.orm import relationship


class Evento(BaseModel):
    """
    Modelo para eventos deportivos.
    
    Attributes:
        id_evento (int): Identificador único del evento.
        nombre (str): Nombre del evento.
        fecha_evento (date): Fecha del evento.
        hora_inicio (time): Hora de inicio del evento.
        hora_fin (time): Hora de finalización del evento.
        lugar (str): Ubicación física del evento.
        descripcion (str): Descripción detallada del evento (opcional).
        id_categoria (int): Clave foránea a la categoría.
        id_tipo_evento (int): Clave foránea al tipo de evento.
    """
    __tablename__ = 'puerta_orion_calendario'
    
    id_evento = Column(Integer, primary_key=True)
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    id_tipo_evento = Column(Integer, ForeignKey('puerta_orion_tipo_evento.id_tipo_evento'), nullable=False)
    nombre = Column(String(250), nullable=False)
    fecha_evento = Column(Date, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    lugar = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # Relaciones
    categoria = relationship('Categoria', lazy=True, overlaps="eventos")
    
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
            'nombre': self.nombre if self.nombre else '',
            'fecha_evento': self.fecha_evento.isoformat() if self.fecha_evento else None,
            'hora_inicio': self.hora_inicio.isoformat() if self.hora_inicio else None,
            'hora_fin': self.hora_fin.isoformat() if self.hora_fin else None,
            'lugar': self.lugar if self.lugar else '',
            'descripcion': self.descripcion if self.descripcion else ''
        }
