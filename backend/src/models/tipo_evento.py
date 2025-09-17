"""
Modelo para tipos de eventos.
"""

from ..database.database import db

class TipoEvento(db.Model):
    """Modelo para tipos de eventos."""
    __tablename__ = 'puerta_orion_tipo_evento'
    
    id_tipo_evento = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(300))
    
    # Relaciones
    eventos = db.relationship('Evento', backref='tipo_evento', lazy=True)
    
    def __repr__(self):
        return f'<TipoEvento {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_tipo_evento': self.id_tipo_evento,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }


