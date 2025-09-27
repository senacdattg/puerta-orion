"""
Modelo para cuotas de pago de deportistas.
Maneja las cuotas individuales que pagan los deportistas.
"""

from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel
from sqlalchemy import Column, Integer, Numeric, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Cuota(BaseModel):
    """
    Modelo para cuotas de pago de deportistas.

    Maneja las cuotas individuales que pagan los deportistas, 
    registrando el monto, la fecha, el método de pago y si aplica un descuento.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_cuota (int): Identificador único de la cuota (clave primaria).
        id_persona (int): Clave foránea a la persona asociada a la cuota.
        id_metodo_pago (int): Clave foránea al método de pago utilizado.
        monto_cuota (Decimal): Monto de la cuota con precisión decimal.
        fecha_cuota (date): Fecha en que se realizó o se debe realizar la cuota.
        descuento (bool): Indica si se aplicó un descuento a la cuota.
        persona (Persona): Relación muchos a uno con el modelo Persona.
        metodo_pago (MetodoPago): Relación muchos a uno con el modelo MetodoPago.
    """
    __tablename__ = 'puerta_orion_cuota'
    
    id_cuota = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False)
    id_metodo_pago = Column(Integer, ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=False)
    monto_cuota = Column(Numeric(10, 2), nullable=False)
    fecha_cuota = Column(Date, nullable=False)
    descuento = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Cuota.

        Returns:
            str: Una cadena que representa la instancia de Cuota.
        """
        return f'<Cuota {self.id_persona} - {self.monto_cuota}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Cuota.
        """
        return {
            'id_cuota': self.id_cuota,
            'id_persona': self.id_persona,
            'id_metodo_pago': self.id_metodo_pago,
            'monto_cuota': float(self.monto_cuota) if self.monto_cuota else None,
            'fecha_cuota': self.fecha_cuota.isoformat() if self.fecha_cuota else None,
            'descuento': self.descuento
        }

