"""
Modelo para permisos del sistema.
"""

from ..database.database import db

class Permiso(db.Model):
    """Modelo para permisos del sistema."""
    __tablename__ = 'puerta_orion_permisos'
    
    id_permiso = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.String(250))
    
    # Relaciones many-to-many con roles
    roles = db.relationship('Rol', secondary='puerta_orion_rol_permiso', back_populates='permisos')
    
    def __repr__(self):
        return f'<Permiso {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_permiso': self.id_permiso,
            'nombre': self.nombre,
            'descripcion': self.descripcion
        }


