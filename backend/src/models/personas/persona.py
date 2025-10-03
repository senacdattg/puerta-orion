"""
Modelo principal para personas del sistema.
Contiene toda la información personal de los deportistas y usuarios.
"""

from datetime import datetime, date
from ..base import BaseModel, db
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship


class Persona(BaseModel):
    """
    Modelo principal para personas del sistema.

    Representa la información básica y general de las personas en el sistema.
    Según el MER actualizado, esta tabla se ha simplificado y solo contiene
    datos personales básicos. Los datos específicos de deportistas (EPS, ciudad,
    grupo sanguíneo, etc.) ahora están en la tabla Deportista.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_persona (int): Identificador único de la persona (clave primaria).
        primer_nombre (str): Primer nombre de la persona.
        segundo_nombre (str): Segundo nombre de la persona (opcional).
        primer_apellido (str): Primer apellido de la persona.
        segundo_apellido (str): Segundo apellido de la persona (opcional).
        documento (int): Número de documento de identificación.
        correo_electronico (str): Correo electrónico de la persona.
        direccion (str): Dirección de residencia.
        telefono (int): Número de teléfono.
        password_hash (str): Hash de la contraseña (VARCHAR(255)).
        estado (bool): Estado activo/inactivo de la persona.
        fecha_registro (date): Fecha de registro en el sistema.
        id_tipo_documento (int): Clave foránea al tipo de documento.
        id_sexo (int): Clave foránea al sexo de la persona.
    """
    __tablename__ = 'puerta_orion_personas'
    
    # Clave primaria
    id_persona = Column(Integer, primary_key=True)
    
    # Campos básicos
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50), nullable=True)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=True)
    documento = Column(Integer, nullable=False)
    correo_electronico = Column(String(50), nullable=False)
    direccion = Column(String(50), nullable=False)
    telefono = Column(Integer, nullable=False)
    password_hash = Column(String(255), nullable=True)
    estado = Column(Boolean, default=True, nullable=False)
    fecha_registro = Column(Date, default=db.func.current_date(), nullable=False)
    
    # Claves foráneas (solo 2 según el MER actualizado)
    id_tipo_documento = Column(Integer, ForeignKey('puerta_orion_tipo_documento.id_documento'), nullable=False)
    id_sexo = Column(Integer, ForeignKey('puerta_orion_sexo.id_sexo'), nullable=False)
    
    # Relaciones con catálogos (solo 2 según el MER actualizado)
    tipo_documento = relationship('TipoDocumento', backref='personas', lazy=True)
    sexo = relationship('Sexo', backref='personas', lazy=True)
    
    # Relaciones con entidades principales (1:1 via backref)
    # deportista_obj, usuario_obj, acudiente_obj, informacion_deportiva_obj
    # se definen en sus respectivos modelos con uselist=False
    

    def __repr__(self):
        """
        Representación de cadena de la instancia de Persona.

        Returns:
            str: Una cadena que representa la instancia de Persona.
        """
        return f'<Persona {self.primer_nombre} {self.primer_apellido}>'
    
    @property
    def nombre_completo(self):
        """
        Retorna el nombre completo de la persona.

        Returns:
            str: El nombre completo de la persona.
        """
        nombres = f"{self.primer_nombre}"
        if self.segundo_nombre:
            nombres += f" {self.segundo_nombre}"
        
        apellidos = f"{self.primer_apellido}"
        if self.segundo_apellido:
            apellidos += f" {self.segundo_apellido}"
        
        return f"{nombres} {apellidos}"
    
    # Nota: Los campos fecha_nacimiento, imagen_perfil y métodos relacionados fueron removidos
    # según el MER actualizado. La fecha de nacimiento ahora está en la tabla Deportista.
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Persona.
        """
        return {
            'id_persona': self.id_persona,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'documento': self.documento,
            'correo_electronico': self.correo_electronico,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'password_hash': self.password_hash,
            'estado': self.estado,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'nombre_completo': self.nombre_completo,
            'id_tipo_documento': self.id_tipo_documento,
            'id_sexo': self.id_sexo
        }
