"""
Modelo para cuotas de pago de deportistas.
Maneja las cuotas individuales que pagan los deportistas.
"""

from datetime import datetime, date
from decimal import Decimal
from ..database.database import db

class Cuota(db.Model):
    """Modelo para cuotas de pago de deportistas."""
    __tablename__ = 'puerta_orion_cuota'
    
    id_cuota = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('puerta_orion_personas.id_persona'), nullable=False)
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=False)
    monto_cuota = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_cuota = db.Column(db.Date, nullable=False)
    descuento = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<Cuota {self.id_persona} - {self.monto_cuota}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_cuota': self.id_cuota,
            'id_persona': self.id_persona,
            'id_metodo_pago': self.id_metodo_pago,
            'monto_cuota': float(self.monto_cuota) if self.monto_cuota else None,
            'fecha_cuota': self.fecha_cuota.isoformat() if self.fecha_cuota else None,
            'descuento': self.descuento
        }

