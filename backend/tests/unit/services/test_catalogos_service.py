"""
Tests for catalogos service.

This module contains tests that verify catalog retrieval operations,
including types of documents, sexes, categories, diagnoses, etc.
"""

import pytest
from unittest.mock import patch, MagicMock

from src.services.catalogos_service import CatalogosService, catalogos_service
from src.models.catalogos.tipo_documento import TipoDocumento
from src.models.categorias.sexo import Sexo
from src.models.categorias.categoria import Categoria
from src.models.salud.diagnostico import Diagnostico
from src.models.salud.tipo_enfermedad import TipoEnfermedad
from src.models.categorias.grupo_sanguineo import GrupoSanguineo
from src.models.categorias.ciudad_residencia import CiudadResidencia
from src.models.categorias.deporte import Deporte
from src.models.categorias.escuela import Escuela
from src.models.categorias.institucion_registro import InstitucionRegistro
from src.models.catalogos.eps import EPS


@pytest.mark.unit
class TestCatalogosService:
    """Tests for CatalogosService."""
    
    @pytest.fixture
    def catalogos_service_instance(self):
        """Create an instance of CatalogosService."""
        return CatalogosService()
    
    def test_obtener_catalogos_completos_success(self, catalogos_service_instance):
        """Test: Successful retrieval of all catalogs."""
        mock_tipos = [MagicMock()]
        mock_sexos = [MagicMock()]
        mock_categorias = [MagicMock()]
        
        with patch.object(catalogos_service_instance, '_obtener_tipos_documento', return_value=mock_tipos) as mock_tipos_doc, \
             patch.object(catalogos_service_instance, '_obtener_sexos', return_value=mock_sexos) as mock_sexos_func, \
             patch.object(catalogos_service_instance, '_obtener_categorias', return_value=mock_categorias) as mock_categorias_func:
            
            result = catalogos_service_instance.obtener_catalogos_completos()
            
            assert 'tipos_documento' in result
            assert 'sexos' in result
            assert 'categorias' in result
            assert result['tipos_documento'] == mock_tipos
            assert result['sexos'] == mock_sexos
            assert result['categorias'] == mock_categorias
            mock_tipos_doc.assert_called_once()
            mock_sexos_func.assert_called_once()
            mock_categorias_func.assert_called_once()
    
    def test_obtener_catalogos_completos_error(self, catalogos_service_instance):
        """Test: Error handling in catalog retrieval."""
        with patch.object(catalogos_service_instance, '_obtener_tipos_documento', side_effect=Exception("Database error")):
            with pytest.raises(Exception, match="Database error"):
                catalogos_service_instance.obtener_catalogos_completos()
    
    def test_obtener_tipos_documento_success(self, catalogos_service_instance):
        """Test: Successful retrieval of document types."""
        mock_tipo1 = MagicMock()
        mock_tipo1.id_documento = 1
        mock_tipo1.nombre_documento = 'Cédula de Ciudadanía'
        
        mock_tipo2 = MagicMock()
        mock_tipo2.id_documento = 2
        mock_tipo2.nombre_documento = 'Cédula de Extranjería'
        
        with patch('src.services.catalogos_service.TipoDocumento') as mock_tipo_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_tipo1, mock_tipo2]
            mock_tipo_class.query = mock_query
            
            result = catalogos_service_instance._obtener_tipos_documento()
            
            assert len(result) == 2
            assert result[0]['id'] == 1
            assert result[0]['nombre'] == 'Cédula de Ciudadanía'
            assert result[0]['codigo'] == 'cc'
            assert result[1]['codigo'] == 'ce'
    
    def test_obtener_tipos_documento_error(self, catalogos_service_instance):
        """Test: Error handling in document types retrieval."""
        with patch('src.services.catalogos_service.TipoDocumento') as mock_tipo_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_tipo_class.query = mock_query
            
            result = catalogos_service_instance._obtener_tipos_documento()
            
            assert result == []
    
    def test_obtener_sexos_success(self, catalogos_service_instance):
        """Test: Successful retrieval of sexes."""
        mock_sexo1 = MagicMock()
        mock_sexo1.id_sexo = 1
        mock_sexo1.nombre = 'Masculino'
        
        mock_sexo2 = MagicMock()
        mock_sexo2.id_sexo = 2
        mock_sexo2.nombre = 'Femenino'
        
        with patch('src.services.catalogos_service.Sexo') as mock_sexo_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_sexo1, mock_sexo2]
            mock_sexo_class.query = mock_query
            
            result = catalogos_service_instance._obtener_sexos()
            
            assert len(result) == 2
            assert result[0]['id'] == 1
            assert result[0]['nombre'] == 'Masculino'
            assert result[0]['valor'] == 'masculino'
            assert result[1]['valor'] == 'femenino'
    
    def test_obtener_sexos_error(self, catalogos_service_instance):
        """Test: Error handling in sexes retrieval."""
        with patch('src.services.catalogos_service.Sexo') as mock_sexo_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_sexo_class.query = mock_query
            
            result = catalogos_service_instance._obtener_sexos()
            
            assert result == []
    
    def test_obtener_categorias_success(self, catalogos_service_instance):
        """Test: Successful retrieval of categories."""
        mock_categoria1 = MagicMock()
        mock_categoria1.id_categoria = 1
        mock_categoria1.nombre_categoria = 'Pre-infantil'
        mock_categoria1.codigo_categoria = 'PRE'
        mock_categoria1.estado = True
        
        mock_categoria2 = MagicMock()
        mock_categoria2.id_categoria = 2
        mock_categoria2.nombre_categoria = 'Infantil'
        mock_categoria2.codigo_categoria = 'INF'
        mock_categoria2.estado = True
        
        with patch('src.services.catalogos_service.Categoria') as mock_categoria_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_categoria1, mock_categoria2]
            mock_categoria_class.query = mock_query
            
            result = catalogos_service_instance._obtener_categorias()
            
            assert len(result) == 2
            assert result[0]['id'] == 1
            assert result[0]['nombre'] == 'Pre-infantil'
            assert result[0]['codigo'] == 'PRE'
    
    def test_obtener_categorias_error(self, catalogos_service_instance):
        """Test: Error handling in categories retrieval."""
        with patch('src.services.catalogos_service.Categoria') as mock_categoria_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.side_effect = Exception("Database error")
            mock_categoria_class.query = mock_query
            
            result = catalogos_service_instance._obtener_categorias()
            
            assert result == []
    
    def test_obtener_diagnosticos_success(self, catalogos_service_instance):
        """Test: Successful retrieval of diagnoses."""
        mock_diagnostico1 = MagicMock()
        mock_diagnostico1.to_dict.return_value = {'id_diagnostico': 1, 'nombre': 'Asma'}
        
        mock_diagnostico2 = MagicMock()
        mock_diagnostico2.to_dict.return_value = {'id_diagnostico': 2, 'nombre': 'Diabetes'}
        
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_diagnostico1, mock_diagnostico2]
            mock_diagnostico_class.query = mock_query
            
            result = catalogos_service_instance.obtener_diagnosticos()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 2
    
    def test_obtener_diagnosticos_with_tipo_enfermedad(self, catalogos_service_instance):
        """Test: Successful retrieval of diagnoses filtered by tipo_enfermedad."""
        mock_diagnostico = MagicMock()
        mock_diagnostico.to_dict.return_value = {'id_diagnostico': 1, 'nombre': 'Asma'}
        
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_diagnostico]
            mock_diagnostico_class.query = mock_query
            
            result = catalogos_service_instance.obtener_diagnosticos(id_tipo_enfermedad=1)
            
            assert result['success'] is True
            assert len(result['data']) == 1
            mock_query.filter_by.assert_called_once_with(id_tipo_enfermedad=1)
    
    def test_obtener_diagnosticos_error(self, catalogos_service_instance):
        """Test: Error handling in diagnoses retrieval."""
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_diagnostico_class.query = mock_query
            
            result = catalogos_service_instance.obtener_diagnosticos()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_tipos_enfermedad_success(self, catalogos_service_instance):
        """Test: Successful retrieval of disease types."""
        mock_tipo = MagicMock()
        mock_tipo.id_tipo_enfermedad = 1
        mock_tipo.to_dict.return_value = {'id_tipo_enfermedad': 1, 'nombre': 'Respiratorias'}
        
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_tipo]
            mock_tipo_class.query = mock_query
            
            result = catalogos_service_instance.obtener_tipos_enfermedad()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_tipos_enfermedad_with_diagnosticos(self, catalogos_service_instance):
        """Test: Successful retrieval of disease types with diagnoses."""
        mock_diagnostico = MagicMock()
        mock_diagnostico.to_dict.return_value = {'id_diagnostico': 1, 'nombre': 'Asma'}
        
        mock_tipo = MagicMock()
        mock_tipo.id_tipo_enfermedad = 1
        mock_tipo.to_dict.return_value = {'id_tipo_enfermedad': 1, 'nombre': 'Respiratorias'}
        
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo_class, \
             patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico_class:
            
            mock_tipo_query = MagicMock()
            mock_tipo_query.all.return_value = [mock_tipo]
            mock_tipo_class.query = mock_tipo_query
            
            mock_diagnostico_query = MagicMock()
            mock_diagnostico_query.filter_by.return_value.all.return_value = [mock_diagnostico]
            mock_diagnostico_class.query = mock_diagnostico_query
            
            result = catalogos_service_instance.obtener_tipos_enfermedad(incluir_diagnosticos=True)
            
            assert result['success'] is True
            assert 'diagnosticos' in result['data'][0]
            assert len(result['data'][0]['diagnosticos']) == 1
    
    def test_obtener_tipos_enfermedad_error(self, catalogos_service_instance):
        """Test: Error handling in disease types retrieval."""
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_tipo_class.query = mock_query
            
            result = catalogos_service_instance.obtener_tipos_enfermedad()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_grupos_sanguineos_success(self, catalogos_service_instance):
        """Test: Successful retrieval of blood groups."""
        mock_grupo = MagicMock()
        mock_grupo.to_dict.return_value = {'id_tipo_sangre': 1, 'nombre': 'O+'}
        
        with patch('src.services.catalogos_service.GrupoSanguineo') as mock_grupo_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_grupo]
            mock_grupo_class.query = mock_query
            
            result = catalogos_service_instance.obtener_grupos_sanguineos()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_grupos_sanguineos_error(self, catalogos_service_instance):
        """Test: Error handling in blood groups retrieval."""
        with patch('src.services.catalogos_service.GrupoSanguineo') as mock_grupo_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_grupo_class.query = mock_query
            
            result = catalogos_service_instance.obtener_grupos_sanguineos()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_ciudades_residencia_success(self, catalogos_service_instance):
        """Test: Successful retrieval of cities of residence."""
        mock_ciudad = MagicMock()
        mock_ciudad.to_dict.return_value = {'id_ciudad': 1, 'nombre': 'Bogotá'}
        
        with patch('src.services.catalogos_service.CiudadResidencia') as mock_ciudad_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_ciudad]
            mock_ciudad_class.query = mock_query
            
            result = catalogos_service_instance.obtener_ciudades_residencia()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_ciudades_residencia_error(self, catalogos_service_instance):
        """Test: Error handling in cities of residence retrieval."""
        with patch('src.services.catalogos_service.CiudadResidencia') as mock_ciudad_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_ciudad_class.query = mock_query
            
            result = catalogos_service_instance.obtener_ciudades_residencia()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_eps_success(self, catalogos_service_instance):
        """Test: Successful retrieval of EPS."""
        mock_eps = MagicMock()
        mock_eps.to_dict.return_value = {'id_eps': 1, 'nombre': 'EPS Test'}
        
        with patch('src.services.catalogos_service.EPS') as mock_eps_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = [mock_eps]
            mock_eps_class.query = mock_query
            
            result = catalogos_service_instance.obtener_eps()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
            mock_query.filter_by.assert_called_once_with(estado=True)
    
    def test_obtener_eps_error(self, catalogos_service_instance):
        """Test: Error handling in EPS retrieval."""
        with patch('src.services.catalogos_service.EPS') as mock_eps_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.side_effect = Exception("Database error")
            mock_eps_class.query = mock_query
            
            result = catalogos_service_instance.obtener_eps()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_deportes_success(self, catalogos_service_instance):
        """Test: Successful retrieval of sports."""
        mock_deporte = MagicMock()
        mock_deporte.to_dict.return_value = {'id_deporte': 1, 'nombre': 'Fútbol'}
        
        with patch('src.services.catalogos_service.Deporte') as mock_deporte_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_deporte]
            mock_deporte_class.query = mock_query
            
            result = catalogos_service_instance.obtener_deportes()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_deportes_error(self, catalogos_service_instance):
        """Test: Error handling in sports retrieval."""
        with patch('src.services.catalogos_service.Deporte') as mock_deporte_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_deporte_class.query = mock_query
            
            result = catalogos_service_instance.obtener_deportes()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_escuelas_success(self, catalogos_service_instance):
        """Test: Successful retrieval of schools."""
        mock_escuela = MagicMock()
        mock_escuela.to_dict.return_value = {'id_escuela': 1, 'nombre': 'Escuela Test'}
        
        with patch('src.services.catalogos_service.Escuela') as mock_escuela_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_escuela]
            mock_escuela_class.query = mock_query
            
            result = catalogos_service_instance.obtener_escuelas()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_escuelas_error(self, catalogos_service_instance):
        """Test: Error handling in schools retrieval."""
        with patch('src.services.catalogos_service.Escuela') as mock_escuela_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_escuela_class.query = mock_query
            
            result = catalogos_service_instance.obtener_escuelas()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_instituciones_registro_success(self, catalogos_service_instance):
        """Test: Successful retrieval of registration institutions."""
        mock_institucion = MagicMock()
        mock_institucion.to_dict.return_value = {'id_institucion': 1, 'nombre': 'Institución Test'}
        
        with patch('src.services.catalogos_service.InstitucionRegistro') as mock_institucion_class:
            mock_query = MagicMock()
            mock_query.all.return_value = [mock_institucion]
            mock_institucion_class.query = mock_query
            
            result = catalogos_service_instance.obtener_instituciones_registro()
            
            assert result['success'] is True
            assert result['status_code'] == 200
            assert len(result['data']) == 1
    
    def test_obtener_instituciones_registro_error(self, catalogos_service_instance):
        """Test: Error handling in registration institutions retrieval."""
        with patch('src.services.catalogos_service.InstitucionRegistro') as mock_institucion_class:
            mock_query = MagicMock()
            mock_query.all.side_effect = Exception("Database error")
            mock_institucion_class.query = mock_query
            
            result = catalogos_service_instance.obtener_instituciones_registro()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_global_catalogos_service_instance(self):
        """Test: Global catalogos_service instance exists."""
        assert catalogos_service is not None
        assert isinstance(catalogos_service, CatalogosService)

