"""
Tests para error_messages.py.

Este módulo contiene tests que verifican que todas las constantes
de mensajes de error estén definidas correctamente.
"""

import pytest
from src.utils import error_messages


@pytest.mark.unit
class TestErrorMessages:
    """Tests para constantes de mensajes de error."""
    
    def test_error_interno_servidor_defined(self):
        """Test: ERROR_INTERNO_SERVIDOR está definido."""
        assert hasattr(error_messages, 'ERROR_INTERNO_SERVIDOR')
        assert isinstance(error_messages.ERROR_INTERNO_SERVIDOR, str)
        assert len(error_messages.ERROR_INTERNO_SERVIDOR) > 0
    
    def test_error_content_type_json_defined(self):
        """Test: ERROR_CONTENT_TYPE_JSON está definido."""
        assert hasattr(error_messages, 'ERROR_CONTENT_TYPE_JSON')
        assert isinstance(error_messages.ERROR_CONTENT_TYPE_JSON, str)
        assert len(error_messages.ERROR_CONTENT_TYPE_JSON) > 0
    
    def test_error_content_type_json_alt_defined(self):
        """Test: ERROR_CONTENT_TYPE_JSON_ALT está definido."""
        assert hasattr(error_messages, 'ERROR_CONTENT_TYPE_JSON_ALT')
        assert isinstance(error_messages.ERROR_CONTENT_TYPE_JSON_ALT, str)
        assert len(error_messages.ERROR_CONTENT_TYPE_JSON_ALT) > 0
    
    def test_error_usuario_no_encontrado_defined(self):
        """Test: ERROR_USUARIO_NO_ENCONTRADO está definido."""
        assert hasattr(error_messages, 'ERROR_USUARIO_NO_ENCONTRADO')
        assert isinstance(error_messages.ERROR_USUARIO_NO_ENCONTRADO, str)
        assert len(error_messages.ERROR_USUARIO_NO_ENCONTRADO) > 0
    
    def test_error_usuario_no_encontrado_contexto_defined(self):
        """Test: ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO está definido."""
        assert hasattr(error_messages, 'ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO')
        assert isinstance(error_messages.ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO, str)
        assert len(error_messages.ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO) > 0
    
    def test_error_usuario_no_autenticado_defined(self):
        """Test: ERROR_USUARIO_NO_AUTENTICADO está definido."""
        assert hasattr(error_messages, 'ERROR_USUARIO_NO_AUTENTICADO')
        assert isinstance(error_messages.ERROR_USUARIO_NO_AUTENTICADO, str)
        assert len(error_messages.ERROR_USUARIO_NO_AUTENTICADO) > 0
    
    def test_error_token_requerido_defined(self):
        """Test: ERROR_TOKEN_REQUERIDO está definido."""
        assert hasattr(error_messages, 'ERROR_TOKEN_REQUERIDO')
        assert isinstance(error_messages.ERROR_TOKEN_REQUERIDO, str)
        assert len(error_messages.ERROR_TOKEN_REQUERIDO) > 0
    
    def test_error_token_invalido_defined(self):
        """Test: ERROR_TOKEN_INVALIDO está definido."""
        assert hasattr(error_messages, 'ERROR_TOKEN_INVALIDO')
        assert isinstance(error_messages.ERROR_TOKEN_INVALIDO, str)
        assert len(error_messages.ERROR_TOKEN_INVALIDO) > 0
    
    def test_error_datos_requeridos_defined(self):
        """Test: ERROR_DATOS_REQUERIDOS está definido."""
        assert hasattr(error_messages, 'ERROR_DATOS_REQUERIDOS')
        assert isinstance(error_messages.ERROR_DATOS_REQUERIDOS, str)
        assert len(error_messages.ERROR_DATOS_REQUERIDOS) > 0
    
    def test_error_datos_vacios_defined(self):
        """Test: ERROR_DATOS_VACIOS está definido."""
        assert hasattr(error_messages, 'ERROR_DATOS_VACIOS')
        assert isinstance(error_messages.ERROR_DATOS_VACIOS, str)
        assert len(error_messages.ERROR_DATOS_VACIOS) > 0
    
    def test_error_no_se_enviaron_datos_defined(self):
        """Test: ERROR_NO_SE_ENVIARON_DATOS está definido."""
        assert hasattr(error_messages, 'ERROR_NO_SE_ENVIARON_DATOS')
        assert isinstance(error_messages.ERROR_NO_SE_ENVIARON_DATOS, str)
        assert len(error_messages.ERROR_NO_SE_ENVIARON_DATOS) > 0
    
    def test_error_no_se_proporcionaron_datos_defined(self):
        """Test: ERROR_NO_SE_PROPORCIONARON_DATOS está definido."""
        assert hasattr(error_messages, 'ERROR_NO_SE_PROPORCIONARON_DATOS')
        assert isinstance(error_messages.ERROR_NO_SE_PROPORCIONARON_DATOS, str)
        assert len(error_messages.ERROR_NO_SE_PROPORCIONARON_DATOS) > 0
    
    def test_error_campo_requerido_defined(self):
        """Test: ERROR_CAMPO_REQUERIDO está definido."""
        assert hasattr(error_messages, 'ERROR_CAMPO_REQUERIDO')
        assert isinstance(error_messages.ERROR_CAMPO_REQUERIDO, str)
        assert len(error_messages.ERROR_CAMPO_REQUERIDO) > 0
    
    def test_error_nombre_minimo_caracteres_defined(self):
        """Test: ERROR_NOMBRE_MINIMO_CARACTERES está definido."""
        assert hasattr(error_messages, 'ERROR_NOMBRE_MINIMO_CARACTERES')
        assert isinstance(error_messages.ERROR_NOMBRE_MINIMO_CARACTERES, str)
        assert len(error_messages.ERROR_NOMBRE_MINIMO_CARACTERES) > 0
    
    def test_error_lugar_minimo_caracteres_defined(self):
        """Test: ERROR_LUGAR_MINIMO_CARACTERES está definido."""
        assert hasattr(error_messages, 'ERROR_LUGAR_MINIMO_CARACTERES')
        assert isinstance(error_messages.ERROR_LUGAR_MINIMO_CARACTERES, str)
        assert len(error_messages.ERROR_LUGAR_MINIMO_CARACTERES) > 0
    
    def test_error_id_invalido_defined(self):
        """Test: ERROR_ID_INVALIDO está definido."""
        assert hasattr(error_messages, 'ERROR_ID_INVALIDO')
        assert isinstance(error_messages.ERROR_ID_INVALIDO, str)
        assert len(error_messages.ERROR_ID_INVALIDO) > 0
    
    def test_error_id_entero_positivo_defined(self):
        """Test: ERROR_ID_ENTERO_POSITIVO está definido."""
        assert hasattr(error_messages, 'ERROR_ID_ENTERO_POSITIVO')
        assert isinstance(error_messages.ERROR_ID_ENTERO_POSITIVO, str)
        assert len(error_messages.ERROR_ID_ENTERO_POSITIVO) > 0
    
    def test_error_recurso_no_encontrado_defined(self):
        """Test: ERROR_RECURSO_NO_ENCONTRADO está definido."""
        assert hasattr(error_messages, 'ERROR_RECURSO_NO_ENCONTRADO')
        assert isinstance(error_messages.ERROR_RECURSO_NO_ENCONTRADO, str)
        assert len(error_messages.ERROR_RECURSO_NO_ENCONTRADO) > 0
    
    def test_error_deportista_no_encontrado_defined(self):
        """Test: ERROR_DEPORTISTA_NO_ENCONTRADO está definido."""
        assert hasattr(error_messages, 'ERROR_DEPORTISTA_NO_ENCONTRADO')
        assert isinstance(error_messages.ERROR_DEPORTISTA_NO_ENCONTRADO, str)
        assert len(error_messages.ERROR_DEPORTISTA_NO_ENCONTRADO) > 0
    
    def test_error_acudiente_no_encontrado_defined(self):
        """Test: ERROR_ACUDIENTE_NO_ENCONTRADO está definido."""
        assert hasattr(error_messages, 'ERROR_ACUDIENTE_NO_ENCONTRADO')
        assert isinstance(error_messages.ERROR_ACUDIENTE_NO_ENCONTRADO, str)
        assert len(error_messages.ERROR_ACUDIENTE_NO_ENCONTRADO) > 0
    
    def test_error_persona_no_encontrada_defined(self):
        """Test: ERROR_PERSONA_NO_ENCONTRADA está definido."""
        assert hasattr(error_messages, 'ERROR_PERSONA_NO_ENCONTRADA')
        assert isinstance(error_messages.ERROR_PERSONA_NO_ENCONTRADA, str)
        assert len(error_messages.ERROR_PERSONA_NO_ENCONTRADA) > 0
    
    def test_mensaje_exito_defined(self):
        """Test: MENSAJE_EXITO está definido."""
        assert hasattr(error_messages, 'MENSAJE_EXITO')
        assert isinstance(error_messages.MENSAJE_EXITO, str)
        assert len(error_messages.MENSAJE_EXITO) > 0
    
    def test_mensaje_creado_defined(self):
        """Test: MENSAJE_CREADO está definido."""
        assert hasattr(error_messages, 'MENSAJE_CREADO')
        assert isinstance(error_messages.MENSAJE_CREADO, str)
        assert len(error_messages.MENSAJE_CREADO) > 0
    
    def test_mensaje_actualizado_defined(self):
        """Test: MENSAJE_ACTUALIZADO está definido."""
        assert hasattr(error_messages, 'MENSAJE_ACTUALIZADO')
        assert isinstance(error_messages.MENSAJE_ACTUALIZADO, str)
        assert len(error_messages.MENSAJE_ACTUALIZADO) > 0
    
    def test_mensaje_eliminado_defined(self):
        """Test: MENSAJE_ELIMINADO está definido."""
        assert hasattr(error_messages, 'MENSAJE_ELIMINADO')
        assert isinstance(error_messages.MENSAJE_ELIMINADO, str)
        assert len(error_messages.MENSAJE_ELIMINADO) > 0
    
    def test_all_constants_are_strings(self):
        """Test: Todas las constantes son strings."""
        constants = [
            'ERROR_INTERNO_SERVIDOR',
            'ERROR_CONTENT_TYPE_JSON',
            'ERROR_CONTENT_TYPE_JSON_ALT',
            'ERROR_USUARIO_NO_ENCONTRADO',
            'ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO',
            'ERROR_USUARIO_NO_AUTENTICADO',
            'ERROR_TOKEN_REQUERIDO',
            'ERROR_TOKEN_INVALIDO',
            'ERROR_DATOS_REQUERIDOS',
            'ERROR_DATOS_VACIOS',
            'ERROR_NO_SE_ENVIARON_DATOS',
            'ERROR_NO_SE_PROPORCIONARON_DATOS',
            'ERROR_CAMPO_REQUERIDO',
            'ERROR_NOMBRE_MINIMO_CARACTERES',
            'ERROR_LUGAR_MINIMO_CARACTERES',
            'ERROR_ID_INVALIDO',
            'ERROR_ID_ENTERO_POSITIVO',
            'ERROR_RECURSO_NO_ENCONTRADO',
            'ERROR_DEPORTISTA_NO_ENCONTRADO',
            'ERROR_ACUDIENTE_NO_ENCONTRADO',
            'ERROR_PERSONA_NO_ENCONTRADA',
            'MENSAJE_EXITO',
            'MENSAJE_CREADO',
            'MENSAJE_ACTUALIZADO',
            'MENSAJE_ELIMINADO'
        ]
        
        for constant_name in constants:
            constant_value = getattr(error_messages, constant_name)
            assert isinstance(constant_value, str), f"{constant_name} no es un string"
            assert len(constant_value) > 0, f"{constant_name} está vacío"
    
    def test_all_constants_are_not_empty(self):
        """Test: Todas las constantes tienen contenido."""
        error_constants = [attr for attr in dir(error_messages) 
                          if attr.startswith('ERROR_') or attr.startswith('MENSAJE_')]
        
        for constant_name in error_constants:
            if not constant_name.startswith('__'):
                constant_value = getattr(error_messages, constant_name)
                assert len(constant_value) > 0, f"{constant_name} está vacío"

