"""
Modelo para roles del sistema.
"""

from ..database.database import db

class Rol(db.Model):
    """Modelo para roles del sistema."""
    __tablename__ = 'puerta_orion_roles'
    
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.String(250))
    
    # Relaciones many-to-many con permisos
    permisos = db.relationship('Permiso', secondary='puerta_orion_rol_permiso', back_populates='roles')
    
    # Relaciones many-to-many con usuarios
    usuarios = db.relationship('Usuario', secondary='puerta_orion_usuario_rol', back_populates='roles')
    
    def __repr__(self):
        return f'<Rol {self.nombre_rol}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_rol': self.id_rol,
            'nombre_rol': self.nombre_rol,
            'descripcion': self.descripcion
        }


