"""
Modelo para métodos de pago.
"""

from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship


class MetodoPago(BaseModel):
    """
    Modelo para métodos de pago.

    Representa los diferentes métodos que los usuarios pueden utilizar
    para realizar pagos dentro del sistema, como efectivo, tarjeta, etc.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_metodo_pago (int): Identificador único del método de pago (clave primaria).
        nombre_metodo (str): Nombre descriptivo del método de pago.
        estado (bool): Indica si el método de pago está activo (tinyint en MER se mapea a Boolean).
        cuotas (list): Relación uno a muchos con el modelo Cuota.
    """
    __tablename__ = 'puerta_orion_metodo_pago'
    
    id_metodo_pago = Column(Integer, primary_key=True)
    nombre_metodo = Column(String(50), nullable=False, unique=True)
    estado = Column(Boolean, default=True, nullable=False) # tinyint en MER se mapea a Boolean
    
    # Relaciones
    cuotas = relationship('Cuota', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de MetodoPago.

        Returns:
            str: Una cadena que representa la instancia de MetodoPago.
        """
        return f'<MetodoPago {self.nombre_metodo}>'
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de MetodoPago.
        """
        return {
            'id_metodo_pago': self.id_metodo_pago,
            'nombre_metodo': self.nombre_metodo,
            'estado': self.estado
        }
