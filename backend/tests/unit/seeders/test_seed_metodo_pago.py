"""
Tests para seed_metodo_pago.py.
"""

import pytest
from src.seeders.seed_metodo_pago import run


@pytest.mark.unit
class TestSeedMetodoPago:
    """Tests para el seeder de métodos de pago."""
    
    def test_run_seeder_creates_records(self, app, db_session):
        """Test: Ejecutar seeder crea registros."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        with app.app_context():
            run()
            
            metodos = MetodoPago.query.all()
            assert len(metodos) == 8
            
            nombres = {m.nombre_metodo for m in metodos}
            assert 'Efectivo' in nombres
            assert 'Transferencia Bancaria' in nombres
            assert 'Tarjeta Débito/Crédito' in nombres
            assert 'Nequi' in nombres
            assert 'Daviplata' in nombres
            assert 'PSE' in nombres
            assert 'Mercado Pago' in nombres
            assert 'Ninguno' in nombres
    
    def test_run_seeder_creates_methods_with_state(self, app, db_session):
        """Test: Seeder crea métodos con estado activo."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        with app.app_context():
            run()
            
            efectivo = MetodoPago.query.filter_by(
                nombre_metodo='Efectivo'
            ).first()
            
            assert efectivo is not None
            assert efectivo.estado is True
    
    def test_run_seeder_idempotent(self, app, db_session):
        """Test: Ejecutar seeder múltiples veces es idempotente."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        with app.app_context():
            run()
            count1 = MetodoPago.query.count()
            
            run()
            count2 = MetodoPago.query.count()
            
            assert count1 == count2
    
    def test_run_seeder_checks_by_name_and_id(self, app, db_session):
        """Test: Seeder verifica duplicados por nombre e ID."""
        from src.models.pagos.metodo_pago import MetodoPago
        
        with app.app_context():
            # Crear un registro existente con mismo nombre
            metodo_existente = MetodoPago(
                id_metodo_pago=99,
                nombre_metodo='Efectivo',
                estado=True
            )
            db_session.add(metodo_existente)
            db_session.commit()
            
            # Ejecutar seeder
            run()
            
            # Verificar que no crea duplicado por nombre
            metodos = MetodoPago.query.filter_by(nombre_metodo='Efectivo').all()
            assert len(metodos) == 1

