"""
Tests para seed_ciudad_residencia.py.
"""

import pytest
from src.seeders.seed_ciudad_residencia import run


@pytest.mark.unit
class TestSeedCiudadResidencia:
    """Tests para el seeder de ciudades de residencia."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        
        with app.app_context():
            result = run()
            
            ciudades = CiudadResidencia.query.all()
            assert len(ciudades) == 1
            
            nombres = {c.nombre_ciudad for c in ciudades}
            assert 'Guaviare' in nombres
            
            # Verificar que retorna tupla con insertados y existentes
            assert isinstance(result, tuple)
            assert len(result) == 2
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        
        with app.app_context():
            run()
            count1 = CiudadResidencia.query.count()
            
            run()
            count2 = CiudadResidencia.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        
        with app.app_context():
            # Crear un registro existente
            ciudad_existente = CiudadResidencia(
                id_ciudad=1,
                nombre_ciudad='Guaviare'
            )
            db_session.add(ciudad_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados por nombre
            ciudades = CiudadResidencia.query.filter_by(
                nombre_ciudad='Guaviare'
            ).all()
            assert len(ciudades) == 1
    
    def test_run_seeder_creates_guaviare(self, app, db_session):
        """Test: Seeder crea la ciudad de Guaviare."""
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        
        with app.app_context():
            run()
            
            ciudades = CiudadResidencia.query.all()
            nombres = {c.nombre_ciudad for c in ciudades}
            
            # Verificar que se creó Guaviare
            assert 'Guaviare' in nombres
            
            # Verificar que solo hay una ciudad
            assert len(ciudades) == 1

