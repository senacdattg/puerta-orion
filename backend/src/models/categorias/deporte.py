"""
Modelo para los deportes en el sistema.
"""

from ..base import db, BaseModel

class Deporte(BaseModel):
    """
    Modelo que representa los deportes en el sistema.
    
    Catálogo de deportes que los deportistas pueden practicar adicionalmente
    a su actividad principal en Puerta Orion.
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_deporte (int): Identificador único del deporte (clave primaria).
        nombre (str): Nombre del deporte (único).
        informaciones_deportivas (list): Relación uno a muchos con InformacionDeportiva.
    """
    __tablename__ = "deporte"

    id_deporte = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    
    # Relaciones
    informaciones_deportivas = db.relationship('InformacionDeportiva', backref='deporte_obj', lazy=True)

    def __repr__(self):
        return f"<Deporte(id_deporte={self.id_deporte}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_deporte': self.id_deporte,
            'nombre': self.nombre
        }
