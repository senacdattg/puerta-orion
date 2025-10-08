"""
Módulo de modelo InformacionDeportiva

Este módulo define la clase InformacionDeportiva, que representa la información deportiva de cada persona en el sistema.
Incluye los campos principales de la información deportiva, su relación con la escuela, el deporte y la persona.

Responsabilidad:
- Definir la estructura de la tabla 'InformacionDeportiva' en la base de datos.
- Proveer métodos de serialización para el modelo InformacionDeportiva.

Cumple con los principios SRP y KISS, manteniendo la lógica de datos separada y simple.
"""

from ..base import db, BaseModel

class InformacionDeportiva(BaseModel):
    """
    Información deportiva de cada persona.
    
    Registra información adicional sobre la práctica deportiva de los deportistas,
    incluyendo si practican otros deportes, participan en escuelas deportivas,
    y si tienen recomendaciones médicas especiales.
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_informacion_deportiva (int): Identificador único (clave primaria).
        practica_otro_deporte (bool): Indica si practica otro deporte.
        participa_escuela (bool): Indica si participa en una escuela deportiva.
        recomendacion_medica (bool): Indica si tiene recomendaciones médicas.
        descripcion_recomendacion (str): Descripción de la recomendación médica (opcional).
        id_escuela (int): Clave foránea a la escuela deportiva (opcional).
        id_deporte (int): Clave foránea al deporte que practica (opcional).
        id_institucion_registro (int): Clave foránea a la institución de registro (opcional).
        id_persona (int): Clave foránea a la persona asociada.
        persona (Persona): Relación muchos a uno con el modelo Persona.
        escuela (Escuela): Relación muchos a uno con el modelo Escuela.
        deporte (Deporte): Relación muchos a uno con el modelo Deporte.
        institucion_registro (InstitucionRegistro): Relación muchos a uno con InstitucionRegistro.
    """
    __tablename__ = "informaciondeportiva"

    id_informacion_deportiva = db.Column(db.Integer, primary_key=True)
    practica_otro_deporte = db.Column(db.Boolean, nullable=False, default=False)
    participa_escuela = db.Column(db.Boolean, nullable=False, default=False)
    recomendacion_medica = db.Column(db.Boolean, nullable=False, default=False)
    descripcion_recomendacion = db.Column(db.String(500))

    id_escuela = db.Column(
        db.Integer,
        db.ForeignKey("escuela.id_escuela"),
        nullable=True
    )
    id_deporte = db.Column(
        db.Integer,
        db.ForeignKey("deporte.id_deporte"),
        nullable=True
    )
    id_institucion_registro = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_institucion_registro.id_institucion"),
        nullable=True
    )
    id_persona = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_personas.id_persona"),
        nullable=False
    )
    
    # Relaciones (sin backrefs para evitar conflictos)
    persona = db.relationship('Persona', uselist=False)
    escuela = db.relationship('Escuela', lazy=True)
    deporte = db.relationship('Deporte', lazy=True)
    institucion_registro = db.relationship('InstitucionRegistro', foreign_keys=[id_institucion_registro], lazy=True)

    def to_dict(self):
        return {
            "id_informacion_deportiva": self.id_informacion_deportiva,
            "practica_otro_deporte": self.practica_otro_deporte,
            "participa_escuela": self.participa_escuela,
            "recomendacion_medica": self.recomendacion_medica,
            "descripcion_recomendacion": self.descripcion_recomendacion,
            "id_escuela": self.id_escuela,
            "id_deporte": self.id_deporte,
            "id_institucion_registro": self.id_institucion_registro,
            "id_persona": self.id_persona
        }
