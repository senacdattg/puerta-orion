"""
Tests para seed_tipo_evento.py.
"""

import pytest
from src.seeders.seed_tipo_evento import run


@pytest.mark.unit
class TestSeedTipoEvento:
    """Tests para el seeder de tipos de evento."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            run()
            
            tipos_evento = TipoEvento.query.all()
            assert len(tipos_evento) == 5
            
            nombres = {t.nombre for t in tipos_evento}
            assert 'Entrenamiento' in nombres
            assert 'Competencia' in nombres
            assert 'Exhibición' in nombres
            assert 'Torneo' in nombres
            assert 'Evaluación Médica' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            run()
            count1 = TipoEvento.query.count()
            
            run()
            count2 = TipoEvento.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            # Crear un registro existente
            tipo_existente = TipoEvento(
                id_tipo_evento=1,
                nombre='Entrenamiento',
                descripcion='Sesión de entrenamiento regular'
            )
            db_session.add(tipo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            tipos = TipoEvento.query.filter_by(nombre='Entrenamiento').all()
            assert len(tipos) == 1
    
    def test_run_seeder_creates_all_tipos_evento(self, app, db_session):
        """Test: Seeder crea todos los tipos de evento esperados con descripciones."""
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            run()
            
            tipos_evento = TipoEvento.query.order_by(TipoEvento.id_tipo_evento).all()
            
            assert len(tipos_evento) == 5
            
            # Verificar primer tipo
            assert tipos_evento[0].id_tipo_evento == 1
            assert tipos_evento[0].nombre == 'Entrenamiento'
            assert tipos_evento[0].descripcion == 'Sesión de entrenamiento regular'
            
            # Verificar último tipo
            assert tipos_evento[4].id_tipo_evento == 5
            assert tipos_evento[4].nombre == 'Evaluación Médica'
            assert tipos_evento[4].descripcion == 'Chequeo médico deportivo'

