"""
Tests unitarios para funciones helper de personas_routes.py.

Cubre todas las funciones auxiliares que no están directamente expuestas como endpoints.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.routes.personas_routes import (
    _obtener_paginacion,
    _filtrar_por_estado,
    _aplicar_busqueda,
    _serializar_paginacion,
    _limpiar_texto,
    _validar_email_unico,
    _validar_documento_unico,
    _validar_relaciones,
    _preparar_actualizacion,
    _aplicar_cambios,
    _obtener_persona,
)
from src.utils.request_validators import RequestValidationError
from src.utils.validations import ValidationError


@pytest.mark.unit
@pytest.mark.personas
class TestObtenerPaginacion:
    """Tests para la función _obtener_paginacion"""

    def test_obtener_paginacion_defaults(self, app_context):
        """Test: Obtener paginación con valores por defecto."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/personas/personas'):
            # Act
            page, per_page = _obtener_paginacion()
            
            # Assert
            assert page == 1
            assert per_page == 10

    def test_obtener_paginacion_custom(self, app_context):
        """Test: Obtener paginación con valores personalizados."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/personas/personas?page=2&per_page=20'):
            # Act
            page, per_page = _obtener_paginacion()
            
            # Assert
            assert page == 2
            assert per_page == 20

    def test_obtener_paginacion_min_values(self, app_context):
        """Test: Obtener paginación con valores mínimos aplicados."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context('/api/personas/personas?page=0&per_page=-5'):
            # Act
            page, per_page = _obtener_paginacion()
            
            # Assert
            assert page == 1  # Debe aplicar mínimo
            assert per_page == 1  # Debe aplicar mínimo


@pytest.mark.unit
@pytest.mark.personas
class TestFiltrarPorEstado:
    """Tests para la función _filtrar_por_estado"""

    def test_filtrar_por_estado_none(self):
        """Test: No filtrar cuando estado es None."""
        # Arrange
        mock_query = MagicMock()
        
        # Act
        result = _filtrar_por_estado(mock_query, None)
        
        # Assert
        assert result == mock_query
        mock_query.filter_by.assert_not_called()

    def test_filtrar_por_estado_true(self):
        """Test: Filtrar por estado activo (true)."""
        # Arrange
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter_by.return_value = mock_filtered
        
        # Act
        result = _filtrar_por_estado(mock_query, 'true')
        
        # Assert
        mock_query.filter_by.assert_called_once_with(estado=True)
        assert result == mock_filtered

    def test_filtrar_por_estado_false(self):
        """Test: Filtrar por estado inactivo (false)."""
        # Arrange
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter_by.return_value = mock_filtered
        
        # Act
        result = _filtrar_por_estado(mock_query, 'false')
        
        # Assert
        mock_query.filter_by.assert_called_once_with(estado=False)
        assert result == mock_filtered


@pytest.mark.unit
@pytest.mark.personas
class TestAplicarBusqueda:
    """Tests para la función _aplicar_busqueda"""

    def test_aplicar_busqueda_vacia(self):
        """Test: No aplicar búsqueda cuando término está vacío."""
        # Arrange
        mock_query = MagicMock()
        
        # Act
        result = _aplicar_busqueda(mock_query, '')
        
        # Assert
        assert result == mock_query
        mock_query.filter.assert_not_called()

    def test_aplicar_busqueda_con_termino(self):
        """Test: Aplicar búsqueda con término válido."""
        # Arrange
        mock_query = MagicMock()
        mock_filtered = MagicMock()
        mock_query.filter.return_value = mock_filtered
        
        # Act
        result = _aplicar_busqueda(mock_query, 'Juan')
        
        # Assert
        mock_query.filter.assert_called_once()
        assert result == mock_filtered


@pytest.mark.unit
@pytest.mark.personas
class TestSerializarPaginacion:
    """Tests para la función _serializar_paginacion"""

    def test_serializar_paginacion_completa(self):
        """Test: Serializar información completa de paginación."""
        # Arrange
        mock_paginado = MagicMock()
        mock_paginado.page = 2
        mock_paginado.per_page = 10
        mock_paginado.total = 25
        mock_paginado.pages = 3
        mock_paginado.has_next = True
        mock_paginado.has_prev = True
        
        # Act
        result = _serializar_paginacion(mock_paginado)
        
        # Assert
        assert result['page'] == 2
        assert result['per_page'] == 10
        assert result['total'] == 25
        assert result['pages'] == 3
        assert result['has_next'] is True
        assert result['has_prev'] is True


@pytest.mark.unit
@pytest.mark.personas
class TestLimpiarTexto:
    """Tests para la función _limpiar_texto"""

    def test_limpiar_texto_none(self):
        """Test: Retornar None cuando el valor es None."""
        # Act
        result = _limpiar_texto(None)
        
        # Assert
        assert result is None

    def test_limpiar_texto_string(self):
        """Test: Limpiar texto normal."""
        # Act
        result = _limpiar_texto('  Juan  Pérez  ')
        
        # Assert
        assert result == 'Juan Pérez'

    def test_limpiar_texto_number(self):
        """Test: Limpiar texto desde número."""
        # Act
        result = _limpiar_texto(123)
        
        # Assert
        assert isinstance(result, str)
        assert result == '123'

    def test_limpiar_texto_vacio(self):
        """Test: Retornar None cuando el texto queda vacío."""
        # Act
        result = _limpiar_texto('   ')
        
        # Assert
        assert result is None


