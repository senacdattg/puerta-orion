"""
Tests adicionales para aumentar la cobertura de deportista_service.py.

Este módulo contiene tests específicos para cubrir las líneas de código
que actualmente no están cubiertas por los tests existentes.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from sqlalchemy.exc import IntegrityError

from src.services.deportista_service import DeportistaService, ERROR_DUPLICACION_DATOS, ERROR_DEPORTISTA_NO_ENCONTRADO
from src.models.deportistas.deportista import Deportista
from src.models.personas.persona import Persona
from src.models.usuarios.usuario import Usuario


@pytest.mark.unit
class TestDeportistaServiceCoverage:
    """Tests adicionales para aumentar cobertura de DeportistaService."""

    def test_procesar_fecha_nacimiento_tipo_invalido(self):
        """Test: Línea 133 - return None, None cuando el tipo no es date, int, str, ni None."""
        fecha_procesada, error = DeportistaService._procesar_fecha_nacimiento(123.45)
        
        assert fecha_procesada is None
        assert error is None

    def test_crear_deportista_exception_generica(self):
        """Test: Líneas 212-219 - except Exception as e en crear_deportista."""
        datos = {
            'id_persona': 1,
            'id_categoria': 1
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_campos_requeridos', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_persona_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_deportista_no_existente', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._procesar_fecha_nacimiento', return_value=(date(2000, 1, 15), None)), \
             patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_deportista_class.side_effect = Exception("Error inesperado")
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.crear_deportista(datos)
            
            assert result['success'] is False
            assert result['status_code'] == 500
            assert 'Error al crear deportista' in result['message']
            mock_db.session.rollback.assert_called_once()

    def test_listar_deportistas_sin_usuario(self, app_context):
        """Test: Línea 318 - datos['id_usuario'] = None cuando no hay usuario."""
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
        mock_persona.id_persona = 1
        
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
        
        with patch('src.services.deportista_service.Deportista.query') as mock_query, \
             patch('src.services.deportista_service.Usuario.query') as mock_usuario_query:
            
            mock_query.paginate.return_value = mock_paginacion
            mock_usuario_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService.listar_deportistas(page=1, per_page=10)
            
            assert result['success'] is True
            assert result['data'][0]['id_usuario'] is None

    def test_extraer_roles_usuario_con_objeto_rol(self):
        """Test: Línea 439 - roles_usuario.append(rol.nombre_rol) cuando rol tiene atributo nombre_rol."""
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Entrenador'
        
        usuario = {
            'roles': [mock_rol]
        }
        
        roles = DeportistaService._extraer_roles_usuario(usuario)
        
        assert 'Entrenador' in roles

    def test_validar_id_tipo_sanguineo_none(self):
        """Test: Línea 487 - return None cuando id_tipo_sanguineo is None."""
        result = DeportistaService._validar_id_tipo_sanguineo(None)
        assert result is None

    def test_validar_id_tipo_sanguineo_no_existe(self, app_context):
        """Test: Líneas 491-495 - Error cuando tipo sanguíneo no existe."""
        with patch('src.models.categorias.grupo_sanguineo.GrupoSanguineo.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_tipo_sanguineo(99999)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
            assert 'tipo sanguíneo' in result['message'].lower()

    def test_validar_id_ciudad_residencia_none(self):
        """Test: Línea 502 - return None cuando id_ciudad is None."""
        result = DeportistaService._validar_id_ciudad_residencia(None)
        assert result is None

    def test_validar_id_ciudad_residencia_no_existe(self, app_context):
        """Test: Líneas 506-510 - Error cuando ciudad no existe."""
        with patch('src.models.categorias.ciudad_residencia.CiudadResidencia.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_ciudad_residencia(99999)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
            assert 'ciudad de residencia' in result['message'].lower()

    def test_validar_id_ciudad_residencia_success(self, app_context):
        """Test: Línea 511 - return None al final cuando ciudad existe."""
        mock_ciudad = MagicMock()
        
        with patch('src.models.categorias.ciudad_residencia.CiudadResidencia.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_ciudad
            
            result = DeportistaService._validar_id_ciudad_residencia(1)
            assert result is None

    def test_validar_id_eps_none(self):
        """Test: Línea 517 - return None cuando id_eps is None."""
        result = DeportistaService._validar_id_eps(None)
        assert result is None

    def test_validar_id_eps_no_existe(self, app_context):
        """Test: Líneas 521-525 - Error cuando EPS no existe."""
        with patch('src.models.catalogos.eps.EPS.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            result = DeportistaService._validar_id_eps(99999)
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400
            assert 'eps' in result['message'].lower()

    def test_validar_ids_deportista_error_categoria(self):
        """Test: Línea 533 - return error cuando categoría no existe."""
        datos = {
            'id_categoria': 99999,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
        
        error_response = {
            'success': False,
            'message': 'La categoría especificada no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_categoria', return_value=error_response):
            result = DeportistaService._validar_ids_deportista(datos)
            assert result == error_response

    def test_validar_ids_deportista_error_tipo_sanguineo(self):
        """Test: Línea 537 - return error cuando tipo sanguíneo no existe."""
        datos = {
            'id_categoria': 1,
            'id_tipo_sanguineo': 99999,
            'id_ciudad_recidencia': 1,
            'id_eps': 1
        }
        
        error_response = {
            'success': False,
            'message': 'El tipo sanguíneo especificado no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_categoria', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_tipo_sanguineo', return_value=error_response):
            result = DeportistaService._validar_ids_deportista(datos)
            assert result == error_response

    def test_validar_ids_deportista_error_ciudad(self):
        """Test: Línea 541 - return error cuando ciudad no existe."""
        datos = {
            'id_categoria': 1,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 99999,
            'id_eps': 1
        }
        
        error_response = {
            'success': False,
            'message': 'La ciudad de residencia especificada no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_categoria', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_tipo_sanguineo', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_ciudad_residencia', return_value=error_response):
            result = DeportistaService._validar_ids_deportista(datos)
            assert result == error_response

    def test_validar_ids_deportista_error_eps(self):
        """Test: Línea 545 - return error cuando EPS no existe."""
        datos = {
            'id_categoria': 1,
            'id_tipo_sanguineo': 1,
            'id_ciudad_recidencia': 1,
            'id_eps': 99999
        }
        
        error_response = {
            'success': False,
            'message': 'La EPS especificada no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_categoria', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_tipo_sanguineo', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_ciudad_residencia', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_eps', return_value=error_response):
            result = DeportistaService._validar_ids_deportista(datos)
            assert result == error_response

    def test_procesar_campo_fecha_error_conversion(self):
        """Test: Línea 582 - return None, error cuando conversión de fecha falla."""
        error_response = {
            'success': False,
            'message': 'Formato de fecha_nacimiento inválido. Use YYYY-MM-DD',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._convertir_fecha_string', return_value=(None, error_response)):
            fecha, error = DeportistaService._procesar_campo_fecha('fecha_nacimiento', 'fecha-invalida')
            
            assert fecha is None
            assert error == error_response

    def test_procesar_campo_fecha_error_edad(self):
        """Test: Línea 585 - return None, error_edad cuando edad mínima no se cumple."""
        fecha_date = date.today().replace(year=date.today().year - 3)
        error_response = {
            'success': False,
            'message': 'El deportista debe tener mínimo 5 años de edad',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._convertir_fecha_string', return_value=(fecha_date, None)), \
             patch('src.services.deportista_service.DeportistaService._validar_edad_minima', return_value=error_response):
            fecha, error = DeportistaService._procesar_campo_fecha('fecha_nacimiento', '2021-01-01')
            
            assert fecha is None
            assert error == error_response

    def test_obtener_o_crear_info_deportiva_con_recomendacion(self):
        """Test: Líneas 629-632 - Bloque de sanitización de recomendación médica."""
        mock_deportista = MagicMock()
        mock_deportista.id_persona = 1
        mock_deportista.id_informacion_deportiva = None
        
        datos = {
            'recomendacion_medica': True,
            'descripcion_recomendacion': 'Test recomendación médica'
        }
        
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        
        with patch('src.services.deportista_service.InformacionDeportiva') as mock_info_class, \
             patch('src.services.deportista_service.db') as mock_db, \
             patch('src.services.deportista_service.sanitize_free_text', return_value='Test recomendación médica'):
            
            mock_info_class.return_value = mock_info
            mock_db.session.add = MagicMock()
            mock_db.session.flush = MagicMock()
            
            result = DeportistaService._obtener_o_crear_info_deportiva(mock_deportista, datos)
            
            assert result == mock_info
            mock_db.session.add.assert_called_once()

    def test_validar_ids_info_deportiva_error_deporte(self):
        """Test: Líneas 703-704 - return error cuando deporte no existe."""
        datos = {
            'id_escuela': 1,
            'id_deporte': 99999,
            'id_institucion_registro': 1
        }
        
        error_response = {
            'success': False,
            'message': 'El deporte especificado no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_escuela', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_deporte', return_value=error_response):
            result = DeportistaService._validar_ids_info_deportiva(datos)
            assert result == error_response

    def test_validar_ids_info_deportiva_error_institucion(self):
        """Test: Líneas 707-708 - return error cuando institución no existe."""
        datos = {
            'id_escuela': 1,
            'id_deporte': 1,
            'id_institucion_registro': 99999
        }
        
        error_response = {
            'success': False,
            'message': 'La institución de registro especificada no existe',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._validar_id_escuela', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_deporte', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._validar_id_institucion_registro', return_value=error_response):
            result = DeportistaService._validar_ids_info_deportiva(datos)
            assert result == error_response

    def test_actualizar_info_deportiva_descripcion_sin_recomendacion(self):
        """Test: Línea 729 - valor = None cuando recom_med es False."""
        mock_info = MagicMock()
        mock_info.recomendacion_medica = False
        
        datos = {
            'descripcion_recomendacion': 'Test descripción'
        }
        
        result = DeportistaService._actualizar_info_deportiva(mock_info, datos)
        
        assert result is None
        assert mock_info.descripcion_recomendacion is None

    def test_actualizar_diagnosticos_tipo_none_y_diagnosticos_vacio(self):
        """Test: Línea 766 - return None cuando tipo_enfermedad is None y diagnosticos está vacío."""
        mock_logger = MagicMock()
        
        result = DeportistaService._actualizar_diagnosticos(1, [], None, mock_logger)
        
        assert result is None

    def test_actualizar_diagnosticos_lista_vacia(self, app_context):
        """Test: Líneas 778-780 - Bloque cuando len(diagnosticos) == 0."""
        mock_logger = MagicMock()
        
        with patch('src.models.salud.diagnostico_deportista.DiagnosticoDeportista.query') as mock_query:
            mock_query.filter_by.return_value.delete = MagicMock()
            
            result = DeportistaService._actualizar_diagnosticos(1, [], 1, mock_logger)
            
            assert result is None
            mock_logger.info.assert_called_once()

    def test_actualizar_diagnosticos_con_validacion_error(self, app_context):
        """Test: Líneas 785-786 - return error cuando validación de diagnósticos falla."""
        mock_logger = MagicMock()
        error_response = {
            'success': False,
            'message': 'El diagnóstico no existe',
            'status_code': 400
        }
        
        with patch('src.models.salud.diagnostico_deportista.DiagnosticoDeportista.query') as mock_query, \
             patch('src.services.deportista_service.DeportistaService._validar_diagnosticos', return_value=error_response), \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query.filter_by.return_value.delete = MagicMock()
            mock_db.session.add = MagicMock()
            
            result = DeportistaService._actualizar_diagnosticos(1, [1, 2], 1, mock_logger)
            
            assert result == error_response

    def test_actualizar_deportista_exception_generica(self, app_context):
        """Test: except Exception as e en actualizar_deportista."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        datos = {'peso': 70.0}
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.commit.side_effect = Exception("Error inesperado")
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista(1, datos)
            
            assert result['success'] is False
            assert result['status_code'] == 500
            assert 'Error al actualizar deportista' in result['message']
            mock_db.session.rollback.assert_called_once()

    def test_actualizar_diagnosticos_con_tipo_enfermedad(self, app_context):
        """Test: Línea 783 - if tipo_enfermedad is not None en _actualizar_diagnosticos."""
        mock_logger = MagicMock()
        
        with patch('src.models.salud.diagnostico_deportista.DiagnosticoDeportista.query') as mock_query, \
             patch('src.services.deportista_service.DeportistaService._validar_diagnosticos', return_value=None), \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query.filter_by.return_value.delete = MagicMock()
            mock_db.session.add = MagicMock()
            
            result = DeportistaService._actualizar_diagnosticos(1, [1, 2], 1, mock_logger)
            
            assert result is None
            mock_query.filter_by.return_value.delete.assert_called_once()

    def test_procesar_actualizacion_info_deportiva_con_id_informacion(self, app_context):
        """Test: Líneas 841-845 - Bloque cuando deportista.id_informacion_deportiva existe."""
        mock_info = MagicMock()
        mock_info.id_informacion_deportiva = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_informacion_deportiva = 1
        
        datos = {'id_escuela': 1}
        
        with patch('src.services.deportista_service.DeportistaService._obtener_o_crear_info_deportiva', return_value=mock_info), \
             patch('src.services.deportista_service.DeportistaService._validar_ids_info_deportiva', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._actualizar_info_deportiva'):
            
            result = DeportistaService._procesar_actualizacion_info_deportiva(mock_deportista, datos)
            assert result is None

    def test_ejecutar_actualizaciones_error_info(self, app_context):
        """Test: Líneas 865-867 - return error_info cuando hay error en info deportiva."""
        mock_deportista = MagicMock()
        error_response = {
            'success': False,
            'message': 'Error en info deportiva',
            'status_code': 400
        }
        
        with patch('src.services.deportista_service.DeportistaService._procesar_actualizacion_deportista', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._procesar_actualizacion_info_deportiva', return_value=error_response), \
             patch('src.services.deportista_service.DeportistaService._actualizar_diagnosticos'):
            
            result = DeportistaService._ejecutar_actualizaciones(
                mock_deportista, {'peso': 70.0}, {'id_escuela': 1}, None, 1, None, None, MagicMock()
            )
            assert result == error_response

    def test_actualizar_deportista_completo_exception_generica(self, app_context):
        """Test: except Exception as e en actualizar_deportista_completo."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._ejecutar_actualizaciones', side_effect=Exception("Error inesperado")), \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista_completo(
                1, datos_deportista={'peso': 70.0}
            )
            
            assert result['success'] is False
            assert result['status_code'] == 500
            assert 'Error al actualizar deportista' in result['message']
            mock_db.session.rollback.assert_called_once()

    def test_actualizar_deportista_completo_integrity_error(self, app_context):
        """Test: except IntegrityError en actualizar_deportista_completo (líneas 931-938)."""
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class, \
             patch('src.services.deportista_service.DeportistaService._validar_datos_entrada', return_value=None), \
             patch('src.services.deportista_service.DeportistaService._ejecutar_actualizaciones', return_value=None), \
             patch('src.services.deportista_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_deportista
            mock_deportista_class.query = mock_query
            
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            result = DeportistaService.actualizar_deportista_completo(
                1, datos_deportista={'peso': 70.0}
            )
            
            assert result['success'] is False
            assert result['status_code'] == 409
            assert ERROR_DUPLICACION_DATOS in result['message']
            mock_db.session.rollback.assert_called_once()

    def test_obtener_deportista_exception(self, app_context):
        """Test: except Exception en obtener_deportista (líneas 257-263)."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.side_effect = Exception("Error inesperado")
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.obtener_deportista(1)
            
            assert result['success'] is False
            assert result['status_code'] == 500
            assert 'Error interno del servidor' in result['message']

    def test_listar_deportistas_exception(self, app_context):
        """Test: except Exception en listar_deportistas (líneas 346-352)."""
        with patch('src.services.deportista_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.paginate.side_effect = Exception("Error inesperado")
            mock_deportista_class.query = mock_query
            
            result = DeportistaService.listar_deportistas()
            
            assert result['success'] is False
            assert result['status_code'] == 500
            assert 'Error interno del servidor' in result['message']
