"""
Modelo para tipos de enfermedades.
"""

from ..base import db, BaseModel

class TipoEnfermedad(BaseModel):
    """Modelo para tipos de enfermedades."""
    __tablename__ = 'TipoEnfermedad'
    
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


