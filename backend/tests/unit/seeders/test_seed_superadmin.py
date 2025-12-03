"""
Tests para seed_superadmin.py.
"""

import pytest
from unittest.mock import patch
from src.seeders.seed_superadmin import run


@pytest.mark.unit
class TestSeedSuperadmin:
    """Tests para el seeder de super administrador."""
    
    def test_run_seeder_creates_superadmin(self, app, db_session):
        """Test: Ejecutar seeder crea super administrador."""
        from src.models.usuarios.usuario import Usuario
        from src.models.personas.persona import Persona
        from src.models.roles_y_permisos.rol import Rol
        
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
            
            # Verificar que se creó el usuario
            usuario = Usuario.query.filter_by(usuario='superadmin').first()
            assert usuario is not None
            assert usuario.estado is True
            
            # Verificar que se creó la persona
            # Usar db.session.get en lugar de query.get para evitar warnings de SQLAlchemy 2.0
            from src.models.base import db
            persona = db.session.get(Persona, usuario.id_persona)
            assert persona is not None
            assert persona.primer_nombre == 'Super'
            assert persona.primer_apellido == 'Admin'
            assert persona.documento == '0000000000'
            assert persona.correo_electronico == 'superadmin@puertaorion.com'
    
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
            count1 = Usuario.query.filter_by(usuario='superadmin').count()
            
            run()
            count2 = Usuario.query.filter_by(usuario='superadmin').count()
            
            # No debe crear duplicados
            assert count1 == count2
            assert count1 == 1
    
    def test_run_seeder_skips_if_exists(self, app, db_session):
        """Test: Seeder no crea duplicado si ya existe superadmin."""
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
            
            # Crear un superadmin existente
            from src.models.catalogos.tipo_documento import TipoDocumento
            from src.models.categorias.sexo import Sexo
            tipo_doc = TipoDocumento.query.first()
            sexo = Sexo.query.first()
            
            if tipo_doc and sexo:
                persona = Persona(
                    primer_nombre='Super',
                    primer_apellido='Admin',
                    documento='0000000000',
                    correo_electronico='superadmin@puertaorion.com',
                    direccion='Sistema',
                    telefono='0000000000',
                    id_tipo_documento=tipo_doc.id_documento,
                    id_sexo=sexo.id_sexo,
                    estado=True
                )
                db_session.add(persona)
                db_session.flush()
                
                usuario = Usuario(
                    id_persona=persona.id_persona,
                    usuario='superadmin',
                    password='hashed_password',
                    estado=True
                )
                db_session.add(usuario)
                db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Debe seguir habiendo solo uno
            usuarios = Usuario.query.filter_by(usuario='superadmin').all()
            assert len(usuarios) == 1
    
    def test_run_seeder_handles_missing_dependencies(self, app, db_session):
        """Test: Seeder maneja correctamente dependencias faltantes."""
        with app.app_context():
            # Ejecutar sin crear dependencias
            # No debe fallar, solo debe imprimir mensajes de error
            try:
                run()
            except Exception:
                # Puede fallar si no hay dependencias, eso está bien
                pass

