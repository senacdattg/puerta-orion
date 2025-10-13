"""
Modelo para tipos de enfermedades.
"""

from ..base import db, BaseModel

class TipoEnfermedad(BaseModel):
    """
    Modelo para tipos de enfermedades.
    
    Clasifica las enfermedades en diferentes tipos o categorías
    (crónicas, agudas, congénitas, etc.).
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_tipo_enfermedad (int): Identificador único del tipo de enfermedad (clave primaria).
        nombre (str): Nombre del tipo de enfermedad (único).
        diagnosticos (list): Relación uno a muchos con el modelo Diagnostico.
    """
    __tablename__ = 'tipoenfermedad'
    
    id_tipo_enfermedad = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relaciones
    diagnosticos = db.relationship('Diagnostico', lazy=True)
    
    def __repr__(self):
        return f'<TipoEnfermedad {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_tipo_enfermedad': self.id_tipo_enfermedad,
            'nombre': self.nombre
        }


