"""
Modelo para roles específicos de usuario en sesiones.
"""

from ..database.database import db

class RolUsuario(db.Model):
    """Modelo para roles específicos de usuario en sesiones."""
    __tablename__ = 'puerta_orion_rol_usuario'
    
    id_rol_usuario = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('puerta_orion_usuario.id_usuario'), nullable=False)
    id_sesion = db.Column(db.Integer, db.ForeignKey('puerta_orion_sesiones.id_sesion'), nullable=False)
    
    def __repr__(self):
        return f'<RolUsuario {self.id_usuario}-{self.id_sesion}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario para serialización."""
        return {
            'id_rol_usuario': self.id_rol_usuario,
            'id_usuario': self.id_usuario,
            'id_sesion': self.id_sesion
        }


