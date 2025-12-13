"""
Tests para seed_parentesco.py.
"""

import pytest
from src.seeders.seed_parentesco import run


@pytest.mark.unit
class TestSeedParentesco:
    """Tests para el seeder de parentescos."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.acudientes.parentesco import Parentesco
        
        with app.app_context():
            run()
            
            parentescos = Parentesco.query.all()
            assert len(parentescos) == 7
            
            nombres = {p.nombre for p in parentescos}
            assert 'Padre' in nombres
            assert 'Madre' in nombres
            assert 'Hermano/a' in nombres
            assert 'Abuelo/a' in nombres
            assert 'Tío/a' in nombres
            assert 'Tutor Legal' in nombres
            assert 'Otro' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.acudientes.parentesco import Parentesco
        
        with app.app_context():
            run()
            count1 = Parentesco.query.count()
            
            run()
            count2 = Parentesco.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.acudientes.parentesco import Parentesco
        
        with app.app_context():
            # Crear un registro existente
            parentesco_existente = Parentesco(id_parentesco=1, nombre='Padre')
            db_session.add(parentesco_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            parentescos = Parentesco.query.filter_by(nombre='Padre').all()
            assert len(parentescos) == 1
    
    def test_run_seeder_creates_all_parentescos(self, app, db_session):
        """Test: Seeder crea todos los parentescos esperados."""
        from src.models.acudientes.parentesco import Parentesco
        
        with app.app_context():
            run()
            
            parentescos = Parentesco.query.order_by(Parentesco.id_parentesco).all()
            
            assert len(parentescos) == 7
            assert parentescos[0].id_parentesco == 1
            assert parentescos[0].nombre == 'Padre'
            assert parentescos[1].id_parentesco == 2
            assert parentescos[1].nombre == 'Madre'
            assert parentescos[6].id_parentesco == 7
            assert parentescos[6].nombre == 'Otro'

