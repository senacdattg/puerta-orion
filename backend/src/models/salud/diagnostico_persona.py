"""
Módulo de modelo DiagnosticoPersona

Este módulo define la clase DiagnosticoPersona, que representa los diagnósticos asignados a personas en el sistema.
Incluye los campos principales del diagnóstico, su relación con la persona y la fecha de asignación.
"""

from ..base import db, BaseModel

class DiagnosticoPersona(BaseModel):
    """Diagnósticos asignados a personas"""
    __tablename__ = "diagnostico_persona"

    id_diagnostico_persona = db.Column(db.Integer, primary_key=True)
    diagnostico = db.Column(
        db.Integer,
        db.ForeignKey("diagnostico.id_diagnostico"),
        nullable=False
    )
    fecha = db.Column(db.Date, nullable=False)
    id_persona = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_personas.id_persona"),
        nullable=False
    )

    def to_dict(self):
        return {
            "id_diagnostico_persona": self.id_diagnostico_persona,
            "diagnostico": self.diagnostico,
            "fecha": str(self.fecha),
            "id_persona": self.id_persona
        }