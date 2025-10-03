"""
Módulo de modelo Diagnostico

Este módulo define la clase Diagnostico, que representa los diagnósticos médicos registrados en el sistema.
Incluye los campos principales del diagnóstico, su relación con el tipo de enfermedad y la relación con los diagnósticos asociados a personas.

Responsabilidad:
- Definir la estructura de la tabla 'diagnostico' en la base de datos.
- Proveer métodos de serialización para el modelo Diagnostico.

Cumple con los principios SRP y KISS, manteniendo la lógica de datos separada y simple.
"""

from ..base import db, BaseModel

class Diagnostico(BaseModel):
    """
    Modelo para la tabla Diagnostico.

    Representa los diagnósticos médicos registrados en el sistema, asociando cada diagnóstico
    a un tipo de enfermedad específico. Permite la relación con los diagnósticos asignados
    a deportistas a través de la tabla DiagnosticoDeportista.

    Atributos:
        id_diagnostico (int): Identificador único del diagnóstico (clave primaria, autoincremental).
        nombre (str): Nombre o descripción del diagnóstico.
        id_tipo_enfermedad (int): Clave foránea al tipo de enfermedad (no nulo).
        tipo_enfermedad (TipoEnfermedad): Relación muchos a uno con el modelo TipoEnfermedad.
        diagnosticos_deportista (list): Relación uno a muchos con DiagnosticoDeportista.

    Métodos:
        __repr__(): Representación en cadena del diagnóstico.
        to_dict(): Serializa el objeto a un diccionario.
    """
    __tablename__ = "diagnostico"

    id_diagnostico = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False)
    id_tipo_enfermedad = db.Column(
        db.Integer,
        db.ForeignKey("tipoenfermedad.id_tipo_enfermedad"),
        nullable=False
    )

    # Relación con TipoEnfermedad (muchos a uno)
    tipo_enfermedad = db.relationship('TipoEnfermedad', backref='diagnosticos', lazy=True)

    # Relación con DiagnosticoDeportista (uno a muchos)
    diagnosticos_deportista = db.relationship('DiagnosticoDeportista', backref='diagnostico_obj', lazy=True)

    def __repr__(self):
        return f"<Diagnostico {self.id_diagnostico} - {self.nombre}>"

    def to_dict(self):
        return {
            "id_diagnostico": self.id_diagnostico,
            "nombre": self.nombre,
            "id_tipo_enfermedad": self.id_tipo_enfermedad
        }