"""
Módulo de modelo DiagnosticoDeportista

Este módulo define la clase DiagnosticoDeportista, que representa los diagnósticos médicos
asignados específicamente a deportistas en el sistema.

Responsabilidad:
- Definir la estructura de la tabla 'diagnostico_deportista' en la base de datos.
- Proveer métodos de serialización para el modelo DiagnosticoDeportista.

Cumple con los principios SRP y KISS, manteniendo la lógica de datos separada y simple.
"""

from ..base import db, BaseModel

class DiagnosticoDeportista(BaseModel):
    """
    Modelo para la tabla DiagnosticoDeportista.

    Representa los diagnósticos médicos asignados a un deportista en una fecha específica.

    Atributos:
        id_diagnostico_deportista (int): Identificador único del diagnóstico asignado al deportista (clave primaria).
        id_diagnostico (int): Clave foránea al diagnóstico médico.
        id_deportista (int): Clave foránea al deportista.
        fecha (date): Fecha en la que se asignó el diagnóstico al deportista.

    Relaciones:
        - diagnostico: Relación muchos a uno con Diagnostico.
        - deportista: Relación muchos a uno con Deportista.
    """
    __tablename__ = "diagnostico_deportista"

    id_diagnostico_deportista = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_diagnostico = db.Column(db.Integer, db.ForeignKey("diagnostico.id_diagnostico"), nullable=False)
    id_deportista = db.Column(db.Integer, db.ForeignKey("puerta_orion_deportista.id_deportista"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)

    # Relaciones
    diagnostico = db.relationship('Diagnostico', backref='diagnostico_deportista_items', lazy=True)
    deportista = db.relationship('Deportista', backref='diagnosticos_deportista', lazy=True)

    def __repr__(self):
        return f"<DiagnosticoDeportista {self.id_diagnostico_deportista} - Deportista {self.id_deportista} - Diagnostico {self.id_diagnostico}>"

    def to_dict(self):
        return {
            "id_diagnostico_deportista": self.id_diagnostico_deportista,
            "id_diagnostico": self.id_diagnostico,
            "id_deportista": self.id_deportista,
            "fecha": self.fecha.isoformat() if self.fecha else None
        }

