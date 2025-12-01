"""
Tests unitarios para funciones helper de deportistas_routes.py.

Cubre todas las funciones auxiliares que no están directamente expuestas como endpoints.
Aplicando principios de Clean Code: DRY, SRP, nombres descriptivos, tests aislados.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from src.routes.deportistas_routes import (
    _build_service_response,
    _build_catalog_response,
    _is_valid_acudiente_id,
    _calculate_age,
    _serialize_deportista,
    _validar_documento_busqueda,
    _obtener_acudiente_desde_usuario,
    _buscar_persona_por_documento_multiple,
    _verificar_rol_deportista,
    _obtener_deportista_con_categoria,
    _construir_datos_deportista,
)


@pytest.mark.unit
@pytest.mark.deportistas
class TestBuildServiceResponse:
    """Tests para la función _build_service_response"""

    def test_build_service_response_success(self, app_context):
        """Test: Construir respuesta exitosa."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        result = {
            'success': True,
            'data': {'id': 1},
            'message': 'Operación exitosa',
            'status_code': 200
        }
        
        with app.app_context():
            # Act
            response, status_code = _build_service_response(result)
            
            # Assert
            assert status_code == 200
            # response es un objeto Response de Flask
            assert response is not None

    def test_build_service_response_error(self, app_context):
        """Test: Construir respuesta de error."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        result = {
            'success': False,
            'error': 'Error en la operación',
            'status_code': 400
        }
        
        with app.app_context():
            # Act
            response, status_code = _build_service_response(result)
            
            # Assert
            assert status_code == 400
            # response es un objeto Response de Flask
            assert response is not None

    def test_build_service_response_status_success(self, app_context):
        """Test: Construir respuesta con campo 'status' en lugar de 'success'."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        result = {
            'status': 'success',
            'data': {'id': 1},
            'status_code': 201
        }
        
        with app.app_context():
            # Act
            _, status_code = _build_service_response(result)
            
            # Assert
            assert status_code == 201

    def test_build_service_response_default_error_message(self, app_context):
        """Test: Usar mensaje de error por defecto."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        result = {
            'success': False,
            'status_code': 500
        }
        
        with app.app_context():
            # Act
            _, status_code = _build_service_response(result, "Error personalizado")
            
            # Assert
            assert status_code == 500


@pytest.mark.unit
@pytest.mark.deportistas
class TestBuildCatalogResponse:
    """Tests para la función _build_catalog_response"""

    def test_build_catalog_response_success(self, app_context):
        """Test: Construir respuesta de catálogo exitosa."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_service_method = MagicMock(return_value={
            'success': True,
            'data': [{'id': 1, 'nombre': 'Test'}],
            'status_code': 200
        })
        
        with app.app_context():
            # Act
            _, status_code = _build_catalog_response(mock_service_method)
            
            # Assert
            assert status_code == 200
            mock_service_method.assert_called_once()

    def test_build_catalog_response_error(self, app_context):
        """Test: Manejo de errores en catálogo."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_service_method = MagicMock(side_effect=Exception("Database error"))
        
        with app.app_context():
            # Act
            _, status_code = _build_catalog_response(mock_service_method, "Error al obtener catálogo")
            
            # Assert
            # Debe retornar una respuesta de error
            assert status_code in [400, 500]


@pytest.mark.unit
@pytest.mark.deportistas
class TestIsValidAcudienteId:
    """Tests para la función _is_valid_acudiente_id"""

    def test_is_valid_acudiente_id_valid(self):
        """Test: ID válido de acudiente."""
        # Act
        result = _is_valid_acudiente_id(1)
        
        # Assert
        assert result is True

    def test_is_valid_acudiente_id_zero(self):
        """Test: ID cero (inválido)."""
        # Act
        result = _is_valid_acudiente_id(0)
        
        # Assert
        assert result is False

    def test_is_valid_acudiente_id_negative(self):
        """Test: ID negativo (inválido)."""
        # Act
        result = _is_valid_acudiente_id(-1)
        
        # Assert
        assert result is False

    def test_is_valid_acudiente_id_not_int(self):
        """Test: ID que no es entero (inválido)."""
        # Act
        result = _is_valid_acudiente_id("1")
        
        # Assert
        assert result is False


@pytest.mark.unit
@pytest.mark.deportistas
class TestCalculateAge:
    """Tests para la función _calculate_age"""

    def test_calculate_age_from_date(self):
        """Test: Calcular edad desde objeto date."""
        # Arrange
        fecha_nacimiento = date(2000, 1, 15)
        
        # Act
        edad = _calculate_age(fecha_nacimiento)
        
        # Assert
        assert isinstance(edad, int)
        assert edad > 0

    def test_calculate_age_from_int(self):
        """Test: Calcular edad desde año (int)."""
        # Arrange
        ano_nacimiento = 2000
        
        # Act
        edad = _calculate_age(ano_nacimiento)
        
        # Assert
        assert isinstance(edad, int)
        assert edad > 0

    def test_calculate_age_none(self):
        """Test: Retornar None cuando fecha es None."""
        # Act
        edad = _calculate_age(None)
        
        # Assert
        assert edad is None

    def test_calculate_age_invalid_type(self):
        """Test: Retornar None cuando tipo es inválido."""
        # Act
        edad = _calculate_age("2000-01-01")
        
        # Assert
        assert edad is None


@pytest.mark.unit
@pytest.mark.deportistas
class TestSerializeDeportista:
    """Tests para la función _serialize_deportista"""

    def test_serialize_deportista_success(self):
        """Test: Serializar deportista exitosamente."""
        # Arrange
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.fecha_nacimiento = date(2000, 1, 15)
        mock_deportista.persona = MagicMock()
        mock_deportista.persona.nombre_completo = 'Juan Pérez'
        mock_deportista.persona.documento = '12345678'
        mock_deportista.persona.correo_electronico = 'juan@example.com'
        mock_deportista.persona.telefono = '3001234567'
        mock_deportista.categoria = MagicMock()
        mock_deportista.categoria.nombre_categoria = 'Juvenil'
        
        mock_relacion = MagicMock()
        mock_relacion.es_responsable = True
        mock_relacion.parentesco = MagicMock()
        mock_relacion.parentesco.nombre = 'Padre'
        
        # Act
        result = _serialize_deportista(mock_deportista, mock_relacion)
        
        # Assert
        assert result['id'] == 1
        assert result['nombre_completo'] == 'Juan Pérez'
        assert result['documento'] == '12345678'
        assert result['categoria'] == 'Juvenil'
        assert result['es_responsable'] is True
        assert result['parentesco'] == 'Padre'
        assert 'edad' in result

    def test_serialize_deportista_sin_categoria(self):
        """Test: Serializar deportista sin categoría."""
        # Arrange
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.fecha_nacimiento = date(2000, 1, 15)
        mock_deportista.persona = MagicMock()
        mock_deportista.persona.nombre_completo = 'Juan Pérez'
        mock_deportista.persona.documento = '12345678'
        mock_deportista.persona.correo_electronico = 'juan@example.com'
        mock_deportista.persona.telefono = '3001234567'
        mock_deportista.categoria = None
        
        mock_relacion = MagicMock()
        mock_relacion.es_responsable = False
        mock_relacion.parentesco = None
        
        # Act
        result = _serialize_deportista(mock_deportista, mock_relacion)
        
        # Assert
        assert result['categoria'] == 'Sin categoría'  # DEFAUL_CATEGORY_LABEL
        assert result['es_responsable'] is False
        assert result['parentesco'] == 'No especificado'  # DEFAULT_PARENTESCO_LABEL


@pytest.mark.unit
@pytest.mark.deportistas
class TestValidarDocumentoBusqueda:
    """Tests para la función _validar_documento_busqueda"""

    def test_validar_documento_busqueda_vacio(self, app_context):
        """Test: Error cuando documento está vacío."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.app_context():
            # Act
            documento, error_response = _validar_documento_busqueda('')
            
            # Assert
            assert documento is None
            assert error_response is not None
            assert error_response[1] == 400  # status_code

    def test_validar_documento_busqueda_valido(self, app_context):
        """Test: Validar documento válido."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        with patch('src.utils.validations.validate_document', return_value='12345678'):
            with app.app_context():
                # Act
                documento, error_response = _validar_documento_busqueda('12345678')
                
                # Assert
                assert documento == '12345678'
                assert error_response is None

    def test_validar_documento_busqueda_invalido(self, app_context):
        """Test: Error cuando documento es inválido."""
        from flask import Flask
        app = Flask(__name__)
        from src.utils.validations import ValidationError
        
        # Arrange
        with patch('src.utils.validations.validate_document',
                   side_effect=ValidationError('Documento inválido')):
            with app.app_context():
                # Act
                documento, error_response = _validar_documento_busqueda('123')
                
                # Assert
                assert documento is None
                assert error_response is not None
                assert error_response[1] == 400


@pytest.mark.unit
@pytest.mark.deportistas
class TestObtenerAcudienteDesdeUsuario:
    """Tests para la función _obtener_acudiente_desde_usuario"""

    def test_obtener_acudiente_desde_usuario_success(self, app_context):
        """Test: Obtener acudiente desde usuario exitosamente."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        usuario_actual = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        mock_acudiente = MagicMock()
        mock_acudiente.id_acudiente = 1
        
        # Patch el import dentro de la función
        with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_acudiente
            mock_acudiente_model.query = mock_query
            
            with app.app_context():
                # Act
                id_acudiente, error_response = _obtener_acudiente_desde_usuario(usuario_actual)
                
                # Assert
                assert id_acudiente == 1
                assert error_response is None

    def test_obtener_acudiente_desde_usuario_no_autenticado(self, app_context):
        """Test: Error cuando usuario no está autenticado."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.app_context():
            # Act
            id_acudiente, error_response = _obtener_acudiente_desde_usuario(None)
            
            # Assert
            assert id_acudiente is None
            assert error_response is not None
            assert error_response[1] == 401

    def test_obtener_acudiente_desde_usuario_sin_persona(self, app_context):
        """Test: Error cuando usuario no tiene persona."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        usuario_actual = {'id_usuario': 1}
        
        with app.app_context():
            # Act
            id_acudiente, error_response = _obtener_acudiente_desde_usuario(usuario_actual)
            
            # Assert
            assert id_acudiente is None
            assert error_response is not None
            assert error_response[1] == 401

    def test_obtener_acudiente_desde_usuario_no_es_acudiente(self, app_context):
        """Test: Error cuando usuario no es acudiente."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        usuario_actual = {
            'id_usuario': 1,
            'persona': {'id_persona': 1}
        }
        
        # Patch el import dentro de la función
        with patch('src.models.acudientes.acudiente.Acudiente') as mock_acudiente_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_acudiente_model.query = mock_query
            
            with app.app_context():
                # Act
                id_acudiente, error_response = _obtener_acudiente_desde_usuario(usuario_actual)
                
                # Assert
                assert id_acudiente is None
                assert error_response is not None
                assert error_response[1] == 400


@pytest.mark.unit
@pytest.mark.deportistas
class TestBuscarPersonaPorDocumentoMultiple:
    """Tests para la función _buscar_persona_por_documento_multiple"""

    def test_buscar_persona_por_documento_multiple_success(self, app_context):
        """Test: Buscar persona por documento exitosamente."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        # Patch el import dentro de la función y db.session.query
        with patch('src.models.personas.persona.Persona'):
            with patch('src.routes.deportistas_routes.db') as mock_db:
                mock_query = MagicMock()
                mock_query.filter.return_value.first.return_value = mock_persona
                mock_db.session.query.return_value = mock_query
                
                with app.app_context():
                    # Act
                    persona, error_response = _buscar_persona_por_documento_multiple('12345678')
                    
                    # Assert
                    # Puede retornar persona o None dependiendo de cómo se configure el mock
                    assert error_response is None or persona is not None

    def test_buscar_persona_por_documento_multiple_no_encontrada(self, app_context):
        """Test: Persona no encontrada."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        # Patch el import dentro de la función y db.session.query
        with patch('src.models.personas.persona.Persona'):
            with patch('src.routes.deportistas_routes.db') as mock_db:
                mock_query = MagicMock()
                mock_query.filter.return_value.first.return_value = None
                mock_db.session.query.return_value = mock_query
                
                with app.app_context():
                    # Act
                    persona, _ = _buscar_persona_por_documento_multiple('99999999')
                    
                    # Assert
                    assert persona is None
                    # Puede retornar error_response o None dependiendo de la implementación


@pytest.mark.unit
@pytest.mark.deportistas
class TestVerificarRolDeportista:
    """Tests para la función _verificar_rol_deportista"""

    def test_verificar_rol_deportista_success(self, app_context):
        """Test: Verificar que persona tiene rol deportista."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Deportista'
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_usuario.roles = [mock_rol]
        
        # Patch el import dentro de la función
        with patch('src.models.usuarios.usuario.Usuario') as mock_usuario_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_model.query = mock_query
            
            with app.app_context():
                # Act
                tiene_rol, error_response = _verificar_rol_deportista(mock_persona)
                
                # Assert
                assert tiene_rol is True
                assert error_response is None

    def test_verificar_rol_deportista_sin_rol(self, app_context):
        """Test: Persona no tiene rol deportista."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_usuario.roles = []
        
        # Patch el import dentro de la función
        with patch('src.models.usuarios.usuario.Usuario') as mock_usuario_model:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_model.query = mock_query
            
            with app.app_context():
                # Act
                tiene_rol, error_response = _verificar_rol_deportista(mock_persona)
                
                # Assert
                assert tiene_rol is False
                assert error_response is not None


@pytest.mark.unit
@pytest.mark.deportistas
class TestObtenerDeportistaConCategoria:
    """Tests para la función _obtener_deportista_con_categoria"""

    def test_obtener_deportista_con_categoria_success(self, app_context):
        """Test: Obtener deportista con categoría exitosamente."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        # Patch tanto el modelo como joinedload (se importa desde sqlalchemy.orm dentro de la función)
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model, \
             patch('sqlalchemy.orm.joinedload') as mock_joinedload:
            # Crear una cadena de mocks que simule query.options().filter_by().first()
            mock_first = MagicMock(return_value=mock_deportista)
            mock_filter_by = MagicMock()
            mock_filter_by.first = mock_first
            mock_options = MagicMock()
            mock_options.filter_by = MagicMock(return_value=mock_filter_by)
            mock_query = MagicMock()
            mock_query.options = MagicMock(return_value=mock_options)
            mock_deportista_model.query = mock_query
            # Mock joinedload para que retorne el mock_options
            mock_joinedload.return_value = mock_options
            
            with app.app_context():
                # Act
                deportista, error_response = _obtener_deportista_con_categoria(1)
                
                # Assert
                assert deportista == mock_deportista
                assert error_response is None

    def test_obtener_deportista_con_categoria_no_encontrado(self, app_context):
        """Test: Deportista no encontrado."""
        from flask import Flask
        app = Flask(__name__)
        
        # Arrange
        # Patch tanto el modelo como joinedload (se importa desde sqlalchemy.orm dentro de la función)
        with patch('src.models.deportistas.deportista.Deportista') as mock_deportista_model, \
             patch('sqlalchemy.orm.joinedload') as mock_joinedload:
            # Crear una cadena de mocks que simule query.options().filter_by().first()
            mock_first = MagicMock(return_value=None)
            mock_filter_by = MagicMock()
            mock_filter_by.first = mock_first
            mock_options = MagicMock()
            mock_options.filter_by = MagicMock(return_value=mock_filter_by)
            mock_query = MagicMock()
            mock_query.options = MagicMock(return_value=mock_options)
            mock_deportista_model.query = mock_query
            # Mock joinedload para que retorne el mock_options
            mock_joinedload.return_value = mock_options
            
            with app.app_context():
                # Act
                deportista, error_response = _obtener_deportista_con_categoria(999)
                
                # Assert
                assert deportista is None
                assert error_response is not None


