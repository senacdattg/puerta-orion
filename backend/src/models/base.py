from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime


db = SQLAlchemy()

class BaseModel(db.Model):
    """
    Clase base abstracta para todos los modelos de la aplicación.

    Proporciona campos comunes como 'created_at' y 'updated_at'
    para asegurar consistencia a través de todos los modelos.

    Attributes:
        created_at (datetime): Marca de tiempo de creación del registro.
        updated_at (datetime): Marca de tiempo de la última actualización del registro.
    """
    __abstract__ = True

    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def __repr__(self):
        """
        Representación de cadena de la instancia del modelo base.
        """
        # Se asume que cada modelo tendrá un atributo id_ (ej. id_persona, id_categoria)
        # para su clave primaria. Si no, se usará el __repr__ por defecto del objeto.
        id_attr = f"id_{self.__tablename__.replace('puerta_orion_', '')}"
        if hasattr(self, id_attr):
            return f"<{self.__class__.__name__}(id={getattr(self, id_attr)})>"
        return f"<{self.__class__.__name__}>"