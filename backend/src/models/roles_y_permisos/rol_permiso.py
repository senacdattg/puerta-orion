"""
Tabla de asociación para roles y permisos (many-to-many).
"""

from sqlalchemy import Column, Integer, ForeignKey
from ..base import db, BaseModel

class RolPermiso(BaseModel):
    """
    Modelo de asociación para la relación muchos a muchos entre roles y permisos.
    """
    __tablename__ = 'puerta_orion_rol_permiso'

    id_rol = Column(Integer, ForeignKey('puerta_orion_roles.id_rol'), primary_key=True)
    id_permiso = Column(Integer, ForeignKey('puerta_orion_permisos.id_permiso'), primary_key=True)

    def __repr__(self):
        return f'<RolPermiso rol={self.id_rol} permiso={self.id_permiso}>'

    def to_dict(self):
        return {
            'id_rol': self.id_rol,
            'id_permiso': self.id_permiso
        }