@pytest.mark.unit
@pytest.mark.personas
class TestValidarEmailUnico:
    """Tests para la función _validar_email_unico"""

    def test_validar_email_unico_no_duplicado(self):
        """Test: No lanzar error cuando el email es único."""
        # Arrange
        with patch('src.routes.personas_routes.Persona') as mock_persona:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.filter.return_value.first.return_value = None
            mock_persona.query = mock_query
            
            # Act & Assert - No debe lanzar excepción
            _validar_email_unico(1, 'test@example.com')

    def test_validar_email_unico_duplicado(self):
        """Test: Lanzar error cuando el email está duplicado."""
        # Arrange
        mock_persona_existente = MagicMock()
        with patch('src.routes.personas_routes.Persona') as mock_persona:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.filter.return_value.first.return_value = mock_persona_existente
            mock_persona.query = mock_query
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _validar_email_unico(1, 'duplicado@example.com')
            
            assert exc_info.value.status_code == 400
            assert 'email' in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.personas
class TestValidarDocumentoUnico:
    """Tests para la función _validar_documento_unico"""

    def test_validar_documento_unico_no_duplicado(self):
        """Test: No lanzar error cuando el documento es único."""
        # Arrange
        with patch('src.routes.personas_routes.Persona') as mock_persona:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.filter.return_value.first.return_value = None
            mock_persona.query = mock_query
            
            # Act & Assert - No debe lanzar excepción
            _validar_documento_unico(1, '12345678')

    def test_validar_documento_unico_duplicado(self):
        """Test: Lanzar error cuando el documento está duplicado."""
        # Arrange
        mock_persona_existente = MagicMock()
        with patch('src.routes.personas_routes.Persona') as mock_persona:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.filter.return_value.first.return_value = mock_persona_existente
            mock_persona.query = mock_query
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _validar_documento_unico(1, '12345678')
            
            assert exc_info.value.status_code == 400
            assert 'documento' in str(exc_info.value).lower()


@pytest.mark.unit
@pytest.mark.personas
class TestValidarRelaciones:
    """Tests para la función _validar_relaciones"""

    def test_validar_relaciones_sin_campos(self):
        """Test: No validar cuando no hay campos de relación."""
        # Act & Assert - No debe lanzar excepción
        _validar_relaciones({})

    def test_validar_relaciones_tipo_documento_valido(self):
        """Test: Validar tipo de documento válido."""
        # Arrange
        mock_tipo_doc = MagicMock()
        with patch('src.routes.personas_routes.TipoDocumento') as mock_tipo:
            mock_query = MagicMock()
            mock_query.get.return_value = mock_tipo_doc
            mock_tipo.query = mock_query
            
            # Act & Assert - No debe lanzar excepción
            _validar_relaciones({'id_tipo_documento': 1})

    def test_validar_relaciones_tipo_documento_invalido(self):
        """Test: Lanzar error cuando tipo de documento no existe."""
        # Arrange
        with patch('src.routes.personas_routes.TipoDocumento') as mock_tipo:
            mock_query = MagicMock()
            mock_query.get.return_value = None
            mock_tipo.query = mock_query
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _validar_relaciones({'id_tipo_documento': 999})
            
            assert exc_info.value.status_code == 400

    def test_validar_relaciones_sexo_valido(self):
        """Test: Validar sexo válido."""
        # Arrange
        mock_sexo = MagicMock()
        with patch('src.routes.personas_routes.Sexo') as mock_sexo_model:
            mock_query = MagicMock()
            mock_query.get.return_value = mock_sexo
            mock_sexo_model.query = mock_query
            
            # Act & Assert - No debe lanzar excepción
            _validar_relaciones({'id_sexo': 1})

    def test_validar_relaciones_sexo_invalido(self):
        """Test: Lanzar error cuando sexo no existe."""
        # Arrange
        with patch('src.routes.personas_routes.Sexo') as mock_sexo:
            mock_query = MagicMock()
            mock_query.get.return_value = None
            mock_sexo.query = mock_query
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _validar_relaciones({'id_sexo': 999})
            
            assert exc_info.value.status_code == 400


