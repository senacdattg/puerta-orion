"""
Tests para el servicio de deportistas.

Este módulo contiene tests que verifican las operaciones CRUD
del servicio de deportistas, incluyendo validaciones y casos de error.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from src.services.deportista_service import DeportistaService
from src.models.deportistas.deportista import Deportista
from src.models.personas.persona import Persona
from src.models.categorias.categoria import Categoria


@pytest.mark.unit
class TestDeportistaService:
    """Tests para DeportistaService."""
    
    @pytest.fixture
    def datos_deportista_validos(self):
        """Datos válidos para crear un deportista."""
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
        """Test: Crear deportista exitosamente."""
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._procesar_fecha_nacimiento', return_value=(date(2000, 1, 15), None)), \
             patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            mock_deportista.to_dict.return_value = {'id_deportista': 1, 'id_persona': 1, 'id_categoria': 1}
            mock_deportista_class.return_value = mock_deportista
            
            mock_db.session.add = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is True
            assert result['status_code'] == 201
            assert 'data' in result
            assert 'id_deportista' in result['data']
            mock_db.session.commit.assert_called_once()
    
    def test_crear_deportista_missing_fields(self):
        """Test: Error cuando faltan campos requeridos."""
        datos_incompletos = {'id_persona': 1}
        
        result = DeportistaService.crear_deportista(datos_incompletos)
        
        assert result['success'] is False
        assert result['status_code'] == 400
        assert 'requeridos' in result['message'].lower()
    
    def test_crear_deportista_persona_no_existe(self, datos_deportista_validos):
        """Test: Error cuando la persona no existe."""
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
        """Test: Error cuando el deportista ya existe."""
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
    
    def test_crear_deportista_fecha_nacimiento_invalida(self, datos_deportista_validos):
        """Test: Error con fecha de nacimiento inválida."""
        datos_deportista_validos['fecha_nacimiento'] = 'fecha-invalida-12345'
        error_response = {
            'success': False,
            'message': 'Formato de fecha de nacimiento inválido',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._procesar_fecha_nacimiento', return_value=(None, error_response)):
            
            result = DeportistaService.crear_deportista(datos_deportista_validos)
            
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_crear_deportista_integrity_error(self, datos_deportista_validos):
        """Test: Manejo de error de integridad."""
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
        """Test: Obtener deportista exitosamente."""
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
    
    def test_obtener_deportista_no_encontrado(self):
        """Test: Error cuando deportista no existe."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.obtener_deportista(99999)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_obtener_deportista_con_persona(self):
        """Test: Obtener deportista con datos de persona."""
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
        """Test: Listar deportistas exitosamente."""
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
    
    def test_listar_deportistas_paginacion(self):
        """Test: Listar deportistas con paginación."""
        mock_paginacion = MagicMock()
        mock_paginacion.items = []
        mock_paginacion.page = 1
        mock_paginacion.pages = 0
        mock_paginacion.per_page = 5
        mock_paginacion.total = 0
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.paginate.return_value = mock_paginacion
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.listar_deportistas(page=1, per_page=5)
            
            assert result['success'] is True
            assert 'pagination' in result
            assert result['pagination']['page'] == 1
            assert result['pagination']['per_page'] == 5
    
    def test_listar_deportistas_vacio(self):
        """Test: Listar deportistas cuando no hay datos."""
        mock_paginacion = MagicMock()
        mock_paginacion.items = []
        mock_paginacion.page = 1
        mock_paginacion.pages = 0
        mock_paginacion.per_page = 10
        mock_paginacion.total = 0
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.paginate.return_value = mock_paginacion
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.listar_deportistas()
            
            assert result['success'] is True
            assert result['data'] == []
            assert result['pagination']['total'] == 0
    
    def test_actualizar_deportista_success(self):
        """Test: Actualizar deportista exitosamente."""
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
            assert mock_deportista.peso == pytest.approx(70.0)
            assert mock_deportista.altura == pytest.approx(1.80)
            mock_db.session.commit.assert_called_once()
    
    def test_actualizar_deportista_no_encontrado(self):
        """Test: Error al actualizar deportista inexistente."""
        datos = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.actualizar_deportista(99999, datos)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_actualizar_deportista_integrity_error(self):
        """Test: Manejo de error de integridad al actualizar."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        datos = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista(1, datos)
            
            assert result['success'] is False
            assert result['status_code'] == 409
            mock_db.session.rollback.assert_called_once()
    
    def test_validar_campos_requeridos_success(self):
        """Test: Validar campos requeridos exitosamente."""
        datos = {
            'id_persona': 1,
            'id_categoria': 1
        }
        
        result = DeportistaService._validar_campos_requeridos(datos)
        
        assert result is None
    
    def test_validar_campos_requeridos_faltantes(self):
        """Test: Error cuando faltan campos requeridos."""
        datos = {'id_persona': 1}
        
        result = DeportistaService._validar_campos_requeridos(datos)
        
        assert result is not None
        assert result['success'] is False
        assert result['status_code'] == 400
    
    def test_validar_persona_existente_success(self):
        """Test: Validar persona existente exitosamente."""
        mock_persona = MagicMock()
        
        with patch('src.services.deportista_service.Persona') as mock_persona_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_persona
            mock_persona_class.query = mock_query
            
            result = DeportistaService._validar_persona_existente(1)
            
            assert result is None
    
    def test_validar_persona_existente_no_existe(self):
        """Test: Error cuando persona no existe."""
        with patch('src.services.deportista_service.Persona') as mock_persona_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_persona_class.query = mock_query
            
            result = DeportistaService._validar_persona_existente(99999)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_validar_deportista_no_existente_success(self):
        """Test: Validar que deportista no existe exitosamente."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = DeportistaService._validar_deportista_no_existente(1)
            
            assert result is None
    
    def test_validar_deportista_no_existente_ya_existe(self):
        """Test: Error cuando deportista ya existe."""
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
        """Test: Procesar fecha de nacimiento como date."""
        fecha_date = date(2000, 1, 15)
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento(fecha_date)
        
        assert fecha_procesada == fecha_date
        assert error is None
    
    def test_procesar_fecha_nacimiento_int(self):
        """Test: Procesar fecha de nacimiento como int (año)."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento(2000)
        
        assert fecha_procesada == date(2000, 1, 1)
        assert error is None
    
    def test_procesar_fecha_nacimiento_string_iso(self):
        """Test: Procesar fecha de nacimiento como string ISO."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento('2000-01-15')
        
        assert fecha_procesada == date(2000, 1, 15)
        assert error is None
    
    def test_procesar_fecha_nacimiento_string_anio(self):
        """Test: Procesar fecha de nacimiento como string de año."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento('2000')
        
        assert fecha_procesada == date(2000, 1, 1)
        assert error is None
    
    def test_procesar_fecha_nacimiento_invalida(self):
        """Test: Error con fecha de nacimiento inválida."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento('fecha-invalida')
        
        assert fecha_procesada is None
        assert error is not None
        assert error['success'] is False
    
    def test_procesar_fecha_nacimiento_none(self):
        """Test: Procesar fecha de nacimiento None."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento(None)
        
        assert fecha_procesada is None
        assert error is None
    
    def test_obtener_logger(self):
        """Test: Obtener logger del servicio."""
        logger = DeportistaService._obtener_logger()
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
    
    def test_validar_datos_entrada_success(self):
        """Test: Validar datos de entrada exitosamente."""
        datos_deportista = {'peso': 70.0}
        
        result = DeportistaService._validar_datos_entrada(datos_deportista, None)
        assert result is None
    
    def test_validar_datos_entrada_con_info_deportiva(self):
        """Test: Validar datos de entrada con información deportiva."""
        datos_info = {'id_deporte': 1}
        
        result = DeportistaService._validar_datos_entrada(None, datos_info)
        assert result is None
    
    def test_validar_datos_entrada_vacio(self):
        """Test: Error cuando no se proporcionan datos."""
        result = DeportistaService._validar_datos_entrada(None, None)
        
        assert result is not None
        assert result['success'] is False
        assert result['status_code'] == 400
    
    def test_extraer_roles_usuario_dict(self):
        """Test: Extraer roles de usuario desde diccionario."""
        usuario = {
            'roles': [
                {'nombre_rol': 'Admin'},
                {'nombre': 'Usuario'},
                'Deportista'
            ]
        }
        
        roles = DeportistaService._extraer_roles_usuario(usuario)
        assert 'Admin' in roles
        assert 'Usuario' in roles
        assert 'Deportista' in roles
    
    def test_extraer_roles_usuario_vacio(self):
        """Test: Extraer roles de usuario vacío."""
        usuario = {}
        
        roles = DeportistaService._extraer_roles_usuario(usuario)
        assert roles == []
    
    def test_validar_permisos_campos_restrictos_success(self, app_context):
        """Test: Validar permisos de campos restrictos con permisos."""
        datos = {'peso': 70.0}
        usuario = {'roles': [{'nombre_rol': 'Acudiente'}]}
        
        result = DeportistaService._validar_permisos_campos_restrictos(datos, usuario)
        assert result is None
    
    def test_validar_permisos_campos_restrictos_sin_permiso(self, app_context):
        """Test: Error cuando no tiene permisos."""
        datos = {'peso': 70.0}
        usuario = {'roles': [{'nombre_rol': 'Deportista'}]}
        
        result = DeportistaService._validar_permisos_campos_restrictos(datos, usuario)
        assert result is not None
        assert result['success'] is False
        assert result['status_code'] == 403
    
    def test_validar_permisos_sin_usuario(self, app_context):
        """Test: Validar permisos sin usuario."""
        datos = {'peso': 70.0}
        
        result = DeportistaService._validar_permisos_campos_restrictos(datos, None)
        assert result is None
    
    def test_validar_id_categoria_success(self, app_context):
        """Test: Validar ID de categoría exitosamente."""
        mock_categoria = MagicMock()
        
        with patch('src.models.categorias.categoria.Categoria.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_categoria
            
            result = DeportistaService._validar_id_categoria(1)
            assert result is None
    
    def test_validar_id_categoria_no_existe(self, app_context):
        """Test: Error cuando categoría no existe."""
        with patch('src.models.categorias.categoria.Categoria.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_categoria(99999)
            assert result is not None
            assert result['success'] is False
    
    def test_validar_id_categoria_none(self, app_context):
        """Test: Validar ID de categoría None."""
        result = DeportistaService._validar_id_categoria(None)
        assert result is None
    
    def test_validar_id_tipo_sanguineo_success(self, app_context):
        """Test: Validar ID de tipo sanguíneo exitosamente."""
        mock_tipo = MagicMock()
        
        with patch('src.models.categorias.grupo_sanguineo.GrupoSanguineo.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_tipo
            
            result = DeportistaService._validar_id_tipo_sanguineo(1)
            assert result is None
    
    def test_validar_id_ciudad_residencia_success(self, app_context):
        """Test: Validar ID de ciudad exitosamente."""
        mock_ciudad = MagicMock()
        
        with patch('src.models.categorias.ciudad_residencia.CiudadResidencia.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_ciudad
            
            result = DeportistaService._validar_id_ciudad_residencia(1)
            assert result is None
    
    def test_validar_id_eps_success(self, app_context):
        """Test: Validar ID de EPS exitosamente."""
        mock_eps = MagicMock()
        
        with patch('src.models.catalogos.eps.EPS.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_eps
            
            result = DeportistaService._validar_id_eps(1)
            assert result is None
    
    def test_validar_ids_deportista_success(self, app_context):
        """Test: Validar todos los IDs del deportista exitosamente."""
        datos = {
            'id_categoria': 1,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_categoria', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_tipo_sanguineo', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_ciudad_residencia', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_eps', return_value=None):
            
            result = DeportistaService._validar_ids_deportista(datos)
            assert result is None
    
    def test_convertir_fecha_string_success(self):
        """Test: Convertir fecha string exitosamente."""
        fecha, error = DeportistaService._convertir_fecha_string('2000-01-15', 'fecha_nacimiento')
        
        assert fecha == date(2000, 1, 15)
        assert error is None
    
    def test_convertir_fecha_string_invalida(self):
        """Test: Error con fecha string inválida."""
        fecha, error = DeportistaService._convertir_fecha_string('fecha-invalida', 'fecha_nacimiento')
        
        assert fecha is None
        assert error is not None
        assert error['success'] is False
    
    def test_validar_edad_minima_success(self):
        """Test: Validar edad mínima exitosamente."""
        fecha_nacimiento = date(2010, 1, 1)  # Más de 5 años
        
        result = DeportistaService._validar_edad_minima(fecha_nacimiento)
        assert result is None
    
    def test_validar_edad_minima_menor(self):
        """Test: Error cuando edad es menor a 5 años."""
        fecha_nacimiento = date.today().replace(year=date.today().year - 3)  # 3 años
        
        result = DeportistaService._validar_edad_minima(fecha_nacimiento)
        assert result is not None
        assert result['success'] is False
    
    def test_procesar_campo_fecha_nacimiento_string(self):
        """Test: Procesar campo fecha_nacimiento como string."""
        fecha, error = DeportistaService._procesar_campo_fecha('fecha_nacimiento', '2010-01-15')
        
        assert fecha == date(2010, 1, 15)
        assert error is None
    
    def test_procesar_campo_fecha_ingreso_string(self):
        """Test: Procesar campo fecha_ingreso como string."""
        fecha, error = DeportistaService._procesar_campo_fecha('fecha_ingreso', '2024-01-01')
        
        assert fecha == date(2024, 1, 1)
        assert error is None
    
    def test_procesar_campo_fecha_date(self):
        """Test: Procesar campo fecha que ya es date."""
        fecha_date = date(2010, 1, 15)
        fecha, error = DeportistaService._procesar_campo_fecha('fecha_nacimiento', fecha_date)
        
        assert fecha == fecha_date
        assert error is None
    
    def test_actualizar_deportista_completo_success(self, app_context):
        """Test: Actualizar deportista completo exitosamente."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        mock_deportista.id_informacion_deportiva = None
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = None
        
        datos_deportista = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista.query') as mock_query, \
             patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._ejecutar_actualizaciones', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._construir_respuesta_actualizacion') as mock_resp, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_resp.return_value = {'id_deportista': 1}
            mock_db.session.commit = MagicMock()
            
            result = DeportistaService.actualizar_deportista_completo(
                1, datos_deportista=datos_deportista
            )
            
            assert result['success'] is True
            assert result['status_code'] == 200
    
    def test_actualizar_deportista_completo_no_encontrado(self, app_context):
        """Test: Error cuando deportista no existe."""
        with patch('src.services.deportista_service.Deportista.query') as mock_query, \
             patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=None):
            
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService.actualizar_deportista_completo(
                99999, datos_deportista={'peso': 70.0}
            )
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_actualizar_deportista_completo_sin_datos(self, app_context):
        """Test: Error cuando no se proporcionan datos."""
        error_validacion = {
            'success': False,
            'message': 'Debe proporcionar al menos datos_deportista o datos_informacion_deportiva',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=error_validacion):
            result = DeportistaService.actualizar_deportista_completo(1)
            
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_actualizar_deportista_completo_integrity_error(self, app_context):
        """Test: Manejo de error de integridad."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        with patch('src.services.deportista_service.Deportista.query') as mock_query, \
             patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._ejecutar_actualizaciones', return_value=None), \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista_completo(
                1, datos_deportista={'peso': 70.0}
            )
            
            assert result['success'] is False
            assert result['status_code'] == 409
    
    def test_listar_deportistas_con_persona_y_categoria(self, app_context):
        """Test: Listar deportistas con datos de persona y categoría."""
        mock_persona = MagicMock()
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.primer_nombre = 'Juan'
        mock_persona.segundo_nombre = None
        mock_persona.primer_apellido = 'Pérez'
        mock_persona.segundo_apellido = None
        mock_persona.correo_electronico = 'juan@test.com'
        mock_persona.telefono = '123456'
        mock_persona.direccion = 'Calle 123'
        mock_persona.documento = '12345678'
        mock_persona.to_dict.return_value = {'id_persona': 1}
        mock_persona.estado = True
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        
        mock_categoria = MagicMock()
        mock_categoria.id_categoria = 1
        mock_categoria.nombre_categoria = 'Infantil'
        mock_categoria.edad_minima = 5
        mock_categoria.edad_maxima = 10
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = mock_persona
        mock_deportista.categoria = mock_categoria
        
        mock_paginacion = MagicMock()
        mock_paginacion.items = [mock_deportista]
        mock_paginacion.page = 1
        mock_paginacion.pages = 1
        mock_paginacion.per_page = 10
        mock_paginacion.total = 1
        
        with patch('src.services.deportista_service.Deportista.query') as mock_query, \
             patch('src.services.deportista_service.Usuario.query') as mock_usuario_query:
            
            mock_query.paginate.return_value = mock_paginacion
            mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
            
            result = DeportistaService.listar_deportistas(page=1, per_page=10)
            
            assert result['success'] is True
            assert len(result['data']) == 1
            assert 'nombre' in result['data'][0]
            assert 'categoria' in result['data'][0]
    
    def test_listar_deportistas_error(self, app_context):
        """Test: Manejo de error al listar deportistas."""
        with patch('src.services.deportista_service.Deportista.query') as mock_query:
            mock_query.paginate.side_effect = Exception("Error de base de datos")
            
            result = DeportistaService.listar_deportistas()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_deportista_error(self, app_context):
        """Test: Manejo de error al obtener deportista."""
        with patch('src.services.deportista_service.Deportista.query') as mock_query:
            mock_query.filter_by.side_effect = Exception("Error de base de datos")
            
            result = DeportistaService.obtener_deportista(1)
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_actualizar_campos_deportista_success(self, app_context):
        """Test: Actualizar campos del deportista exitosamente."""
        mock_deportista = MagicMock()
        
        datos = {
            'peso': 70.0,
            'altura': 1.80,
            'fecha_nacimiento': date(2010, 1, 15),
            'id_categoria': 1
        }
        
        with patch('src.services.deportista_service.DeportistaService._procesar_campo_fecha', return_value=(date(2010, 1, 15), None)):
            result = DeportistaService._actualizar_campos_deportista(mock_deportista, datos)
            
            assert result is None
            assert mock_deportista.peso == pytest.approx(70.0)
            assert mock_deportista.altura == pytest.approx(1.80)
    
    def test_actualizar_campos_deportista_fecha_error(self, app_context):
        """Test: Error al procesar fecha."""
        mock_deportista = MagicMock()
        datos = {'fecha_nacimiento': 'fecha-invalida'}
        
        error_response = {
            'success': False,
            'message': 'Formato inválido',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._procesar_campo_fecha', return_value=(None, error_response)):
            result = DeportistaService._actualizar_campos_deportista(mock_deportista, datos)
            
            assert result == error_response
    
    def test_construir_respuesta_actualizacion(self, app_context):
        """Test: Construir respuesta de actualización."""
        mock_persona = MagicMock()
        mock_persona.to_dict.return_value = {'id_persona': 1}
        
        mock_info_deportiva = MagicMock()
        mock_info_deportiva.to_dict.return_value = {'id_informacion_deportiva': 1}
        
        mock_deportista = MagicMock()
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = mock_persona
        mock_deportista.informacion_deportiva = mock_info_deportiva
        
        result = DeportistaService._construir_respuesta_actualizacion(mock_deportista)
        
        assert 'id_deportista' in result
        assert 'persona' in result
        assert 'informacion_deportiva' in result
    
    def test_construir_respuesta_sin_relaciones(self, app_context):
        """Test: Construir respuesta sin relaciones."""
        mock_deportista = MagicMock()
        mock_deportista.to_dict.return_value = {'id_deportista': 1}
        mock_deportista.persona = None
        mock_deportista.informacion_deportiva = None
        
        result = DeportistaService._construir_respuesta_actualizacion(mock_deportista)
        
        assert 'id_deportista' in result
        assert 'persona' not in result
        assert 'informacion_deportiva' not in result
    
    def test_validar_id_escuela_success(self, app_context):
        """Test: Validar ID de escuela exitosamente."""
        mock_escuela = MagicMock()
        
        with patch('src.models.categorias.escuela.Escuela.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_escuela
            
            result = DeportistaService._validar_id_escuela(1)
            assert result is None
    
    def test_validar_id_escuela_no_existe(self, app_context):
        """Test: Error cuando escuela no existe."""
        with patch('src.models.categorias.escuela.Escuela.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_escuela(99999)
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_validar_id_escuela_none(self, app_context):
        """Test: Validar ID de escuela None."""
        result = DeportistaService._validar_id_escuela(None)
        assert result is None
    
    def test_validar_id_deporte_success(self, app_context):
        """Test: Validar ID de deporte exitosamente."""
        mock_deporte = MagicMock()
        
        with patch('src.models.categorias.deporte.Deporte.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_deporte
            
            result = DeportistaService._validar_id_deporte(1)
            assert result is None
    
    def test_validar_id_deporte_no_existe(self, app_context):
        """Test: Error cuando deporte no existe."""
        with patch('src.models.categorias.deporte.Deporte.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_deporte(99999)
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_validar_id_deporte_none(self, app_context):
        """Test: Validar ID de deporte None."""
        result = DeportistaService._validar_id_deporte(None)
        assert result is None
    
    def test_validar_id_institucion_registro_success(self, app_context):
        """Test: Validar ID de institución exitosamente."""
        mock_institucion = MagicMock()
        
        with patch('src.models.categorias.institucion_registro.InstitucionRegistro.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_institucion
            
            result = DeportistaService._validar_id_institucion_registro(1)
            assert result is None
    
    def test_validar_id_institucion_registro_no_existe(self, app_context):
        """Test: Error cuando institución no existe."""
        with patch('src.models.categorias.institucion_registro.InstitucionRegistro.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_institucion_registro(99999)
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_validar_id_institucion_registro_none(self, app_context):
        """Test: Validar ID de institución None."""
        result = DeportistaService._validar_id_institucion_registro(None)
        assert result is None
    
    def test_validar_ids_info_deportiva_success(self, app_context):
        """Test: Validar todos los IDs de información deportiva exitosamente."""
        datos = {
            'id_escuela': 1,
            'id_deporte': 1,
            'id_institucion_registro': 1
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_escuela', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_deporte', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_institucion_registro', return_value=None):
            
            result = DeportistaService._validar_ids_info_deportiva(datos)
            assert result is None
    
    def test_validar_ids_info_deportiva_con_error(self, app_context):
        """Test: Validar IDs cuando hay error."""
        datos = {'id_escuela': 99999}
        
        error_response = {
            'success': False,
            'message': 'La escuela especificada no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_escuela', return_value=error_response):
            
            result = DeportistaService._validar_ids_info_deportiva(datos)
            assert result == error_response
    
    def test_validar_diagnosticos_success(self, app_context):
        """Test: Validar diagnósticos exitosamente."""
        mock_diag1 = MagicMock()
        mock_diag1.id_tipo_enfermedad = 1
        mock_diag2 = MagicMock()
        mock_diag2.id_tipo_enfermedad = 1
        
        with patch('src.models.salud.diagnostico.Diagnostico.query') as mock_query:
            mock_query.filter_by.return_value.first.side_effect = [mock_diag1, mock_diag2]
            
            result = DeportistaService._validar_diagnosticos([1, 2], 1)
            assert result is None
    
    def test_validar_diagnosticos_no_existe(self, app_context):
        """Test: Error cuando diagnóstico no existe."""
        with patch('src.models.salud.diagnostico.Diagnostico.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_diagnosticos([99999], 1)
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_validar_diagnosticos_tipo_enfermedad_no_coincide(self, app_context):
        """Test: Error cuando diagnóstico no coincide con tipo de enfermedad."""
        mock_diag = MagicMock()
        mock_diag.id_tipo_enfermedad = 2  # Diferente al tipo esperado
        
        with patch('src.models.salud.diagnostico.Diagnostico.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_diag
            
            result = DeportistaService._validar_diagnosticos([1], 1)
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
    
    def test_validar_diagnosticos_sin_tipo_enfermedad(self, app_context):
        """Test: Validar diagnósticos sin tipo de enfermedad."""
        result = DeportistaService._validar_diagnosticos([1, 2], None)
        assert result is None
    
    def test_obtener_o_crear_info_deportiva_existente(self, app_context):
        """Test: Obtener información deportiva existente."""
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 1
        mock_deportista.id_informacion_deportiva = 1
        
        with patch('src.services.deportista_service.InformacionDeportiva.query') as mock_query:
            
            mock_query.filter_by.return_value.first.return_value = mock_info
            
            result = DeportistaService._obtener_o_crear_info_deportiva(mock_deportista, {})
            
            assert result == mock_info
    
    def test_obtener_o_crear_info_deportiva_nueva(self, app_context):
        """Test: Crear nueva información deportiva."""
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 1
        mock_deportista.id_informacion_deportiva = None
        
        datos = {
            'practica_otro_deporte': False,
            'participa_escuela': True,
            'recomendacion_medica': False,
            'id_escuela': 1,
            'id_deporte': 1
        }
        
        with patch('src.services.deportista_service.InformacionDeportiva') as mock_info_class, \
             patch('src.services.deportista_service.db') as mock_db, \
             patch('src.services.deportista_service.sanitize_free_text', return_value='test'):
            
            mock_info_class.return_value = mock_info
            mock_db.session.add = MagicMock()
            mock_db.session.flush = MagicMock()
            
            result = DeportistaService._obtener_o_crear_info_deportiva(mock_deportista, datos)
            
            assert result == mock_info
            mock_db.session.add.assert_called_once()
    
    def test_actualizar_info_deportiva_success(self, app_context):
        """Test: Actualizar información deportiva exitosamente."""
        mock_info = MagicMock()
        
        datos = {
            'practica_otro_deporte': True,
            'participa_escuela': False,
            'id_escuela': 2,
            'id_deporte': 2
        }
        
        with patch('src.services.deportista_service.sanitize_free_text', return_value='test'):
            result = DeportistaService._actualizar_info_deportiva(mock_info, datos)
            
            assert result is None
            assert mock_info.practica_otro_deporte is True
            assert mock_info.participa_escuela is False
    
    def test_actualizar_info_deportiva_con_recomendacion(self, app_context):
        """Test: Actualizar información deportiva con recomendación médica."""
        mock_info = MagicMock()
        mock_info.recomendacion_medica = False
        
        datos = {
            'recomendacion_medica': True,
            'descripcion_recomendacion': 'Test recomendación'
        }
        
        with patch('src.services.deportista_service.sanitize_free_text', return_value='Test recomendación'):
            result = DeportistaService._actualizar_info_deportiva(mock_info, datos)
            
            assert result is None
            assert mock_info.recomendacion_medica is True
    
    def test_actualizar_info_deportiva_sin_recomendacion(self, app_context):
        """Test: Actualizar información deportiva sin recomendación médica."""
        mock_info = MagicMock()
        mock_info.recomendacion_medica = True
        mock_info.descripcion_recomendacion = 'Test'
        
        datos = {
            'recomendacion_medica': False
        }
        
        result = DeportistaService._actualizar_info_deportiva(mock_info, datos)
        
        assert result is None
        assert mock_info.recomendacion_medica is False
        assert mock_info.descripcion_recomendacion is None
    
    def test_procesar_actualizacion_deportista_success(self, app_context):
        """Test: Procesar actualización de deportista exitosamente."""
        mock_deportista = MagicMock()
        datos = {'peso': 70.0}
        usuario = {'roles': [{'nombre_rol': 'Administrador'}]}
        
        with patch('src.services.deportista_service.DeportistaService._validar_permisos_campos_restrictos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_ids_deportista', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._actualizar_campos_deportista', return_value=None):
            
            result = DeportistaService._procesar_actualizacion_deportista(mock_deportista, datos, usuario)
            assert result is None
    
    def test_procesar_actualizacion_deportista_sin_datos(self, app_context):
        """Test: Procesar actualización sin datos de deportista."""
        mock_deportista = MagicMock()
        
        result = DeportistaService._procesar_actualizacion_deportista(mock_deportista, None, None)
        assert result is None
    
    def test_procesar_actualizacion_info_deportiva_success(self, app_context):
        """Test: Procesar actualización de información deportiva exitosamente."""
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_informacion_deportiva = 1
        mock_deportista.informacion_deportiva = mock_info
        
        datos = {'id_escuela': 1}
        
        with patch('src.services.deportista_service.DeportistaService._obtener_o_crear_info_deportiva', return_value=mock_info), \
             patch('src.services.deportista_service.DeportistaService._validar_ids_info_deportiva', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._actualizar_info_deportiva'):
            
            result = DeportistaService._procesar_actualizacion_info_deportiva(mock_deportista, datos)
            assert result is None
    
    def test_procesar_actualizacion_info_deportiva_sin_datos(self, app_context):
        """Test: Procesar actualización sin datos de información deportiva."""
        mock_deportista = MagicMock()
        
        result = DeportistaService._procesar_actualizacion_info_deportiva(mock_deportista, None)
        assert result is None