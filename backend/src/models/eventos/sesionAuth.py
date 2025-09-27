"""
Módulo de modelo SesionAuth

Este módulo define la clase SesionAuth, que representa las sesiones de autenticación de usuarios en el sistema.
Incluye los campos principales de la sesión, su relación con el usuario, el token de sesión, la fecha de inicio, la fecha de expiración, el IP de origen y el agente de usuario.
"""

from ..base import db, BaseModel

class SesionAuth(BaseModel):
    """Sesiones de autenticación de usuarios"""
    __tablename__ = "SesionAuth"

    id_sesion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer,
        db.ForeignKey("puerta_orion_usuario.id_usuario"),
        nullable=False
    )
    token_sesion = db.Column(db.String(500), nullable=False, unique=True)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_expiracion = db.Column(db.DateTime, nullable=False)
    ip_origen = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    estado = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id_sesion": self.id_sesion,
            "id_usuario": self.id_usuario,
            "token_sesion": self.token_sesion,
            "fecha_inicio": str(self.fecha_inicio),
            "fecha_expiracion": str(self.fecha_expiracion),
            "ip_origen": self.ip_origen,
            "user_agent": self.user_agent,
            "estado": self.estado
        }
