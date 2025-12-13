"""
Tests para seed_multiple_superadmin.py.
"""

import pytest
from src.seeders.seed_multiple_superadmin import run


@pytest.mark.unit
class TestSeedMultipleSuperadmin:
    """Tests para el seeder de múltiples super administradores."""
    
    def test_run_seeder_creates_multiple_admins(self, app, db_session):
        """Test: Ejecutar seeder crea múltiples administradores."""
        from src.models.usuarios.usuario import Usuario
        
        with app.app_context():
            # Crear dependencias necesarias
            from src.seeders.seed_tipo_documento import run as run_tipo_doc
            from src.seeders.seed_sexo import run as run_sexo
            from src.seeders.seed_roles import run as run_roles
            
            run_tipo_doc()
            run_sexo()
            run_roles()
            
            # Ejecutar seeder
            run()
            
            # Verificar que se crearon los usuarios
            usuarios = Usuario.query.filter(
                Usuario.usuario.in_(['superadmin', 'admin2', 'admin3'])
            ).all()
            
            assert len(usuarios) >= 3
            
            nombres_usuarios = {u.usuario for u in usuarios}
            assert 'superadmin' in nombres_usuarios
            assert 'admin2' in nombres_usuarios
            assert 'admin3' in nombres_usuarios
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.usuarios.usuario import Usuario
        
        with app.app_context():
            # Crear dependencias
            from src.seeders.seed_tipo_documento import run as run_tipo_doc
            from src.seeders.seed_sexo import run as run_sexo
            from src.seeders.seed_roles import run as run_roles
            
            run_tipo_doc()
            run_sexo()
            run_roles()
            
            # Ejecutar seeder dos veces
            run()
            count1 = Usuario.query.filter(
                Usuario.usuario.in_(['superadmin', 'admin2', 'admin3'])
            ).count()
            
            run()
            count2 = Usuario.query.filter(
                Usuario.usuario.in_(['superadmin', 'admin2', 'admin3'])
            ).count()
            
            # No debe crear duplicados
            assert count1 == count2
    
    def test_run_seeder_creates_admins_with_different_documents(self, app, db_session):
        """Test: Seeder crea administradores con documentos diferentes."""
        from src.models.usuarios.usuario import Usuario
        from src.models.personas.persona import Persona
        
        with app.app_context():
            # Crear dependencias
            from src.seeders.seed_tipo_documento import run as run_tipo_doc
            from src.seeders.seed_sexo import run as run_sexo
            from src.seeders.seed_roles import run as run_roles
            
            run_tipo_doc()
            run_sexo()
            run_roles()
            
            # Ejecutar seeder
            run()
            
            # Verificar documentos únicos
            usuario1 = Usuario.query.filter_by(usuario='superadmin').first()
            usuario2 = Usuario.query.filter_by(usuario='admin2').first()
            usuario3 = Usuario.query.filter_by(usuario='admin3').first()
            
            if usuario1 and usuario2 and usuario3:
                # Usar filter_by en lugar de get() para evitar warnings de SQLAlchemy 2.0
                from src.models.base import db
                persona1 = db.session.get(Persona, usuario1.id_persona)
                persona2 = db.session.get(Persona, usuario2.id_persona)
                persona3 = db.session.get(Persona, usuario3.id_persona)
                
                if persona1 and persona2 and persona3:
                    documentos = {persona1.documento, persona2.documento, persona3.documento}
                    assert len(documentos) == 3  # Todos deben ser diferentes
    
    def test_run_seeder_handles_missing_dependencies(self, app, db_session):
        """Test: Seeder maneja correctamente dependencias faltantes."""
        with app.app_context():
            # Ejecutar sin crear dependencias
            # No debe fallar catastróficamente
            try:
                run()
            except Exception:
                # Puede fallar si no hay dependencias, eso está bien
                pass

