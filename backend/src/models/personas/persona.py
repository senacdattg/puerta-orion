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

    Contiene toda la información personal de los deportistas y usuarios, 
    y define las relaciones con otras entidades clave del sistema como 
    documentos, ciudades de residencia, grupos sanguíneos, instituciones, 
    EPS, sexo y enfermedades. Hereda de BaseModel para incluir campos 
    de auditoría como `created_at` y `updated_at`.

    Attributes:
        id_persona (int): Identificador único de la persona (clave primaria).
        primer_nombre (str): Primer nombre de la persona.
        segundo_nombre (str): Segundo nombre de la persona (opcional).
        primer_apellido (str): Primer apellido de la persona.
        segundo_apellido (str): Segundo apellido de la persona (opcional).
        documento (int): Número de documento de identificación de la persona.
        correo_electronico (str): Correo electrónico de la persona.
        direccion (str): Dirección de residencia de la persona.
        telefono (int): Número de teléfono de la persona.
        password_hash (str): Hash de la contraseña para usuarios del sistema.
        estado (bool): Estado activo/inactivo de la persona.
        fecha_nacimiento (date): Fecha de nacimiento de la persona.
        fecha_registro (date): Fecha de registro en el sistema.
        id_mensualidad (int): Clave foránea a la mensualidad.
        id_sexo (int): Clave foránea al sexo de la persona.
        id_ciudad (int): Clave foránea a la ciudad de residencia de la persona.
        id_tipo_documento (int): Clave foránea al tipo de documento de la persona.
        id_eps (int): Clave foránea a la EPS de la persona.
        id_institucion (int): Clave foránea a la institución de registro de la persona.
        id_tipo_sangre (int): Clave foránea al grupo sanguíneo de la persona.
    """
    __tablename__ = 'puerta_orion_personas'
    
    # Clave primaria
    id_persona = Column(Integer, primary_key=True)
    
    # Campos básicos
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50))
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50))
    documento = Column(Integer, nullable=False)
    correo_electronico = Column(String(50), nullable=False)
    direccion = Column(String(150), nullable=False)
    telefono = Column(Integer, nullable=False)
    password_hash = Column(String(255))
    estado = Column(Boolean, default=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    fecha_registro = Column(Date, default=db.func.current_date(), nullable=False)
    
    # Claves foráneas
    id_mensualidad = Column(Integer, ForeignKey('puerta_orion_mensualidad.id_mensualidad'))
    id_sexo = Column(Integer, ForeignKey('puerta_orion_sexo.id_sexo'), nullable=False)
    id_ciudad = Column(Integer, ForeignKey('puerta_orion_ciudad_residencia.id_ciudad'), nullable=False)
    id_tipo_documento = Column(Integer, ForeignKey('puerta_orion_tipo_documento.id_documento'), nullable=False)
    id_eps = Column(Integer, ForeignKey('puerta_orion_eps.id_eps'), nullable=False)
    id_institucion = Column(Integer, ForeignKey('puerta_orion_institucion_registro.id_institucion'), nullable=False)
    id_tipo_sangre = Column(Integer, ForeignKey('puerta_orion_grupo_sanguineo.id_tipo_sangre'), nullable=False)
    
    # Relaciones
    mensualidad = relationship('Mensualidad', backref='personas')
    sexo = relationship('Sexo', backref='personas')
    ciudad_residencia = relationship('CiudadResidencia', backref='personas')
    tipo_documento = relationship('TipoDocumento', backref='personas')
    eps = relationship('EPS', backref='personas')
    institucion_registro = relationship('InstitucionRegistro', backref='personas')
    tipo_sangre = relationship('GrupoSanguineo', backref='personas')

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
    
    @property
    def edad(self):
        """
        Calcula la edad actual de la persona.

        Returns:
            int or None: La edad actual de la persona o None si la fecha de nacimiento no está definida.
        """
        if not self.fecha_nacimiento:
            return None
        
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def imagen_perfil_url(self):
        """
        Retorna la URL de la imagen de perfil o una imagen por defecto.

        Returns:
            str: La URL de la imagen de perfil o la URL de una imagen por defecto.
        """
        if self.imagen_perfil:
            return self.imagen_perfil
        return "/static/images/default-avatar.png"  # Imagen por defecto
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Persona.
        """
        return {
            'id_persona': self.id_persona,
            'doc_identificacion': self.doc_identificacion,
            'primer_nombre': self.primer_nombre,
            'segundo_nombre': self.segundo_nombre,
            'primer_apellido': self.primer_apellido,
            'segundo_apellido': self.segundo_apellido,
            'correo_electronico': self.correo_electronico,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'imagen_perfil_url': self.imagen_perfil_url,
            'edad': self.edad,
            'nombre_completo': self.nombre_completo,
            'id_documento': self.id_documento,
            'id_ciudad': self.id_ciudad,
            'id_tipo_sangre': self.id_tipo_sangre,
            'id_institucion': self.id_institucion,
            'id_eps': self.id_eps,
            'id_sexo': self.id_sexo,
            'id_enfermedad': self.id_enfermedad
        }
