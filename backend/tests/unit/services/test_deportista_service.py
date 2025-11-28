"""
Tests for deportista service.

This module contains tests that verify CRUD operations for deportistas,
including creation, retrieval, listing, and update operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from src.services.deportista_service import DeportistaService
from src.models.deportistas.deportista import Deportista
from src.models.personas.persona import Persona
from src.models.deportistas.informacion_deportiva import InformacionDeportiva


@pytest.mark.unit
class TestDeportistaService:
    """Tests for DeportistaService."""
    
    @pytest.fixture
    def datos_deportista_validos(self):
        """Valid deportista data for testing."""
        return {
            'id_persona': 1,
            'id_categoria': 1,
            'peso': 65.5,
            'altura': 1.75,
            'fecha_nacimiento': date(2000, 1, 15),
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
    
    def test_crear_deportista_success(self, datos_deportista_validos):
        """Test: Successful deportista creation."""
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None) as mock_validar_campos, \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None) as mock_validar_persona, \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=None) as mock_validar_deportista, \
             patch('src.services.deportista_service.DeportistaService._procesar_fecha_nacimiento', return_value=(date(2000, 1, 15), None)) as mock_fecha, \
             patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            mock_deportista.to_dict.return_value = {'id_deportista': 1}
            mock_deportista_class.return_value = mock_deportista
            
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is True
            assert result['status_code'] == 201
            assert 'data' in result
            mock_validar_campos.assert_called_once()
            mock_validar_persona.assert_called_once()
            mock_validar_deportista.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_crear_deportista_missing_fields(self):
        """Test: Deportista creation with missing required fields."""
        datos_incompletos = {
            'id_persona': 1
            # Missing id_categoria
        }
        
        error_response = {
            'success': False,
            'message': 'Campos requeridos faltantes: id_categoria',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=error_response):
            result = DeportistaService.crear_deportista(datos_incompletos)
            
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_crear_deportista_persona_no_existe(self, datos_deportista_validos):
        """Test: Deportista creation when person doesn't exist."""
        error_response = {
            'success': False,
            'message': 'La persona especificada no existe',
            'status_code': 404
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=error_response):
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_crear_deportista_ya_existe(self, datos_deportista_validos):
        """Test: Deportista creation when deportista already exists."""
        error_response = {
            'success': False,
            'message': 'Ya existe un deportista para esta persona',
            'status_code': 409
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=error_response):
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is False
            assert result['status_code'] == 409
    
    def test_crear_deportista_integrity_error(self, datos_deportista_validos):
        """Test: Deportista creation with integrity error."""
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._procesar_fecha_nacimiento', return_value=(date(2000, 1, 15), None)), \
             patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_deportista_class.return_value = MagicMock()
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is False
            assert result['status_code'] == 409
            mock_db.session.rollback.assert_called_once()
    
    def test_obtener_deportista_success(self):
        """Test: Successful deportista retrieval."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = None
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.obtener_deportista(1)
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert 'data' in result
    
    def test_obtener_deportista_not_found(self):
        """Test: Deportista retrieval when deportista doesn't exist."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.obtener_deportista(999)
            
            assert result['success'] is False
            assert result['status_code'] == 404
            assert 'Deportista no encontrado' in result['message']
    
    def test_obtener_deportista_with_persona(self):
        """Test: Deportista retrieval with persona data."""
        mock_persona = MagicMock()
        mock_persona.to_dict.return_value = {'id_persona': 1}
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = mock_persona
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.obtener_deportista(1)
            
            assert result['success'] is True
            assert 'persona' in result['data']
    
    def test_listar_deportistas_success(self):
        """Test: Successful deportistas listing."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = None
        mock_deportista.categoria = None
        
        mock_paginacion = MagicMock()
        mock_paginacion.items = [mock_deportista]
        mock_paginacion.page = 1
        mock_paginacion.pages = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 1
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.paginate.return_value = mock_paginacion
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.listar_deportistas(page=1, per_page=10)
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
            assert 'pagination' in result
    
    def test_listar_deportistas_with_persona(self):
        """Test: Deportistas listing with persona data."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test User'
        mock_persona.primer_nombre = 'Test'
        mock_persona.segundo_nombre = None
        mock_persona.primer_apellido = 'User'
        mock_persona.segundo_apellido = None
        mock_persona.correo_electronico = 'test@example.com'
        mock_persona.telefono = '3001234567'
        mock_persona.direccion = 'Calle 123'
        mock_persona.documento = '12345678'
        mock_persona.to_dict.return_value = {'id_persona': 1}
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_usuario.id_usuario = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = mock_persona
        mock_deportista.categoria = None
        
        mock_paginacion = MagicMock()
        mock_paginacion.items = [mock_deportista]
        mock_paginacion.page = 1
        mock_paginacion.pages = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 1
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.Usuario') as mock_usuario_class:
            
            mock_deportista_query = MagicMock()
            mock_deportista_query.paginate.return_value = mock_paginacion
            mock_deportista_class.query = mock_deportista_query
            
            mock_usuario_query = MagicMock()
            mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_usuario_query
            
            result = DeportistaService.listar_deportistas(page=1, per_page=10)
            
            assert result['success'] is True
            assert result['data'][0]['nombre'] == 'Test User'
            assert result['data'][0]['id_usuario'] == 1
    
    def test_actualizar_deportista_success(self):
        """Test: Successful deportista update."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        
        datos_actualizacion = {
            'peso': 70.0,
            'altura': 1.80
        }
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.commit = MagicMock()
            
            result = DeportistaService.actualizar_deportista(1, datos_actualizacion)
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert mock_deportista.peso == 70.0
            assert mock_deportista.altura == 1.80
            mock_db.session.commit.assert_called_once()
    
    def test_actualizar_deportista_not_found(self):
        """Test: Deportista update when deportista doesn't exist."""
        datos_actualizacion = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.actualizar_deportista(999, datos_actualizacion)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_actualizar_deportista_integrity_error(self):
        """Test: Deportista update with integrity error."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        datos_actualizacion = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista(1, datos_actualizacion)
            
            assert result['success'] is False
            assert result['status_code'] == 409
            mock_db.session.rollback.assert_called_once()
    
    def test_validar_campos_requeridos_success(self):
        """Test: Successful required fields validation."""
        datos = {
            'id_persona': 1,
            'id_categoria': 1
        }
        
        result = DeportistaService._validar_campos_requeridos(datos)
        
        assert result is None
    
    def test_validar_campos_requeridos_missing(self):
        """Test: Required fields validation with missing fields."""
        datos = {
            'id_persona': 1
            # Missing id_categoria
        }
        
        result = DeportistaService._validar_campos_requeridos(datos)
        
        assert result is not None
        assert result['success'] is False
        assert 'id_categoria' in result['message']
    
    def test_validar_persona_existente_success(self):
        """Test: Successful person existence validation."""
        mock_persona = MagicMock()
        
        with patch('src.services.deportista_service.Persona') as mock_persona_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_persona
            mock_persona_class.query = mock_query
            
            result = DeportistaService._validar_persona_existente(1)
            
            assert result is None
    
    def test_validar_persona_existente_not_found(self):
        """Test: Person existence validation when person doesn't exist."""
        with patch('src.services.deportista_service.Persona') as mock_persona_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_persona_class.query = mock_query
            
            result = DeportistaService._validar_persona_existente(999)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_validar_deportista_no_existente_success(self):
        """Test: Successful deportista non-existence validation."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService._validar_deportista_no_existente(1)
            
            assert result is None
    
    def test_validar_deportista_no_existente_already_exists(self):
        """Test: Deportista non-existence validation when deportista already exists."""
        mock_deportista = MagicMock()
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            result = DeportistaService._validar_deportista_no_existente(1)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 409
    
    def test_procesar_fecha_nacimiento_date(self):
        """Test: Date of birth processing with date object."""
        fecha = date(2000, 1, 15)
        
        fecha_result, error = DeportistaService._procesar_fecha_nacimiento(fecha)
        
        assert fecha_result == fecha
        assert error is None
    
    def test_procesar_fecha_nacimiento_int(self):
        """Test: Date of birth processing with integer (year)."""
        fecha = 2000
        
        fecha_result, error = DeportistaService._procesar_fecha_nacimiento(fecha)
        
        assert fecha_result == date(2000, 1, 1)
        assert error is None
    
    def test_procesar_fecha_nacimiento_string(self):
        """Test: Date of birth processing with ISO string."""
        fecha = '2000-01-15'
        
        fecha_result, error = DeportistaService._procesar_fecha_nacimiento(fecha)
        
        assert fecha_result == date(2000, 1, 15)
        assert error is None
    
    def test_procesar_fecha_nacimiento_invalid_string(self):
        """Test: Date of birth processing with invalid string."""
        fecha = 'invalid-date'
        
        fecha_result, error = DeportistaService._procesar_fecha_nacimiento(fecha)
        
        assert fecha_result is None
        assert error is not None
        assert error['success'] is False

