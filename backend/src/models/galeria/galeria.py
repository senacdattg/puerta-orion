"""
Modelo para la galería de imágenes del sistema.
"""

from datetime import datetime
from ..base import db, BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Galeria(BaseModel):
    """Modelo para la galería de imágenes del sistema."""
    __tablename__ = 'puerta_orion_galeria'

    id_galeria = Column(Integer, primary_key=True)
    titulo = Column(String(250), nullable=False)
    url_imagen = Column(String(500), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_subida = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign Keys
    id_tipo_evento = Column(Integer, ForeignKey('puerta_orion_tipo_evento.id_tipo_evento'), nullable=True)
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=True)
    
    # Relaciones
    tipo_evento = relationship('TipoEvento', lazy=True)
    categoria = relationship('Categoria', lazy=True)

    def __repr__(self):
        return f'<Galeria {self.titulo}>'

    def to_dict(self):
        return {
            'id_galeria': self.id_galeria,
            'titulo': self.titulo,
            'url_imagen': self.url_imagen,
            'descripcion': self.descripcion,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None,
            'id_tipo_evento': self.id_tipo_evento,
            'id_categoria': self.id_categoria,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

