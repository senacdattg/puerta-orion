"""
Modelo para tipos de sexo.
"""

from ..database.database import db

class Sexo(db.Model):
    """Modelo para tipos de sexo."""
    __tablename__ = 'puerta_orion_sexo'
    
    id_sexo = db.Column(db.Integer, primary_key=True)
    sexo = db.Column(db.Boolean, nullable=False)
    
    # Relaciones
    personas = db.relationship('Persona', backref='sexo', lazy=True)
    
    def __repr__(self):
        return f'<Sexo {self.sexo}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_sexo': self.id_sexo,
            'sexo': self.sexo
        }


