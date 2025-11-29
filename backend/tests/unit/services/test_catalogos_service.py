"""
Tests para el servicio de catálogos.

Este módulo contiene tests que verifican la funcionalidad
del servicio de catálogos, incluyendo la obtención de todos
los catálogos y catálogos individuales.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.services.catalogos_service import CatalogosService


@pytest.mark.unit
class TestCatalogosService:
    """Tests para CatalogosService."""
    
    def test_init(self):
        """Test: Inicialización del servicio."""
        service = CatalogosService()
        assert service is not None
        assert service.logger is not None
    
    def test_obtener_catalogos_completos_success(self, db_session, tipo_documento, sexo, categoria):
        """Test: Obtener todos los catálogos exitosamente."""
        service = CatalogosService()
        
        result = service.obtener_catalogos_completos()
        
        assert 'tipos_documento' in result
        assert 'sexos' in result
        assert 'categorias' in result
        assert isinstance(result['tipos_documento'], list)
        assert isinstance(result['sexos'], list)
        assert isinstance(result['categorias'], list)
    
    def test_obtener_catalogos_completos_error(self, db_session):
        """Test: Error al obtener catálogos completos."""
        service = CatalogosService()
        
        with patch.object(service, '_obtener_tipos_documento', side_effect=Exception("DB Error")):
            with pytest.raises(Exception):
                service.obtener_catalogos_completos()
    
    def test_obtener_tipos_documento_success(self, db_session, tipo_documento):
        """Test: Obtener tipos de documento exitosamente."""
        service = CatalogosService()
        
        result = service._obtener_tipos_documento()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'id' in result[0]
            assert 'codigo' in result[0]
            assert 'nombre' in result[0]
    
    def test_obtener_tipos_documento_error(self, db_session):
        """Test: Error al obtener tipos de documento."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.TipoDocumento') as mock_tipo:
            mock_tipo.query.all.side_effect = Exception("DB Error")
            
            result = service._obtener_tipos_documento()
            
            assert result == []
    
    def test_obtener_sexos_success(self, db_session, sexo):
        """Test: Obtener sexos exitosamente."""
        service = CatalogosService()
        
        result = service._obtener_sexos()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'id' in result[0]
            assert 'valor' in result[0]
            assert 'nombre' in result[0]
    
    def test_obtener_sexos_error(self, db_session):
        """Test: Error al obtener sexos."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Sexo') as mock_sexo:
            mock_sexo.query.all.side_effect = Exception("DB Error")
            
            result = service._obtener_sexos()
            
            assert result == []
    
    def test_obtener_categorias_success(self, db_session, categoria):
        """Test: Obtener categorías exitosamente."""
        service = CatalogosService()
        
        result = service._obtener_categorias()
        
        assert isinstance(result, list)
        if len(result) > 0:
            assert 'id' in result[0]
            assert 'codigo' in result[0]
            assert 'nombre' in result[0]
    
    def test_obtener_categorias_error(self, db_session):
        """Test: Error al obtener categorías."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Categoria') as mock_categoria:
            mock_categoria.query.filter_by.return_value.all.side_effect = Exception("DB Error")
            
            result = service._obtener_categorias()
            
            assert result == []
    
    def test_obtener_diagnosticos_success(self, db_session):
        """Test: Obtener diagnósticos exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico:
            mock_diagnostico.query.all.return_value = []
            
            result = service.obtener_diagnosticos()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_diagnosticos_con_filtro(self, db_session):
        """Test: Obtener diagnósticos con filtro de tipo enfermedad."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico:
            mock_diagnostico.query.filter_by.return_value.all.return_value = []
            
            result = service.obtener_diagnosticos(id_tipo_enfermedad=1)
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_diagnosticos_error(self, db_session):
        """Test: Error al obtener diagnósticos."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Diagnostico') as mock_diagnostico:
            mock_diagnostico.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_diagnosticos()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_tipos_enfermedad_success(self, db_session):
        """Test: Obtener tipos de enfermedad exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Test'}
            mock_tipo.query.all.return_value = [mock_obj]
            
            result = service.obtener_tipos_enfermedad()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_tipos_enfermedad_con_diagnosticos(self, db_session):
        """Test: Obtener tipos de enfermedad con diagnósticos incluidos."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo, \
             patch('src.services.catalogos_service.Diagnostico') as mock_diag:
            mock_obj = MagicMock()
            mock_obj.id_tipo_enfermedad = 1
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Test'}
            mock_tipo.query.all.return_value = [mock_obj]
            mock_diag.query.filter_by.return_value.all.return_value = []
            
            result = service.obtener_tipos_enfermedad(incluir_diagnosticos=True)
            
            assert result['success'] is True
            assert 'data' in result
    
    def test_obtener_tipos_enfermedad_error(self, db_session):
        """Test: Error al obtener tipos de enfermedad."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.TipoEnfermedad') as mock_tipo:
            mock_tipo.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_tipos_enfermedad()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_grupos_sanguineos_success(self, db_session):
        """Test: Obtener grupos sanguíneos exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.GrupoSanguineo') as mock_grupo:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'O+'}
            mock_grupo.query.all.return_value = [mock_obj]
            
            result = service.obtener_grupos_sanguineos()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_grupos_sanguineos_error(self, db_session):
        """Test: Error al obtener grupos sanguíneos."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.GrupoSanguineo') as mock_grupo:
            mock_grupo.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_grupos_sanguineos()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_ciudades_residencia_success(self, db_session):
        """Test: Obtener ciudades de residencia exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.CiudadResidencia') as mock_ciudad:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Bogotá'}
            mock_ciudad.query.all.return_value = [mock_obj]
            
            result = service.obtener_ciudades_residencia()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_ciudades_residencia_error(self, db_session):
        """Test: Error al obtener ciudades de residencia."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.CiudadResidencia') as mock_ciudad:
            mock_ciudad.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_ciudades_residencia()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_eps_success(self, db_session):
        """Test: Obtener EPS exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.EPS') as mock_eps:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'EPS Test'}
            mock_eps.query.filter_by.return_value.all.return_value = [mock_obj]
            
            result = service.obtener_eps()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_eps_error(self, db_session):
        """Test: Error al obtener EPS."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.EPS') as mock_eps:
            mock_eps.query.filter_by.return_value.all.side_effect = Exception("DB Error")
            
            result = service.obtener_eps()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_deportes_success(self, db_session):
        """Test: Obtener deportes exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Deporte') as mock_deporte:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Fútbol'}
            mock_deporte.query.all.return_value = [mock_obj]
            
            result = service.obtener_deportes()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_deportes_error(self, db_session):
        """Test: Error al obtener deportes."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Deporte') as mock_deporte:
            mock_deporte.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_deportes()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_escuelas_success(self, db_session):
        """Test: Obtener escuelas exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Escuela') as mock_escuela:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Escuela Test'}
            mock_escuela.query.all.return_value = [mock_obj]
            
            result = service.obtener_escuelas()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_escuelas_error(self, db_session):
        """Test: Error al obtener escuelas."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.Escuela') as mock_escuela:
            mock_escuela.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_escuelas()
            
            assert result['success'] is False
            assert result['status_code'] == 500
    
    def test_obtener_instituciones_registro_success(self, db_session):
        """Test: Obtener instituciones de registro exitosamente."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.InstitucionRegistro') as mock_inst:
            mock_obj = MagicMock()
            mock_obj.to_dict.return_value = {'id': 1, 'nombre': 'Inst Test'}
            mock_inst.query.all.return_value = [mock_obj]
            
            result = service.obtener_instituciones_registro()
            
            assert result['success'] is True
            assert 'data' in result
            assert result['status_code'] == 200
    
    def test_obtener_instituciones_registro_error(self, db_session):
        """Test: Error al obtener instituciones de registro."""
        service = CatalogosService()
        
        with patch('src.services.catalogos_service.InstitucionRegistro') as mock_inst:
            mock_inst.query.all.side_effect = Exception("DB Error")
            
            result = service.obtener_instituciones_registro()
            
            assert result['success'] is False
            assert result['status_code'] == 500
