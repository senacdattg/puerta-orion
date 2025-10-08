"""
Módulo de modelo PersonasRol

Este módulo define la clase PersonasRol, que representa la relación muchos a muchos entre Personas y Roles en el sistema.
Incluye los campos principales de la relación, su relación con la persona y el rol.

Responsabilidad:
- Definir la estructura de la tabla 'PersonasRol' en la base de datos.
- Proveer métodos de serialización para el modelo PersonasRol.

Cumple con los principios SRP y KISS, manteniendo la lógica de datos separada y simple.
"""

from ..base import db, BaseModel

class PersonasRol(BaseModel):
    """
    Relación muchos a muchos entre Personas y Roles.
    
    Tabla intermedia que asocia personas con roles del sistema,
    permitiendo asignar roles a personas que no son necesariamente usuarios.
    Incluye un campo de estado para activar/desactivar la asignación.
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_persona (int): Clave foránea a la persona (clave primaria compuesta).
        id_rol (int): Clave foránea al rol (clave primaria compuesta).
        estado (bool): Estado activo/inactivo de la asignación.
        persona (Persona): Relación muchos a uno con Persona.
        rol (Rol): Relación muchos a uno con Rol.
    """
    __tablename__ = "personasrol"

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
    
    # Relaciones (sin backrefs para evitar conflictos)
    persona = db.relationship('Persona', lazy=True)
    rol = db.relationship('Rol', lazy=True)

    def to_dict(self):
        return {
            "id_persona": self.id_persona,
            "id_rol": self.id_rol,
            "estado": self.estado
        }
