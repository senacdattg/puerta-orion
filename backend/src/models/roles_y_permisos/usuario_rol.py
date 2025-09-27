"""
Modelo de asociación para usuarios y roles (many-to-many).
"""

from ..base import db, BaseModel

class UsuarioRol(BaseModel):
    """
    Modelo de asociación para la relación muchos a muchos entre usuarios y roles.
    """
    __tablename__ = 'puerta_orion_usuario_rol'

    id_usuario = db.Column(db.Integer, db.ForeignKey('puerta_orion_usuario.id_usuario'), primary_key=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('puerta_orion_roles.id_rol'), primary_key=True)

    def __repr__(self):
        return f'<UsuarioRol usuario={self.id_usuario} rol={self.id_rol}>'

    def to_dict(self):
        return {
            'id_usuario': self.id_usuario,
            'id_rol': self.id_rol
        }


