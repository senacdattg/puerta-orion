"""
Modelo para usuarios del sistema.
"""


from ..base import BaseModel
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Usuario(BaseModel):
    """
    Modelo para usuarios del sistema.

    Representa a los usuarios que acceden a la aplicación, vinculándolos
    con sus datos personales (Modelo Persona) y sus roles/permisos.
    Hereda de BaseModel para incluir campos de auditoría.

    Attributes:
        id_usuario (int): Identificador único del usuario (clave primaria).
        id_persona (int): Clave foránea a la tabla de personas (única).
        usuario (str): Nombre de usuario (único).
        password (str): Hash de la contraseña del usuario.
        estado (bool): Estado activo/inactivo del usuario.
        persona (Persona): Relación uno a uno con el modelo Persona.
        roles (list): Relación muchos a muchos con el modelo Rol a través de UsuarioRol.
        roles_usuarios (list): Relación uno a muchos con el modelo RolUsuario.
    """
    __tablename__ = 'puerta_orion_usuario'
    
    id_usuario = Column(Integer, primary_key=True)
    id_persona = Column(Integer, ForeignKey('puerta_orion_personas.id_persona'), nullable=False, unique=True)
    usuario = Column(String(200), nullable=False, unique=True)
    password = Column(String(200), nullable=False)
    estado = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    persona = relationship('Persona', uselist=False)
    roles = relationship('Rol', secondary='puerta_orion_usuario_rol', back_populates='usuarios')
    # Nota: RolUsuario es una tabla de asociación para la relación muchos a muchos entre Usuario y Rol.
    # Si RolUsuario es un modelo aparte para añadir atributos a la relación, entonces esta definición está bien.
    # Si es solo una tabla de unión simple, se puede simplificar la relación 'roles'.
    # Para mantener la flexibilidad, mantendremos roles_usuarios.
    roles_usuarios = relationship('UsuarioRol', lazy=True)
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de Usuario.

        Returns:
            str: Una cadena que representa la instancia de Usuario.
        """
        return f'<Usuario {self.usuario}>'
    
    def is_active(self):
        """
        Verifica si el usuario está activo.

        Returns:
            bool: True si el usuario está activo, False en caso contrario.
        """
        return self.estado
    
    def get_id(self):
        """
        Retorna el ID del usuario para Flask-Login.

        Returns:
            str: El ID del usuario en formato string.
        """
        return str(self.id_usuario)
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia de Usuario.
        """
        return {
            'id_usuario': self.id_usuario,
            'id_persona': self.id_persona,
            'usuario': self.usuario,
            'estado': self.estado
        }
