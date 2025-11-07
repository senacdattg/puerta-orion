"""
Modelo para mensualidades del sistema.
Maneja las mensualidades por persona.
"""

from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel
from sqlalchemy import Column, Integer, Numeric, Date, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class Mensualidad(BaseModel):
    """
    Modelo para mensualidades del sistema.

    Registra por cada persona el monto, la fecha de pago, el estado y el método de pago.
    """
    __tablename__ = 'puerta_orion_mensualidad'

    __table_args__ = (
        UniqueConstraint('id_persona', 'fecha_vencimiento', name='uq_persona_mes'),
    )
    
    id_mensualidad = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=False)
    estado = Column(Boolean, default=False, nullable=False)
    fecha_pago = Column(Date, nullable=True)
    monto_pago = Column(Numeric(10, 2), nullable=False)
    saldo_pendiente = Column(Numeric(10, 2), nullable=False, default=0)
    fecha_vencimiento = Column(Date, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    persona = relationship('Persona', lazy=True)
    metodo_pago = relationship('MetodoPago', lazy=True)
    
    def __repr__(self):
        return f'<Mensualidad persona={self.id_persona} monto={self.monto_pago} estado={"pagado" if self.estado else "pendiente"}>'
    
    def to_dict(self):
        return {
            'id_mensualidad': self.id_mensualidad,
            'id_persona': self.id_persona,
            'id_metodo_pago': self.id_metodo_pago,
            'estado': self.estado,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'monto_pago': float(self.monto_pago) if self.monto_pago is not None else None,
            'saldo_pendiente': float(self.saldo_pendiente) if self.saldo_pendiente is not None else None,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat() if self.fecha_vencimiento else None,
            'activo': self.activo,
        }

