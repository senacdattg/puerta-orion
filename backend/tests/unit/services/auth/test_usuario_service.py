"""
Tests for user service.

This module contains tests that verify user registration, update,
and retrieval operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date
from sqlalchemy.exc import IntegrityError

from src.services.Auth.usuario_service import UsuarioService, UsuarioServiceError
from src.models.usuarios.usuario import Usuario
from src.models.personas.persona import Persona
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.usuario_rol import UsuarioRol
from src.models.deportistas.deportista import Deportista
from src.models.acudientes.acudiente import Acudiente


@pytest.mark.unit
class TestUsuarioService:
    """Tests for UsuarioService."""
    
    @pytest.fixture
    def usuario_service(self):
        """Create an instance of UsuarioService."""
        return UsuarioService()
    
    @pytest.fixture
    def datos_persona_validos(self):
        """Valid person data for testing."""
        return {
            'primer_nombre': 'Juan',
            'segundo_nombre': 'Carlos',
            'primer_apellido': 'Pérez',
            'segundo_apellido': 'García',
            'documento': '12345678',
            'correo_electronico': 'juan@example.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123',
            'id_tipo_documento': 1,
            'id_sexo': 1
        }
    
    @pytest.fixture
    def datos_usuario_validos(self):
        """Valid user data for testing."""
        return {
            'usuario': 'juanperez',
            'password': 'password123'
        }
    
    def test_registrar_usuario_completo_success(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Successful complete user registration."""
        with patch.object(usuario_service, '_validar_datos_persona') as mock_validar_persona, \
             patch.object(usuario_service, '_validar_datos_usuario') as mock_validar_usuario, \
             patch.object(usuario_service, '_validar_unicidad') as mock_validar_unicidad, \
             patch.object(usuario_service, '_crear_persona_y_usuario') as mock_crear:
            
            mock_result = {
                'id_usuario': 1,
                'usuario': 'juanperez',
                'estado': True
            }
            mock_crear.return_value = mock_result
            
            result = usuario_service.registrar_usuario_completo(
                datos_persona_validos,
                datos_usuario_validos
            )
            
            assert result == mock_result
            mock_validar_persona.assert_called_once()
            mock_validar_usuario.assert_called_once()
            mock_validar_unicidad.assert_called_once()
            mock_crear.assert_called_once()
    
    def test_registrar_usuario_completo_validation_error(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: User registration with validation error."""
        with patch.object(usuario_service, '_validar_datos_persona') as mock_validar:
            mock_validar.side_effect = UsuarioServiceError("Validation error")
            
            with pytest.raises(UsuarioServiceError, match="Validation error"):
                usuario_service.registrar_usuario_completo(
                    datos_persona_validos,
                    datos_usuario_validos
                )
    
    def test_validar_datos_persona_success(self, usuario_service, datos_persona_validos):
        """Test: Successful person data validation."""
        with patch('src.services.Auth.usuario_service.validate_name', return_value='Juan'), \
             patch('src.services.Auth.usuario_service.validate_document', return_value='12345678'), \
             patch('src.services.Auth.usuario_service.validate_email', return_value='juan@example.com'), \
             patch('src.services.Auth.usuario_service.validate_phone', return_value='3001234567'), \
             patch('src.services.Auth.usuario_service.sanitize_address', return_value='Calle 123'):
            
            usuario_service._validar_datos_persona(datos_persona_validos)
            
            assert datos_persona_validos['primer_nombre'] == 'Juan'
            assert datos_persona_validos['documento'] == '12345678'
    
    def test_validar_datos_persona_missing_required(self, usuario_service, app_context):
        """Test: Person data validation with missing required fields."""
        datos_incompletos = {
            'primer_nombre': 'Juan',
            # Missing primer_apellido, id_tipo_documento and id_sexo
        }
        
        with pytest.raises(UsuarioServiceError, match="obligatorio"):
            usuario_service._validar_datos_persona(datos_incompletos)
    
    def test_validar_datos_usuario_success(self, usuario_service, datos_usuario_validos):
        """Test: Successful user data validation."""
        usuario_service._validar_datos_usuario(datos_usuario_validos)
        
        assert datos_usuario_validos['usuario'] == 'juanperez'
    
    def test_validar_datos_usuario_missing_fields(self, usuario_service):
        """Test: User data validation with missing fields."""
        datos_incompletos = {}
        
        with pytest.raises(UsuarioServiceError, match="Campos de usuario requeridos faltantes"):
            usuario_service._validar_datos_usuario(datos_incompletos)
    
    def test_validar_datos_usuario_short_password(self, usuario_service):
        """Test: User data validation with short password."""
        datos = {
            'usuario': 'testuser',
            'password': '12345'  # NOSONAR: S2068 - Test password only, intentionally short for validation test
        }
        
        with pytest.raises(UsuarioServiceError, match="La contraseña debe tener al menos 6 caracteres"):
            usuario_service._validar_datos_usuario(datos)
    
    def test_validar_datos_usuario_short_username(self, usuario_service):
        """Test: User data validation with short username."""
        datos = {
            'usuario': 'ab',  # Less than 3 characters
            'password': 'password123'
        }
        
        with pytest.raises(UsuarioServiceError, match="El nombre de usuario debe tener al menos 3 caracteres"):
            usuario_service._validar_datos_usuario(datos)
    
    def test_validar_datos_usuario_long_username(self, usuario_service):
        """Test: User data validation with username too long."""
        datos = {
            'usuario': 'a' * 201,  # More than 200 characters
            'password': 'password123'
        }
        
        with pytest.raises(UsuarioServiceError, match="El nombre de usuario excede la longitud máxima"):
            usuario_service._validar_datos_usuario(datos)
    
    def test_validar_unicidad_documento_duplicado(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Uniqueness validation with duplicate document."""
        with patch('src.services.Auth.usuario_service.Persona') as mock_persona_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = MagicMock()  # Document exists
            mock_persona_class.query = mock_query
            
            with pytest.raises(UsuarioServiceError, match="Ya existe una persona con el documento"):
                usuario_service._validar_unicidad(datos_persona_validos, datos_usuario_validos)
    
    def test_validar_unicidad_email_duplicado(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Uniqueness validation with duplicate email."""
        with patch('src.services.Auth.usuario_service.Persona') as mock_persona_class, \
             patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            
            # Document doesn't exist, but email does
            mock_persona_query = MagicMock()
            mock_persona_query.filter_by.return_value.first.side_effect = [None, MagicMock()]
            mock_persona_class.query = mock_persona_query
            
            mock_usuario_query = MagicMock()
            mock_usuario_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_usuario_query
            
            with pytest.raises(UsuarioServiceError, match="Ya existe una persona con el email"):
                usuario_service._validar_unicidad(datos_persona_validos, datos_usuario_validos)
    
    def test_validar_unicidad_username_duplicado(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Uniqueness validation with duplicate username."""
        with patch('src.services.Auth.usuario_service.Persona') as mock_persona_class, \
             patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            
            # Document and email don't exist, but username does
            mock_persona_query = MagicMock()
            mock_persona_query.filter_by.return_value.first.return_value = None
            mock_persona_class.query = mock_persona_query
            
            mock_usuario_query = MagicMock()
            mock_usuario_query.filter_by.return_value.first.return_value = MagicMock()  # Username exists
            mock_usuario_class.query = mock_usuario_query
            
            with pytest.raises(UsuarioServiceError, match="Ya existe un usuario con el nombre"):
                usuario_service._validar_unicidad(datos_persona_validos, datos_usuario_validos)
    
    def test_crear_persona_y_usuario_success(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Successful creation of person and user."""
        with patch.object(usuario_service, '_crear_persona') as mock_crear_persona, \
             patch.object(usuario_service, '_crear_usuario') as mock_crear_usuario, \
             patch.object(usuario_service, '_asignar_rol_por_defecto') as mock_rol, \
             patch.object(usuario_service, '_procesar_rol_opcional'), \
             patch.object(usuario_service, '_serializar_usuario', return_value={'id_usuario': 1, 'usuario': 'juanperez'}), \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_persona = MagicMock()
            mock_persona.id_persona = 1
            mock_crear_persona.return_value = mock_persona
            
            mock_usuario = MagicMock()
            mock_usuario.id_usuario = 1
            mock_crear_usuario.return_value = mock_usuario
            
            mock_rol_obj = MagicMock()
            mock_rol.return_value = mock_rol_obj
            
            mock_db.session.flush = MagicMock()
            mock_db.session.commit = MagicMock()
            
            result = usuario_service._crear_persona_y_usuario(
                datos_persona_validos,
                datos_usuario_validos
            )
            
            assert result['id_usuario'] == 1
            mock_crear_persona.assert_called_once()
            mock_crear_usuario.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_crear_persona_y_usuario_integrity_error(self, usuario_service, datos_persona_validos, datos_usuario_validos, app_context):
        """Test: Person and user creation with integrity error."""
        with patch.object(usuario_service, '_crear_persona') as mock_crear_persona, \
             patch.object(usuario_service, '_crear_usuario') as mock_crear_usuario, \
             patch.object(usuario_service, '_asignar_rol_por_defecto'), \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_persona = MagicMock()
            mock_persona.id_persona = 1
            mock_crear_persona.return_value = mock_persona
            
            mock_usuario = MagicMock()
            mock_usuario.id_usuario = 1
            mock_crear_usuario.return_value = mock_usuario
            
            # Simulate integrity error on commit
            mock_db.session.commit.side_effect = IntegrityError("Duplicate entry", None, None)
            mock_db.session.rollback = MagicMock()
            
            with pytest.raises(UsuarioServiceError, match="Error de duplicación|Error al crear usuario"):
                usuario_service._crear_persona_y_usuario(
                    datos_persona_validos,
                    datos_usuario_validos
                )
            
            mock_db.session.rollback.assert_called_once()
    
    def test_crear_persona(self, usuario_service, datos_persona_validos):
        """Test: Person creation."""
        with patch('src.services.Auth.usuario_service.Persona') as mock_persona_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_persona = MagicMock()
            mock_persona_class.return_value = mock_persona
            mock_db.session.add = MagicMock()
            
            result = usuario_service._crear_persona(datos_persona_validos)
            
            assert result == mock_persona
            mock_persona_class.assert_called_once()
            mock_db.session.add.assert_called_once()
    
    def test_crear_usuario(self, usuario_service, datos_usuario_validos):
        """Test: User creation."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.generate_password_hash', return_value='hashed_password') as mock_hash, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_usuario = MagicMock()
            mock_usuario_class.return_value = mock_usuario
            mock_db.session.add = MagicMock()
            
            result = usuario_service._crear_usuario(1, datos_usuario_validos)
            
            assert result == mock_usuario
            mock_usuario_class.assert_called_once()
            mock_hash.assert_called_once_with('password123')
            mock_db.session.add.assert_called_once()
    
    def test_verificar_credenciales_success(self, usuario_service):
        """Test: Successful credential verification."""
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_usuario.password = 'hashed_password'
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.check_password_hash', return_value=True):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = usuario_service.verificar_credenciales('testuser', 'password123')
            
            assert result == mock_usuario
    
    def test_verificar_credenciales_user_not_found(self, usuario_service):
        """Test: Credential verification with user not found."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            
            result = usuario_service.verificar_credenciales('testuser', 'password123')
            
            assert result is None
    
    def test_verificar_credenciales_wrong_password(self, usuario_service):
        """Test: Credential verification with wrong password."""
        mock_usuario = MagicMock()
        mock_usuario.estado = True
        mock_usuario.password = 'hashed_password'
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.check_password_hash', return_value=False):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = usuario_service.verificar_credenciales('testuser', 'wrongpassword')
            
            assert result is None
    
    def test_obtener_usuario_por_id_success(self, usuario_service):
        """Test: Successful user retrieval by ID."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = usuario_service.obtener_usuario_por_id(1)
            
            assert result == mock_usuario
    
    def test_obtener_usuario_por_id_not_found(self, usuario_service):
        """Test: User retrieval by ID when user doesn't exist."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            
            result = usuario_service.obtener_usuario_por_id(999)
            
            assert result is None
    
    def test_obtener_usuario_con_roles_success(self, usuario_service):
        """Test: Successful user retrieval with roles."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch.object(usuario_service, '_serializar_usuario', return_value={'id_usuario': 1}) as mock_serializar:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            result = usuario_service.obtener_usuario_con_roles(1)
            
            assert result == {'id_usuario': 1}
            mock_serializar.assert_called_once_with(mock_usuario)
    
    def test_obtener_usuario_con_roles_not_found(self, usuario_service):
        """Test: User retrieval with roles when user doesn't exist."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            
            result = usuario_service.obtener_usuario_con_roles(999)
            
            assert result is None
    
    def test_actualizar_usuario_success(self, usuario_service, app_context):
        """Test: Successful user update."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        mock_usuario.id_persona = 1
        mock_usuario.persona = None  # Will be set later
        
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_persona.primer_nombre = 'Juan'
        mock_persona.primer_apellido = 'Pérez'
        
        datos_persona = {'primer_nombre': 'Juan Updated'}
        datos_usuario = {'usuario': 'juanupdated'}
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.Persona') as mock_persona_class, \
             patch('src.models.personas.persona.Persona') as mock_persona_import, \
             patch.object(usuario_service, '_validar_y_actualizar_persona') as mock_validar_persona, \
             patch.object(usuario_service, '_validar_y_actualizar_usuario') as mock_validar_usuario, \
             patch.object(usuario_service, '_serializar_usuario', return_value={'id_usuario': 1}), \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_usuario_query = MagicMock()
            mock_usuario_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_usuario_query
            
            # Mock both Persona.query (from import at top) and the local import inside the method
            mock_persona_query = MagicMock()
            mock_persona_query.get.return_value = mock_persona
            mock_persona_class.query = mock_persona_query
            mock_persona_import.query = mock_persona_query
            
            # Set persona on usuario after mocking
            mock_usuario.persona = mock_persona
            
            mock_db.session.add = MagicMock()
            mock_db.session.flush = MagicMock()
            mock_db.session.commit = MagicMock()
            mock_db.session.refresh = MagicMock()
            
            result = usuario_service.actualizar_usuario(1, datos_persona, datos_usuario)
            
            assert result['success'] is True
            assert result['status_code'] == 200
            mock_validar_persona.assert_called_once()
            mock_validar_usuario.assert_called_once()
            mock_db.session.commit.assert_called_once()
    
    def test_actualizar_usuario_not_found(self, usuario_service, app_context):
        """Test: User update when user doesn't exist."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_usuario_class.query = mock_query
            mock_db.session.rollback = MagicMock()
            
            with pytest.raises(UsuarioServiceError, match="Usuario con ID .* no encontrado"):
                usuario_service.actualizar_usuario(999, {}, {})
    
    def test_actualizar_usuario_inactive(self, usuario_service, app_context):
        """Test: User update when user is inactive."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = False
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            mock_db.session.rollback = MagicMock()
            
            with pytest.raises(UsuarioServiceError, match="Usuario con ID .* está inactivo"):
                usuario_service.actualizar_usuario(1, {}, {})
    
    def test_actualizar_usuario_no_data(self, usuario_service):
        """Test: User update with no data provided."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            mock_usuario_class.query = mock_query
            
            mock_db.session.rollback = MagicMock()
            
            with pytest.raises(UsuarioServiceError, match="Debe proporcionar al menos datos_persona o datos_usuario"):
                usuario_service.actualizar_usuario(1, None, None)
            
            mock_db.session.rollback.assert_called_once()

