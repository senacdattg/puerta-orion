"""
Modelo para ciudades de residencia.
"""

from ..database.database import db

class CiudadResidencia(db.Model):
    """Modelo para ciudades de residencia."""
    __tablename__ = 'puerta_orion_ciudad_residencia'
    
    id_ciudad = db.Column(db.Integer, primary_key=True)
    nombre_ciudad = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relaciones
    personas = db.relationship('Persona', backref='ciudad_residencia', lazy=True)
    
    def __repr__(self):
        return f'<CiudadResidencia {self.nombre_ciudad}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_ciudad': self.id_ciudad,
            'nombre_ciudad': self.nombre_ciudad
        }

