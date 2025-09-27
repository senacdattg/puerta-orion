"""
Módulo de modelo Diagnostico

Este módulo define la clase Diagnostico, que representa los diagnósticos médicos registrados en el sistema.
Incluye los campos principales del diagnóstico, su relación con el tipo de enfermedad y la relación con los diagnósticos asociados a personas.

Responsabilidad:
- Definir la estructura de la tabla 'puerta_orion_diagnostico' en la base de datos.
- Proveer métodos de serialización para el modelo Diagnostico.

Cumple con los principios SRP y KISS, manteniendo la lógica de datos separada y simple.
"""

from ..base import db, BaseModel

class Diagnostico(BaseModel):
    """Modelo de diagnósticos médicos"""
    __tablename__ = "diagnostico"

    id_diagnostico = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    id_tipo_enfermedad = db.Column(
        db.Integer,
        db.ForeignKey("TipoEnfermedad.id_tipo_enfermedad"),
        nullable=False
    )

    # Relaciones
    diagnosticos_persona = db.relationship("DiagnosticoPersona", backref="diagnostico", lazy=True)

    def to_dict(self):
        return {
            "id_diagnostico": self.id_diagnostico,
            "nombre": self.nombre,
            "id_tipo_enfermedad": self.id_tipo_enfermedad
        }