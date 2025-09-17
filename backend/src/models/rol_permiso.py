"""
Tabla de asociación para roles y permisos (many-to-many).
"""

from ..database.database import db

# Tabla de asociación para roles y permisos
rol_permiso = db.Table('puerta_orion_rol_permiso',
    db.Column('id_rol', db.Integer, db.ForeignKey('puerta_orion_roles.id_rol'), primary_key=True),
    db.Column('id_permiso', db.Integer, db.ForeignKey('puerta_orion_permisos.id_permiso'), primary_key=True)
)


