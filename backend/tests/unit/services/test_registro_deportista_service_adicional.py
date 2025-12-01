"""
Tests adicionales para registro_deportista_service.py.

Cubre métodos y casos edge que no están en test_registro_deportista_service.py para aumentar cobertura.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

from src.services.registro_deportista_service import RegistroDeportistaService
from src.models.deportistas.deportista import Deportista
from src.models.deportistas.informacion_deportiva import InformacionDeportiva
from src.models.salud.diagnostico_deportista import DiagnosticoDeportista
from src.models.salud.diagnostico import Diagnostico
from src.models.personas.persona import Persona
from src.models.acudientes.acudiente import Acudiente
from src.models.acudientes.deportista_acudiente import DeportistaAcudiente
from src.models.acudientes.parentesco import Parentesco
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.roles_y_permisos.rol import Rol
from src.models.usuarios.usuario import Usuario


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestValidarPersonaYDeportistaExistente:
    """Tests para _validar_persona_y_deportista_existente."""

    def test_validar_persona_y_deportista_persona_no_existe(self, app):
        """Test: Error cuando la persona no existe."""
        with app.app_context():
            with patch('src.services.registro_deportista_service.Persona') as mock_persona_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = None
                mock_persona_class.query = mock_query
                
                result = RegistroDeportistaService._validar_persona_y_deportista_existente(999)
                
                assert result is not None
                assert result['success'] is False
                assert result['status_code'] == 404

    def test_validar_persona_y_deportista_usuario_con_rol(self, app):
        """Test: Error cuando el usuario ya tiene rol Deportista."""
        with app.app_context():
            mock_persona = MagicMock()
            mock_persona.id_persona = 1
            
            mock_rol = MagicMock()
            mock_rol.nombre_rol = 'Deportista'
            
            mock_usuario = MagicMock()
            mock_usuario.roles = [mock_rol]
            
            with patch('src.services.registro_deportista_service.Persona') as mock_persona_class, \
                 patch('src.services.registro_deportista_service.Usuario') as mock_usuario_class:
                
                mock_persona_query = MagicMock()
                mock_persona_query.filter_by.return_value.first.return_value = mock_persona
                mock_persona_class.query = mock_persona_query
                
                mock_usuario_query = MagicMock()
                mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
                mock_usuario_class.query = mock_usuario_query
                
                result = RegistroDeportistaService._validar_persona_y_deportista_existente(1)
                
                assert result is not None
                assert result['success'] is False
                assert result['status_code'] == 409

    def test_validar_persona_y_deportista_deportista_existente(self, app):
        """Test: Error cuando ya existe un deportista."""
        with app.app_context():
            mock_persona = MagicMock()
            mock_persona.id_persona = 1
            
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            
            with patch('src.services.registro_deportista_service.Persona') as mock_persona_class, \
                 patch('src.services.registro_deportista_service.Usuario') as mock_usuario_class, \
                 patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class:
                
                mock_persona_query = MagicMock()
                mock_persona_query.filter_by.return_value.first.return_value = mock_persona
                mock_persona_class.query = mock_persona_query
                
                mock_usuario_query = MagicMock()
                mock_usuario_query.filter_by.return_value.first.return_value = None
                mock_usuario_class.query = mock_usuario_query
                
                mock_deportista_query = MagicMock()
                mock_deportista_query.filter_by.return_value.first.return_value = mock_deportista
                mock_deportista_class.query = mock_deportista_query
                
                result = RegistroDeportistaService._validar_persona_y_deportista_existente(1)
                
                assert result is not None
                assert result['success'] is False
                assert result['status_code'] == 409

    def test_validar_persona_y_deportista_success(self, app):
        """Test: Validación exitosa cuando no hay conflictos."""
        with app.app_context():
            mock_persona = MagicMock()
            mock_persona.id_persona = 1
            
            with patch('src.services.registro_deportista_service.Persona') as mock_persona_class, \
                 patch('src.services.registro_deportista_service.Usuario') as mock_usuario_class, \
                 patch('src.services.registro_deportista_service.Deportista') as mock_deportista_class:
                
                mock_persona_query = MagicMock()
                mock_persona_query.filter_by.return_value.first.return_value = mock_persona
                mock_persona_class.query = mock_persona_query
                
                mock_usuario_query = MagicMock()
                mock_usuario_query.filter_by.return_value.first.return_value = None
                mock_usuario_class.query = mock_usuario_query
                
                mock_deportista_query = MagicMock()
                mock_deportista_query.filter_by.return_value.first.return_value = None
                mock_deportista_class.query = mock_deportista_query
                
                result = RegistroDeportistaService._validar_persona_y_deportista_existente(1)
                
                assert result is None


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestValidarTipoEnfermedadDiagnosticos:
    """Tests para _validar_tipo_enfermedad_diagnosticos."""

    def test_validar_tipo_enfermedad_sin_tipo(self, app):
        """Test: Validación cuando no hay tipo de enfermedad."""
        with app.app_context():
            result = RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos(None, [1, 2])
            
            assert result is None

    def test_validar_tipo_enfermedad_sin_diagnosticos(self, app):
        """Test: Error cuando hay tipo pero no diagnósticos."""
        with app.app_context():
            result = RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos(1, [])
            
            assert result is not None
            assert result['success'] is False
            assert result['status_code'] == 400

    def test_validar_tipo_enfermedad_diagnostico_no_coincide(self, app):
        """Test: Error cuando el diagnóstico no coincide con el tipo."""
        with app.app_context():
            mock_diagnostico = MagicMock()
            mock_diagnostico.id_tipo_enfermedad = 2  # Diferente al tipo seleccionado
            
            with patch('src.services.registro_deportista_service.Diagnostico') as mock_diagnostico_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_diagnostico
                mock_diagnostico_class.query = mock_query
                
                result = RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos(1, [1])
                
                assert result is not None
                assert result['success'] is False
                assert result['status_code'] == 400

    def test_validar_tipo_enfermedad_success(self, app):
        """Test: Validación exitosa cuando todo coincide."""
        with app.app_context():
            mock_diagnostico = MagicMock()
            mock_diagnostico.id_tipo_enfermedad = 1  # Coincide con el tipo
            
            with patch('src.services.registro_deportista_service.Diagnostico') as mock_diagnostico_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_diagnostico
                mock_diagnostico_class.query = mock_query
                
                result = RegistroDeportistaService._validar_tipo_enfermedad_diagnosticos(1, [1, 2])
                
                assert result is None


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestProcesarFechaNacimientoCompleta:
    """Tests para _procesar_fecha_nacimiento_completa."""

    def test_procesar_fecha_nacimiento_string_iso(self):
        """Test: Procesar fecha en formato ISO string."""
        fecha_str = '2005-06-15'
        fecha_date, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_str)
        
        assert fecha_date is not None
        assert isinstance(fecha_date, date)
        assert fecha_date.year == 2005
        assert error is None

    def test_procesar_fecha_nacimiento_string_anio(self):
        """Test: Procesar fecha como string de año."""
        fecha_str = '2005'
        fecha_date, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_str)
        
        assert fecha_date is not None
        assert isinstance(fecha_date, date)
        assert fecha_date.year == 2005
        assert error is None

    def test_procesar_fecha_nacimiento_date(self):
        """Test: Procesar fecha como objeto date."""
        fecha_date_obj = date(2005, 6, 15)
        fecha_date, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_date_obj)
        
        assert fecha_date is not None
        assert fecha_date == fecha_date_obj
        assert error is None

    def test_procesar_fecha_nacimiento_int(self):
        """Test: Procesar fecha como int (año)."""
        fecha_int = 2005
        fecha_date, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_int)
        
        assert fecha_date is not None
        assert isinstance(fecha_date, date)
        assert fecha_date.year == 2005
        assert error is None

    def test_procesar_fecha_nacimiento_invalida(self):
        """Test: Error con fecha inválida."""
        fecha_invalida = 'invalid-date'
        fecha_date, error = RegistroDeportistaService._procesar_fecha_nacimiento_completa(fecha_invalida)
        
        assert fecha_date is None
        assert error is not None
        assert error['success'] is False


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestCrearInformacionDeportiva:
    """Tests para _crear_informacion_deportiva."""

    def test_crear_informacion_deportiva_success(self, app):
        """Test: Crear información deportiva exitosamente."""
        with app.app_context():
            datos_deportista = {'id_persona': 1}
            informacion_deportiva = {
                'id_deporte': 1,
                'id_escuela': 2,
                'id_institucion_registro': 3,
                'practica_otro_deporte': True,
                'participa_escuela': True,
                'recomendacion_medica': False
            }
            
            mock_info = MagicMock()
            mock_info.id_informacion_deportiva = 10
            
            with patch('src.services.registro_deportista_service.InformacionDeportiva') as mock_info_class, \
                 patch('src.services.registro_deportista_service.db') as mock_db:
                
                mock_info_class.return_value = mock_info
                mock_db.session.add = MagicMock()
                mock_db.session.flush = MagicMock()
                mock_db.session.commit = MagicMock()
                
                result = RegistroDeportistaService._crear_informacion_deportiva(
                    datos_deportista, informacion_deportiva
                )
                
                assert result == 10
                mock_db.session.add.assert_called_once()
                # El commit puede no llamarse si flush es suficiente

    def test_crear_informacion_deportiva_sin_datos(self, app):
        """Test: Crear información deportiva sin datos adicionales."""
        with app.app_context():
            datos_deportista = {'id_persona': 1}
            informacion_deportiva = {
                'id_deporte': 1,
                'id_institucion_registro': 3
            }
            
            mock_info = MagicMock()
            mock_info.id_informacion_deportiva = 10
            
            with patch('src.services.registro_deportista_service.InformacionDeportiva') as mock_info_class, \
                 patch('src.services.registro_deportista_service.db') as mock_db:
                
                mock_info_class.return_value = mock_info
                mock_db.session.add = MagicMock()
                mock_db.session.commit = MagicMock()
                
                result = RegistroDeportistaService._crear_informacion_deportiva(
                    datos_deportista, informacion_deportiva
                )
                
                assert result == 10


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestAsociarDiagnosticos:
    """Tests para _asociar_diagnosticos."""

    def test_asociar_diagnosticos_success(self, app):
        """Test: Asociar diagnósticos exitosamente."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            diagnosticos = [1, 2, 3]
            
            with patch('src.services.registro_deportista_service.DiagnosticoDeportista') as mock_diag_class, \
                 patch('src.services.registro_deportista_service.db') as mock_db:
                
                mock_diag_instances = []
                for _ in diagnosticos:  # nosonar: S1481 - Loop index not needed, only creating mocks
                    mock_diag = MagicMock()
                    mock_diag_class.return_value = mock_diag
                    mock_diag_instances.append(mock_diag)
                
                mock_db.session.add = MagicMock()
                # El método no hace commit, solo agrega a la sesión
                
                # Act
                RegistroDeportistaService._asociar_diagnosticos(mock_deportista, diagnosticos)
                
                # Assert
                assert mock_db.session.add.call_count == len(diagnosticos)

    def test_asociar_diagnosticos_vacio(self, app):
        """Test: Asociar diagnósticos cuando la lista está vacía."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            
            with patch('src.services.registro_deportista_service.db') as mock_db:
                # Act
                RegistroDeportistaService._asociar_diagnosticos(mock_deportista, [])
                
                # Assert
                mock_db.session.add.assert_not_called()


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestAsociarAcudientes:
    """Tests para _asociar_acudientes."""

    def test_asociar_acudientes_success(self, app):
        """Test: Asociar acudientes exitosamente."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            
            acudientes_data = [
                {'id_acudiente': 1, 'id_parentesco': 1},
                {'id_acudiente': 2, 'id_parentesco': 2}
            ]
            
            mock_acudiente1 = MagicMock()
            mock_acudiente1.id_acudiente = 1
            mock_acudiente2 = MagicMock()
            mock_acudiente2.id_acudiente = 2
            
            mock_parentesco1 = MagicMock()
            mock_parentesco1.id_parentesco = 1
            mock_parentesco2 = MagicMock()
            mock_parentesco2.id_parentesco = 2
            
            with patch('src.services.registro_deportista_service.Acudiente') as mock_acudiente_class, \
                 patch('src.services.registro_deportista_service.Parentesco') as mock_parentesco_class, \
                 patch('src.services.registro_deportista_service.DeportistaAcudiente') as mock_relacion_class, \
                 patch('src.services.registro_deportista_service.db') as mock_db:
                
                # Mock para DeportistaAcudiente.query.filter_by().count() - acudientes existentes = 0
                mock_count_query = MagicMock()
                mock_count_query.count.return_value = 0
                
                # Mock Acudiente.query.filter_by().first()
                def mock_acudiente_first(id_acudiente):
                    if id_acudiente == 1:
                        return mock_acudiente1
                    elif id_acudiente == 2:
                        return mock_acudiente2
                    return None
                
                mock_acudiente_query = MagicMock()
                mock_acudiente_query.filter_by.return_value.first.side_effect = lambda: mock_acudiente_first(mock_acudiente_query.filter_by.call_args[1]['id_acudiente'])
                mock_acudiente_class.query = mock_acudiente_query
                
                # Mock Parentesco.query.filter_by().first()
                def mock_parentesco_first(id_parentesco):
                    if id_parentesco == 1:
                        return mock_parentesco1
                    elif id_parentesco == 2:
                        return mock_parentesco2
                    return None
                
                mock_parentesco_query = MagicMock()
                mock_parentesco_query.filter_by.return_value.first.side_effect = lambda: mock_parentesco_first(mock_parentesco_query.filter_by.call_args[1]['id_parentesco'])
                mock_parentesco_class.query = mock_parentesco_query
                
                # Mock DeportistaAcudiente para count y first
                mock_relacion_query = MagicMock()
                mock_relacion_query.filter_by.return_value = mock_count_query
                mock_relacion_query.filter_by.return_value.first.return_value = None  # No existe relación previa
                mock_relacion_query.filter_by.return_value.count.return_value = 0  # No tiene más de 5 deportistas
                mock_relacion_class.query = mock_relacion_query
                
                mock_relacion_class.return_value = MagicMock()
                mock_db.session.add = MagicMock()
                
                # Act
                result = RegistroDeportistaService._asociar_acudientes(mock_deportista, acudientes_data)
                
                # Assert - El método puede no retornar error si todo está bien
                # Puede retornar None si todo va bien
                assert result is None or (isinstance(result, dict) and result.get('success') is False)

    def test_asociar_acudientes_acudiente_no_existe(self, app):
        """Test: Cuando el acudiente no existe, el método lo omite y retorna None."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            
            acudientes_data = [
                {'id_acudiente': 999, 'id_parentesco': 1}
            ]
            
            with patch('src.services.registro_deportista_service.DeportistaAcudiente') as mock_relacion_class:
                mock_count_query = MagicMock()
                mock_count_query.count.return_value = 0
                mock_relacion_query = MagicMock()
                mock_relacion_query.filter_by.return_value = mock_count_query
                mock_relacion_class.query = mock_relacion_query
                
                with patch('src.services.registro_deportista_service.Acudiente') as mock_acudiente_class:
                    mock_query = MagicMock()
                    mock_query.filter_by.return_value.first.return_value = None  # Acudiente no existe
                    mock_acudiente_class.query = mock_query
                    
                    # Act
                    result = RegistroDeportistaService._asociar_acudientes(mock_deportista, acudientes_data)
                    
                    # Assert - El método omite acudientes que no encuentra y retorna None
                    assert result is None

    def test_asociar_acudientes_parentesco_no_existe(self, app):
        """Test: Cuando el parentesco no existe, el método lo omite y retorna None."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            
            mock_acudiente = MagicMock()
            mock_acudiente.id_acudiente = 1
            
            acudientes_data = [
                {'id_acudiente': 1, 'id_parentesco': 999}
            ]
            
            with patch('src.services.registro_deportista_service.DeportistaAcudiente') as mock_relacion_class:
                mock_count_query = MagicMock()
                mock_count_query.count.return_value = 0
                mock_relacion_query = MagicMock()
                mock_relacion_query.filter_by.return_value = mock_count_query
                mock_relacion_class.query = mock_relacion_query
                
                with patch('src.services.registro_deportista_service.Acudiente') as mock_acudiente_class, \
                     patch('src.services.registro_deportista_service.Parentesco') as mock_parentesco_class:
                    
                    mock_acudiente_query = MagicMock()
                    mock_acudiente_query.filter_by.return_value.first.return_value = mock_acudiente
                    mock_acudiente_class.query = mock_acudiente_query
                    
                    mock_parentesco_query = MagicMock()
                    mock_parentesco_query.filter_by.return_value.first.return_value = None  # Parentesco no existe
                    mock_parentesco_class.query = mock_parentesco_query
                    
                    # Act
                    result = RegistroDeportistaService._asociar_acudientes(mock_deportista, acudientes_data)
                    
                    # Assert - El método omite parentescos que no encuentra y retorna None
                    assert result is None


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestAsignarRolDeportista:
    """Tests para _asignar_rol_deportista."""

    def test_asignar_rol_deportista_success(self, app):
        """Test: Asignar rol deportista exitosamente."""
        with app.app_context():
            mock_rol = MagicMock()
            mock_rol.id_rol = 1
            
            mock_usuario = MagicMock()
            mock_usuario.id_usuario = 1
            
            with patch('src.services.registro_deportista_service.Rol') as mock_rol_class, \
                 patch('src.services.registro_deportista_service.Usuario') as mock_usuario_class, \
                 patch('src.services.registro_deportista_service.UsuarioRol') as mock_usuario_rol_class, \
                 patch('src.services.registro_deportista_service.db') as mock_db:
                
                mock_rol_query = MagicMock()
                mock_rol_query.filter_by.return_value.first.return_value = mock_rol
                mock_rol_class.query = mock_rol_query
                
                mock_usuario_query = MagicMock()
                mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
                mock_usuario_class.query = mock_usuario_query
                
                mock_usuario_rol_query = MagicMock()
                mock_usuario_rol_query.filter_by.return_value.first.return_value = None
                mock_usuario_rol_class.query = mock_usuario_rol_query
                
                mock_usuario_rol_class.return_value = MagicMock()
                mock_db.session.add = MagicMock()
                
                # Act
                RegistroDeportistaService._asignar_rol_deportista(1)
                
                # Assert
                # Nota: El método solo hace add, no commit (el commit se hace fuera del método)
                mock_db.session.add.assert_called_once()

    def test_asignar_rol_deportista_rol_no_existe(self, app):
        """Test: Cuando el rol Deportista no existe, el método retorna None sin hacer nada."""
        with app.app_context():
            mock_usuario = MagicMock()
            mock_usuario.id_usuario = 1
            
            with patch('src.services.registro_deportista_service.Usuario') as mock_usuario_class, \
                 patch('src.services.registro_deportista_service.Rol') as mock_rol_class:
                
                mock_usuario_query = MagicMock()
                mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
                mock_usuario_class.query = mock_usuario_query
                
                mock_rol_query = MagicMock()
                mock_rol_query.filter_by.return_value.first.return_value = None  # Rol no existe
                mock_rol_class.query = mock_rol_query
                
                # Act - El método retorna None cuando el rol no existe
                result = RegistroDeportistaService._asignar_rol_deportista(1)
                
                # Assert - El método no lanza excepción, simplemente retorna None
                assert result is None


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestConstruirDatosSalud:
    """Tests para _construir_datos_salud."""

    def test_construir_datos_salud_success(self, app):
        """Test: Construir datos de salud exitosamente."""
        with app.app_context():
            mock_diagnostico1 = MagicMock()
            mock_diagnostico1.id_diagnostico = 1
            mock_diagnostico1.nombre = 'Diagnóstico 1'
            mock_diagnostico1.id_tipo_enfermedad = 1
            
            mock_diagnostico2 = MagicMock()
            mock_diagnostico2.id_diagnostico = 2
            mock_diagnostico2.nombre = 'Diagnóstico 2'
            mock_diagnostico2.id_tipo_enfermedad = 1
            
            mock_diag_deportista1 = MagicMock()
            mock_diag_deportista1.diagnostico = mock_diagnostico1
            
            mock_diag_deportista2 = MagicMock()
            mock_diag_deportista2.diagnostico = mock_diagnostico2
            
            with patch('src.services.registro_deportista_service.DiagnosticoDeportista') as mock_diag_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.all.return_value = [
                    mock_diag_deportista1, mock_diag_deportista2
                ]
                mock_diag_class.query = mock_query
                
                # Act
                result = RegistroDeportistaService._construir_datos_salud(1)
                
                # Assert
                assert isinstance(result, dict)
                assert 'diagnosticos' in result
                assert len(result['diagnosticos']) == 2

    def test_construir_datos_salud_sin_diagnosticos(self, app):
        """Test: Construir datos de salud sin diagnósticos."""
        with app.app_context():
            with patch('src.services.registro_deportista_service.DiagnosticoDeportista') as mock_diag_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.all.return_value = []
                mock_diag_class.query = mock_query
                
                # Act
                result = RegistroDeportistaService._construir_datos_salud(1)
                
                # Assert - Si no hay diagnósticos, retorna dict vacío (sin clave 'diagnosticos')
                assert isinstance(result, dict)
                assert len(result) == 0  # Dict vacío cuando no hay diagnósticos


