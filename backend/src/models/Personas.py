"""
Modelo principal para personas del sistema.
Contiene toda la información personal de los deportistas y usuarios.
"""

from datetime import datetime, date
from ..database.database import db

class Persona(db.Model):
    """Modelo principal para personas del sistema."""
    __tablename__ = 'puerta_orion_personas'
    
    id_persona = db.Column(db.Integer, primary_key=True)
    doc_identificacion = db.Column(db.String(150), nullable=False, unique=True)
    primer_nombre = db.Column(db.String(150), nullable=False)
    segundo_nombre = db.Column(db.String(150))
    primer_apellido = db.Column(db.String(150), nullable=False)
    segundo_apellido = db.Column(db.String(150))
    correo_electronico = db.Column(db.String(200), unique=True)
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    imagen_perfil = db.Column(db.String(500))  # URL de la imagen de perfil
    
    # Claves foráneas
    id_documento = db.Column(db.Integer, db.ForeignKey('puerta_orion_tipo_documento.id_documento'), nullable=False)
    id_ciudad = db.Column(db.Integer, db.ForeignKey('puerta_orion_ciudad_residencia.id_ciudad'), nullable=False)
    id_tipo_sangre = db.Column(db.Integer, db.ForeignKey('puerta_orion_grupo_sanguineo.id_tipo_sangre'), nullable=False)
    id_institucion = db.Column(db.Integer, db.ForeignKey('puerta_orion_institucion_registro.id_institucion'), nullable=False)
    id_eps = db.Column(db.Integer, db.ForeignKey('puerta_orion_eps.id_eps'), nullable=False)
    id_sexo = db.Column(db.Integer, db.ForeignKey('puerta_orion_sexo.id_sexo'), nullable=False)
    id_enfermedad = db.Column(db.Integer, db.ForeignKey('puerta_orion_enfermedad.id_enfermedad'))
    
    # Relaciones
    cuotas = db.relationship('Cuota', backref='persona', lazy=True)
    
    def __repr__(self):
        return f'<Persona {self.primer_nombre} {self.primer_apellido}>'
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo de la persona."""
        nombres = f"{self.primer_nombre}"
        if self.segundo_nombre:
            nombres += f" {self.segundo_nombre}"
        
        apellidos = f"{self.primer_apellido}"
        if self.segundo_apellido:
            apellidos += f" {self.segundo_apellido}"
        
        return f"{nombres} {apellidos}"
    
    @property
    def edad(self):
        """Calcula la edad actual de la persona."""
        if not self.fecha_nacimiento:
            return None
        
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
    @property
    def imagen_perfil_url(self):
        """Retorna la URL de la imagen de perfil o una imagen por defecto."""
        if self.imagen_perfil:
            return self.imagen_perfil
        return "/static/images/default-avatar.png"  # Imagen por defecto
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
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



