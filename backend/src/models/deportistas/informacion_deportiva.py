"""
Módulo de modelo InformacionDeportiva

Este módulo define la clase InformacionDeportiva, que representa la información deportiva de cada persona en el sistema.
Incluye los campos principales de la información deportiva, su relación con la escuela, el deporte y la persona.
"""

from ..base import db, BaseModel

class InformacionDeportiva(BaseModel):
    """Información deportiva de cada persona"""
    __tablename__ = "InformacionDeportiva"

    id_informacion_deportiva = db.Column(db.Integer, primary_key=True)
    practica_otro_deporte = db.Column(db.Boolean, nullable=False, default=False)
    participa_escuela = db.Column(db.Boolean, nullable=False, default=False)
    recomendacion_medica = db.Column(db.Boolean, nullable=False, default=False)
    descripcion_recomendacion = db.Column(db.String(500))

    id_escuela = db.Column(
        db.Integer,
        db.ForeignKey("Escuela.id_escuela"),
        nullable=True
    )
    id_deporte = db.Column(
        db.Integer,
        db.ForeignKey("deporte.id_deporte"),
        nullable=True
    )
    id_persona = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_personas.id_persona"),
        nullable=False
    )

    def to_dict(self):
        return {
            "id_informacion_deportiva": self.id_informacion_deportiva,
            "practica_otro_deporte": self.practica_otro_deporte,
            "participa_escuela": self.participa_escuela,
            "recomendacion_medica": self.recomendacion_medica,
            "descripcion_recomendacion": self.descripcion_recomendacion,
            "id_escuela": self.id_escuela,
            "id_deporte": self.id_deporte,
            "id_persona": self.id_persona
        }
