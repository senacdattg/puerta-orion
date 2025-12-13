"""
Modelo para tokens de recuperación de contraseña.
"""

from datetime import datetime, timedelta, timezone
from ..base import BaseModel
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class PasswordResetToken(BaseModel):
    """
    Modelo para tokens de recuperación de contraseña.

    Almacena los tokens generados para el proceso de restablecimiento
    de contraseña de usuarios, con su respectiva fecha de expiración.

    Attributes:
        id_token (int): Identificador único del token (clave primaria).
        id_usuario (int): Clave foránea a la tabla de usuarios.
        token (str): Token único de recuperación (UUID).
        expires_at (datetime): Fecha y hora de expiración del token.
    """
    __tablename__ = 'puerta_orion_password_reset_tokens'
    
    id_token = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('puerta_orion_usuario.id_usuario'), nullable=False)
    token = Column(String(100), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relaciones
    usuario = relationship('Usuario', back_populates='password_reset_tokens')
    
    def __repr__(self):
        """
        Representación de cadena de la instancia de PasswordResetToken.
        """
        return f'<PasswordResetToken {self.token[:8]}...>'
    
    def is_expired(self):
        """
        Verifica si el token ha expirado.

        Returns:
            bool: True si el token ha expirado, False en caso contrario.
        """
        return datetime.now(timezone.utc) > self.expires_at
    
    def to_dict(self):
        """
        Convierte el objeto a diccionario para serialización.

        Returns:
            dict: Un diccionario que contiene los atributos de la instancia.
        """
        return {
            'id_token': self.id_token,
            'id_usuario': self.id_usuario,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

