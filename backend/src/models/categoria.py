"""
Modelo para categorías de deportistas.
"""

from ..database.database import db

class Categoria(db.Model):
    """Modelo para categorías de deportistas."""
    __tablename__ = 'puerta_orion_categoria'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    codigo_categoria = db.Column(db.Integer, nullable=False, unique=True)
    nombre_categoria = db.Column(db.String(150), nullable=False)
    edad_minima = db.Column(db.Integer, nullable=False)
    edad_maxima = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    eventos = db.relationship('Evento', backref='categoria', lazy=True)
    mensualidades = db.relationship('Mensualidad', backref='categoria', lazy=True)
    
    def __repr__(self):
        return f'<Categoria {self.nombre_categoria}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_categoria': self.id_categoria,
            'codigo_categoria': self.codigo_categoria,
            'nombre_categoria': self.nombre_categoria,
            'edad_minima': self.edad_minima,
            'edad_maxima': self.edad_maxima,
            'estado': self.estado
        }


