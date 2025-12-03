"""
Tests para seed_tipo_documento.py.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.seeders.seed_tipo_documento import run


@pytest.mark.unit
class TestSeedTipoDocumento:
    """Tests para el seeder de tipos de documento."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            run()
            
            tipos = TipoDocumento.query.all()
            assert len(tipos) == 5
            
            nombres = {t.nombre_documento for t in tipos}
            assert 'Cédula de Ciudadanía' in nombres
            assert 'Tarjeta de Identidad' in nombres
            assert 'Cédula de Extranjería' in nombres
            assert 'Pasaporte' in nombres
            assert 'Registro Civil' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            run()
            count1 = TipoDocumento.query.count()
            
            run()
            count2 = TipoDocumento.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            # Crear un registro existente
            tipo_existente = TipoDocumento(
                id_documento=1,
                nombre_documento='Cédula de Ciudadanía'
            )
            db_session.add(tipo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            tipos_cc = TipoDocumento.query.filter_by(
                nombre_documento='Cédula de Ciudadanía'
            ).all()
            assert len(tipos_cc) == 1
    
    def test_run_seeder_commits_transaction(self, app, db_session):
        """Test: Seeder hace commit de la transacción."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            with patch('src.seeders.seed_tipo_documento.db.session.commit') as mock_commit:
                run()
                mock_commit.assert_called_once()
    
    def test_run_seeder_with_existing_by_name_but_not_id(self, app, db_session):
        """Test: Seeder detecta existencia por nombre aunque no por ID (líneas 46-47)."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            # Crear un tipo de documento con nombre existente pero diferente ID
            tipo_existente = TipoDocumento(
                id_documento=99,  # ID diferente
                nombre_documento='Cédula de Ciudadanía'  # Nombre igual
            )
            db_session.add(tipo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no se creó un duplicado (líneas 46-47)
            tipos_cc = TipoDocumento.query.filter_by(
                nombre_documento='Cédula de Ciudadanía'
            ).all()
            # Debería haber solo el que creamos manualmente
            assert len(tipos_cc) == 1
            assert tipos_cc[0].id_documento == 99
    
    def test_run_seeder_with_existing_by_id(self, app, db_session):
        """Test: Seeder detecta existencia por ID (líneas 49-50)."""
        from src.models.catalogos.tipo_documento import TipoDocumento
        
        with app.app_context():
            # Crear un tipo de documento existente por ID
            tipo_existente = TipoDocumento(
                id_documento=1,  # ID que coincide con el seeder
                nombre_documento='Documento Existente'  # Nombre diferente
            )
            db_session.add(tipo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no se creó un duplicado por ID (líneas 49-50)
            tipos_id_1 = TipoDocumento.query.filter_by(id_documento=1).all()
            assert len(tipos_id_1) == 1
            # El nombre debería ser el que ya existía, no el del seeder
            assert tipos_id_1[0].nombre_documento == 'Documento Existente'

