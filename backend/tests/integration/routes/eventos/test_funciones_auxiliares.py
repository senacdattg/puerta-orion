"""
Tests para funciones auxiliares de eventos.

Estas funciones son helpers internos del módulo eventos_routes.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from tests.helpers import (
    assert_success_response
)


@pytest.mark.unit
class TestFuncionesAuxiliares:
    """Tests para funciones auxiliares de eventos."""
    
    def test_parse_date(self):
        """Test: Parsear fecha válida."""
        from src.routes.eventos_routes import _parse_date
        
        fecha = _parse_date('2024-12-31')
        assert fecha == date(2024, 12, 31)
    
    def test_parse_date_invalida(self):
        """Test: Parsear fecha inválida."""
        from src.routes.eventos_routes import _parse_date
        
        fecha = _parse_date('invalid-date')
        assert fecha is None
    
    def test_parse_time(self):
        """Test: Parsear hora válida."""
        from src.routes.eventos_routes import _parse_time
        
        hora = _parse_time('10:30')
        assert hora.hour == 10
        assert hora.minute == 30
    
    def test_parse_time_con_segundos(self):
        """Test: Parsear hora con segundos."""
        from src.routes.eventos_routes import _parse_time
        
        hora = _parse_time('10:30:45')
        assert hora.hour == 10
        assert hora.minute == 30
        assert hora.second == 45
    
    def test_parse_time_invalida(self):
        """Test: Parsear hora inválida."""
        from src.routes.eventos_routes import _parse_time
        
        hora = _parse_time('invalid-time')
        assert hora is None
    
    def test_validar_lugar(self):
        """Test: Validar lugar válido."""
        from src.routes.eventos_routes import _validar_lugar
        
        assert _validar_lugar('Cancha Principal') is True
        assert _validar_lugar('AB') is False
        assert _validar_lugar('') is False
    
    def test_obtener_categoria_todos(self, app):
        """Test: Obtener categoría 'Todos'."""
        from src.routes.eventos_routes import _obtener_categoria_todos
        
        with app.app_context():
            with patch('src.routes.eventos_routes.Categoria.query') as mock_query:
                mock_categoria = MagicMock()
                mock_categoria.id_categoria = 1
                mock_query.filter_by.return_value.first.return_value = mock_categoria
                
                categoria_id = _obtener_categoria_todos()
                assert categoria_id == 1
    
    def test_obtener_categoria_todos_no_existe(self, app):
        """Test: Categoría 'Todos' no existe."""
        from src.routes.eventos_routes import _obtener_categoria_todos
        
        with app.app_context():
            with patch('src.routes.eventos_routes.Categoria.query') as mock_query:
                mock_query.filter_by.return_value.first.return_value = None
                
                categoria_id = _obtener_categoria_todos()
                assert categoria_id is None

