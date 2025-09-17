"""
Modelo para grupos sanguíneos.
"""

from ..database.database import db

class GrupoSanguineo(db.Model):
    """Modelo para grupos sanguíneos."""
    __tablename__ = 'puerta_orion_grupo_sanguineo'
    
    id_tipo_sangre = db.Column(db.Integer, primary_key=True)
    tipo_sangre = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relaciones
    personas = db.relationship('Persona', backref='grupo_sanguineo', lazy=True)
    
    def __repr__(self):
        return f'<GrupoSanguineo {self.tipo_sangre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_tipo_sangre': self.id_tipo_sangre,
            'tipo_sangre': self.tipo_sangre
        }