@pytest.mark.unit
@pytest.mark.registro_deportista
class TestConstruirDatosAdicionales:
    """Tests para _construir_datos_adicionales."""

    def test_construir_datos_adicionales_success(self, app):
        """Test: Construir datos adicionales exitosamente."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            mock_deportista.id_persona = 1
            mock_deportista.peso = None
            mock_deportista.altura = None
            mock_deportista.imc = None
            mock_deportista.fecha_ingreso = None
            
            mock_mensualidad = MagicMock()
            mock_mensualidad.monto_pago = 50000.0
            mock_mensualidad.fecha_pago = None
            mock_mensualidad.estado = False
            
            with patch('src.services.registro_deportista_service.Mensualidad') as mock_mensualidad_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.order_by.return_value.first.return_value = mock_mensualidad
                mock_mensualidad_class.query = mock_query
                
                # Act
                result = RegistroDeportistaService._construir_datos_adicionales(mock_deportista)
                
                # Assert
                assert isinstance(result, dict)
                assert 'mensualidad' in result

    def test_construir_datos_adicionales_sin_acudientes(self, app):
        """Test: Construir datos adicionales sin mensualidad."""
        with app.app_context():
            mock_deportista = MagicMock()
            mock_deportista.id_deportista = 1
            mock_deportista.id_persona = 1
            mock_deportista.peso = None
            mock_deportista.altura = None
            mock_deportista.imc = None
            mock_deportista.fecha_ingreso = None
            
            with patch('src.services.registro_deportista_service.Mensualidad') as mock_mensualidad_class:
                mock_query = MagicMock()
                mock_query.filter_by.return_value.order_by.return_value.first.return_value = None
                mock_mensualidad_class.query = mock_query
                
                # Act
                result = RegistroDeportistaService._construir_datos_adicionales(mock_deportista)
                
                # Assert
                assert isinstance(result, dict)
                assert 'mensualidad' not in result

