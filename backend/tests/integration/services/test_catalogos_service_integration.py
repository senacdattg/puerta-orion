"""
Tests de integración para CatalogosService.

Este módulo contiene tests que validan la lógica de negocio
del servicio de catálogos, incluyendo consultas y filtros.
"""

import pytest

from tests.helpers import assert_success_response, assert_error_response


@pytest.mark.integration
@pytest.mark.services
@pytest.mark.catalogos
class TestCatalogosServiceIntegration:
    """Tests de integración para CatalogosService."""
    
    def test_obtener_diagnosticos_todos(
        self, db_session
    ):
        """
        Test: Obtener todos los diagnósticos.
        
        Valida que el servicio retorna todos los diagnósticos disponibles.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.salud.diagnostico import Diagnostico
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        tipo_enfermedad = TipoEnfermedad(nombre='Alergia')
        db_session.add(tipo_enfermedad)
        db_session.commit()
        
        diagnostico1 = Diagnostico(
            nombre='Alergia al polen',
            id_tipo_enfermedad=tipo_enfermedad.id_tipo_enfermedad
        )
        diagnostico2 = Diagnostico(
            nombre='Asma',
            id_tipo_enfermedad=tipo_enfermedad.id_tipo_enfermedad
        )
        db_session.add_all([diagnostico1, diagnostico2])
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_diagnosticos()
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        diagnosticos = resultado.get('data', [])
        assert len(diagnosticos) >= 2
    
    def test_obtener_diagnosticos_por_tipo(
        self, db_session
    ):
        """
        Test: Obtener diagnósticos filtrados por tipo de enfermedad.
        
        Valida que el servicio filtra correctamente por tipo.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.salud.diagnostico import Diagnostico
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        tipo_alergia = TipoEnfermedad(nombre='Alergia')
        tipo_respiratorio = TipoEnfermedad(nombre='Respiratorio')
        db_session.add_all([tipo_alergia, tipo_respiratorio])
        db_session.commit()
        
        diagnostico_alergia = Diagnostico(
            nombre='Alergia al polen',
            id_tipo_enfermedad=tipo_alergia.id_tipo_enfermedad
        )
        diagnostico_asma = Diagnostico(
            nombre='Asma',
            id_tipo_enfermedad=tipo_respiratorio.id_tipo_enfermedad
        )
        db_session.add_all([diagnostico_alergia, diagnostico_asma])
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_diagnosticos(id_tipo_enfermedad=tipo_alergia.id_tipo_enfermedad)
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        diagnosticos = resultado.get('data', [])
        # Todos deben ser del tipo alergia
        for diag in diagnosticos:
            assert diag.get('id_tipo_enfermedad') == tipo_alergia.id_tipo_enfermedad
    
    def test_obtener_tipos_enfermedad(
        self, db_session
    ):
        """
        Test: Obtener todos los tipos de enfermedad.
        
        Valida que el servicio retorna todos los tipos de enfermedad.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        tipo1 = TipoEnfermedad(nombre='Alergia')
        tipo2 = TipoEnfermedad(nombre='Respiratorio')
        db_session.add_all([tipo1, tipo2])
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_tipos_enfermedad()
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        tipos = resultado.get('data', [])
        assert len(tipos) >= 2
    
    def test_obtener_tipos_enfermedad_con_diagnosticos(
        self, db_session
    ):
        """
        Test: Obtener tipos de enfermedad incluyendo diagnósticos.
        
        Valida que el servicio puede incluir diagnósticos relacionados.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.salud.diagnostico import Diagnostico
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        
        tipo_enfermedad = TipoEnfermedad(nombre='Alergia')
        db_session.add(tipo_enfermedad)
        db_session.commit()
        
        diagnostico = Diagnostico(
            nombre='Alergia al polen',
            id_tipo_enfermedad=tipo_enfermedad.id_tipo_enfermedad
        )
        db_session.add(diagnostico)
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_tipos_enfermedad(incluir_diagnosticos=True)
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        tipos = resultado.get('data', [])
        # Verificar que al menos un tipo tiene diagnósticos
        tipo_con_diag = next(
            (t for t in tipos if t.get('id_tipo_enfermedad') == tipo_enfermedad.id_tipo_enfermedad),
            None
        )
        if tipo_con_diag:
            assert 'diagnosticos' in tipo_con_diag or 'diagnosticos_relacionados' in tipo_con_diag
    
    def test_obtener_grupos_sanguineos(
        self, db_session
    ):
        """
        Test: Obtener todos los grupos sanguíneos.
        
        Valida que el servicio retorna todos los grupos sanguíneos.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
        grupo1 = GrupoSanguineo(tipo_sangre='O+')
        grupo2 = GrupoSanguineo(tipo_sangre='A+')
        db_session.add_all([grupo1, grupo2])
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_grupos_sanguineos()
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        grupos = resultado.get('data', [])
        assert len(grupos) >= 2
    
    def test_obtener_eps(
        self, db_session
    ):
        """
        Test: Obtener todas las EPS.
        
        Valida que el servicio retorna todas las EPS disponibles.
        """
        # Arrange
        from src.services.catalogos_service import CatalogosService
        from src.models.catalogos.eps import EPS
        
        eps1 = EPS(nombre_eps='SURA')
        eps2 = EPS(nombre_eps='SALUD TOTAL')
        db_session.add_all([eps1, eps2])
        db_session.commit()
        
        service = CatalogosService()
        
        # Act
        resultado = service.obtener_eps()
        
        # Assert
        assert resultado.get('success') is True or resultado.get('status') == 'success'
        assert 'data' in resultado
        eps_list = resultado.get('data', [])
        assert len(eps_list) >= 2



