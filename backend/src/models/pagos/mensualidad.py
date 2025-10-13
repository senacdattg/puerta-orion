"""
Modelo para mensualidades del sistema.
Maneja las mensualidades por categorías de deportistas.
"""

from datetime import datetime, date
from decimal import Decimal
from ..base import BaseModel
from sqlalchemy import Column, Integer, Numeric, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Mensualidad(BaseModel):
    """
    Modelo para mensualidades del sistema.

    Maneja las mensualidades por categorías de deportistas, 
    registrando el monto, la fecha de pago, el estado y el método de pago.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_mensualidad (int): Identificador único de la mensualidad (clave primaria).
        id_metodo_pago (int): Clave foránea al método de pago utilizado.
        id_categoria (int): Clave foránea a la categoría de deportista asociada.
        estado (bool): Indica si la mensualidad está pagada o pendiente.
        fecha_pago (date): Fecha en que se realizó o se debe realizar la mensualidad.
        monto_pago (Decimal): Monto de la mensualidad con precisión decimal.
        metodo_pago (MetodoPago): Relación muchos a uno con el modelo MetodoPago.
        categoria (Categoria): Relación muchos a uno con el modelo Categoria.
    """
    __tablename__ = 'puerta_orion_mensualidad'
    
    id_mensualidad = Column(Integer, primary_key=True)
    id_metodo_pago = Column(Integer, ForeignKey('puerta_orion_metodo_pago.id_metodo_pago'), nullable=False)
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    fecha_pago = Column(Date, nullable=False)
    monto_pago = Column(Numeric(10, 2), nullable=False)
    
    # Relaciones
    metodo_pago = relationship('MetodoPago', lazy=True)
    categoria = relationship('Categoria', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Mensualidad.

        Returns:
            str: Una cadena que representa la instancia de Mensualidad.
        """
        return f'<Mensualidad {self.id_categoria} - {self.monto_pago}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Mensualidad.
        """
        return {
            'id_mensualidad': self.id_mensualidad,
            'id_metodo_pago': self.id_metodo_pago,
            'id_categoria': self.id_categoria,
            'estado': self.estado,
            'fecha_pago': self.fecha_pago.isoformat() if self.fecha_pago else None,
            'monto_pago': float(self.monto_pago) if self.monto_pago else None
        }

