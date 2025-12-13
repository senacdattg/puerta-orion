"""
Tests unitarios para aumentar la cobertura de archivos_routes.py.

Cubre bloques de excepciones llamando directamente a las funciones de las rutas.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from src.routes.archivos_routes import (
    _validar_relaciones,
    subir_archivo,
    eliminar_archivo,
    arreglar_urls,
    registrar_archivos_routes,
    archivos_bp,
)
from src.utils.request_validators import RequestValidationError


@pytest.mark.unit
@pytest.mark.archivos
class TestArchivosRoutesCoverage:
    """Tests unitarios para aumentar cobertura de archivos_routes.py"""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_validar_relaciones_categoria_value_error(self, app):
        """Test: ValueError al convertir id_categoria a int (línea 124)."""
        with app.app_context():
            with patch('src.routes.archivos_routes.Categoria') as mock_categoria:
                # Act & Assert
                with pytest.raises(RequestValidationError) as exc_info:
                    _validar_relaciones(id_tipo_evento=None, id_categoria='invalid')

                assert 'categoría' in str(exc_info.value).lower()
                assert exc_info.value.status_code == 400

    def test_subir_archivo_exception(self, app):
        """Test: Exception handling en subir_archivo (línea 222)."""
        from flask import g
        
        # Mock function to bypass token_required decorator
        def mock_process_authenticated_request(self, f, *args, **kwargs):
            """Mock que ejecuta la función directamente sin validar autenticación."""
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            g.current_session = {'id_sesion': 1}
            g.token_payload = {'usuario_id': 1}
            return f(*args, **kwargs)
        
        with app.test_request_context('/api/archivos/upload', method='POST'):
            with patch('src.middleware.auth_decorator.TokenRequired._process_authenticated_request', mock_process_authenticated_request, autospec=False):
                with patch('src.routes.archivos_routes._validar_y_obtener_archivo') as mock_validar:
                    with patch('src.routes.archivos_routes.db') as mock_db:
                        with patch('src.routes.archivos_routes.logger') as mock_logger:
                            with patch('src.routes.archivos_routes.sanitize_free_text') as mock_sanitize:
                                with patch('src.routes.archivos_routes._validar_relaciones') as mock_validar_rel:
                                    with patch('src.routes.archivos_routes._obtener_upload_folder') as mock_folder:
                                        with patch('src.routes.archivos_routes._construir_url_imagen') as mock_url:
                                            with patch('src.routes.archivos_routes.Galeria') as mock_galeria:
                                                with patch('src.routes.archivos_routes.request') as mock_request:
                                                    # Arrange
                                                    mock_file = MagicMock()
                                                    mock_file.filename = 'test.jpg'
                                                    mock_file.save = MagicMock()
                                                    mock_validar.return_value = (mock_file, 1024)
                                                    mock_sanitize.return_value = 'Test Title'
                                                    mock_validar_rel.return_value = (None, None)
                                                    mock_folder.return_value = MagicMock()
                                                    mock_url.return_value = 'http://test.com/image.jpg'
                                                    mock_request.form.get.side_effect = ['Test Title', '']
                                                    
                                                    # Simular error en db.session.commit
                                                    mock_db.session.commit.side_effect = Exception('Database error')
                                                    mock_db.session.rollback = MagicMock()
                                                    mock_db.session.add = MagicMock()

                                                    # Act
                                                    response, status_code = subir_archivo()

                                                    # Assert
                                                    assert status_code == 500
                                                    assert mock_db.session.rollback.called
                                                    mock_logger.error.assert_called_once()
                                                    data = response.get_json()
                                                    assert data.get('success') is False
                                                    assert 'error' in data

    def test_eliminar_archivo_exception(self, app):
        """Test: Exception handling en eliminar_archivo (línea 246)."""
        from flask import g
        
        # Mock function to bypass token_required decorator
        def mock_process_authenticated_request(self, f, *args, **kwargs):
            """Mock que ejecuta la función directamente sin validar autenticación."""
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            g.current_session = {'id_sesion': 1}
            g.token_payload = {'usuario_id': 1}
            return f(*args, **kwargs)
        
        with app.test_request_context('/api/archivos/delete/1', method='DELETE'):
            with patch('src.middleware.auth_decorator.TokenRequired._process_authenticated_request', mock_process_authenticated_request, autospec=False):
                with patch('src.routes.archivos_routes.Galeria') as mock_galeria:
                    with patch('src.routes.archivos_routes._eliminar_archivo_fisico') as mock_eliminar:
                        with patch('src.routes.archivos_routes.db') as mock_db:
                            with patch('src.routes.archivos_routes.logger') as mock_logger:
                                # Arrange
                                mock_imagen = MagicMock()
                                mock_imagen.url_imagen = '/static/uploads/test.jpg'
                                mock_galeria.query.get.return_value = mock_imagen
                                mock_db.session.delete = MagicMock()
                                mock_db.session.commit.side_effect = Exception('Database error')
                                mock_db.session.rollback = MagicMock()

                                # Act
                                response, status_code = eliminar_archivo(1)

                                # Assert
                                assert status_code == 500
                                assert mock_db.session.rollback.called
                                mock_logger.error.assert_called_once()
                                data = response.get_json()
                                assert data.get('success') is False
                                assert 'error' in data

    def test_arreglar_urls_exception(self, app):
        """Test: Exception handling en arreglar_urls (línea 272)."""
        from flask import g
        
        # Mock function to bypass token_required decorator
        def mock_process_authenticated_request(self, f, *args, **kwargs):
            """Mock que ejecuta la función directamente sin validar autenticación."""
            g.current_user = {'id_usuario': 1, 'username': 'testuser'}
            g.current_session = {'id_sesion': 1}
            g.token_payload = {'usuario_id': 1}
            return f(*args, **kwargs)
        
        with app.test_request_context('/api/archivos/fix-urls', method='POST'):
            with patch('src.middleware.auth_decorator.TokenRequired._process_authenticated_request', mock_process_authenticated_request, autospec=False):
                with patch('src.routes.archivos_routes.Galeria') as mock_galeria:
                    with patch('src.routes.archivos_routes._obtener_base_url') as mock_base_url:
                        with patch('src.routes.archivos_routes.db') as mock_db:
                            with patch('src.routes.archivos_routes.logger') as mock_logger:
                                # Arrange
                                mock_imagen = MagicMock()
                                mock_imagen.url_imagen = '/static/uploads/test.jpg'
                                mock_filter = MagicMock()
                                mock_filter.all.return_value = [mock_imagen]
                                mock_galeria.query.filter.return_value = mock_filter
                                mock_base_url.return_value = 'http://localhost:5000'
                                mock_db.session.commit.side_effect = Exception('Database error')
                                mock_db.session.rollback = MagicMock()

                                # Act
                                response, status_code = arreglar_urls()

                                # Assert
                                assert status_code == 500
                                assert mock_db.session.rollback.called
                                mock_logger.error.assert_called_once()
                                data = response.get_json()
                                assert data.get('success') is False
                                assert 'error' in data

    def test_registrar_archivos_routes(self, app):
        """Test: registrar_archivos_routes (línea 282-285)."""
        with patch('src.routes.archivos_routes.logger') as mock_logger:
            # Act
            registrar_archivos_routes(app)

            # Assert
            assert archivos_bp.name in [bp.name for bp in app.blueprints.values()]
            mock_logger.info.assert_called_once_with('Rutas de archivos registradas exitosamente')

