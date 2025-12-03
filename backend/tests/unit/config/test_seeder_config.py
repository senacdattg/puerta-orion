"""
Tests para seeder_config.py.

Este módulo contiene tests que verifican la obtención de passwords
desde variables de entorno para los seeders.
"""

import pytest
import os
from unittest.mock import patch

from src.config.seeder_config import (
    get_superadmin_password,
    get_admin2_password,
    get_admin3_password
)


@pytest.mark.unit
class TestSeederConfig:
    """Tests para seeder_config."""
    
    def test_get_superadmin_password_default(self):
        """Test: Obtener password de superadmin con valor por defecto."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove the env var if it exists
            os.environ.pop('SEEDER_SUPERADMIN_PASSWORD', None)
            password = get_superadmin_password()
            
            assert password == 'SuperAdmin2024!'
    
    def test_get_superadmin_password_from_env(self):
        """Test: Obtener password de superadmin desde variable de entorno."""
        with patch.dict(os.environ, {'SEEDER_SUPERADMIN_PASSWORD': 'CustomPassword123!'}, clear=False):
            password = get_superadmin_password()
            
            assert password == 'CustomPassword123!'
    
    def test_get_admin2_password_default(self):
        """Test: Obtener password de admin2 con valor por defecto."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('SEEDER_ADMIN2_PASSWORD', None)
            password = get_admin2_password()
            
            assert password == 'Admin2024!'
    
    def test_get_admin2_password_from_env(self):
        """Test: Obtener password de admin2 desde variable de entorno."""
        with patch.dict(os.environ, {'SEEDER_ADMIN2_PASSWORD': 'AdminCustom123!'}, clear=False):
            password = get_admin2_password()
            
            assert password == 'AdminCustom123!'
    
    def test_get_admin3_password_default(self):
        """Test: Obtener password de admin3 con valor por defecto."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('SEEDER_ADMIN3_PASSWORD', None)
            password = get_admin3_password()
            
            assert password == 'Admin2024!'
    
    def test_get_admin3_password_from_env(self):
        """Test: Obtener password de admin3 desde variable de entorno."""
        with patch.dict(os.environ, {'SEEDER_ADMIN3_PASSWORD': 'Admin3Custom456!'}, clear=False):
            password = get_admin3_password()
            
            assert password == 'Admin3Custom456!'
    
    def test_get_superadmin_password_env_override(self):
        """Test: Variable de entorno sobrescribe valor por defecto."""
        original_value = os.environ.get('SEEDER_SUPERADMIN_PASSWORD')
        
        try:
            os.environ['SEEDER_SUPERADMIN_PASSWORD'] = 'OverridePassword'
            password = get_superadmin_password()
            
            assert password == 'OverridePassword'
            assert password != 'SuperAdmin2024!'
        finally:
            if original_value is None:
                os.environ.pop('SEEDER_SUPERADMIN_PASSWORD', None)
            else:
                os.environ['SEEDER_SUPERADMIN_PASSWORD'] = original_value
    
    def test_all_passwords_are_strings(self):
        """Test: Todas las funciones retornan strings."""
        password1 = get_superadmin_password()
        password2 = get_admin2_password()
        password3 = get_admin3_password()
        
        assert isinstance(password1, str)
        assert isinstance(password2, str)
        assert isinstance(password3, str)
    
    def test_all_passwords_are_not_empty(self):
        """Test: Todas las passwords retornadas no están vacías."""
        password1 = get_superadmin_password()
        password2 = get_admin2_password()
        password3 = get_admin3_password()
        
        assert len(password1) > 0
        assert len(password2) > 0
        assert len(password3) > 0

