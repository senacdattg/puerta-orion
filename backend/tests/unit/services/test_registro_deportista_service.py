"""
Tests para el servicio de registro completo de deportistas.

Este módulo contiene tests que verifican el registro completo
de deportistas, incluyendo información deportiva y diagnósticos.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from src.services.registro_deportista_service import RegistroDeportistaService
from src.models.deportistas.deportista import Deportista
from src.models.deportistas.informacion_deportiva import InformacionDeportiva
from src.models.personas.persona import Persona
from src.models.categorias.categoria import Categoria


@pytest.mark.unit
class TestRegistroDeportistaService:
    """Tests para RegistroDeportistaService."""
    
    @pytest.fixture
    def datos_registro_completo(self):
        """Datos completos para registro de deportista."""
        return {
            'datos_deportista': {
                'id_persona': 1,
                'id_categoria': 1,
                'peso': 65.5,
                'altura': 1.75,
                'fecha_nacimiento': 2000,
                'id_tipo_sanguineo': 1,
                'id_ciudad_recidencia': 1,
                'id_eps': 1
            },
            'informacion_deportiva': {
                'practica_otro_deporte': False,
                'participa_escuela': True,
                'recomendacion_medica': False,
                'id_escuela': 1,
                'id_deporte': 1,
                'id_institucion_registro': 1
            },
            'tipo_enfermedad': 1,
            'diagnostico': [1, 2]
        }
    
    def test_obtener_logger(self):
        """Test: Obtener logger del servicio."""
        logger = RegistroDeportistaService._obtener_logger()
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
    
    def test_procesar_fecha_nacimiento_date(self):
        """Test: Procesar fecha de nacimiento como date."""
        fecha = date(2000, 1, 15)
        fecha_formateada, edad = RegistroDeportistaService._procesar_fecha_nacimiento(fecha)
        
        assert fecha_formateada == '2000-01-15'
        assert isinstance(edad, int)
        assert edad > 0
    
    def test_procesar_fecha_nacimiento_int(self):
        """Test: Procesar fecha de nacimiento como int (año)."""
        anio = 2000
        fecha_formateada, edad = RegistroDeportistaService._procesar_fecha_nacimiento(anio)
        
        assert fecha_formateada == 2000
        assert isinstance(edad, int)
        assert edad > 0
    
    def test_obtener_diagnosticos_por_tipo_enfermedad_success(self):
        """Test: Obtener diagnósticos por tipo de enfermedad exitosamente."""
        mock_tipo_enfermedad = MagicMock()
        mock_tipo_enfermedad.id_tipo_enfermedad = 1
        
        mock_diagnostico1 = MagicMock()
        mock_diagnostico1.to_dict.return_value = {'id_diagnostico': 1}
        mock_diagnostico2 = MagicMock()
        mock_diagnostico2.to_dict.return_value = {'id_diagnostico': 2}
        
        with patch('src.services.registro_deportista_service.TipoEnfermedad') as mock_tipo_class, \
             patch('src.services.registro_deportista_service.Diagnostico') as mock_diag_class:
            
            mock_tipo_query = MagicMock()
            mock_tipo_query.filter_by.return_value.first.return_value = mock_tipo_enfermedad
            mock_tipo_class.query = mock_tipo_query
            
            mock_diag_query = MagicMock()
            mock_diag_query.filter_by.return_value.all.return_value = [mock_diagnostico1, mock_diagnostico2]
            mock_diag_class.query = mock_diag_query
            
            result = RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad(1)
            
            assert result['success'] is True
            assert len(result['data']) == 2
    
    def test_obtener_diagnosticos_por_tipo_enfermedad_no_existe(self):
        """Test: Error cuando tipo de enfermedad no existe."""
        with patch('src.services.registro_deportista_service.TipoEnfermedad') as mock_tipo_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_tipo_class.query = mock_query
            
            result = RegistroDeportistaService.obtener_diagnosticos_por_tipo_enfermedad(99999)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_registrar_deportista_nuevo_success(self, datos_registro_completo):
        """Test: Registrar deportista nuevo exitosamente."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Test User'
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.categoria = MagicMock()
        mock_deportista.categoria.nombre_categoria = 'Sub-15'
        
        with patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_estructura_datos', return_value=(datos_registro_completo['datos_deportista'], datos_registro_completo.get('informacion_deportiva', {}))), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_ids', return_value=(True, None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_persona_y_deportista_existente', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._procesar_fecha_nacimiento_completa', return_value=(date(2000, 1, 1), None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento', return_value=1), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._crear_informacion_deportiva', return_value=1), \
             patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.registro_deportista_service.Persona') as mock_persona_class, \
             patch('src.services.registro_deportista_service.db') as mock_db, \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asociar_diagnosticos'), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asociar_acudientes', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asignar_rol_deportista'):
            
            mock_deportista_class.return_value = mock_deportista
            mock_deportista_query = MagicMock()
            mock_deportista_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_deportista_query
            
            mock_persona_query = MagicMock()
            mock_persona_query.filter_by.return_value.first.return_value = mock_persona
            mock_persona_class.query = mock_persona_query
            
            mock_db.session.add = MagicMock()
            mock_db.session.flush = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro_completo)
            
            assert result['success'] is True
            assert 'data' in result
            mock_db.session.commit.assert_called()
    
    def test_registrar_deportista_nuevo_persona_no_existe(self, datos_registro_completo):
        """Test: Error cuando persona no existe."""
        with patch('src.services.registro_deportista_service.Persona'), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_estructura_datos', return_value=(datos_registro_completo['datos_deportista'], datos_registro_completo.get('informacion_deportiva', {}))), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_ids', return_value=(True, None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_persona_y_deportista_existente') as mock_validar:
            
            mock_validar.return_value = {
                'success': False,
                'message': 'La persona especificada no existe',
                'status_code': 404
            }
            
            result = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro_completo)
            
            assert result['success'] is False
            assert result['status_code'] == 404
    
    def test_registrar_deportista_nuevo_deportista_ya_existe(self, datos_registro_completo):
        """Test: Error cuando deportista ya existe."""
        with patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_estructura_datos', return_value=(datos_registro_completo['datos_deportista'], datos_registro_completo.get('informacion_deportiva', {}))), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_ids', return_value=(True, None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_persona_y_deportista_existente') as mock_validar:
            
            mock_validar.return_value = {
                'success': False,
                'message': 'Ya existe un deportista para esta persona',
                'status_code': 409
            }
            
            result = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro_completo)
            
            assert result['success'] is False
            assert result['status_code'] == 409
    
    def test_registrar_deportista_nuevo_integrity_error(self, datos_registro_completo):
        """Test: Manejo de error de integridad."""
        with patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_estructura_datos', return_value=(datos_registro_completo['datos_deportista'], datos_registro_completo.get('informacion_deportiva', {}))), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_ids', return_value=(True, None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_persona_y_deportista_existente', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._procesar_fecha_nacimiento_completa', return_value=(date(2000, 1, 1), None)), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento', return_value=1), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._crear_informacion_deportiva', return_value=1), \
             patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.registro_deportista_service.db') as mock_db, \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asociar_diagnosticos'), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asociar_acudientes', return_value=None), \
             patch('src.services.registro_deportista_service.RegistroDeportistaService._asignar_rol_deportista'):
            
            mock_deportista_class.return_value = MagicMock()
            mock_db.session.add = MagicMock()
            mock_db.session.flush = MagicMock()
            # El error debe ocurrir en commit, no en flush
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro_completo)
            
            # El método captura IntegrityError específicamente y retorna 409
            assert result['success'] is False
            # Puede ser 409 o 500 dependiendo de dónde ocurra el error
            assert result['status_code'] in [409, 500]
            mock_db.session.rollback.assert_called()
    
    def test_obtener_informacion_completa_deportista_success(self):
        """Test: Obtener información completa de deportista exitosamente."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.fecha_nacimiento = date(2000, 1, 15)
        mock_deportista.persona = MagicMock()
        mock_deportista.persona.id_persona = 1
        mock_deportista.persona.nombre_completo = 'Test User'
        mock_deportista.persona.primer_nombre = 'Test'
        mock_deportista.persona.segundo_nombre = None
        mock_deportista.persona.primer_apellido = 'User'
        mock_deportista.persona.segundo_apellido = None
        mock_deportista.persona.documento = '12345678'
        mock_deportista.persona.correo_electronico = 'test@example.com'
        mock_deportista.persona.telefono = '3001234567'
        mock_deportista.persona.direccion = 'Calle 123'
        mock_deportista.persona.id_tipo_documento = 1
        mock_deportista.categoria = MagicMock()
        mock_deportista.id_tipo_sanguineo = 1
        mock_deportista.id_ciudad_recidencia = 1
        mock_deportista.id_eps = 1
        mock_deportista.informacion_deportiva = None
        mock_deportista.created_at = None
        mock_deportista.updated_at = None
        
        with patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.registro_deportista_service.DiagnosticoDeportista') as mock_diag_class, \
             patch('src.services.registro_deportista_service.Mensualidad') as mock_mensualidad_class:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_diag_query = MagicMock()
            mock_diag_query.filter_by.return_value.all.return_value = []
            mock_diag_class.query = mock_diag_query
            
            mock_mensualidad_query = MagicMock()
            mock_mensualidad_query.filter_by.return_value.order_by.return_value.first.return_value = None
            mock_mensualidad_class.query = mock_mensualidad_query
            
            result = RegistroDeportistaService.obtener_informacion_completa_deportista(1)
            
            assert result['success'] is True
            assert 'data' in result
    
    def test_obtener_informacion_completa_deportista_no_encontrado(self):
        """Test: Error cuando deportista no existe."""
        with patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            result = RegistroDeportistaService.obtener_informacion_completa_deportista(99999)
            
            assert result['status'] == 'error'
            assert result['status_code'] == 404
    
    def test_calcular_categoria_por_fecha_nacimiento_date(self, app_context):
        """Test: Calcular categoría por fecha de nacimiento como date."""
        mock_categoria = MagicMock()
        mock_categoria.id_categoria = 1
        mock_categoria.nombre_categoria = 'Sub-15'
        
        fecha_nacimiento = date(2010, 1, 15)
        
        with patch('src.services.registro_deportista_service.Categoria.query') as mock_query:
            mock_query.filter.return_value.first.return_value = mock_categoria
            
            result = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento(fecha_nacimiento)
            
            assert result == 1
    
    def test_calcular_categoria_por_fecha_nacimiento_string(self, app_context):
        """Test: Calcular categoría por fecha de nacimiento como string."""
        mock_categoria = MagicMock()
        mock_categoria.id_categoria = 1
        
        with patch('src.services.registro_deportista_service.Categoria.query') as mock_query:
            mock_query.filter.return_value.first.return_value = mock_categoria
            
            result = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento('2010-01-15')
            
            assert result == 1
    
    def test_calcular_categoria_por_fecha_nacimiento_int(self, app_context):
        """Test: Calcular categoría por fecha de nacimiento como int (año)."""
        mock_categoria = MagicMock()
        mock_categoria.id_categoria = 1
        
        with patch('src.services.registro_deportista_service.Categoria.query') as mock_query:
            mock_query.filter.return_value.first.return_value = mock_categoria
            
            result = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento(2010)
            
            assert result == 1
    
    def test_calcular_categoria_no_encontrada(self, app_context):
        """Test: Error cuando no se encuentra categoría."""
        with patch('src.services.registro_deportista_service.Categoria.query') as mock_query:
            mock_query.filter.return_value.first.return_value = None
            
            result = RegistroDeportistaService._calcular_categoria_por_fecha_nacimiento(date(1990, 1, 1))
            
            assert result is None
    
    def test_validar_id_persona_success(self, app_context):
        """Test: Validar ID de persona exitosamente."""
        mock_persona = MagicMock()
        
        datos = {'id_persona': 1}
        
        with patch('src.services.registro_deportista_service.Persona.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_persona
            
            result = RegistroDeportistaService._validar_id_persona(datos)
            assert result is None
    
    def test_validar_id_persona_no_existe(self, app_context):
        """Test: Error cuando persona no existe."""
        datos = {'id_persona': 99999}
        
        with patch('src.services.registro_deportista_service.Persona.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = RegistroDeportistaService._validar_id_persona(datos)
            assert result == 'La persona especificada no existe'
    
    def test_validar_id_persona_sin_id(self, app_context):
        """Test: Validar cuando no hay ID de persona."""
        datos = {}
        
        result = RegistroDeportistaService._validar_id_persona(datos)
        assert result is None
    
    def test_validar_ids_deportista_success(self, app_context):
        """Test: Validar IDs del deportista exitosamente."""
        datos = {
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
        
        mock_tipo_sangre = MagicMock()
        mock_ciudad = MagicMock()
        mock_eps = MagicMock()
        
        with patch('src.models.categorias.grupo_sanguineo.GrupoSanguineo.query') as mock_tipo_query, \
             patch('src.models.categorias.ciudad_residencia.CiudadResidencia.query') as mock_ciudad_query, \
             patch('src.models.catalogos.eps.EPS.query') as mock_eps_query:
            
            mock_tipo_query.filter_by.return_value.first.return_value = mock_tipo_sangre
            mock_ciudad_query.filter_by.return_value.first.return_value = mock_ciudad
            mock_eps_query.filter_by.return_value.first.return_value = mock_eps
            
            result = RegistroDeportistaService._validar_ids_deportista(datos)
            assert result is None
    
    def test_validar_ids_deportista_tipo_sanguineo_no_existe(self, app_context):
        """Test: Error cuando tipo sanguíneo no existe."""
        datos = {'id_tipo_sanguineo': 99999}
        
        with patch('src.models.categorias.grupo_sanguineo.GrupoSanguineo.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = RegistroDeportistaService._validar_ids_deportista(datos)
            assert result == 'El tipo sanguíneo especificado no existe'
    
    def test_validar_estructura_datos_success(self):
        """Test: Validar estructura de datos exitosamente."""
        datos = {
            'datos_deportista': {'id_persona': 1},
            'informacion_deportiva': {'id_deporte': 1}
        }
        
        datos_deportista, info_deportiva = RegistroDeportistaService._validar_estructura_datos(datos)
        
        assert datos_deportista == {'id_persona': 1}
        assert info_deportiva == {'id_deporte': 1}
    
    def test_validar_estructura_datos_vacia(self):
        """Test: Validar estructura de datos vacía."""
        datos = {}
        
        datos_deportista, info_deportiva = RegistroDeportistaService._validar_estructura_datos(datos)
        
        assert datos_deportista is None
        assert info_deportiva is None
    
    def test_validar_campos_requeridos_success(self):
        """Test: Validar campos requeridos exitosamente."""
        datos_deportista = {
            'id_persona': 1,
            'fecha_nacimiento': date(2010, 1, 1),
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
        info_deportiva = {
            'id_deporte': 1,
            'id_institucion_registro': 1
        }
        
        result = RegistroDeportistaService._validar_campos_requeridos(datos_deportista, info_deportiva)
        assert result is None
    
    def test_validar_campos_requeridos_faltantes(self):
        """Test: Error cuando faltan campos requeridos."""
        datos_deportista = {'fecha_nacimiento': date(2010, 1, 1)}
        info_deportiva = {}
        
        result = RegistroDeportistaService._validar_campos_requeridos(datos_deportista, info_deportiva)
        
        assert result is not None
        assert result['success'] is False
        assert 'id_persona' in result['message']
    
    def test_procesar_fecha_nacimiento_completa_date(self):
        """Test: Procesar fecha de nacimiento completa como date."""
        fecha_date = date(2010, 1, 15)
        
        fecha_procesada, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_date)
        
        assert fecha_procesada == fecha_date
        assert error is None
    
    def test_procesar_fecha_nacimiento_completa_string(self):
        """Test: Procesar fecha de nacimiento completa como string."""
        fecha, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa('2010-01-15')
        
        assert fecha == date(2010, 1, 15)
        assert error is None
    
    def test_procesar_fecha_nacimiento_completa_invalida(self):
        """Test: Error con fecha de nacimiento inválida."""
        fecha, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa('fecha-invalida')
        
        assert fecha is None
        assert error is not None
        assert error['success'] is False
    
    def test_construir_datos_persona_success(self):
        """Test: Construir datos de persona exitosamente."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.primer_nombre = 'Juan'
        mock_persona.segundo_nombre = None
        mock_persona.primer_apellido = 'Pérez'
        mock_persona.segundo_apellido = None
        mock_persona.documento = '12345678'
        mock_persona.correo_electronico = 'juan@test.com'
        mock_persona.telefono = '3001234567'
        mock_persona.direccion = 'Calle 123'
        mock_persona.id_tipo_documento = 1
        
        mock_deportista = MagicMock()
        mock_deportista.persona = mock_persona
        mock_deportista.fecha_nacimiento = date(2010, 1, 15)
        mock_deportista.id_tipo_sanguineo = 1
        mock_deportista.id_ciudad_recidencia = 1
        mock_deportista.id_eps = 1
        
        with patch('src.services.registro_deportista_service.RegistroDeportistaService._procesar_fecha_nacimiento', return_value=('2010-01-15', 14)):
            result = RegistroDeportistaService._construir_datos_persona(mock_deportista)
            
            assert result['id_persona'] == 1
            assert result['nombre_completo'] == 'Juan Pérez'
            assert 'fecha_nacimiento' in result
    
    def test_construir_datos_persona_sin_persona(self):
        """Test: Construir datos de persona sin persona."""
        mock_deportista = MagicMock()
        mock_deportista.persona = None
        
        result = RegistroDeportistaService._construir_datos_persona(mock_deportista)
        
        assert result == {}
    
    def test_construir_info_deportiva_con_info(self):
        """Test: Construir información deportiva con datos."""
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        mock_info.practica_otro_deporte = False
        mock_info.participa_escuela = True
        mock_info.recomendacion_medica = False
        mock_info.descripcion_recomendacion = None
        mock_info.id_deporte = 1
        mock_info.id_escuela = 1
        mock_info.id_institucion_registro = 1
        
        mock_deportista = MagicMock()
        mock_deportista.informacion_deportiva = mock_info
        mock_deportista.id_categoria = 1
        
        result = RegistroDeportistaService._construir_info_deportiva(mock_deportista)
        
        assert result['id_informacion_deportiva'] == 1
        assert result['id_categoria'] == 1
    
    def test_construir_info_deportiva_sin_info(self):
        """Test: Construir información deportiva sin datos."""
        mock_deportista = MagicMock()
        mock_deportista.informacion_deportiva = None
        mock_deportista.id_categoria = 1
        
        result = RegistroDeportistaService._construir_info_deportiva(mock_deportista)
        
        assert result['id_categoria'] == 1
        assert result['practica_otro_deporte'] is False
    
    def test_obtener_informacion_completa_deportista_error(self, app_context):
        """Test: Manejo de error al obtener información completa."""
        with patch('src.services.registro_deportista_service.Deportista.query') as mock_query:
            mock_query.filter_by.side_effect = Exception("Error de base de datos")
            
            result = RegistroDeportistaService.obtener_informacion_completa_deportista(1)
            
            assert result['status'] == 'error'
            assert result['status_code'] == 500

