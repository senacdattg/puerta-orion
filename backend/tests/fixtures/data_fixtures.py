"""
Fixtures para datos de prueba.

Este módulo contiene fixtures que proporcionan datos de ejemplo
para crear entidades en los tests.
"""

import pytest
from datetime import date
from typing import Dict, Any

from tests.conftest import TEST_PRIMER_NOMBRE, TEST_PRIMER_APELLIDO


@pytest.fixture
def sample_persona_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear una persona."""
    return {
        'primer_nombre': TEST_PRIMER_NOMBRE,
        'segundo_nombre': 'Carlos',
        'primer_apellido': TEST_PRIMER_APELLIDO,
        'segundo_apellido': 'García',
        'documento': 12345678,
        'correo_electronico': 'juan.perez@example.com',
        'telefono': '3001234567',
        'direccion': 'Calle 123 #45-67',
        'id_tipo_documento': 1,
        'id_sexo': 1,
        'fecha_nacimiento': date(2000, 1, 15)
    }


@pytest.fixture
def sample_deportista_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un deportista."""
    return {
        'datos_deportista': {
            'id_persona': 1,
            'id_categoria': 1,
            'peso': 65.5,
            'altura': 1.75,
            'fecha_nacimiento': 2000,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        },
        'informacion_deportiva': {
            'practica_otro_deporte': False,
            'participa_escuela': True,
            'recomendacion_medica': False,
            'id_escuela': 1,
            'id_deporte': 1,
            'id_institucion_registro': 1
        },
        'tipo_enfermedad': 1,
        'diagnostico': [1, 2]
    }


@pytest.fixture
def sample_evento_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un evento."""
    return {
        'nombre': 'Torneo de Fútbol',
        'fecha_evento': '2024-12-31',
        'hora_inicio': '10:00',
        'hora_fin': '12:00',
        'lugar': 'Cancha Principal',
        'descripcion': 'Torneo anual de fútbol',
        'id_categoria': 1,
        'id_tipo_evento': 1
    }


@pytest.fixture
def sample_usuario_data() -> Dict[str, Any]:
    """Datos de ejemplo para crear un usuario."""
    from tests.helpers.test_config import TEST_PASSWORD, TEST_USERNAME, TEST_EMAIL
    
    return {
        'persona': {
            'primer_nombre': 'Test',
            'primer_apellido': 'User',
            'documento': 99999999,
            'correo_electronico': TEST_EMAIL,
            'telefono': '3009999999',
            'id_tipo_documento': 1,
            'id_sexo': 1
        },
        'usuario': {
            'usuario': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
    }

