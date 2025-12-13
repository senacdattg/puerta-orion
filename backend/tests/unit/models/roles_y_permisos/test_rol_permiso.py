"""
Tests para rol_permiso.py.
"""

import pytest
from src.models.roles_y_permisos.rol_permiso import RolPermiso


@pytest.mark.unit
class TestRolPermiso:
    """Tests para el modelo RolPermiso."""
    
    def test_rol_permiso_repr(self, app, db_session):
        """Test: __repr__ de RolPermiso (línea 18)."""
        with app.app_context():
            rol_permiso = RolPermiso(id_rol=1, id_permiso=2)
            
            repr_str = repr(rol_permiso)
            
            assert 'RolPermiso' in repr_str
            assert '1' in repr_str or 'rol=1' in repr_str
            assert '2' in repr_str or 'permiso=2' in repr_str
    
    def test_rol_permiso_to_dict(self, app, db_session):
        """Test: to_dict de RolPermiso (línea 21)."""
        with app.app_context():
            rol_permiso = RolPermiso(id_rol=1, id_permiso=2)
            
            result = rol_permiso.to_dict()
            
            assert result == {
                'id_rol': 1,
                'id_permiso': 2
            }
            assert isinstance(result, dict)

