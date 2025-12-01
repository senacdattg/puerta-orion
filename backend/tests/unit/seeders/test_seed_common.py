"""
Tests comunes para seeders simples con patrón similar.
"""

import pytest


@pytest.mark.unit
class TestSeedParentesco:
    """Tests para seed_parentesco.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_parentesco import run
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
        from src.seeders.seed_parentesco import run
        from src.models.acudientes.parentesco import Parentesco
        
        with app.app_context():
            run()
            count1 = Parentesco.query.count()
            
            run()
            count2 = Parentesco.query.count()
            
            assert count1 == count2


@pytest.mark.unit
class TestSeedDeporte:
    """Tests para seed_deporte.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_deporte import run
        from src.models.categorias.deporte import Deporte
        
        with app.app_context():
            run()
            
            deportes = Deporte.query.all()
            assert len(deportes) == 8
            
            nombres = {d.nombre for d in deportes}
            assert 'Fútbol' in nombres
            assert 'Atletismo' in nombres
            assert 'Baloncesto' in nombres
            assert 'Natación' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.seeders.seed_deporte import run
        from src.models.categorias.deporte import Deporte
        
        with app.app_context():
            run()
            count1 = Deporte.query.count()
            
            run()
            count2 = Deporte.query.count()
            
            assert count1 == count2


@pytest.mark.unit
class TestSeedTipoEvento:
    """Tests para seed_tipo_evento.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_tipo_evento import run
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            run()
            
            tipos = TipoEvento.query.all()
            assert len(tipos) == 5
            
            nombres = {t.nombre for t in tipos}
            assert 'Entrenamiento' in nombres
            assert 'Competencia' in nombres
            assert 'Exhibición' in nombres
            assert 'Torneo' in nombres
            assert 'Evaluación Médica' in nombres
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.seeders.seed_tipo_evento import run
        from src.models.eventos.tipo_evento import TipoEvento
        
        with app.app_context():
            run()
            count1 = TipoEvento.query.count()
            
            run()
            count2 = TipoEvento.query.count()
            
            assert count1 == count2


@pytest.mark.unit
class TestSeedEscuela:
    """Tests para seed_escuela.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_escuela import run
        from src.models.categorias.escuela import Escuela
        
        with app.app_context():
            run()
            
            escuelas = Escuela.query.all()
            assert len(escuelas) == 10
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.seeders.seed_escuela import run
        from src.models.categorias.escuela import Escuela
        
        with app.app_context():
            run()
            count1 = Escuela.query.count()
            
            run()
            count2 = Escuela.query.count()
            
            assert count1 == count2


@pytest.mark.unit
class TestSeedEPS:
    """Tests para seed_eps.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_eps import run
        from src.models.catalogos.eps import EPS
        
        with app.app_context():
            run()
            
            eps_list = EPS.query.all()
            assert len(eps_list) == 10
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.seeders.seed_eps import run
        from src.models.catalogos.eps import EPS
        
        with app.app_context():
            run()
            count1 = EPS.query.count()
            
            run()
            count2 = EPS.query.count()
            
            assert count1 == count2


@pytest.mark.unit
class TestSeedInstitucionRegistro:
    """Tests para seed_institucion_registro.py."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.seeders.seed_institucion_registro import run
        from src.models.categorias.institucion_registro import InstitucionRegistro
        
        with app.app_context():
            run()
            
            instituciones = InstitucionRegistro.query.all()
            assert len(instituciones) == 10
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.seeders.seed_institucion_registro import run
        from src.models.categorias.institucion_registro import InstitucionRegistro
        
        with app.app_context():
            run()
            count1 = InstitucionRegistro.query.count()
            
            run()
            count2 = InstitucionRegistro.query.count()
            
            assert count1 == count2

