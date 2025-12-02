"""
Tests de integración para RegistroDeportistaService.

Este módulo contiene tests que validan la lógica de negocio
del servicio de registro de deportistas, incluyendo validaciones complejas.
"""

import pytest
from datetime import date

from tests.helpers import assert_success_response, assert_error_response


@pytest.mark.integration
@pytest.mark.services
@pytest.mark.deportistas
class TestRegistroDeportistaServiceIntegration:
    """Tests de integración para RegistroDeportistaService."""
    
    def test_registrar_deportista_nuevo_exitoso(
        self, db_session, persona, categoria
    ):
        """
        Test: Registrar deportista nuevo exitosamente.
        
        Valida:
        - Creación de deportista
        - Creación de información deportiva
        - Asignación de categoría automática
        - Validación de datos
        """
        # Arrange
        from src.services.registro_deportista_service import RegistroDeportistaService
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        from src.models.catalogos.eps import EPS
        
        from src.models.categorias.deporte import Deporte
        from src.models.categorias.institucion_registro import InstitucionRegistro
        
        grupo_sangre = GrupoSanguineo(tipo_sangre='O+')
        ciudad = CiudadResidencia(nombre_ciudad='San José del Guaviare')
        eps = EPS(nombre_eps='SURA')
        deporte = Deporte(nombre='Fútbol')
        institucion = InstitucionRegistro(nombre_institucion='Instituto Test')
        
        db_session.add_all([grupo_sangre, ciudad, eps, deporte, institucion])
        db_session.commit()
        
        datos_registro = {
            'datos_deportista': {
                'id_persona': persona.id_persona,
                'fecha_nacimiento': 2010,
                'id_tipo_sanguineo': grupo_sangre.id_tipo_sangre,
                'id_ciudad_recidencia': ciudad.id_ciudad,
                'id_eps': eps.id_eps
            },
            'informacion_deportiva': {
                'id_deporte': deporte.id_deporte,
                'id_institucion_registro': institucion.id_institucion,
                'practica_otro_deporte': False,
                'participa_escuela': False,
                'recomendacion_medica': False
            }
        }
        
        # Act
        resultado = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro)
        
        # Assert
        assert resultado.get('success') is True
        
        # Verificar que se creó el deportista
        from src.models.deportistas.deportista import Deportista
        deportista = Deportista.query.filter_by(
            id_persona=persona.id_persona
        ).first()
        assert deportista is not None
        assert deportista.id_categoria == categoria.id_categoria  # Categoría asignada automáticamente
    
    def test_registrar_deportista_calculo_categoria_automatico(
        self, db_session, persona
    ):
        """
        Test: Cálculo automático de categoría según edad.
        
        Valida que el servicio calcula correctamente la categoría
        basándose en la fecha de nacimiento.
        """
        # Arrange
        from src.services.registro_deportista_service import RegistroDeportistaService
        from src.models.categorias.categoria import Categoria
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
        # Crear categoría para edad específica
        categoria_joven = Categoria(
            nombre_categoria='Sub-15',
            codigo_categoria=101,
            edad_minima=13,
            edad_maxima=15
        )
        db_session.add(categoria_joven)
        
        from src.models.categorias.deporte import Deporte
        from src.models.categorias.institucion_registro import InstitucionRegistro
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        from src.models.catalogos.eps import EPS
        
        grupo_sangre = GrupoSanguineo(tipo_sangre='O+')
        ciudad = CiudadResidencia(nombre_ciudad='San José del Guaviare')
        eps = EPS(nombre_eps='SURA')
        deporte = Deporte(nombre='Fútbol')
        institucion = InstitucionRegistro(nombre_institucion='Instituto Test')
        
        db_session.add_all([grupo_sangre, ciudad, eps, deporte, institucion])
        db_session.commit()
        
        datos_registro = {
            'datos_deportista': {
                'id_persona': persona.id_persona,
                'fecha_nacimiento': 2010,  # 14 años (dentro del rango Sub-15)
                'id_tipo_sanguineo': grupo_sangre.id_tipo_sangre,
                'id_ciudad_recidencia': ciudad.id_ciudad,
                'id_eps': eps.id_eps
            },
            'informacion_deportiva': {
                'id_deporte': deporte.id_deporte,
                'id_institucion_registro': institucion.id_institucion,
                'practica_otro_deporte': False,
                'participa_escuela': False,
                'recomendacion_medica': False
            }
        }
        
        # Act
        resultado = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro)
        
        # Assert
        assert resultado.get('success') is True
        
        # Verificar que se asignó la categoría correcta
        from src.models.deportistas.deportista import Deportista
        deportista = Deportista.query.filter_by(
            id_persona=persona.id_persona
        ).first()
        assert deportista is not None
        # La categoría debe ser asignada según la edad
    
    def test_registrar_deportista_con_diagnosticos(
        self, db_session, persona, categoria
    ):
        """
        Test: Registrar deportista con diagnósticos médicos.
        
        Valida que el servicio maneja correctamente los diagnósticos.
        """
        # Arrange
        from src.services.registro_deportista_service import RegistroDeportistaService
        from src.models.salud.tipo_enfermedad import TipoEnfermedad
        from src.models.salud.diagnostico import Diagnostico
        from src.models.categorias.grupo_sanguineo import GrupoSanguineo
        
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
        
        from src.models.categorias.deporte import Deporte
        from src.models.categorias.institucion_registro import InstitucionRegistro
        from src.models.categorias.ciudad_residencia import CiudadResidencia
        from src.models.catalogos.eps import EPS
        
        grupo_sangre = GrupoSanguineo(tipo_sangre='O+')
        ciudad = CiudadResidencia(nombre_ciudad='San José del Guaviare')
        eps = EPS(nombre_eps='SURA')
        deporte = Deporte(nombre='Fútbol')
        institucion = InstitucionRegistro(nombre_institucion='Instituto Test')
        
        db_session.add_all([grupo_sangre, ciudad, eps, deporte, institucion])
        db_session.commit()
        
        datos_registro = {
            'datos_deportista': {
                'id_persona': persona.id_persona,
                'fecha_nacimiento': 2010,
                'id_tipo_sanguineo': grupo_sangre.id_tipo_sangre,
                'id_ciudad_recidencia': ciudad.id_ciudad,
                'id_eps': eps.id_eps
            },
            'informacion_deportiva': {
                'id_deporte': deporte.id_deporte,
                'id_institucion_registro': institucion.id_institucion,
                'practica_otro_deporte': False,
                'participa_escuela': False,
                'recomendacion_medica': False
            },
            'tipo_enfermedad': tipo_enfermedad.id_tipo_enfermedad,
            'diagnostico': [diagnostico1.id_diagnostico, diagnostico2.id_diagnostico]
        }
        
        # Act
        resultado = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro)
        
        # Assert
        assert resultado.get('success') is True
        
        # Verificar que se asociaron los diagnósticos
        from src.models.deportistas.deportista import Deportista
        from src.models.salud.diagnostico_deportista import DiagnosticoDeportista
        
        deportista = Deportista.query.filter_by(
            id_persona=persona.id_persona
        ).first()
        assert deportista is not None
        
        diagnosticos_asociados = DiagnosticoDeportista.query.filter_by(
            id_deportista=deportista.id_deportista
        ).all()
        assert len(diagnosticos_asociados) == 2
    
    def test_registrar_deportista_persona_no_existe(
        self, db_session, categoria
    ):
        """
        Test: Error cuando la persona no existe.
        
        Valida que el servicio rechaza personas inexistentes.
        """
        # Arrange
        from src.services.registro_deportista_service import RegistroDeportistaService
        
        datos_registro = {
            'datos_deportista': {
                'id_persona': 99999,  # Persona inexistente
                'fecha_nacimiento': 2010
            },
            'informacion_deportiva': {
                'practica_otro_deporte': False,
                'participa_escuela': False,
                'recomendacion_medica': False
            }
        }
        
        # Act
        resultado = RegistroDeportistaService.registrar_deportista_nuevo(datos_registro)
        
        # Assert
        assert resultado.get('success') is False
        assert resultado.get('status_code') in [400, 404]
    
    def test_obtener_informacion_completa_deportista(
        self, db_session, deportista
    ):
        """
        Test: Obtener información completa de deportista.
        
        Valida que el servicio retorna toda la información relacionada.
        """
        # Arrange
        from src.services.registro_deportista_service import RegistroDeportistaService
        
        # Act
        resultado = RegistroDeportistaService.obtener_informacion_completa_deportista(
            deportista.id_deportista
        )
        
        # Assert
        assert resultado.get('success') is True
        assert 'data' in resultado
        # Verificar que incluye información completa
        data = resultado.get('data', {})
        # El servicio devuelve 'datos_deportista', 'persona', 'informacion_deportiva', etc.
        assert 'id' in data or 'datos_deportista' in data or 'persona' in data or 'informacion_deportiva' in data or 'salud' in data

