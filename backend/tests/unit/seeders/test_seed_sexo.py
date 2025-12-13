"""
Tests para seed_sexo.py.
"""

import pytest
from src.seeders.seed_sexo import run


@pytest.mark.unit
class TestSeedSexo:
    """Tests para el seeder de sexos."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.categorias.sexo import Sexo
        
        with app.app_context():
            run()
            
            sexos = Sexo.query.all()
            assert len(sexos) == 3
            
            nombres = {s.nombre for s in sexos}
            assert 'Masculino' in nombres
            assert 'Femenino' in nombres
            assert 'Otro' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.categorias.sexo import Sexo
        
        with app.app_context():
            run()
            count1 = Sexo.query.count()
            
            run()
            count2 = Sexo.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.categorias.sexo import Sexo
        
        with app.app_context():
            # Crear un registro existente
            sexo_existente = Sexo(id_sexo=1, nombre='Masculino')
            db_session.add(sexo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            sexos = Sexo.query.filter_by(nombre='Masculino').all()
            assert len(sexos) == 1