@pytest.mark.unit
@pytest.mark.personas
class TestPrepararActualizacion:
    """Tests para la función _preparar_actualizacion"""

    def test_preparar_actualizacion_email_valido(self):
        """Test: Preparar actualización con email válido."""
        # Arrange
        data = {'correo_electronico': 'test@example.com'}
        
        with patch('src.utils.validations.validate_email', return_value='test@example.com'):
            with patch('src.routes.personas_routes._validar_email_unico'):
                # Act
                cambios = _preparar_actualizacion(1, data)
                
                # Assert
                assert cambios['correo_electronico'] == 'test@example.com'

    def test_preparar_actualizacion_email_invalido(self):
        """Test: Lanzar error cuando email es inválido."""
        # Arrange
        data = {'correo_electronico': 'email-invalido'}
        
        with patch('src.utils.validations.validate_email') as mock_validate:
            mock_validate.side_effect = ValidationError('Email inválido')
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _preparar_actualizacion(1, data)
            
            assert exc_info.value.status_code == 400

    def test_preparar_actualizacion_telefono_valido(self):
        """Test: Preparar actualización con teléfono válido."""
        # Arrange
        data = {'telefono': '3001234567'}
        
        with patch('src.utils.validations.validate_phone', return_value='3001234567'):
                # Act
                cambios = _preparar_actualizacion(1, data)
                
                # Assert
                assert cambios['telefono'] == '3001234567'

    def test_preparar_actualizacion_telefono_invalido(self):
        """Test: Lanzar error cuando teléfono es inválido."""
        # Arrange
        data = {'telefono': '123'}  # Muy corto
        
        with patch('src.utils.validations.validate_phone') as mock_validate:
            mock_validate.side_effect = ValidationError('Teléfono inválido')
            
            # Act & Assert
            with pytest.raises(RequestValidationError) as exc_info:
                _preparar_actualizacion(1, data)
            
            assert exc_info.value.status_code == 400

    def test_preparar_actualizacion_documento_valido(self):
        """Test: Preparar actualización con documento válido."""
        # Arrange
        data = {'documento': '12345678'}
        
        with patch('src.utils.validations.validate_document', return_value='12345678'):
            with patch('src.routes.personas_routes._validar_documento_unico'):
                # Act
                cambios = _preparar_actualizacion(1, data)
                
                # Assert
                assert cambios['documento'] == '12345678'

    def test_preparar_actualizacion_campos_texto(self):
        """Test: Preparar actualización con campos de texto."""
        # Arrange
        data = {
            'primer_nombre': '  Juan  ',
            'primer_apellido': '  Pérez  ',
            'direccion': '  Calle 123  '
        }
        
        with patch('src.routes.personas_routes._limpiar_texto') as mock_limpiar:
            mock_limpiar.side_effect = lambda x: x.strip() if x else None
            
            # Act
            cambios = _preparar_actualizacion(1, data)
            
            # Assert
            assert 'primer_nombre' in cambios
            assert 'primer_apellido' in cambios
            assert 'direccion' in cambios

    def test_preparar_actualizacion_campos_relacion(self):
        """Test: Preparar actualización con campos de relación."""
        # Arrange
        data = {
            'id_tipo_documento': 1,
            'id_sexo': 2,
            'estado': True
        }
        
        # Act
        cambios = _preparar_actualizacion(1, data)
        
        # Assert
        assert cambios['id_tipo_documento'] == 1
        assert cambios['id_sexo'] == 2
        assert cambios['estado'] is True


@pytest.mark.unit
@pytest.mark.personas
class TestAplicarCambios:
    """Tests para la función _aplicar_cambios"""

    def test_aplicar_cambios_success(self):
        """Test: Aplicar cambios exitosamente."""
        # Arrange
        mock_persona = MagicMock()
        cambios = {
            'primer_nombre': 'Juan',
            'telefono': '3001234567',
            'estado': True
        }
        
        # Act
        _aplicar_cambios(mock_persona, cambios)
        
        # Assert
        assert mock_persona.primer_nombre == 'Juan'
        assert mock_persona.telefono == '3001234567'
        assert mock_persona.estado is True

    def test_aplicar_cambios_vacio(self):
        """Test: Aplicar cambios vacíos (no debe fallar)."""
        # Arrange
        mock_persona = MagicMock()
        cambios = {}
        
        # Act & Assert - No debe lanzar excepción
        _aplicar_cambios(mock_persona, cambios)


@pytest.mark.unit
@pytest.mark.personas
class TestObtenerPersona:
    """Tests para la función _obtener_persona"""

    def test_obtener_persona_success(self):
        """Test: Obtener persona exitosamente."""
        # Arrange
        mock_persona = MagicMock()
        with patch('src.routes.personas_routes.Persona') as mock_persona_model:
            mock_query = MagicMock()
            mock_query.get.return_value = mock_persona
            mock_persona_model.query = mock_query
            
            # Act
            result = _obtener_persona(1)
            
            # Assert
            assert result == mock_persona
            mock_query.get.assert_called_once_with(1)

    def test_obtener_persona_no_encontrada(self):
        """Test: Retornar None cuando persona no existe."""
        # Arrange
        with patch('src.routes.personas_routes.Persona') as mock_persona_model:
            mock_query = MagicMock()
            mock_query.get.return_value = None
            mock_persona_model.query = mock_query
            
            # Act
            result = _obtener_persona(999)
            
            # Assert
            assert result is None

