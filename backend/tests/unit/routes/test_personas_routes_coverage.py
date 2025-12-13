"""
Tests unitarios para aumentar la cobertura de personas_routes.py.

Cubre bloques de excepciones llamando directamente a las funciones de las rutas.
"""

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask

from src.routes.personas_routes import (
    listar_personas,
    obtener_persona,
    actualizar_persona,
    eliminar_persona,
    activar_persona,
    _preparar_actualizacion,
    registrar_personas_routes,
    personas_bp,
)
from src.utils.request_validators import RequestValidationError
from src.utils.validations import ValidationError


@pytest.mark.unit
@pytest.mark.personas
class TestPersonasRoutesCoverage:
    """Tests unitarios para aumentar cobertura de personas_routes.py"""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Flask."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def test_listar_personas_exception(self, app):
        """Test: Exception handling en listar_personas (líneas 242-247)."""
        with app.test_request_context('/api/personas/personas'):
            with patch('src.routes.personas_routes._obtener_paginacion', return_value=(1, 10)):
                with patch('src.routes.personas_routes.request') as mock_request:
                    mock_request.args.get.return_value = None
                    with patch('src.routes.personas_routes.Persona.query') as mock_query:
                        mock_query.filter_by.return_value = mock_query
                        mock_query.filter.return_value = mock_query
                        mock_query.paginate.side_effect = Exception("Database connection error")
                        
                        # Act
                        response, status = listar_personas()
                        
                        # Assert
                        assert status == 500
                        data = response.get_json()
                        assert data is not None
                        assert data.get('success') is False
                        assert 'error' in data

    def test_obtener_persona_exception(self, app):
        """Test: Exception handling en obtener_persona (líneas 266-271)."""
        with app.test_request_context('/api/personas/personas/1'):
            with patch('src.routes.personas_routes._obtener_persona') as mock_obtener:
                mock_obtener.side_effect = Exception("Database error")
                
                # Act
                response, status = obtener_persona(1)
                
                # Assert
                assert status == 500
                data = response.get_json()
                assert data is not None
                assert data.get('success') is False
                assert 'error' in data

    def test_actualizar_persona_validation_error(self, app):
        """Test: ValidationError handling en actualizar_persona (líneas 320-330)."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.to_dict.return_value = {'id_persona': 1}
        
        with app.test_request_context('/api/personas/personas/1', method='PUT', json={'telefono': '123'}):
            with patch('src.routes.personas_routes.obtener_json_requerido', return_value={'telefono': '123'}):
                with patch('src.routes.personas_routes._obtener_persona', return_value=mock_persona):
                    with patch('src.routes.personas_routes._validar_relaciones'):
                        with patch('src.routes.personas_routes._preparar_actualizacion') as mock_preparar:
                            with patch('src.routes.personas_routes.db') as mock_db:
                                mock_preparar.side_effect = ValidationError('Teléfono inválido')
                                mock_db.session.rollback = MagicMock()
                                
                                # Act
                                response, status = actualizar_persona(1)
                                
                                # Assert
                                assert status == 400
                                data = response.get_json()
                                assert data is not None
                                assert data.get('success') is False
                                assert 'error' in data

    def test_actualizar_persona_exception(self, app):
        """Test: Exception handling en actualizar_persona (líneas 331-337)."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        
        with app.test_request_context('/api/personas/personas/1', method='PUT', json={'primer_nombre': 'Juan'}):
            with patch('src.routes.personas_routes.obtener_json_requerido', return_value={'primer_nombre': 'Juan'}):
                with patch('src.routes.personas_routes._obtener_persona', return_value=mock_persona):
                    with patch('src.routes.personas_routes._validar_relaciones') as mock_validar:
                        with patch('src.routes.personas_routes.db') as mock_db:
                            mock_validar.side_effect = Exception("Unexpected database error")
                            mock_db.session.rollback = MagicMock()
                            
                            # Act
                            response, status = actualizar_persona(1)
                            
                            # Assert
                            assert status == 500
                            data = response.get_json()
                            assert data is not None
                            assert data.get('success') is False
                            assert 'error' in data

    def test_eliminar_persona_exception(self, app):
        """Test: Exception handling en eliminar_persona (líneas 359-365)."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.estado = True
        
        with app.test_request_context('/api/personas/personas/1', method='DELETE'):
            with patch('src.routes.personas_routes._obtener_persona', return_value=mock_persona):
                with patch('src.routes.personas_routes.db') as mock_db:
                    mock_db.session.commit.side_effect = Exception("Database commit error")
                    mock_db.session.rollback = MagicMock()
                    
                    # Act
                    response, status = eliminar_persona(1)
                    
                    # Assert
                    assert status == 500
                    data = response.get_json()
                    assert data is not None
                    assert data.get('success') is False
                    assert 'error' in data

    def test_activar_persona_exception(self, app):
        """Test: Exception handling en activar_persona (líneas 388-394)."""
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.estado = False
        mock_persona.to_dict.return_value = {'id_persona': 1, 'estado': True}
        
        with app.test_request_context('/api/personas/personas/1/activar', method='PUT'):
            with patch('src.routes.personas_routes._obtener_persona', return_value=mock_persona):
                with patch('src.routes.personas_routes.db') as mock_db:
                    mock_db.session.commit.side_effect = Exception("Database commit error")
                    mock_db.session.rollback = MagicMock()
                    
                    # Act
                    response, status = activar_persona(1)
                    
                    # Assert
                    assert status == 500
                    data = response.get_json()
                    assert data is not None
                    assert data.get('success') is False
                    assert 'error' in data

    def test_preparar_actualizacion_documento_invalido(self, app):
        """Test: ValidationError handling en _preparar_actualizacion para documento (líneas 190-191)."""
        with app.app_context():
            # Arrange
            data = {'documento': '123'}  # Muy corto
            
            with patch('src.utils.validations.validate_document') as mock_validate:
                mock_validate.side_effect = ValidationError('Documento inválido')
                
                # Act & Assert
                with pytest.raises(RequestValidationError) as exc_info:
                    _preparar_actualizacion(1, data)
                
                assert exc_info.value.status_code == 400
                assert 'documento' in str(exc_info.value).lower()

    def test_registrar_personas_routes(self):
        """Test: registrar_personas_routes (líneas 397-400)."""
        # Arrange
        test_app = Flask(__name__)
        
        with patch('src.routes.personas_routes.logger') as mock_logger:
            # Act
            registrar_personas_routes(test_app)
            
            # Assert
            # Verificar que el blueprint está registrado
            assert personas_bp.name in [bp.name for bp in test_app.blueprints.values()]
            mock_logger.info.assert_called_once_with("Rutas de personas registradas exitosamente")

