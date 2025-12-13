"""
Tests para permiso.py.
"""

import pytest
from src.models.roles_y_permisos.permiso import Permiso


@pytest.mark.unit
class TestPermiso:
    """Tests para el modelo Permiso."""
    
    def test_permiso_repr(self, app, db_session):
        """Test: __repr__ de Permiso (línea 19)."""
        with app.app_context():
            permiso = Permiso(id_permiso=1, nombre='crear_deportista', descripcion='Permite crear deportistas')
            
            repr_str = repr(permiso)
            
            assert 'Permiso' in repr_str
            assert 'crear_deportista' in repr_str
    
    def test_permiso_to_dict(self, app, db_session):
        """Test: to_dict de Permiso (línea 22)."""
        with app.app_context():
            permiso = Permiso(
                id_permiso=1,
                nombre='crear_deportista',
                descripcion='Permite crear deportistas'
            )
            
            result = permiso.to_dict()
            
            assert result == {
                'id_permiso': 1,
                'nombre': 'crear_deportista',
                'descripcion': 'Permite crear deportistas'
            }
            assert isinstance(result, dict)
            assert 'id_permiso' in result
            assert 'nombre' in result
            assert 'descripcion' in result

