"""
Tests para seed_categoria.py.
"""

import pytest
from src.seeders.seed_categoria import run


@pytest.mark.unit
class TestSeedCategoria:
    """Tests para el seeder de categorías."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.categorias.categoria import Categoria
        
        with app.app_context():
            run()
            
            categorias = Categoria.query.all()
            assert len(categorias) == 8
            
            nombres = {c.nombre_categoria for c in categorias}
            assert 'Pre-infantil' in nombres
            assert 'Infantil' in nombres
            assert 'Pre-juvenil' in nombres
            assert 'Juvenil' in nombres
            assert 'Mayores' in nombres
            assert 'Sénior' in nombres
            assert 'Máster' in nombres
            assert 'Todos' in nombres
    
    def test_run_seeder_creates_categories_with_age_ranges(self, app, db_session):
        """Test: Seeder crea categorías con rangos de edad correctos."""
        from src.models.categorias.categoria import Categoria
        
        with app.app_context():
            run()
            
            pre_infantil = Categoria.query.filter_by(
                nombre_categoria='Pre-infantil'
            ).first()
            
            assert pre_infantil is not None
            assert pre_infantil.edad_minima == 5
            assert pre_infantil.edad_maxima == 7
            assert pre_infantil.estado is True
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.categorias.categoria import Categoria
        
        with app.app_context():
            run()
            count1 = Categoria.query.count()
            
            run()
            count2 = Categoria.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_with_existing_records(self, app, db_session):
        """Test: Seeder no crea duplicados si ya existen."""
        from src.models.categorias.categoria import Categoria
        
        with app.app_context():
            # Crear un registro existente
            categoria_existente = Categoria(
                id_categoria=1,
                nombre_categoria='Pre-infantil',
                codigo_categoria=1,
                edad_minima=5,
                edad_maxima=7,
                estado=True
            )
            db_session.add(categoria_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no hay duplicados
            categorias = Categoria.query.filter_by(
                nombre_categoria='Pre-infantil'
            ).all()
            assert len(categorias) == 1

