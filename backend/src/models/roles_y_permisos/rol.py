"""
Modelo para roles del sistema.
"""

from ..base import db, BaseModel

class Rol(BaseModel):
    """Modelo para roles del sistema."""
    __tablename__ = 'puerta_orion_roles'
    
    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(150), nullable=False, unique=True)
    descripcion = db.Column(db.String(250))
    
    # Relaciones many-to-many con permisos
    permisos = db.relationship('Permiso', secondary='puerta_orion_rol_permiso', back_populates='roles')
    
    # Relaciones many-to-many con usuarios
    usuarios = db.relationship('Usuario', secondary='puerta_orion_usuario_rol', back_populates='roles', overlaps="roles_usuarios")
    usuarios_activos = db.relationship(
        'Usuario',
        back_populates='rol_activo',
        lazy='dynamic',
        foreign_keys='Usuario.rol_activo_id'
    )
    
    def __repr__(self):
        return f'<Rol {self.nombre_rol}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_rol': self.id_rol,
            'nombre_rol': self.nombre_rol,
            'descripcion': self.descripcion
        }



