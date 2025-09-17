"""
Tabla de asociación para usuarios y roles (many-to-many).
"""

from ..database.database import db

# Tabla de asociación para usuarios y roles
usuario_rol = db.Table('puerta_orion_usuario_rol',
    db.Column('id_usuario', db.Integer, db.ForeignKey('puerta_orion_usuario.id_usuario'), primary_key=True),
    db.Column('id_rol', db.Integer, db.ForeignKey('puerta_orion_roles.id_rol'), primary_key=True)
)


