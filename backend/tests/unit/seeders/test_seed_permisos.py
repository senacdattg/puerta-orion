"""
Tests para seed_permisos.py.
"""

import pytest
from src.seeders.seed_permisos import run


@pytest.mark.unit
class TestSeedPermisos:
    """Tests para el seeder de permisos."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.roles_y_permisos.permiso import Permiso
        
        with app.app_context():
            run()
            
            permisos = Permiso.query.all()
            assert len(permisos) > 40  # Hay muchos permisos
            
            nombres = {p.nombre for p in permisos}
            assert 'crear_deportista' in nombres
            assert 'ver_deportista' in nombres
            assert 'crear_usuario' in nombres
            assert 'crear_evento' in nombres
            assert 'crear_mensualidad' in nombres
            assert 'gestionar_usuarios' in nombres
            assert 'acceso_panel_admin' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.roles_y_permisos.permiso import Permiso
        
        with app.app_context():
            run()
            count1 = Permiso.query.count()
            
            run()
            count2 = Permiso.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_creates_permisos_with_descriptions(self, app, db_session):
        """Test: Seeder crea permisos con descripciones."""
        from src.models.roles_y_permisos.permiso import Permiso
        
        with app.app_context():
            run()
            
            permiso = Permiso.query.filter_by(
                nombre='crear_deportista'
            ).first()
            
            assert permiso is not None
            assert permiso.descripcion is not None
            assert 'deportista' in permiso.descripcion.lower()
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.roles_y_permisos.permiso import Permiso
        
        with app.app_context():
            # Crear un permiso existente
            permiso_existente = Permiso(
                nombre='crear_deportista',
                descripcion='Permite crear deportistas'
            )
            db_session.add(permiso_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            permisos = Permiso.query.filter_by(
                nombre='crear_deportista'
            ).all()
            assert len(permisos) == 1
    
    def test_run_seeder_creates_all_permission_categories(self, app, db_session):
        """Test: Seeder crea permisos de todas las categorías."""
        from src.models.roles_y_permisos.permiso import Permiso
        
        with app.app_context():
            run()
            
            permisos = Permiso.query.all()
            nombres = {p.nombre for p in permisos}
            
            # Verificar diferentes categorías de permisos
            assert any('deportista' in nombre for nombre in nombres)
            assert any('usuario' in nombre for nombre in nombres)
            assert any('evento' in nombre for nombre in nombres)
            assert any('mensualidad' in nombre for nombre in nombres)
            assert any('acudiente' in nombre for nombre in nombres)
            assert any('diagnostico' in nombre for nombre in nombres)
            assert any('reporte' in nombre for nombre in nombres)
            assert any('catalogo' in nombre for nombre in nombres)
            assert any('galeria' in nombre for nombre in nombres)
            assert any('calendario' in nombre for nombre in nombres)

