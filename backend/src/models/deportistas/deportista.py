"""
Modelo para deportistas del sistema.
"""

from datetime import date
from ..base import BaseModel
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, SmallInteger
from sqlalchemy.orm import relationship


class Deportista(BaseModel):
    """
    Modelo para deportistas del sistema.

    Representa a los deportistas registrados en el sistema, incluyendo
    información específica como peso, altura, datos médicos y ubicación.
    Según el MER, el deportista tiene sus propias FKs a catálogos (EPS, ciudad, etc.)
    además de la relación con Persona.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_deportista (int): Identificador único del deportista (clave primaria).
        peso (float): Peso del deportista en kilogramos (opcional).
        altura (float): Altura del deportista en metros (opcional).
        fecha_ingreso (date): Fecha de ingreso del deportista al sistema.
        id_categoria (int): Clave foránea a la categoría del deportista.
        id_persona (int): Clave foránea a la tabla de personas.
        id_tipo_sanguineo (int): Clave foránea al grupo sanguíneo.
        id_diagnosco_deportista (int): Clave foránea al diagnóstico del deportista.
        id_ciudad_recidencia (int): Clave foránea a la ciudad de residencia.
        id_mensualidad (int): Clave foránea a la mensualidad.
        id_informacion_deportiva (int): Clave foránea a información deportiva adicional.
        id_eps (int): Clave foránea a la EPS.
        fecha_nacimiento (int): Fecha de nacimiento (tinyint en MER).
    """
    __tablename__ = 'puerta_orion_deportista'
    
    # Clave primaria
    id_deportista = Column(Integer, primary_key=True)
    
    # Campos básicos del deportista
    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    fecha_nacimiento = Column(SmallInteger, nullable=True)  # tinyint en MER
    
    # Claves foráneas según el MER
    id_categoria = Column(Integer, ForeignKey('puerta_orion_categoria.id_categoria'), nullable=False)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False, unique=True)
    id_tipo_sanguineo = Column(Integer, ForeignKey('puerta_orion_grupo_sanguineo.id_tipo_sangre'), nullable=True)
    # id_diagnostico_deportista = Column(Integer, ForeignKey('diagnostico.id_diagnostico'), nullable=True)  # Relación eliminada
    id_ciudad_recidencia = Column(Integer, ForeignKey('puerta_orion_ciudad_residencia.id_ciudad'), nullable=True)
    id_mensualidad = Column(Integer, ForeignKey('puerta_orion_mensualidad.id_mensualidad'), nullable=True)
    id_informacion_deportiva = Column(Integer, ForeignKey('informaciondeportiva.id_informacion_deportiva'), nullable=True)
    id_eps = Column(Integer, ForeignKey('puerta_orion_eps.id_eps'), nullable=True)
    
    # Relaciones
    persona = relationship('Persona', uselist=False)
    categoria = relationship('Categoria', lazy=True)
    tipo_sanguineo = relationship('GrupoSanguineo', foreign_keys=[id_tipo_sanguineo], lazy=True)
    # diagnostico = relationship('Diagnostico', foreign_keys=[id_diagnostico_deportista], backref='deportistas_diagnostico', lazy=True)  # Relación eliminada
    ciudad_residencia = relationship('CiudadResidencia', foreign_keys=[id_ciudad_recidencia], lazy=True)
    mensualidad = relationship('Mensualidad', foreign_keys=[id_mensualidad], lazy=True)
    informacion_deportiva = relationship('InformacionDeportiva', foreign_keys=[id_informacion_deportiva], lazy=True)
    eps = relationship('EPS', foreign_keys=[id_eps], lazy=True)
    
    # Relación muchos a muchos con acudientes a través de DeportistaAcudiente
    deportistas_acudientes = relationship('DeportistaAcudiente', lazy=True)
    
    # Relación uno a muchos con diagnósticos históricos de deportistas
    # La relación diagnosticos_deportista se define vía backref desde DiagnosticoDeportista
    
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
            'id_tipo_sanguineo': self.id_tipo_sanguineo,
            'id_diagnostico_deportista': self.id_diagnostico_deportista,
            'id_ciudad_recidencia': self.id_ciudad_recidencia,
            'id_mensualidad': self.id_mensualidad,
            'id_informacion_deportiva': self.id_informacion_deportiva,
            'id_eps': self.id_eps,
            'peso': self.peso,
            'altura': self.altura,
            'fecha_ingreso': self.fecha_ingreso.isoformat() if self.fecha_ingreso else None,
            'fecha_nacimiento': self.fecha_nacimiento,
            'imc': self.imc
        }
