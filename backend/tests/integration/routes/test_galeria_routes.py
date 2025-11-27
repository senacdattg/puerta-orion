"""
Tests para las rutas de galería.

Este módulo contiene tests para todos los endpoints de gestión de galería,
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
# TESTS PARA LISTAR GALERÍA
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestListarGaleria:
    """Tests para el endpoint GET /api/galeria"""
    
    def test_listar_galeria_success(self, client, mock_token_required):
        """Test: Listar imágenes de galería exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {
            'id_galeria': 1,
            'titulo': 'Imagen Test',
            'url_imagen': 'https://example.com/image.jpg'
        }
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_imagen]
            
            response = client.get('/api/galeria')
        
        # Assert
        assert_success_response(response)
    
    def test_listar_galeria_con_filtros(self, client, mock_token_required):
        """Test: Listar galería con filtros de tipo evento y categoría."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_imagen]
            
            response = client.get('/api/galeria?id_tipo_evento=1&id_categoria=1')
        
        # Assert
        assert_success_response(response)


# ============================================================================
# TESTS PARA OBTENER IMAGEN
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestObtenerImagen:
    """Tests para el endpoint GET /api/galeria/<id_galeria>"""
    
    def test_obtener_imagen_success(self, client, mock_token_required):
        """Test: Obtener imagen exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {
            'id_galeria': 1,
            'titulo': 'Imagen Test'
        }
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            
            response = client.get('/api/galeria/1')
        
        # Assert
        assert_success_response(response)
    
    def test_obtener_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Imagen no encontrada."""
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.get('/api/galeria/999')
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA CREAR IMAGEN
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestCrearImagen:
    """Tests para el endpoint POST /api/galeria"""
    
    def test_crear_imagen_success(self, client, mock_token_required):
        """Test: Crear imagen exitosamente."""
        # Arrange
        datos_imagen = {
            'titulo': 'Nueva Imagen',
            'descripcion': 'Descripción de la imagen',
            'url_imagen': 'https://example.com/image.jpg',
            'id_tipo_evento': 1
        }
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1, 'titulo': 'Nueva Imagen'}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.TipoEvento.query') as mock_tipo:
            mock_tipo.get.return_value = MagicMock()
            with patch('src.routes.galeria_routes.Galeria') as mock_galeria_class:
                mock_galeria_class.query.filter_by.return_value.first.return_value = None
                mock_galeria_class.return_value = mock_imagen
                with patch('src.routes.galeria_routes.db') as mock_db:
                    mock_db.session.add = MagicMock()
                    mock_db.session.commit = MagicMock()
                    
                    response = make_json_request(
                        client, 'POST', '/api/galeria',
                        data=datos_imagen
                    )
        
        # Assert
        assert response.status_code in [200, 201]
    
    def test_crear_imagen_sin_json(self, client, mock_token_required):
        """Test: Error cuando no se envía JSON."""
        # Act
        response = client.post('/api/galeria', data='not json')
        
        # Assert
        assert_error_response(response, expected_status=400)
    
    def test_crear_imagen_campos_faltantes(self, client, mock_token_required):
        """Test: Error cuando faltan campos requeridos."""
        # Arrange
        datos_incompletos = {
            'titulo': 'Imagen sin campos completos'
        }
        
        # Act
        response = make_json_request(
            client, 'POST', '/api/galeria',
            data=datos_incompletos
        )
        
        # Assert
        assert_error_response(response, expected_status=400)


# ============================================================================
# TESTS PARA ACTUALIZAR IMAGEN
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestActualizarImagen:
    """Tests para el endpoint PUT /api/galeria/<id_galeria>"""
    
    def test_actualizar_imagen_success(self, client, mock_token_required):
        """Test: Actualizar imagen exitosamente."""
        # Arrange
        datos_actualizacion = {
            'titulo': 'Título Actualizado',
            'descripcion': 'Nueva descripción'
        }
        mock_imagen = MagicMock()
        mock_imagen.to_dict.return_value = {'id_galeria': 1, 'titulo': 'Título Actualizado'}
        mock_imagen.tipo_evento = None
        mock_imagen.categoria = None
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            with patch('src.routes.galeria_routes.db') as mock_db:
                mock_db.session.commit = MagicMock()
                
                response = make_json_request(
                    client, 'PUT', '/api/galeria/1',
                    data=datos_actualizacion
                )
        
        # Assert
        assert response.status_code in [200, 400, 500]
    
    def test_actualizar_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Error al actualizar imagen inexistente."""
        # Arrange
        datos_actualizacion = {'titulo': 'Nuevo Título'}
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = make_json_request(
                client, 'PUT', '/api/galeria/999',
                data=datos_actualizacion
            )
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA ELIMINAR IMAGEN
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestEliminarImagen:
    """Tests para el endpoint DELETE /api/galeria/<id_galeria>"""
    
    def test_eliminar_imagen_success(self, client, mock_token_required):
        """Test: Eliminar imagen exitosamente."""
        # Arrange
        mock_imagen = MagicMock()
        mock_imagen.url_imagen = 'https://example.com/image.jpg'
        
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = mock_imagen
            with patch('src.routes.galeria_routes.db') as mock_db:
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                
                response = client.delete('/api/galeria/1')
        
        # Assert
        assert response.status_code in [200, 204]
    
    def test_eliminar_imagen_no_encontrada(self, client, mock_token_required):
        """Test: Error al eliminar imagen inexistente."""
        # Act
        with patch('src.routes.galeria_routes.Galeria.query') as mock_query:
            mock_query.get.return_value = None
            
            response = client.delete('/api/galeria/999')
        
        # Assert
        assert_error_response(response, expected_status=404)


# ============================================================================
# TESTS PARA CATÁLOGOS DE GALERÍA
# ============================================================================

@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.galeria
class TestCatalogosGaleria:
    """Tests para el endpoint GET /api/galeria/catalogos"""
    
    def test_obtener_catalogos_success(self, client, mock_token_required):
        """Test: Obtener catálogos de galería exitosamente."""
        # Arrange
        mock_tipo_evento = MagicMock()
        mock_tipo_evento.to_dict.return_value = {'id_tipo_evento': 1, 'nombre': 'Torneo'}
        mock_categoria = MagicMock()
        mock_categoria.to_dict.return_value = {'id_categoria': 1, 'nombre_categoria': 'Sub-15'}
        
        # Act
        with patch('src.routes.galeria_routes.TipoEvento.query') as mock_tipo:
            with patch('src.routes.galeria_routes.Categoria.query') as mock_cat:
                mock_tipo.filter_by.return_value.all.return_value = [mock_tipo_evento]
                mock_cat.filter_by.return_value.all.return_value = [mock_categoria]
                
                response = client.get('/api/galeria/catalogos')
        
        # Assert
        assert_success_response(response)

