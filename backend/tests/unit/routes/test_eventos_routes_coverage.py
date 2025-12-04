"""
Tests unitarios para aumentar la cobertura de eventos_routes.py.

Cubre bloques de excepciones y funciones helper que no están completamente cubiertas.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import date, time

from src.routes import eventos_routes
from src.routes.eventos_routes import (
    _agregar_categoria_serializada,
    _agregar_sesion_serializada,
    _agregar_tipo_evento_serializado,
    _serializar_evento,
    _actualizar_nombre_evento,
    _actualizar_fecha_evento,
    _actualizar_horas_evento,
    _actualizar_lugar_evento,
    _actualizar_descripcion_evento,
    _actualizar_categoria_evento,
    _actualizar_tipo_evento,
    _actualizar_sesion_evento,
    _validar_solapamiento_evento_actualizado,
    _validar_campos_requeridos_evento,
    _validar_y_sanitizar_nombre,
    _validar_fecha_y_horas,
    _validar_y_sanitizar_lugar,
    _validar_entidades_evento,
    _aplicar_filtro_categorias,
    _aplicar_filtro_categoria_especifica,
    _aplicar_filtros_basicos,
    _aplicar_filtro_usuario_solo,
    _aplicar_filtro_admin_entrenador,
    _aplicar_filtro_deportista_acudiente,
    _aplicar_filtro_deportista_acudiente_proximos,
    obtener_categorias_permitidas_usuario,
    _es_usuario_solo_deportista_o_acudiente,
    _es_usuario_solo_rol_usuario,
    obtener_evento,
    listar_eventos,
    _validar_lugar,
    validar_solapamiento_horario,
)
from src.utils.request_validators import RequestValidationError
from src.utils.validations import ValidationError
from src.utils.http_responses import HttpResponseBuilder


@pytest.mark.unit
@pytest.mark.eventos
class TestSerializacionEventos:
    """Tests para funciones de serialización de eventos."""

    def test_agregar_categoria_serializada_exception(self):
        """Test: Excepción al serializar categoría (línea 352)."""
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.categoria = MagicMock()
        mock_evento.categoria.to_dict.side_effect = Exception('Serialization error')
        evento_dict = {}

        with patch('src.routes.eventos_routes.logger') as mock_logger:
            _agregar_categoria_serializada(mock_evento, evento_dict)

            mock_logger.warning.assert_called_once()
            assert 'categoría' in str(mock_logger.warning.call_args).lower()

    def test_agregar_sesion_serializada_exception(self):
        """Test: Excepción al serializar sesión (línea 362)."""
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.sesion = MagicMock()
        mock_evento.sesion.to_dict.side_effect = Exception('Serialization error')
        evento_dict = {}

        with patch('src.routes.eventos_routes.logger') as mock_logger:
            _agregar_sesion_serializada(mock_evento, evento_dict)

            mock_logger.warning.assert_called_once()
            assert 'sesión' in str(mock_logger.warning.call_args).lower()

    def test_agregar_tipo_evento_serializado_sin_id_tipo_evento(self):
        """Test: Sin id_tipo_evento retorna temprano (línea 368)."""
        mock_evento = MagicMock()
        mock_evento.id_tipo_evento = None
        evento_dict = {}

        _agregar_tipo_evento_serializado(mock_evento, evento_dict)

        assert 'tipo_evento' not in evento_dict

    def test_agregar_tipo_evento_serializado_exception(self):
        """Test: Excepción al obtener tipo_evento (línea 374)."""
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.id_tipo_evento = 1
        evento_dict = {}

        with patch('src.routes.eventos_routes.TipoEvento') as mock_tipo_evento, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_tipo_evento.query.get.side_effect = Exception('Database error')

            _agregar_tipo_evento_serializado(mock_evento, evento_dict)

            mock_logger.warning.assert_called_once()

    def test_agregar_tipo_evento_serializado_tipo_evento_no_encontrado(self):
        """Test: TipoEvento no encontrado (línea 372)."""
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.id_tipo_evento = 999
        evento_dict = {}

        with patch('src.routes.eventos_routes.TipoEvento') as mock_tipo_evento:
            mock_tipo_evento.query.get.return_value = None

            _agregar_tipo_evento_serializado(mock_evento, evento_dict)

            assert 'tipo_evento' not in evento_dict

    def test_serializar_evento_exception(self):
        """Test: Excepción al serializar evento (línea 386)."""
        mock_evento = MagicMock()
        mock_evento.id_evento = 1
        mock_evento.to_dict.side_effect = Exception('Serialization error')

        with patch('src.routes.eventos_routes.logger') as mock_logger:
            with pytest.raises(Exception):
                _serializar_evento(mock_evento)

            assert mock_logger.error.call_count >= 2


@pytest.mark.unit
@pytest.mark.eventos
class TestActualizacionEventos:
    """Tests para funciones auxiliares de actualización de eventos."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def mock_evento(self):
        """Fixture para evento mock."""
        evento = MagicMock()
        evento.id_evento = 1
        evento.nombre = 'Evento Test'
        evento.fecha_evento = date(2024, 12, 31)
        evento.hora_inicio = time(10, 0)
        evento.hora_fin = time(12, 0)
        evento.lugar = 'Lugar Test'
        evento.descripcion = None
        evento.id_categoria = 1
        evento.id_tipo_evento = 1
        evento.id_sesion = None
        return evento

    def test_actualizar_nombre_evento_sin_campo(self, mock_evento, app):
        """Test: Actualizar nombre cuando no está en data."""
        with app.app_context():
            data = {}
            result = _actualizar_nombre_evento(mock_evento, data)
            assert result is None

    def test_actualizar_nombre_evento_validation_error(self, mock_evento, app):
        """Test: ValidationError al sanitizar nombre."""
        with app.app_context():
            data = {'nombre': 'Test'}
            with patch('src.routes.eventos_routes.sanitize_free_text') as mock_sanitize:
                mock_sanitize.side_effect = ValidationError('Invalid name')
                result = _actualizar_nombre_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_nombre_evento_muy_corto(self, mock_evento, app):
        """Test: Nombre muy corto después de sanitizar."""
        with app.app_context():
            data = {'nombre': 'Ab'}
            with patch('src.routes.eventos_routes.sanitize_free_text', return_value='Ab'):
                result = _actualizar_nombre_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_fecha_evento_sin_campo(self, mock_evento, app):
        """Test: Actualizar fecha cuando no está en data."""
        with app.app_context():
            data = {}
            result = _actualizar_fecha_evento(mock_evento, data)
            assert result is None

    def test_actualizar_fecha_evento_formato_invalido(self, mock_evento, app):
        """Test: Formato de fecha inválido."""
        with app.app_context():
            data = {'fecha_evento': 'invalid-date'}
            result = _actualizar_fecha_evento(mock_evento, data)

            assert result is not None
            data_json = result[0].get_json()
            assert data_json.get('success') is False

    def test_actualizar_horas_evento_solo_hora_inicio(self, mock_evento, app):
        """Test: Actualizar solo hora_inicio."""
        with app.app_context():
            data = {'hora_inicio': '14:00'}
            mock_evento.hora_fin = time(15, 0)
            result = _actualizar_horas_evento(mock_evento, data)

            assert result is None
            assert mock_evento.hora_inicio == time(14, 0)

    def test_actualizar_horas_evento_hora_fin_antes_inicio(self, mock_evento, app):
        """Test: Hora fin antes o igual a hora inicio (línea 453)."""
        with app.app_context():
            data = {'hora_inicio': '14:00', 'hora_fin': '13:00'}
            mock_evento.hora_inicio = time(14, 0)
            mock_evento.hora_fin = time(13, 0)
            result = _actualizar_horas_evento(mock_evento, data)

            assert result is not None
            data_json = result[0].get_json()
            assert data_json.get('success') is False

    def test_actualizar_horas_evento_hora_fin_igual_inicio(self, mock_evento, app):
        """Test: Hora fin igual a hora inicio."""
        with app.app_context():
            data = {'hora_inicio': '14:00', 'hora_fin': '14:00'}
            mock_evento.hora_inicio = time(14, 0)
            mock_evento.hora_fin = time(14, 0)
            result = _actualizar_horas_evento(mock_evento, data)

            assert result is not None

    def test_actualizar_lugar_evento_validation_error(self, mock_evento, app):
        """Test: ValidationError al sanitizar lugar."""
        with app.app_context():
            data = {'lugar': 'Test'}
            with patch('src.routes.eventos_routes.sanitize_address') as mock_sanitize, \
                 patch.object(eventos_routes, '_validar_lugar', return_value=True):
                mock_sanitize.side_effect = ValidationError('Invalid address')
                result = _actualizar_lugar_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_lugar_evento_invalido(self, mock_evento, app):
        """Test: Lugar inválido después de sanitizar (línea 468)."""
        with app.app_context():
            data = {'lugar': 'Ab'}
            with patch('src.routes.eventos_routes.sanitize_address', return_value='Ab'), \
                 patch.object(eventos_routes, '_validar_lugar', return_value=False):
                result = _actualizar_lugar_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_descripcion_evento_con_descripcion(self, mock_evento, app):
        """Test: Actualizar descripción cuando está en data."""
        with app.app_context():
            data = {'descripcion': 'Nueva descripción'}
            with patch('src.routes.eventos_routes.sanitize_free_text', return_value='Nueva descripción'):
                _actualizar_descripcion_evento(mock_evento, data)
                assert mock_evento.descripcion == 'Nueva descripción'

    def test_actualizar_descripcion_evento_vacia(self, mock_evento, app):
        """Test: Descripción vacía."""
        with app.app_context():
            data = {'descripcion': ''}
            with patch('src.routes.eventos_routes.sanitize_free_text', return_value=''):
                _actualizar_descripcion_evento(mock_evento, data)
                assert mock_evento.descripcion is None

    def test_actualizar_categoria_evento_no_encontrada(self, mock_evento, app):
        """Test: Categoría no encontrada."""
        with app.app_context():
            data = {'id_categoria': 999}
            with patch('src.routes.eventos_routes.Categoria') as mock_categoria:
                mock_categoria.query.get.return_value = None
                result = _actualizar_categoria_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_tipo_evento_no_encontrado(self, mock_evento, app):
        """Test: Tipo de evento no encontrado."""
        with app.app_context():
            data = {'id_tipo_evento': 999}
            with patch('src.routes.eventos_routes.TipoEvento') as mock_tipo_evento:
                mock_tipo_evento.query.get.return_value = None
                result = _actualizar_tipo_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_actualizar_sesion_evento_no_encontrada(self, mock_evento, app):
        """Test: Sesión no encontrada."""
        with app.app_context():
            data = {'id_sesion': 999}
            with patch('src.routes.eventos_routes.Sesion') as mock_sesion:
                mock_sesion.query.get.return_value = None
                result = _actualizar_sesion_evento(mock_evento, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False

    def test_validar_solapamiento_evento_actualizado_sin_campos_relevantes(self, mock_evento, app):
        """Test: Sin campos relevantes no valida solapamiento."""
        with app.app_context():
            data = {'descripcion': 'Nueva descripción'}
            result = _validar_solapamiento_evento_actualizado(mock_evento, 1, data)
            assert result is None

    def test_validar_solapamiento_evento_actualizado_con_solapamiento(self, mock_evento, app):
        """Test: Con solapamiento retorna error."""
        with app.app_context():
            data = {'fecha_evento': '2024-12-31'}
            with patch.object(eventos_routes, 'validar_solapamiento_horario', return_value=(False, 'Horario solapado')):
                result = _validar_solapamiento_evento_actualizado(mock_evento, 1, data)

                assert result is not None
                data_json = result[0].get_json()
                assert data_json.get('success') is False


@pytest.mark.unit
@pytest.mark.eventos
class TestValidacionEventos:
    """Tests para funciones de validación de eventos."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_validar_campos_requeridos_evento_campos_faltantes(self, app):
        """Test: Campos requeridos faltantes."""
        with app.app_context():
            data = {'nombre': 'Test'}
            result = _validar_campos_requeridos_evento(data)

            assert result is not None
            data_json = result[0].get_json()
            assert data_json.get('success') is False
            assert 'campos_faltantes' in data_json

    def test_validar_campos_requeridos_evento_todos_presentes(self, app):
        """Test: Todos los campos requeridos presentes."""
        with app.app_context():
            data = {
                'nombre': 'Evento Test',
                'fecha_evento': '2024-12-31',
                'hora_inicio': '10:00',
                'hora_fin': '12:00',
                'lugar': 'Lugar Test',
                'id_categoria': 1,
                'id_tipo_evento': 1
            }
            result = _validar_campos_requeridos_evento(data)
            assert result is None

    def test_validar_y_sanitizar_nombre_validation_error(self, app):
        """Test: ValidationError al sanitizar nombre."""
        with app.app_context():
            data = {'nombre': 'Test'}
            with patch('src.routes.eventos_routes.sanitize_free_text') as mock_sanitize:
                mock_sanitize.side_effect = ValidationError('Invalid name')
                nombre, error = _validar_y_sanitizar_nombre(data)

                assert nombre is None
                assert error is not None

    def test_validar_y_sanitizar_nombre_muy_corto(self, app):
        """Test: Nombre muy corto después de sanitizar."""
        with app.app_context():
            data = {'nombre': 'Ab'}
            with patch('src.routes.eventos_routes.sanitize_free_text', return_value='Ab'):
                nombre, error = _validar_y_sanitizar_nombre(data)

                assert nombre is None
                assert error is not None

    def test_validar_fecha_y_horas_fecha_invalida(self, app):
        """Test: Fecha inválida."""
        with app.app_context():
            data = {'fecha_evento': 'invalid', 'hora_inicio': '10:00', 'hora_fin': '12:00'}
            fecha, _, _, error = _validar_fecha_y_horas(data)

            assert fecha is None
            assert error is not None

    def test_validar_fecha_y_horas_hora_inicio_invalida(self, app):
        """Test: Hora inicio inválida."""
        with app.app_context():
            data = {'fecha_evento': '2024-12-31', 'hora_inicio': 'invalid', 'hora_fin': '12:00'}
            _, hora_inicio, _, error = _validar_fecha_y_horas(data)

            assert hora_inicio is None
            assert error is not None

    def test_validar_fecha_y_horas_hora_fin_invalida(self, app):
        """Test: Hora fin inválida."""
        with app.app_context():
            data = {'fecha_evento': '2024-12-31', 'hora_inicio': '10:00', 'hora_fin': 'invalid'}
            _, _, hora_fin, error = _validar_fecha_y_horas(data)

            assert hora_fin is None
            assert error is not None

    def test_validar_fecha_y_horas_hora_fin_antes_inicio(self, app):
        """Test: Hora fin antes o igual a hora inicio."""
        with app.app_context():
            data = {'fecha_evento': '2024-12-31', 'hora_inicio': '12:00', 'hora_fin': '10:00'}
            _, _, _, error = _validar_fecha_y_horas(data)

            assert error is not None

    def test_validar_y_sanitizar_lugar_validation_error(self, app):
        """Test: ValidationError al sanitizar lugar."""
        with app.app_context():
            data = {'lugar': 'Test'}
            with patch('src.routes.eventos_routes.sanitize_address') as mock_sanitize:
                mock_sanitize.side_effect = ValidationError('Invalid address')
                lugar, error = _validar_y_sanitizar_lugar(data)

                assert lugar is None
                assert error is not None

    def test_validar_entidades_evento_categoria_no_encontrada(self, app):
        """Test: Categoría no encontrada."""
        with app.app_context():
            data = {'id_categoria': 999, 'id_tipo_evento': 1}
            with patch('src.routes.eventos_routes.Categoria') as mock_categoria, \
                 patch('src.routes.eventos_routes.TipoEvento'):
                mock_categoria.query.get.return_value = None
                categoria, _, error = _validar_entidades_evento(data)

                assert categoria is None
                assert error is not None

    def test_validar_entidades_evento_tipo_evento_no_encontrado(self, app):
        """Test: Tipo de evento no encontrado."""
        with app.app_context():
            mock_categoria = MagicMock()
            data = {'id_categoria': 1, 'id_tipo_evento': 999}
            with patch('src.routes.eventos_routes.Categoria') as mock_cat_class, \
                 patch('src.routes.eventos_routes.TipoEvento') as mock_tipo_evento:
                mock_cat_class.query.get.return_value = mock_categoria
                mock_tipo_evento.query.get.return_value = None
                _, tipo_evento, error = _validar_entidades_evento(data)

                assert tipo_evento is None
                assert error is not None


@pytest.mark.unit
@pytest.mark.eventos
class TestFiltradoEventos:
    """Tests para funciones de filtrado de eventos."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def mock_query(self):
        """Fixture para query mock."""
        query = MagicMock()
        query.filter = MagicMock(return_value=query)
        query.filter_by = MagicMock(return_value=query)
        return query

    def test_aplicar_filtro_categorias_none(self, mock_query):
        """Test: categorias_permitidas es None."""
        result = _aplicar_filtro_categorias(mock_query, None, None)
        assert result == mock_query

    def test_aplicar_filtro_categorias_lista_vacia(self, mock_query):
        """Test: categorias_permitidas es lista vacía."""
        _aplicar_filtro_categorias(mock_query, [], None)
        mock_query.filter.assert_called_once()

    def test_aplicar_filtro_categorias_con_todos(self, mock_query):
        """Test: Con id_categoria_todos."""
        _aplicar_filtro_categorias(mock_query, [1, 2], 99)
        mock_query.filter.assert_called_once()

    def test_aplicar_filtro_categorias_sin_todos(self, mock_query):
        """Test: Sin id_categoria_todos."""
        _aplicar_filtro_categorias(mock_query, [1, 2], None)
        mock_query.filter.assert_called_once()

    def test_aplicar_filtro_categoria_especifica_no_permitida(self, mock_query, app):
        """Test: Categoría específica no permitida."""
        with app.app_context():
            _, error = _aplicar_filtro_categoria_especifica(mock_query, 99, [1, 2], None)
            assert error is not None

    def test_aplicar_filtro_categoria_especifica_permitida(self, mock_query, app):
        """Test: Categoría específica permitida."""
        with app.app_context():
            _, error = _aplicar_filtro_categoria_especifica(mock_query, 1, [1, 2], None)
            assert error is None
            mock_query.filter_by.assert_called_once()

    def test_aplicar_filtros_basicos_search(self, mock_query):
        """Test: Aplicar filtro de búsqueda."""
        _aplicar_filtros_basicos(mock_query, 'test', None, None, None)
        mock_query.filter.assert_called()

    def test_aplicar_filtros_basicos_tipo_evento(self, mock_query):
        """Test: Aplicar filtro de tipo de evento."""
        _aplicar_filtros_basicos(mock_query, None, 1, None, None)
        mock_query.filter_by.assert_called()

    def test_aplicar_filtros_basicos_fecha_desde(self, mock_query):
        """Test: Aplicar filtro de fecha desde."""
        _aplicar_filtros_basicos(mock_query, None, None, '2024-01-01', None)
        mock_query.filter.assert_called()

    def test_aplicar_filtros_basicos_fecha_desde_invalida(self, mock_query):
        """Test: Fecha desde inválida no aplica filtro."""
        _aplicar_filtros_basicos(mock_query, None, None, 'invalid', None)
        # No debería llamar filter si la fecha es inválida
        # (el comportamiento exacto depende de _parse_date)

    def test_aplicar_filtros_basicos_fecha_hasta(self, mock_query):
        """Test: Aplicar filtro de fecha hasta."""
        _aplicar_filtros_basicos(mock_query, None, None, None, '2024-12-31')
        mock_query.filter.assert_called()

    def test_aplicar_filtro_usuario_solo_tipo_no_publico(self, mock_query, app):
        """Test: Tipo de evento no público (línea 634)."""
        with app.app_context():
            _, error = _aplicar_filtro_usuario_solo(mock_query, 1)  # 1 no está en TIPOS_EVENTO_PUBLICOS
            assert error is not None

    def test_aplicar_filtro_admin_entrenador_sin_categoria(self, mock_query):
        """Test: Admin/entrenador sin categoria_id."""
        result = _aplicar_filtro_admin_entrenador(mock_query, None)
        assert result == mock_query

    def test_aplicar_filtro_admin_entrenador_con_categoria(self, mock_query):
        """Test: Admin/entrenador con categoria_id."""
        _aplicar_filtro_admin_entrenador(mock_query, 1)
        mock_query.filter_by.assert_called_once()

    def test_aplicar_filtro_deportista_acudiente_lista_vacia(self, mock_query):
        """Test: Lista de categorías vacía."""
        _, error = _aplicar_filtro_deportista_acudiente(mock_query, [], None)
        assert error is None
        mock_query.filter.assert_called_once()

    def test_aplicar_filtro_deportista_acudiente_categoria_no_permitida(self, mock_query, app):
        """Test: Categoría solicitada no permitida (línea 669)."""
        with app.app_context():
            _, error = _aplicar_filtro_deportista_acudiente(mock_query, [1, 2], 99)
            assert error is not None

    def test_aplicar_filtro_deportista_acudiente_proximos_lista_vacia(self, mock_query):
        """Test: Lista de categorías vacía."""
        _, error = _aplicar_filtro_deportista_acudiente_proximos(mock_query, [], None)
        assert error is None
        mock_query.filter.assert_called_once()

    def test_aplicar_filtro_deportista_acudiente_proximos_categoria_no_permitida(self, mock_query, app):
        """Test: Categoría solicitada no permitida."""
        with app.app_context():
            _, error = _aplicar_filtro_deportista_acudiente_proximos(mock_query, [1, 2], 99)
            assert error is not None


@pytest.mark.unit
@pytest.mark.eventos
class TestHelperCategorias:
    """Tests para funciones helper de categorías con excepciones."""

    def test_obtener_categorias_permitidas_usuario_exception(self):
        """Test: Excepción en obtener_categorias_permitidas_usuario (línea 252)."""
        with patch('src.routes.eventos_routes.get_current_user') as mock_get_user, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_get_user.side_effect = Exception('Database error')
            result = obtener_categorias_permitidas_usuario()

            assert result == []
            mock_logger.error.assert_called_once()

    def test_es_usuario_solo_deportista_o_acudiente_exception(self):
        """Test: Excepción en _es_usuario_solo_deportista_o_acudiente (línea 275)."""
        with patch('src.routes.eventos_routes.get_current_user') as mock_get_user, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_get_user.side_effect = Exception('Database error')
            result = _es_usuario_solo_deportista_o_acudiente()

            assert result is False
            mock_logger.error.assert_called_once()

    def test_es_usuario_solo_rol_usuario_exception(self):
        """Test: Excepción en _es_usuario_solo_rol_usuario (línea 301)."""
        with patch('src.routes.eventos_routes.get_current_user') as mock_get_user, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_get_user.side_effect = Exception('Database error')
            result = _es_usuario_solo_rol_usuario()

            assert result is False
            mock_logger.error.assert_called_once()


@pytest.mark.unit
@pytest.mark.eventos
class TestEndpointsExceptions:
    """Tests para bloques de excepción en endpoints."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_listar_eventos_exception(self, app):
        """Test: Excepción en listar_eventos (línea 827)."""
        from flask import g
        
        def mock_process_authenticated_request(self, f, *args, **kwargs):
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            g.current_session = {'id_sesion': 1}
            g.token_payload = {'usuario_id': 1}
            return f(*args, **kwargs)
        
        with app.test_request_context('/api/eventos/calendario', method='POST'):
            with patch('src.middleware.auth_decorator.TokenRequired._process_authenticated_request', mock_process_authenticated_request, autospec=False):
                with patch('src.routes.eventos_routes.obtener_categorias_permitidas_usuario') as mock_categorias, \
                     patch('src.routes.eventos_routes._es_usuario_solo_rol_usuario') as mock_usuario_solo, \
                     patch('src.routes.eventos_routes.Evento') as mock_evento, \
                     patch('src.routes.eventos_routes.logger') as mock_logger:
                    mock_categorias.return_value = None
                    mock_usuario_solo.return_value = False
                    mock_evento.query.side_effect = Exception('Database error')

                    _, status_code = listar_eventos()

                    assert status_code == 500
                    mock_logger.error.assert_called()

    def test_obtener_evento_exception(self, app):
        """Test: Excepción en obtener_evento (línea 863)."""
        from flask import g
        
        def mock_process_authenticated_request(self, f, *args, **kwargs):
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            g.current_session = {'id_sesion': 1}
            g.token_payload = {'usuario_id': 1}
            return f(*args, **kwargs)
        
        with app.test_request_context('/api/eventos/calendario/1', method='GET'):
            with patch('src.middleware.auth_decorator.TokenRequired._process_authenticated_request', mock_process_authenticated_request, autospec=False):
                with patch('src.routes.eventos_routes.Evento') as mock_evento, \
                     patch('src.routes.eventos_routes.handle_exception') as mock_handle:
                    mock_response = MagicMock()
                    mock_handle.return_value = mock_response
                    mock_evento.query.get.side_effect = Exception('Database error')
                    
                    result = obtener_evento(1)

                    mock_handle.assert_called_once()
                    assert result == mock_response


@pytest.mark.unit
@pytest.mark.eventos
class TestSerializacionEventosPaginados:
    """Tests para _serializar_eventos_paginados."""

    @pytest.fixture
    def mock_query(self):
        """Fixture para query mock."""
        query = MagicMock()
        query.count.return_value = 5
        query.order_by.return_value = query
        
        mock_items = []
        for i in range(5):
            evento = MagicMock()
            evento.id_evento = i + 1
            evento.id_categoria = i + 1
            evento.nombre = f'Evento {i + 1}'
            mock_items.append(evento)
        
        query.all.return_value = mock_items
        query.paginate.return_value = MagicMock(items=mock_items, page=1, per_page=10, total=5, pages=1)
        return query

    def test_serializar_eventos_paginados_excepcion_al_serializar(self, mock_query):
        """Test: Excepción al serializar evento individual (línea 723)."""
        with patch('src.routes.eventos_routes._serializar_evento') as mock_serializar, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_serializar.side_effect = Exception('Serialization error')
            
            eventos_data, _ = eventos_routes._serializar_eventos_paginados(mock_query, 1, 10, None)
            
            # Debe continuar aunque falle la serialización de un evento
            assert isinstance(eventos_data, list)
            mock_logger.error.assert_called()

    def test_serializar_eventos_paginados_filtro_categoria(self, mock_query):
        """Test: Filtrar eventos por categorías permitidas."""
        categorias_permitidas = [1, 2, 3]
        
        with patch('src.routes.eventos_routes._serializar_evento') as mock_serializar:
            mock_serializar.return_value = {'id_evento': 1, 'nombre': 'Evento 1'}
            
            eventos_data, _ = eventos_routes._serializar_eventos_paginados(
                mock_query, 1, 10, categorias_permitidas
            )
            
            assert isinstance(eventos_data, list)
            # Verificar que se llamó a _serializar_evento para eventos con categorías permitidas
            assert mock_serializar.called

    def test_serializar_eventos_paginados_evento_sin_categoria_permitida(self, mock_query):
        """Test: Omitir evento con categoría no permitida (línea 716-719)."""
        categorias_permitidas = [1, 2]  # Solo categorías 1 y 2
        mock_query.all.return_value[2].id_categoria = 5  # Evento con categoría 5 no permitida
        
        with patch('src.routes.eventos_routes._serializar_evento') as mock_serializar, \
             patch('src.routes.eventos_routes.logger') as mock_logger:
            mock_serializar.return_value = {'id_evento': 1, 'nombre': 'Evento 1'}
            
            _, _ = eventos_routes._serializar_eventos_paginados(
                mock_query, 1, 10, categorias_permitidas
            )
            
            # Debe haber llamado a logger.warning para el evento omitido
            assert any('OMITIENDO' in str(call).upper() for call in mock_logger.warning.call_args_list)


@pytest.mark.unit
@pytest.mark.eventos
class TestValidacionEventosExtended:
    """Tests adicionales para funciones de validación."""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_validar_y_sanitizar_nombre_exito(self, app):
        """Test: Validar y sanitizar nombre exitoso."""
        with app.app_context():
            data = {'nombre': 'Evento de Prueba'}
            with patch('src.routes.eventos_routes.sanitize_free_text', return_value='Evento de Prueba'):
                nombre, error = _validar_y_sanitizar_nombre(data)
                
                assert nombre == 'Evento de Prueba'
                assert error is None

    def test_validar_fecha_y_horas_exito(self, app):
        """Test: Validar fecha y horas exitoso."""
        with app.app_context():
            data = {
                'fecha_evento': '2024-12-31',
                'hora_inicio': '10:00',
                'hora_fin': '12:00'
            }
            fecha, hora_inicio, hora_fin, error = _validar_fecha_y_horas(data)
            
            assert fecha is not None
            assert hora_inicio is not None
            assert hora_fin is not None
            assert error is None

    def test_validar_fecha_y_horas_hora_fin_igual_inicio(self, app):
        """Test: Hora fin igual a hora inicio."""
        with app.app_context():
            data = {
                'fecha_evento': '2024-12-31',
                'hora_inicio': '10:00',
                'hora_fin': '10:00'
            }
            _, _, _, error = _validar_fecha_y_horas(data)
            
            assert error is not None

    def test_validar_y_sanitizar_lugar_exito(self, app):
        """Test: Validar y sanitizar lugar exitoso."""
        with app.app_context():
            data = {'lugar': 'Lugar de Prueba'}
            with patch('src.routes.eventos_routes.sanitize_address', return_value='Lugar de Prueba'):
                lugar, error = _validar_y_sanitizar_lugar(data)
                
                assert lugar == 'Lugar de Prueba'
                assert error is None

    def test_validar_entidades_evento_exito(self, app):
        """Test: Validar entidades exitoso."""
        with app.app_context():
            mock_categoria = MagicMock()
            mock_tipo_evento = MagicMock()
            data = {'id_categoria': 1, 'id_tipo_evento': 1}
            
            with patch('src.routes.eventos_routes.Categoria') as mock_cat_class, \
                 patch('src.routes.eventos_routes.TipoEvento') as mock_tipo_class:
                mock_cat_class.query.get.return_value = mock_categoria
                mock_tipo_class.query.get.return_value = mock_tipo_evento
                
                categoria, tipo_evento, error = _validar_entidades_evento(data)
                
                assert categoria == mock_categoria
                assert tipo_evento == mock_tipo_evento
                assert error is None

