"""
Tests para seed_tipo_enfermedad.py.
"""

import pytest
from src.seeders.seed_tipo_enfermedad import run


@pytest.mark.unit
class TestSeedTipoEnfermedad:
    """Tests para el seeder de tipos de enfermedad."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        with app.app_context():
            run()
            
            tipos = TipoEnfermedad.query.all()
            assert len(tipos) == 10
            
            nombres = {t.nombre for t in tipos}
            assert 'Lesión Muscular' in nombres
            assert 'Lesión Ósea' in nombres
            assert 'Lesión Articular' in nombres
            assert 'Enfermedad Respiratoria' in nombres
            assert 'Enfermedad Cardiovascular' in nombres
            assert 'Condición Crónica' in nombres
            assert 'Enfermedad Infecciosa' in nombres
            assert 'Trastorno Mental' in nombres
            assert 'Alergia' in nombres
            assert 'Otro' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        with app.app_context():
            run()
            count1 = TipoEnfermedad.query.count()
            
            run()
            count2 = TipoEnfermedad.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        with app.app_context():
            # Crear un registro existente
            tipo_existente = TipoEnfermedad(
                id_tipo_enfermedad=1,
                nombre='Lesión Muscular'
            )
            db_session.add(tipo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            tipos = TipoEnfermedad.query.filter_by(
                nombre='Lesión Muscular'
            ).all()
            assert len(tipos) == 1

