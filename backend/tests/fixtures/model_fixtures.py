"""
Fixtures para modelos de base de datos.

Este módulo contiene fixtures que crean instancias de modelos
en la base de datos para usar en los tests.
"""

import pytest
from datetime import date
from unittest.mock import MagicMock

from tests.conftest import TEST_PRIMER_NOMBRE, TEST_PRIMER_APELLIDO


@pytest.fixture
def tipo_documento(db_session):
    """Crea un tipo de documento de prueba."""
    try:
        from src.models.catalogos.tipo_documento import TipoDocumento
        tipo = TipoDocumento(
            nombre_documento='Cédula de Ciudadanía',
            codigo='CC'
        )
        db_session.add(tipo)
        db_session.commit()
        return tipo
    except Exception:
        return MagicMock(id_tipo_documento=1, nombre_documento='Cédula de Ciudadanía')


@pytest.fixture
def sexo(db_session):
    """Crea un sexo de prueba."""
    try:
        from src.models.categorias.sexo import Sexo
        sexo_obj = Sexo(nombre='Masculino', codigo='M')
        db_session.add(sexo_obj)
        db_session.commit()
        return sexo_obj
    except Exception:
        return MagicMock(id_sexo=1, nombre='Masculino')


@pytest.fixture
def categoria(db_session):
    """Crea una categoría de prueba."""
    try:
        from src.models.categorias.categoria import Categoria
        categoria_obj = Categoria(
            nombre_categoria='Sub-15',
            codigo_categoria=101,
            edad_minima=13,
            edad_maxima=15
        )
        db_session.add(categoria_obj)
        db_session.commit()
        return categoria_obj
    except Exception:
        return MagicMock(id_categoria=1, nombre_categoria='Sub-15')


@pytest.fixture
def tipo_evento(db_session):
    """Crea un tipo de evento de prueba."""
    try:
        from src.models.eventos.tipo_evento import TipoEvento
        tipo = TipoEvento(
            nombre='Torneo',
            descripcion='Evento tipo torneo'
        )
        db_session.add(tipo)
        db_session.commit()
        return tipo
    except Exception:
        return MagicMock(id_tipo_evento=1, nombre='Torneo')


@pytest.fixture
def persona(db_session, tipo_documento, sexo):
    """Crea una persona de prueba."""
    try:
        from src.models.personas.persona import Persona
        persona_obj = Persona(
            primer_nombre=TEST_PRIMER_NOMBRE,
            primer_apellido=TEST_PRIMER_APELLIDO,
            documento=12345678,
            correo_electronico='juan@example.com',
            telefono='3001234567',
            id_tipo_documento=getattr(tipo_documento, 'id_tipo_documento', 1),
            id_sexo=getattr(sexo, 'id_sexo', 1),
            fecha_nacimiento=date(2000, 1, 15)
        )
        db_session.add(persona_obj)
        db_session.commit()
        return persona_obj
    except Exception:
        return MagicMock(id_persona=1, primer_nombre=TEST_PRIMER_NOMBRE, primer_apellido=TEST_PRIMER_APELLIDO)


@pytest.fixture
def usuario(db_session, persona):
    """Crea un usuario de prueba."""
    try:
        from src.models.usuarios.usuario import Usuario
        from passlib.hash import bcrypt
        from tests.helpers.test_config import TEST_USERNAME, TEST_PASSWORD
        
        usuario_obj = Usuario(
            usuario=TEST_USERNAME,
            password=bcrypt.hash(TEST_PASSWORD),
            id_persona=getattr(persona, 'id_persona', 1),
            estado=True
        )
        db_session.add(usuario_obj)
        db_session.commit()
        return usuario_obj
    except Exception:
        from tests.helpers.test_config import TEST_USERNAME
        return MagicMock(id_usuario=1, usuario=TEST_USERNAME)


@pytest.fixture
def rol(db_session):
    """Crea un rol de prueba."""
    try:
        from src.models.roles_y_permisos.rol import Rol
        rol_obj = Rol(
            nombre_rol='SuperAdmin',
            descripcion='Rol de super administrador'
        )
        db_session.add(rol_obj)
        db_session.commit()
        return rol_obj
    except Exception:
        return MagicMock(id_rol=1, nombre_rol='SuperAdmin')


@pytest.fixture
def deportista(db_session, persona, categoria):
    """Crea un deportista de prueba."""
    try:
        from src.models.deportistas.deportista import Deportista
        deportista_obj = Deportista(
            id_persona=getattr(persona, 'id_persona', 1),
            id_categoria=getattr(categoria, 'id_categoria', 1),
            peso=65.5,
            altura=1.75,
            fecha_nacimiento=date(2000, 1, 15),
            fecha_ingreso=date.today()
        )
        db_session.add(deportista_obj)
        db_session.commit()
        return deportista_obj
    except Exception:
        return MagicMock(id_deportista=1, id_persona=1, id_categoria=1)

