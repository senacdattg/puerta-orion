"""
Modelo para enfermedades específicas.
"""

from ..database.database import db

class Enfermedad(db.Model):
    """Modelo para enfermedades específicas."""
    __tablename__ = 'puerta_orion_enfermedad'
    
    id_enfermedad = db.Column(db.Integer, primary_key=True)
    id_tipo_enfermedad = db.Column(db.Integer, db.ForeignKey('puerta_orion_tipo_enfermedad.id_tipo_enfermedad'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    
    # Relaciones
    personas = db.relationship('Persona', backref='enfermedad', lazy=True)
    
    def __repr__(self):
        return f'<Enfermedad {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_enfermedad': self.id_enfermedad,
            'id_tipo_enfermedad': self.id_tipo_enfermedad,
            'nombre': self.nombre
        }


