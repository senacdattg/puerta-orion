"""
Tests para seed_grupo_sanguineo.py.
"""

import pytest
from src.seeders.seed_grupo_sanguineo import run


@pytest.mark.unit
class TestSeedGrupoSanguineo:
    """Tests para el seeder de grupos sanguíneos."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
        with app.app_context():
            run()
            
            grupos = GrupoSanguineo.query.all()
            assert len(grupos) == 8
            
            tipos = {g.tipo_sangre for g in grupos}
            assert 'A+' in tipos
            assert 'A-' in tipos
            assert 'B+' in tipos
            assert 'B-' in tipos
            assert 'AB+' in tipos
            assert 'AB-' in tipos
            assert 'O+' in tipos
            assert 'O-' in tipos
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
        with app.app_context():
            run()
            count1 = GrupoSanguineo.query.count()
            
            run()
            count2 = GrupoSanguineo.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
        with app.app_context():
            # Crear un registro existente
            grupo_existente = GrupoSanguineo(
                id_tipo_sangre=1,
                tipo_sangre='A+'
            )
            db_session.add(grupo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            grupos = GrupoSanguineo.query.filter_by(tipo_sangre='A+').all()
            assert len(grupos) == 1

