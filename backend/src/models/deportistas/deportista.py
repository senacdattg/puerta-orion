"""
Modelo para deportistas del sistema.
"""

from datetime import date
from ..base import BaseModel
from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship


class Deportista(BaseModel):
    """
    Modelo para deportistas del sistema.

    Representa a los deportistas registrados en el sistema, incluyendo
    información específica como peso, altura, fecha de ingreso y estado deportivo.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_deportista (int): Identificador único del deportista (clave primaria).
        id_persona (int): Clave foránea a la tabla de personas.
        id_categoria (int): Clave foránea a la categoría del deportista.
        peso (float): Peso del deportista en kilogramos.
        altura (float): Altura del deportista en metros.
        fecha_ingreso (date): Fecha de ingreso del deportista al sistema.
        estado_deportivo (int): Estado deportivo del deportista (tinyint en MER).
        persona (Persona): Relación uno a uno con el modelo Persona.
        categoria (Categoria): Relación muchos a uno con el modelo Categoria.
        deportistas_acudientes (list): Relación muchos a muchos con Acudiente a través de DeportistaAcudiente.
    """
    __tablename__ = 'puerta_orion_deportista'
    
    id_deportista = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False, unique=True)
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    estado_deportivo = Column(Integer, nullable=False)  # tinyint en MER se mapea a Integer
    
    # Relaciones
    persona = relationship('Persona', backref='deportista_obj', uselist=False)
    categoria = relationship('Categoria', backref='deportistas', lazy=True)
    deportistas_acudientes = relationship('DeportistaAcudiente', backref='deportista_obj', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Deportista.

        Returns:
            str: Una cadena que representa la instancia de Deportista.
        """
        return f'<Deportista {self.id_deportista}>'
    
    @property
    def imc(self):
        """
        Calcula el índice de masa corporal (IMC) del deportista.

        Returns:
            float or None: El IMC calculado o None si faltan datos.
        """
        if self.peso and self.altura and self.altura > 0:
            return round(self.peso / (self.altura ** 2), 2)
        return None
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Deportista.
        """
        return {
            'id_deportista': self.id_deportista,
            'id_persona': self.id_persona,
            'id_categoria': self.id_categoria,
            'peso': self.peso,
            'altura': self.altura,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'estado_deportivo': self.estado_deportivo,
            'imc': self.imc
        }
