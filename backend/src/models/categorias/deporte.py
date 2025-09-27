"""
Modelo para los deportes en el sistema.
"""

from ..base import db, BaseModel

class Deporte(BaseModel):
    """
    Modelo que representa los deportes en el sistema.
    """
    __tablename__ = "deporte"

    id_deporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"<Deporte(id_deporte={self.id_deporte}, nombre='{self.nombre}')>"
