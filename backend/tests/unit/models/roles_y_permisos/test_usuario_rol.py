"""
Tests para usuario_rol.py.
"""

import pytest
from src.models.roles_y_permisos.usuario_rol import UsuarioRol


@pytest.mark.unit
class TestUsuarioRol:
    """Tests para el modelo UsuarioRol."""
    
    def test_usuario_rol_repr(self, app, db_session):
        """Test: __repr__ de UsuarioRol (línea 17)."""
        with app.app_context():
            usuario_rol = UsuarioRol(id_usuario=1, id_rol=2)
            
            repr_str = repr(usuario_rol)
            
            assert 'UsuarioRol' in repr_str
            assert '1' in repr_str or 'usuario=1' in repr_str
            assert '2' in repr_str or 'rol=2' in repr_str
    
    def test_usuario_rol_to_dict(self, app, db_session):
        """Test: to_dict de UsuarioRol (línea 20)."""
        with app.app_context():
            usuario_rol = UsuarioRol(id_usuario=1, id_rol=2)
            
            result = usuario_rol.to_dict()
            
            assert result == {
                'id_usuario': 1,
                'id_rol': 2
            }
            assert isinstance(result, dict)

