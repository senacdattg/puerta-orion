"""
Tests unitarios para funciones helper de auth_reset.

Cubre validaciones, construcción de mensajes y envío de correos.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import smtplib

from src.routes.auth_reset import (
    _build_response,
    _validar_configuracion_email,
    _obtener_persona_por_email,
    _obtener_usuario_por_persona,
    _validar_usuario_activo,
    _eliminar_tokens_previos,
    _generar_y_guardar_token,
    _extraer_email_remitente,
    _construir_mensaje_correo,
    _validar_datos_reset,
    _obtener_y_validar_token,
    RequestValidationError,
)


@pytest.mark.unit
@pytest.mark.auth
class TestAuthResetHelpers:
    """Tests para funciones helper de auth_reset"""
    
    def test_build_response_success(self, app_context):
        """Test: Construir respuesta exitosa."""
        response, status = _build_response(True, 200, message="Success")
        
        assert status == 200
        assert response.json['success'] is True
        assert response.json['message'] == "Success"
    
    def test_build_response_error(self, app_context):
        """Test: Construir respuesta de error."""
        response, status = _build_response(False, 400, error="Bad request")
        
        assert status == 400
        assert response.json['success'] is False
        assert response.json['error'] == "Bad request"
    
    def test_validar_configuracion_email_success(self):
        """Test: Validar configuración de email exitosa."""
        with patch('src.routes.auth_reset.EMAIL_PASSWORD', '1234567890123456'):
            with patch('src.routes.auth_reset.EMAIL_ADDRESS', 'test@example.com'):
                # No debe lanzar excepción
                _validar_configuracion_email()
    
    def test_validar_configuracion_email_sin_password(self):
        """Test: Error cuando no hay password configurado."""
        with patch('src.routes.auth_reset.EMAIL_PASSWORD', ''):
            with pytest.raises(RequestValidationError) as exc:
                _validar_configuracion_email()
            assert exc.value.status_code == 500
    
    def test_validar_configuracion_email_password_incorrecto(self):
        """Test: Error cuando password no tiene longitud correcta."""
        with patch('src.routes.auth_reset.EMAIL_PASSWORD', '12345'):
            with patch('src.routes.auth_reset.EMAIL_ADDRESS', 'test@example.com'):
                with pytest.raises(RequestValidationError) as exc:
                    _validar_configuracion_email()
                assert exc.value.status_code == 500
    
    def test_obtener_persona_por_email_success(self, app_context):
        """Test: Obtener persona por email exitosamente."""
        from src.models.personas.persona import Persona
        
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.correo_electronico = 'test@example.com'
        
        with patch('src.routes.auth_reset.Persona.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_persona
            
            result = _obtener_persona_por_email('test@example.com')
            assert result == mock_persona
    
    def test_obtener_persona_por_email_no_encontrada(self, app_context):
        """Test: Persona no encontrada por email."""
        with patch('src.routes.auth_reset.Persona.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with pytest.raises(RequestValidationError) as exc:
                _obtener_persona_por_email('notfound@example.com')
            assert exc.value.status_code == 404
    
    def test_obtener_usuario_por_persona_success(self, app_context):
        """Test: Obtener usuario por persona exitosamente."""
        from src.models.personas.persona import Persona
        from src.models.usuarios.usuario import Usuario
        
        mock_persona = MagicMock(spec=Persona)
        mock_persona.id_persona = 1
        
        mock_usuario = MagicMock(spec=Usuario)
        mock_usuario.id_usuario = 1
        
        with patch('src.routes.auth_reset.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            
            result = _obtener_usuario_por_persona(mock_persona)
            assert result == mock_usuario
    
    def test_obtener_usuario_por_persona_no_encontrado(self, app_context):
        """Test: Usuario no encontrado para persona."""
        from src.models.personas.persona import Persona
        
        mock_persona = MagicMock(spec=Persona)
        mock_persona.id_persona = 1
        
        with patch('src.routes.auth_reset.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with pytest.raises(RequestValidationError) as exc:
                _obtener_usuario_por_persona(mock_persona)
            assert exc.value.status_code == 404
    
    def test_validar_usuario_activo_success(self, app_context):
        """Test: Validar usuario activo exitosamente."""
        from src.models.usuarios.usuario import Usuario
        
        mock_usuario = MagicMock(spec=Usuario)
        mock_usuario.estado = True
        
        # No debe lanzar excepción
        _validar_usuario_activo(mock_usuario)
    
    def test_validar_usuario_activo_inactivo(self, app_context):
        """Test: Error cuando usuario está inactivo."""
        from src.models.usuarios.usuario import Usuario
        
        mock_usuario = MagicMock(spec=Usuario)
        mock_usuario.estado = False
        
        with pytest.raises(RequestValidationError) as exc:
            _validar_usuario_activo(mock_usuario)
        assert exc.value.status_code == 403
    
    def test_eliminar_tokens_previos(self, app_context):
        """Test: Eliminar tokens previos del usuario."""
        from src.models.usuarios.password_reset_token import PasswordResetToken
        from src.models.base import db
        
        mock_token1 = MagicMock(spec=PasswordResetToken)
        mock_token2 = MagicMock(spec=PasswordResetToken)
        
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_query:
            mock_query.filter_by.return_value.all.return_value = [mock_token1, mock_token2]
            with patch('src.routes.auth_reset.db') as mock_db:
                mock_db.session.delete = MagicMock()
                
                _eliminar_tokens_previos(1)
                
                assert mock_db.session.delete.call_count == 2
    
    def test_generar_y_guardar_token(self):
        """Test: Generar y guardar token exitosamente."""
        from src.models.usuarios.password_reset_token import PasswordResetToken
        from src.models.base import db
        
        with patch('src.routes.auth_reset.PasswordResetToken') as mock_token_class:
            mock_instance = MagicMock()
            mock_token_class.return_value = mock_instance
            with patch('src.routes.auth_reset.db') as mock_db:
                mock_db.session.add = MagicMock()
                mock_db.session.commit = MagicMock()
                
                token = _generar_y_guardar_token(1)
                
                assert isinstance(token, str)
                assert len(token) > 0
                mock_db.session.add.assert_called_once()
                mock_db.session.commit.assert_called_once()
    
    def test_extraer_email_remitente_directo(self):
        """Test: Extraer email remitente directo."""
        with patch('src.routes.auth_reset.DEFAULT_FROM_EMAIL', 'test@example.com'):
            result = _extraer_email_remitente()
            assert result == 'test@example.com'
    
    def test_extraer_email_remitente_con_formato(self):
        """Test: Extraer email remitente con formato nombre <email>."""
        with patch('src.routes.auth_reset.DEFAULT_FROM_EMAIL', 'Nombre <test@example.com>'):
            result = _extraer_email_remitente()
            assert result == 'test@example.com'
    
    def test_extraer_email_remitente_fallback(self):
        """Test: Extraer email remitente usando fallback."""
        with patch('src.routes.auth_reset.DEFAULT_FROM_EMAIL', ''):
            with patch('src.routes.auth_reset.EMAIL_ADDRESS', 'fallback@example.com'):
                result = _extraer_email_remitente()
                assert result == 'fallback@example.com'
    
    def test_construir_mensaje_correo(self):
        """Test: Construir mensaje de correo."""
        from email.mime.multipart import MIMEMultipart
        
        with patch('src.routes.auth_reset.DEFAULT_FROM_EMAIL', 'test@example.com'):
            msg = _construir_mensaje_correo(
                'user@example.com',
                'Juan Pérez',
                'https://example.com/reset?token=123'
            )
            
            assert isinstance(msg, MIMEMultipart)
            assert msg['From'] == 'test@example.com'
            assert msg['To'] == 'user@example.com'
    
    def test_validar_datos_reset_success(self):
        """Test: Validar datos de reset exitosamente."""
        data = {
            'token': 'valid_token',
            'new_password': 'nueva_password123',
            'confirm_password': 'nueva_password123'
        }
        
        token, new_password, confirm_password = _validar_datos_reset(data)
        
        assert token == 'valid_token'
        assert new_password == 'nueva_password123'
        assert confirm_password == 'nueva_password123'
    
    def test_validar_datos_reset_faltantes(self):
        """Test: Error cuando faltan datos."""
        data = {'token': 'valid_token'}
        
        with pytest.raises(RequestValidationError) as exc:
            _validar_datos_reset(data)
        assert exc.value.status_code == 400
    
    def test_obtener_y_validar_token_success(self, app_context):
        """Test: Obtener y validar token exitosamente."""
        from src.models.usuarios.password_reset_token import PasswordResetToken
        
        mock_token = MagicMock()
        mock_token.token = 'valid_token'
        mock_token.expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_token.is_expired.return_value = False
        
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_token
            
            result = _obtener_y_validar_token('valid_token')
            assert result == mock_token
    
    def test_obtener_y_validar_token_no_encontrado(self, app_context):
        """Test: Token no encontrado."""
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = None
            
            with pytest.raises(RequestValidationError) as exc:
                _obtener_y_validar_token('invalid_token')
            assert exc.value.status_code == 400
    
    def test_obtener_y_validar_token_expirado(self, app_context):
        """Test: Token expirado."""
        from src.models.usuarios.password_reset_token import PasswordResetToken
        from src.models.base import db
        
        mock_token = MagicMock()
        mock_token.token = 'expired_token'
        mock_token.expires_at = datetime.now(timezone.utc) - timedelta(hours=2)
        mock_token.is_expired.return_value = True
        
        with patch('src.routes.auth_reset.PasswordResetToken.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_token
            with patch('src.routes.auth_reset.db') as mock_db:
                mock_db.session.delete = MagicMock()
                mock_db.session.commit = MagicMock()
                
                with pytest.raises(RequestValidationError) as exc:
                    _obtener_y_validar_token('expired_token')
                assert exc.value.status_code == 400

