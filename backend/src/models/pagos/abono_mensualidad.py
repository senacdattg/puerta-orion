"""
Modelo para abonos de mensualidad (histórico de pagos parciales o totales).
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship


class AbonoMensualidad(BaseModel):
    __tablename__ = 'puerta_orion_abonos_mensualidad'

    id_abono = Column(Integer, primary_key=True)
    id_mensualidad = Column(Integer, ForeignKey('puerta_orion_mensualidad.id_mensualidad'), nullable=False)
    monto = Column(Numeric(10, 2), nullable=False)
    fecha_abono = Column(Date, nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=True)

    mensualidad = relationship('Mensualidad', lazy=True)
    metodo_pago = relationship('MetodoPago', lazy=True)

    def to_dict(self):
        return {
            'id_abono': self.id_abono,
            'id_mensualidad': self.id_mensualidad,
            'monto': float(self.monto) if self.monto is not None else None,
            'fecha_abono': self.fecha_abono.isoformat() if self.fecha_abono else None,
            'id_metodo_pago': self.id_metodo_pago,
        }


