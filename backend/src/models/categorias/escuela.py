"""
Modelo para la tabla Escuela.
"""

from ..base import db, BaseModel

class Escuela(BaseModel):
    """
    Modelo para la tabla Escuela.
    
    Catálogo de escuelas deportivas donde los deportistas pueden participar
    adicionalmente a su entrenamiento en Puerta Orion.
    Hereda de BaseModel para incluir campos de auditoría.
    
    Attributes:
        id_escuela (int): Identificador único de la escuela (clave primaria).
        nombre (str): Nombre de la escuela deportiva (único).
        informaciones_deportivas (list): Relación uno a muchos con InformacionDeportiva.
    """
    __tablename__ = "escuela"
    
    id_escuela = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)
    
    # Relaciones
    informaciones_deportivas = db.relationship('InformacionDeportiva', lazy=True)

    def __repr__(self):
        return f"<Escuela {self.nombre}>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario."""
        return {
            "id_escuela": self.id_escuela,
            "nombre": self.nombre
        }