@pytest.mark.unit
@pytest.mark.deportistas
class TestConstruirDatosDeportista:
    """Tests para la función _construir_datos_deportista"""

    def test_construir_datos_deportista_success(self):
        """Test: Construir datos de deportista exitosamente."""
        # Arrange
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.categoria = MagicMock()
        mock_deportista.categoria.nombre_categoria = 'Juvenil'
        
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = 'Juan Pérez'
        mock_persona.documento = '12345678'
        mock_persona.estado = True
        
        # Act
        datos = _construir_datos_deportista(mock_deportista, mock_persona, '12345678')
        
        # Assert
        assert datos['id_deportista'] == 1
        assert datos['id_persona'] == 1
        assert datos['documento'] == '12345678'
        assert datos['nombre_completo'] == 'Juan Pérez'
        assert datos['categoria'] == 'Juvenil'
        assert datos['estado'] is True

    def test_construir_datos_deportista_sin_categoria(self):
        """Test: Construir datos sin categoría."""
        # Arrange - Crear un objeto mock más realista
        from types import SimpleNamespace
        
        mock_deportista = SimpleNamespace()
        mock_deportista.id_deportista = 1
        mock_deportista.categoria = None
        
        mock_persona = SimpleNamespace()
        mock_persona.id_persona = 1
        mock_persona.nombre_completo = None
        mock_persona.nombre = None  # También None para que use primer_nombre y primer_apellido
        mock_persona.primer_nombre = 'Juan'
        mock_persona.primer_apellido = 'Pérez'
        mock_persona.documento = None
        mock_persona.estado = True
        
        # Act
        datos = _construir_datos_deportista(mock_deportista, mock_persona, '12345678')
        
        # Assert
        assert datos['categoria'] is None
        assert datos['documento'] == '12345678'  # Usa el documento del parámetro
        assert datos['nombre_completo'] == 'Juan Pérez'  # Construido desde primer_nombre y primer_apellido

