"""
Modelo para mensualidades del sistema.
Maneja las mensualidades por categorías de deportistas.
"""

from datetime import datetime, date
from decimal import Decimal
from ..database.database import db

class Mensualidad(db.Model):
    """Modelo para mensualidades del sistema."""
    __tablename__ = 'puerta_orion_mensualidad'
    
    id_mensualidad = db.Column(db.Integer, primary_key=True)
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=False)
    id_categoria = db.Column(db.Integer, db.ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    fecha_pago = db.Column(db.Date, nullable=False)
    monto_pago = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<Mensualidad {self.id_categoria} - {self.monto_pago}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_mensualidad': self.id_mensualidad,
            'id_metodo_pago': self.id_metodo_pago,
            'id_categoria': self.id_categoria,
            'estado': self.estado,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'monto_pago': float(self.monto_pago) if self.monto_pago else None
        }

