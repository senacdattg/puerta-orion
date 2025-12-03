"""
Tests para seed_diagnostico.py.
"""

import pytest
from src.seeders.seed_diagnostico import run


@pytest.mark.unit
class TestSeedDiagnostico:
    """Tests para el seeder de diagnósticos."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.salud.diagnostico import Diagnostico
        
        with app.app_context():
            # Primero crear tipos de enfermedad (dependencia)
            from src.seeders.seed_tipo_enfermedad import run as run_tipo_enfermedad
            run_tipo_enfermedad()
            
            run()
            
            diagnosticos = Diagnostico.query.all()
            assert len(diagnosticos) == 44
            
            nombres = {d.nombre for d in diagnosticos}
            assert 'Esguince de tobillo' in nombres
            assert 'Fractura de pierna' in nombres
            assert 'Asma' in nombres
            assert 'Diabetes mellitus' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.salud.diagnostico import Diagnostico
        
        with app.app_context():
            # Crear dependencias
            from src.seeders.seed_tipo_enfermedad import run as run_tipo_enfermedad
            run_tipo_enfermedad()
            
            run()
            count1 = Diagnostico.query.count()
            
            run()
            count2 = Diagnostico.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_creates_diagnosticos_with_tipo_enfermedad(self, app, db_session):
        """Test: Seeder crea diagnósticos asociados a tipos de enfermedad."""
        from src.models.salud.diagnostico import Diagnostico
        
        with app.app_context():
            # Crear dependencias
            from src.seeders.seed_tipo_enfermedad import run as run_tipo_enfermedad
            run_tipo_enfermedad()
            
            run()
            
            # Verificar que los diagnósticos tienen id_tipo_enfermedad
            esguince = Diagnostico.query.filter_by(
                nombre='Esguince de tobillo'
            ).first()
            
            assert esguince is not None
            assert esguince.id_tipo_enfermedad is not None
            assert esguince.id_tipo_enfermedad == 1  # Lesión Muscular
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.salud.diagnostico import Diagnostico
        
        with app.app_context():
            # Crear dependencias
            from src.seeders.seed_tipo_enfermedad import run as run_tipo_enfermedad
            run_tipo_enfermedad()
            
            # Crear un registro existente
            diagnostico_existente = Diagnostico(
                id_diagnostico=1,
                nombre='Esguince de tobillo',
                id_tipo_enfermedad=1
            )
            db_session.add(diagnostico_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            diagnosticos = Diagnostico.query.filter_by(
                id_diagnostico=1
            ).all()
            assert len(diagnosticos) == 1

