"""
Modelo para tipos de enfermedades.
"""

from ..database.database import db

class TipoEnfermedad(db.Model):
    """Modelo para tipos de enfermedades."""
    __tablename__ = 'puerta_orion_tipo_enfermedad'
    
    id_tipo_enfermedad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relaciones
    enfermedades = db.relationship('Enfermedad', backref='tipo_enfermedad', lazy=True)
    
    def __repr__(self):
        return f'<TipoEnfermedad {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_tipo_enfermedad': self.id_tipo_enfermedad,
            'nombre': self.nombre
        }


