"""
Modelo para transacciones de Mercado Pago.
Maneja las transacciones procesadas a través de Mercado Pago.
"""

from datetime import datetime
from decimal import Decimal
from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship


class TransaccionMercadoPago(BaseModel):
    """
    Modelo para transacciones de Mercado Pago.

    Maneja las transacciones procesadas a través de Mercado Pago,
    almacenando información del pago, estado y datos relacionados.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_transaccion (int): Identificador único de la transacción (clave primaria).
        id_pago_mercadopago (str): ID único del pago en Mercado Pago.
        preference_id (str): ID de la preferencia creada en Mercado Pago.
        estado (str): Estado del pago (pending, approved, rejected, etc.).
        monto (Decimal): Monto de la transacción con precisión decimal.
        moneda (str): Moneda de la transacción (por defecto 'COP').
        fecha_creacion (datetime): Fecha de creación de la transacción.
        fecha_actualizacion (datetime): Fecha de última actualización.
        datos_pago (JSON): Datos completos de la respuesta de Mercado Pago.
        id_cuota (int): Clave foránea a la cuota asociada (opcional).
        id_mensualidad (int): Clave foránea a la mensualidad asociada (opcional).
        cuota (Cuota): Relación muchos a uno con el modelo Cuota.
        mensualidad (Mensualidad): Relación muchos a uno con el modelo Mensualidad.
    """
    __tablename__ = 'puerta_orion_transaccion_mercadopago'
    
    id_transaccion = Column(Integer, primary_key=True)
    id_pago_mercadopago = Column(String(255), unique=True, nullable=False)
    preference_id = Column(String(255), nullable=True)
    estado = Column(String(50), nullable=False, default='pending')
    monto = Column(Numeric(10, 2), nullable=False)
    moneda = Column(String(3), nullable=False, default='COP')
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    datos_pago = Column(JSON, nullable=True)
    
    # Relaciones con tus modelos existentes (opcionales)
    id_cuota = Column(Integer, ForeignKey('puerta_orion_cuota.id_cuota'), nullable=True)
    id_mensualidad = Column(Integer, ForeignKey('puerta_orion_mensualidad.id_mensualidad'), nullable=True)
    
    # Relaciones
    cuota = relationship('Cuota', backref='transacciones_mercadopago', lazy=True)
    mensualidad = relationship('Mensualidad', backref='transacciones_mercadopago', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de TransaccionMercadoPago.

        Returns:
            str: Una cadena que representa la instancia de TransaccionMercadoPago.
        """
        return f'<TransaccionMercadoPago {self.id_pago_mercadopago} - {self.estado}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de TransaccionMercadoPago.
        """
        return {
            'id_transaccion': self.id_transaccion,
            'id_pago_mercadopago': self.id_pago_mercadopago,
            'preference_id': self.preference_id,
            'estado': self.estado,
            'monto': float(self.monto) if self.monto else None,
            'moneda': self.moneda,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'datos_pago': self.datos_pago,
            'id_cuota': self.id_cuota,
            'id_mensualidad': self.id_mensualidad
        }
    
    @classmethod
    def crear_transaccion(cls, id_pago_mp, preference_id, monto, estado='pending', datos_pago=None, id_cuota=None, id_mensualidad=None):
        """
        Método de clase para crear una nueva transacción.

        Args:
            id_pago_mp (str): ID del pago en Mercado Pago.
            preference_id (str): ID de la preferencia.
            monto (Decimal): Monto de la transacción.
            estado (str): Estado inicial del pago.
            datos_pago (dict): Datos adicionales del pago.
            id_cuota (int): ID de la cuota asociada (opcional).
            id_mensualidad (int): ID de la mensualidad asociada (opcional).

        Returns:
            TransaccionMercadoPago: Nueva instancia de transacción.
        """
        return cls(
            id_pago_mercadopago=id_pago_mp,
            preference_id=preference_id,
            monto=monto,
            estado=estado,
            datos_pago=datos_pago,
            id_cuota=id_cuota,
            id_mensualidad=id_mensualidad
        )
    
    def actualizar_estado(self, nuevo_estado, datos_pago=None):
        """
        Actualiza el estado de la transacción.

        Args:
            nuevo_estado (str): Nuevo estado del pago.
            datos_pago (dict): Datos actualizados del pago.
        """
        self.estado = nuevo_estado
        if datos_pago:
            self.datos_pago = datos_pago
        self.fecha_actualizacion = datetime.utcnow()