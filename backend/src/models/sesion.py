"""
Modelo para sesiones de entrenamiento.
"""

from ..database.database import db

class Sesion(db.Model):
    """Modelo para sesiones de entrenamiento."""
    __tablename__ = 'puerta_orion_sesiones'
    
    id_sesion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250), nullable=False)
    descripcion = db.Column(db.String(250))
    
    # Relaciones
    eventos = db.relationship('Evento', backref='sesion', lazy=True)
    roles_usuarios = db.relationship('RolUsuario', backref='sesion', lazy=True)
    
    def __repr__(self):
        return f'<Sesion {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_sesion': self.id_sesion,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }


