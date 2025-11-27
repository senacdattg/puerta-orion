"""
Tests para el seeder de roles.

Este módulo contiene tests para verificar que el seeder de roles
funciona correctamente.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.seeders.seed_roles import (
    run,
    _obtener_configuracion_roles,
    _crear_o_obtener_rol,
    _asignar_todos_los_permisos,
    _asignar_permisos_especificos,
    _sincronizar_permisos
)


# ============================================================================
# TESTS PARA CONFIGURACIÓN DE ROLES
# ============================================================================

@pytest.mark.unit
class TestObtenerConfiguracionRoles:
    """Tests para obtener configuración de roles."""
    
    def test_obtener_configuracion_roles(self):
        """Test: Obtener configuración de roles."""
        config = _obtener_configuracion_roles()
        
        assert 'SuperAdmin' in config
        assert 'Administrador' in config
        assert 'Entrenador' in config
        assert 'Deportista' in config
        assert 'Acudiente' in config
        assert 'Usuario' in config
    
    def test_configuracion_superadmin(self):
        """Test: Verificar configuración de SuperAdmin."""
        config = _obtener_configuracion_roles()
        
        assert config['SuperAdmin']['permisos'] == 'ALL'
        assert 'Super Administrador' in config['SuperAdmin']['descripcion']
    
    def test_configuracion_administrador(self):
        """Test: Verificar configuración de Administrador."""
        config = _obtener_configuracion_roles()
        
        assert isinstance(config['Administrador']['permisos'], list)
        assert 'crear_deportista' in config['Administrador']['permisos']
        assert 'gestionar_eventos' in config['Administrador']['permisos']


# ============================================================================
# TESTS PARA CREAR O OBTENER ROL
# ============================================================================

@pytest.mark.unit
class TestCrearObtenerRol:
    """Tests para crear o obtener rol."""
    
    def test_crear_rol_nuevo(self, app, db_session):
        """Test: Crear un rol nuevo."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            rol, es_nuevo = _crear_o_obtener_rol('TestRol', 'Rol de prueba')
            
            assert es_nuevo is True
            assert rol.nombre_rol == 'TestRol'
            assert rol.descripcion == 'Rol de prueba'
    
    def test_obtener_rol_existente(self, app, db_session):
        """Test: Obtener un rol existente."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            # Crear rol primero
            rol_existente = Rol(nombre_rol='RolExistente', descripcion='Rol existente')
            db_session.add(rol_existente)
            db_session.commit()
            
            # Intentar crear/obtener el mismo rol
            rol, es_nuevo = _crear_o_obtener_rol('RolExistente', 'Nueva descripción')
            
            assert es_nuevo is False
            assert rol.id_rol == rol_existente.id_rol
            assert rol.nombre_rol == 'RolExistente'


# ============================================================================
# TESTS PARA ASIGNAR PERMISOS
# ============================================================================

@pytest.mark.unit
class TestAsignarPermisos:
    """Tests para asignar permisos a roles."""
    
    def test_asignar_todos_los_permisos(self, app, db_session):
        """Test: Asignar todos los permisos a un rol."""
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        with app.app_context():
            # Crear rol y permisos
            rol = Rol(nombre_rol='TestRol', descripcion='Test')
            db_session.add(rol)
            db_session.flush()
            
            permiso1 = Permiso(nombre='permiso1', descripcion='Permiso 1')
            permiso2 = Permiso(nombre='permiso2', descripcion='Permiso 2')
            db_session.add_all([permiso1, permiso2])
            db_session.commit()
            
            # Asignar todos los permisos
            asignados = _asignar_todos_los_permisos(rol)
            
            assert asignados == 2
            
            # Verificar que se asignaron
            rol_permisos = RolPermiso.query.filter_by(id_rol=rol.id_rol).all()
            assert len(rol_permisos) == 2
    
    def test_asignar_permisos_especificos(self, app, db_session):
        """Test: Asignar permisos específicos a un rol."""
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        with app.app_context():
            # Crear rol y permisos
            rol = Rol(nombre_rol='TestRol', descripcion='Test')
            db_session.add(rol)
            db_session.flush()
            
            permiso1 = Permiso(nombre='crear_deportista', descripcion='Crear deportista')
            permiso2 = Permiso(nombre='ver_deportista', descripcion='Ver deportista')
            db_session.add_all([permiso1, permiso2])
            db_session.commit()
            
            # Asignar permisos específicos
            nombres_permisos = ['crear_deportista', 'ver_deportista']
            asignados = _asignar_permisos_especificos(rol, nombres_permisos)
            
            assert asignados == 2
    
    def test_asignar_permisos_especificos_inexistente(self, app, db_session):
        """Test: Intentar asignar permiso que no existe."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            rol = Rol(nombre_rol='TestRol', descripcion='Test')
            db_session.add(rol)
            db_session.flush()
            
            nombres_permisos = ['permiso_inexistente']
            asignados = _asignar_permisos_especificos(rol, nombres_permisos)
            
            assert asignados == 0
    
    def test_asignar_permisos_duplicados(self, app, db_session):
        """Test: No asignar permisos duplicados."""
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        with app.app_context():
            # Crear rol y permiso
            rol = Rol(nombre_rol='TestRol', descripcion='Test')
            db_session.add(rol)
            db_session.flush()
            
            permiso = Permiso(nombre='permiso1', descripcion='Permiso 1')
            db_session.add(permiso)
            db_session.commit()
            
            # Asignar permiso dos veces
            nombres_permisos = ['permiso1']
            asignados1 = _asignar_permisos_especificos(rol, nombres_permisos)
            asignados2 = _asignar_permisos_especificos(rol, nombres_permisos)
            
            assert asignados1 == 1
            assert asignados2 == 0  # No debe asignar duplicado


# ============================================================================
# TESTS PARA SINCRONIZAR PERMISOS
# ============================================================================

@pytest.mark.unit
class TestSincronizarPermisos:
    """Tests para sincronizar permisos de roles."""
    
    def test_sincronizar_permisos_superadmin(self, app, db_session):
        """Test: No sincronizar permisos de SuperAdmin."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            rol = Rol(nombre_rol='SuperAdmin', descripcion='Super Admin')
            db_session.add(rol)
            db_session.commit()
            
            removidos = _sincronizar_permisos(rol, 'SuperAdmin', set())
            
            assert removidos == 0
    
    def test_sincronizar_permisos_remover(self, app, db_session):
        """Test: Remover permisos que no están en la configuración."""
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        with app.app_context():
            # Crear rol y permisos
            rol = Rol(nombre_rol='TestRol', descripcion='Test')
            db_session.add(rol)
            db_session.flush()
            
            permiso1 = Permiso(nombre='permiso1', descripcion='Permiso 1')
            permiso2 = Permiso(nombre='permiso2', descripcion='Permiso 2')
            db_session.add_all([permiso1, permiso2])
            db_session.commit()
            
            # Asignar ambos permisos
            rol_permiso1 = RolPermiso(id_rol=rol.id_rol, id_permiso=permiso1.id_permiso)
            rol_permiso2 = RolPermiso(id_rol=rol.id_rol, id_permiso=permiso2.id_permiso)
            db_session.add_all([rol_permiso1, rol_permiso2])
            db_session.commit()
            
            # Sincronizar solo con permiso1
            permisos_config = {'permiso1'}
            removidos = _sincronizar_permisos(rol, 'TestRol', permisos_config)
            
            assert removidos == 1
            
            # Verificar que solo queda permiso1
            rol_permisos = RolPermiso.query.filter_by(id_rol=rol.id_rol).all()
            assert len(rol_permisos) == 1
            assert rol_permisos[0].id_permiso == permiso1.id_permiso


# ============================================================================
# TESTS PARA EJECUTAR SEEDER
# ============================================================================

@pytest.mark.unit
class TestRunSeeder:
    """Tests para ejecutar el seeder completo."""
    
    def test_run_seeder_crear_roles(self, app, db_session):
        """Test: Ejecutar seeder y crear roles."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            # Ejecutar seeder
            run()
            
            # Verificar que se crearon los roles
            roles = Rol.query.all()
            assert len(roles) >= 6  # SuperAdmin, Administrador, Entrenador, Deportista, Acudiente, Usuario
            
            nombres_roles = {rol.nombre_rol for rol in roles}
            assert 'SuperAdmin' in nombres_roles
            assert 'Administrador' in nombres_roles
            assert 'Entrenador' in nombres_roles
            assert 'Deportista' in nombres_roles
            assert 'Acudiente' in nombres_roles
            assert 'Usuario' in nombres_roles
    
    def test_run_seeder_idempotente(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces (idempotente)."""
        from src.models.roles_y_permisos.rol import Rol
        
        with app.app_context():
            # Ejecutar seeder dos veces
            run()
            count1 = Rol.query.count()
            
            run()
            count2 = Rol.query.count()
            
            # No debe crear roles duplicados
            assert count1 == count2
    
    def test_run_seeder_asignar_permisos(self, app, db_session):
        """Test: Verificar que se asignan permisos."""
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.permiso import Permiso
        from src.models.roles_y_permisos.rol_permiso import RolPermiso
        
        with app.app_context():
            # Crear algunos permisos primero
            permisos = [
                Permiso(nombre='crear_deportista', descripcion='Crear deportista'),
                Permiso(nombre='ver_deportista', descripcion='Ver deportista'),
                Permiso(nombre='gestionar_eventos', descripcion='Gestionar eventos')
            ]
            db_session.add_all(permisos)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que se asignaron permisos
            rol_admin = Rol.query.filter_by(nombre_rol='Administrador').first()
            assert rol_admin is not None
            
            rol_permisos = RolPermiso.query.filter_by(id_rol=rol_admin.id_rol).all()
            assert len(rol_permisos) > 0

