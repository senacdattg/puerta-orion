"""
Fixtures para tests de utils.

Proporciona contexto de aplicación Flask y mocks necesarios.
"""

import pytest
from flask import Flask


@pytest.fixture
def app_context():
    """Proporciona un contexto de aplicación Flask para los tests."""
    from app import create_app
    
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test_secret_key'  # nosonar: S2068, S6418 - Test secret only, never used in production
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600
    
    with app.app_context():
        yield app

