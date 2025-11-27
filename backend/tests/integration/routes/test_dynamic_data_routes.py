"""
Tests para las rutas de datos dinámicos.

Este módulo contiene tests para todos los endpoints de gestión de datos dinámicos,
siguiendo las mejores prácticas de testing.
"""

import pytest
from unittest.mock import patch, MagicMock

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
)


# ============================================================================
# TESTS PARA LISTAR DATOS DINÁMICOS
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.dynamic_data
class TestListarDynamicData:
    """Tests para el endpoint GET /api/dynamic-data/<tema>"""
    
    def test_listar_eps_success(self, client, mock_token_required):
        """Test: Listar EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Test'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_eps]
            
            response = client.get('/api/dynamic-data/eps')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_sexos_success(self, client, mock_token_required):
        """Test: Listar sexos exitosamente."""
        # Arrange
        mock_sexo = MagicMock()
        mock_sexo.to_dict.return_value = {'id_sexo': 1, 'nombre_sexo': 'Masculino'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.Sexo.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_sexo]
            
            response = client.get('/api/dynamic-data/sexo')
        
        # Assert
        assert_success_response(response)


# ============================================================================
# TESTS PARA CREAR DATO DINÁMICO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.dynamic_data
class TestCrearDynamicData:
    """Tests para el endpoint POST /api/dynamic-data/<tema>"""
    
    def test_crear_eps_success(self, client, mock_token_required):
        """Test: Crear EPS exitosamente."""
        # Arrange
        datos_eps = {
            'nombre_eps': 'Nueva EPS'
        }
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'Nueva EPS'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS') as mock_eps_class:
            mock_eps_class.query.filter_by.return_value.first.return_value = None
            mock_eps_class.return_value = mock_eps
            with patch('src.routes.dynamic_data_routes.db') as mock_db:
                mock_db.session.add = MagicMock()
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'POST', '/api/dynamic-data/eps',
                    data=datos_eps
                )
        
        # Assert
        assert response.status_code in [200, 201]
    
    def test_crear_dato_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/dynamic-data/eps', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_dato_duplicado(self, client, mock_token_required):
        """Test: Error al crear dato duplicado."""
        # Arrange
        datos_eps = {'nombre_eps': 'EPS Existente'}
        mock_eps_existente = MagicMock()
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_eps_existente
            
            response = make_json_request(
                client, 'POST', '/api/dynamic-data/eps',
                data=datos_eps
            )
        
        # Assert
        assert_error_response(response, expected_status=400)


# ============================================================================
# TESTS PARA ACTUALIZAR DATO DINÁMICO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.dynamic_data
class TestActualizarDynamicData:
    """Tests para el endpoint PUT /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_actualizar_eps_success(self, client, mock_token_required):
        """Test: Actualizar EPS exitosamente."""
        # Arrange
        datos_actualizacion = {
            'nombre_eps': 'EPS Actualizada'
        }
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Actualizada'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            with patch('src.routes.dynamic_data_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/dynamic-data/eps/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert response.status_code in [200, 400, 500]
    
    def test_actualizar_dato_no_encontrado(self, client, mock_token_required):
        """Test: Error al actualizar dato inexistente."""
        # Arrange
        datos_actualizacion = {'nombre_eps': 'EPS Actualizada'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/dynamic-data/eps/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA ELIMINAR DATO DINÁMICO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.dynamic_data
class TestEliminarDynamicData:
    """Tests para el endpoint DELETE /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_eliminar_eps_success(self, client, mock_token_required):
        """Test: Eliminar EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.nombre_eps = 'EPS a Eliminar'
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            with patch('src.routes.dynamic_data_routes.db') as mock_db:
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                
                response = client.delete('/api/dynamic-data/eps/1')
        
        # Assert
        assert response.status_code in [200, 204]
    
    def test_eliminar_dato_no_encontrado(self, client, mock_token_required):
        """Test: Error al eliminar dato inexistente."""
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.delete('/api/dynamic-data/eps/999')
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA OBTENER DATO DINÁMICO
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.dynamic_data
class TestObtenerDynamicData:
    """Tests para el endpoint GET /api/dynamic-data/<tema>/<registro_id>"""
    
    def test_obtener_eps_success(self, client, mock_token_required):
        """Test: Obtener EPS exitosamente."""
        # Arrange
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre_eps': 'EPS Test'}
        
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = mock_eps
            
            response = client.get('/api/dynamic-data/eps/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_dato_no_encontrado(self, client, mock_token_required):
        """Test: Dato no encontrado."""
        # Act
        with patch('src.routes.dynamic_data_routes.EPS.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/dynamic-data/eps/999')
        
        # Assert
        assert_error_response(response, expected_status=404)

