"""
Modelo para usuarios del sistema.
"""

from ..database.database import db

class Usuario(db.Model):
    """Modelo para usuarios del sistema."""
    __tablename__ = 'puerta_orion_usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('puerta_orion_personas.id_persona'), nullable=False, unique=True)
    usuario = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    estado = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relaciones
    persona = db.relationship('Persona', backref='usuario', uselist=False)
    roles = db.relationship('Rol', secondary='puerta_orion_usuario_rol', back_populates='usuarios')
    roles_usuarios = db.relationship('RolUsuario', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.usuario}>'
    
    def is_active(self):
        """Verifica si el usuario está activo."""
        return self.estado
    
    def get_id(self):
        """Retorna el ID del usuario para Flask-Login."""
        return str(self.id_usuario)
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_usuario': self.id_usuario,
            'id_persona': self.id_persona,
            'usuario': self.usuario,
            'estado': self.estado
        }


