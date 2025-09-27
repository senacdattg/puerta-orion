"""
Módulo de modelo PersonasRol

Este módulo define la clase PersonasRol, que representa la relación muchos a muchos entre Personas y Roles en el sistema.
Incluye los campos principales de la relación, su relación con la persona y el rol.
"""

from ..base import db, BaseModel

class PersonasRol(BaseModel):
    """Relación muchos a muchos entre Personas y Roles"""
    __tablename__ = "PersonasRol"

    id_persona = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_personas.id_persona"),
        primary_key=True
    )
    id_rol = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_roles.id_rol"),
        primary_key=True
    )
    estado = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id_persona": self.id_persona,
            "id_rol": self.id_rol,
            "estado": self.estado
        }
