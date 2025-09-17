"""
Modelo para instituciones de registro.
"""

from ..database.database import db

class InstitucionRegistro(db.Model):
    """Modelo para instituciones de registro."""
    __tablename__ = 'puerta_orion_institucion_registro'
    
    id_institucion = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(200), nullable=False, unique=True)
    
    # Relaciones
    personas = db.relationship('Persona', backref='institucion_registro', lazy=True)
    
    def __repr__(self):
        return f'<InstitucionRegistro {self.nombre_institucion}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_institucion': self.id_institucion,
            'nombre_institucion': self.nombre_institucion
        }

