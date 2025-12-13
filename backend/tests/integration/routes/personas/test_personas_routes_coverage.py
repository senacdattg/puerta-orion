"""
Tests adicionales para aumentar la cobertura de personas_routes.py.

Cubre casos edge y bloques de excepciones que no están cubiertos en los tests existentes.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)
from tests.integration.test_utils import create_mock_persona


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.personas
class TestPersonasRoutesCoverage:
    """Tests adicionales para aumentar cobertura de personas_routes.py"""

    # Los tests de excepciones se movieron a tests/unit/routes/test_personas_routes_coverage.py
    # porque los tests de integración tienen problemas para encontrar las rutas cuando se patchea Persona.query
    pass

