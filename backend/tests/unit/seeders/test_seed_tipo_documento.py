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

