"""
Tests para base.py.

Este módulo contiene tests que verifican la funcionalidad
de la clase BaseModel.
"""

import pytest
from datetime import datetime
from sqlalchemy import Column, Integer, String
from src.models.base import BaseModel, db


@pytest.mark.unit
class TestBaseModel:
    """Tests para BaseModel."""
    
    @pytest.fixture
    def app(self):
        """Crea una aplicación Flask para testing."""
        from flask import Flask
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True
        
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_base_model_is_abstract(self, app):
        """Test: BaseModel es abstracto."""
        with app.app_context():
            # Verificar que BaseModel es abstracto (tiene __abstract__ = True)
            assert hasattr(BaseModel, '__abstract__')
            assert BaseModel.__abstract__ is True
            
            # SQLAlchemy permite instanciar modelos abstractos sin lanzar excepción
            # pero no se pueden usar directamente (no tienen tabla definida).
            # Los modelos abstractos no tienen __tablename__ hasta que se heredan.
            # Verificamos que la clase es abstracta verificando que no se puede crear tabla directamente
            from sqlalchemy.exc import InvalidRequestError
            # Intentar crear una tabla para BaseModel debería fallar porque es abstracto
            try:
                BaseModel.__table__
                # Si llegamos aquí, tiene tabla, lo cual no debería pasar para un modelo abstracto
                assert False, "BaseModel no debería tener tabla definida (es abstracto)"
            except (InvalidRequestError, AttributeError):
                # Esto es lo esperado - los modelos abstractos no tienen tabla
                pass
    
    def test_base_model_has_created_at_and_updated_at(self, app):
        """Test: BaseModel tiene campos created_at y updated_at."""
        with app.app_context():
            # Crear un modelo de prueba que herede de BaseModel
            class TestModel(BaseModel):
                __tablename__ = 'test_model'
                id_test = Column(Integer, primary_key=True)
                nombre = Column(String(50))
            
            db.create_all()
            
            # Crear instancia
            test_obj = TestModel(nombre='Test')
            db.session.add(test_obj)
            db.session.commit()
            
            # Verificar que tiene los campos
            assert hasattr(test_obj, 'created_at')
            assert hasattr(test_obj, 'updated_at')
            assert isinstance(test_obj.created_at, datetime)
            assert isinstance(test_obj.updated_at, datetime)
    
    def test_base_model_repr_with_id(self, app):
        """Test: __repr__ funciona con id (líneas 30-32)."""
        with app.app_context():
            # Crear un modelo de prueba que herede de BaseModel
            # El __repr__ busca: id_{tablename.replace('puerta_orion_', '')}
            # Si tablename = 'test_model', buscará 'id_test_model'
            class TestModelReprId(BaseModel):
                __tablename__ = 'test_model_repr'
                id_test_model_repr = Column(Integer, primary_key=True)
                nombre = Column(String(50))
            
            db.create_all()
            
            # Crear instancia
            test_obj = TestModelReprId(nombre='Test')
            db.session.add(test_obj)
            db.session.commit()
            
            # Verificar __repr__ (debería usar id_test_model_repr)
            repr_str = repr(test_obj)
            assert 'TestModelReprId' in repr_str
            assert 'id=' in repr_str
    
    def test_base_model_repr_without_id(self, app):
        """Test: __repr__ funciona sin id (línea 33)."""
        with app.app_context():
            # Crear un modelo de prueba sin atributo id estándar
            class TestModelWithoutId(BaseModel):
                __tablename__ = 'test_model_no_id'
                codigo = Column(String(50), primary_key=True)
                nombre = Column(String(50))
            
            db.create_all()
            
            # Crear instancia
            test_obj = TestModelWithoutId(codigo='ABC123', nombre='Test')
            db.session.add(test_obj)
            db.session.commit()
            
            # Verificar __repr__ (debería usar el nombre de la clase sin id)
            repr_str = repr(test_obj)
            assert 'TestModelWithoutId' in repr_str
            # Como no tiene id_test, debería retornar solo el nombre de la clase
            assert '<TestModelWithoutId' in repr_str
    
    def test_base_model_repr_with_standard_id_naming(self, app):
        """Test: __repr__ funciona con nomenclatura estándar de id."""
        with app.app_context():
            # Crear modelo con id estándar
            # El __repr__ busca: id_{tablename.replace('puerta_orion_', '')}
            # Si tablename = 'persona', buscará 'id_persona'
            class PersonaTestModel(BaseModel):
                __tablename__ = 'persona'
                id_persona = Column(Integer, primary_key=True)
                nombre = Column(String(50))
            
            db.create_all()
            
            # Crear instancia
            persona = PersonaTestModel(id_persona=1, nombre='Juan')
            db.session.add(persona)
            db.session.commit()
            
            # Verificar __repr__
            repr_str = repr(persona)
            assert 'PersonaTestModel' in repr_str
            # Debería incluir el id ya que id_persona coincide con lo que busca
            assert 'id=' in repr_str
            assert '1' in repr_str

