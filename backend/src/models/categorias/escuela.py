"""
Modelo para la tabla Escuela.
"""

from ..base import db, BaseModel

class Escuela(BaseModel):
    """Modelo para la tabla Escuela."""
    __tablename__ = "Escuela"
    
    id_escuela = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(150), nullable=False, unique=True)

    def __repr__(self):
        return f"<Escuela {self.nombre}>"
    
    def to_dict(self):
        """Convierte el objeto a diccionario."""
        return {
            "id_escuela": self.id_escuela,
            "nombre": self.nombre
        }
