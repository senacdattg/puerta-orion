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
            'password': '12345'  # nosonar: S2068 - Test password only, intentionally short for validation test
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
    
    def test_registrar_usuario_completo_unexpected_error(self, usuario_service, datos_persona_validos, datos_usuario_validos):
        """Test: Unexpected error handling in registrar_usuario_completo (líneas 102-104)."""
        with patch.object(usuario_service, '_validar_datos_persona') as mock_validar:
            mock_validar.side_effect = Exception("Unexpected error")
            
            with pytest.raises(UsuarioServiceError, match="Error interno del servidor"):
                usuario_service.registrar_usuario_completo(
                    datos_persona_validos,
                    datos_usuario_validos
                )
    
    def test_validar_datos_persona_with_observaciones(self, usuario_service, datos_persona_validos):
        """Test: Person data validation with observaciones field (línea 131)."""
        datos_persona_validos['observaciones'] = 'Test observations'
        
        with patch('src.services.Auth.usuario_service.validate_name', return_value='Juan'), \
             patch('src.services.Auth.usuario_service.validate_document', return_value='12345678'), \
             patch('src.services.Auth.usuario_service.validate_email', return_value='juan@example.com'), \
             patch('src.services.Auth.usuario_service.validate_phone', return_value='3001234567'), \
             patch('src.services.Auth.usuario_service.sanitize_address', return_value='Calle 123'), \
             patch('src.services.Auth.usuario_service.sanitize_free_text', return_value='Test observations'):
            
            usuario_service._validar_datos_persona(datos_persona_validos)
            
            assert datos_persona_validos['observaciones'] == 'Test observations'
    
    def test_validar_datos_persona_empty_second_name(self, usuario_service, datos_persona_validos):
        """Test: Person data validation with empty second name (línea 144)."""
        datos_persona_validos['segundo_nombre'] = ''
        
        with patch('src.services.Auth.usuario_service.validate_name', return_value=''), \
             patch('src.services.Auth.usuario_service.validate_document', return_value='12345678'), \
             patch('src.services.Auth.usuario_service.validate_email', return_value='juan@example.com'), \
             patch('src.services.Auth.usuario_service.validate_phone', return_value='3001234567'), \
             patch('src.services.Auth.usuario_service.sanitize_address', return_value='Calle 123'):
            
            usuario_service._validar_datos_persona(datos_persona_validos)
            
            assert datos_persona_validos['segundo_nombre'] is None
    
    def test_validar_datos_persona_empty_second_lastname(self, usuario_service, datos_persona_validos):
        """Test: Person data validation with empty second lastname (línea 146)."""
        datos_persona_validos['segundo_apellido'] = ''
        
        with patch('src.services.Auth.usuario_service.validate_name', side_effect=['Juan', '', 'Pérez', '']), \
             patch('src.services.Auth.usuario_service.validate_document', return_value='12345678'), \
             patch('src.services.Auth.usuario_service.validate_email', return_value='juan@example.com'), \
             patch('src.services.Auth.usuario_service.validate_phone', return_value='3001234567'), \
             patch('src.services.Auth.usuario_service.sanitize_address', return_value='Calle 123'):
            
            usuario_service._validar_datos_persona(datos_persona_validos)
            
            assert datos_persona_validos['segundo_apellido'] is None
    
    def test_validar_datos_persona_missing_ids(self, usuario_service, datos_persona_validos):
        """Test: Person data validation with missing ID fields (línea 138)."""
        datos_persona_validos.pop('id_tipo_documento', None)
        datos_persona_validos.pop('id_sexo', None)
        
        with patch('src.services.Auth.usuario_service.validate_name', return_value='Juan'), \
             patch('src.services.Auth.usuario_service.validate_document', return_value='12345678'), \
             patch('src.services.Auth.usuario_service.validate_email', return_value='juan@example.com'), \
             patch('src.services.Auth.usuario_service.validate_phone', return_value='3001234567'), \
             patch('src.services.Auth.usuario_service.sanitize_address', return_value='Calle 123'):
            
            with pytest.raises(UsuarioServiceError, match="Campos requeridos faltantes"):
                usuario_service._validar_datos_persona(datos_persona_validos)
    
    def test_asignar_rol_especifico_success(self, usuario_service, app_context):
        """Test: Assign specific role successfully (líneas 210-224)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.set_rol_activo = MagicMock()
        
        mock_rol_especifico = MagicMock()
        mock_rol_especifico.id_rol = 2
        mock_rol_especifico.nombre_rol = 'Deportista'
        
        mock_rol_por_defecto = MagicMock()
        mock_rol_por_defecto.id_rol = 1
        
        with patch('src.services.Auth.usuario_service.Rol') as mock_rol_class, \
             patch('src.services.Auth.usuario_service.UsuarioRol') as mock_usuario_rol_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_rol_query = MagicMock()
            mock_rol_query.filter_by.return_value.first.return_value = mock_rol_especifico
            mock_rol_class.query = mock_rol_query
            
            mock_usuario_rol_query = MagicMock()
            mock_usuario_rol_query.filter_by.return_value.first.return_value = None
            mock_usuario_rol_class.query = mock_usuario_rol_query
            
            mock_db.session.add = MagicMock()
            
            usuario_service._asignar_rol_especifico(mock_usuario, 'deportista', mock_rol_por_defecto)
            
            mock_db.session.add.assert_called_once()
            mock_usuario.set_rol_activo.assert_called_once_with(mock_rol_especifico)
    
    def test_asignar_rol_especifico_with_default_rol(self, usuario_service):
        """Test: Assign default role when specific role not found (línea 224)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.set_rol_activo = MagicMock()
        
        mock_rol_por_defecto = MagicMock()
        mock_rol_por_defecto.id_rol = 1
        
        with patch('src.services.Auth.usuario_service.Rol') as mock_rol_class:
            mock_rol_query = MagicMock()
            mock_rol_query.filter_by.return_value.first.return_value = None
            mock_rol_class.query = mock_rol_query
            
            usuario_service._asignar_rol_especifico(mock_usuario, 'unknown', mock_rol_por_defecto)
            
            mock_usuario.set_rol_activo.assert_called_once_with(mock_rol_por_defecto)
    
    def test_procesar_rol_opcional_deportista(self, usuario_service):
        """Test: Process optional deportista role (líneas 227-235)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.set_rol_activo = MagicMock()
        
        datos_rol = {'id_categoria': 1}
        
        with patch.object(usuario_service, '_crear_registro_rol') as mock_crear, \
             patch.object(usuario_service, '_asignar_rol_especifico') as mock_asignar:
            
            usuario_service._procesar_rol_opcional(mock_usuario, 'deportista', datos_rol, None)
            
            mock_crear.assert_called_once_with(mock_usuario, 'deportista', datos_rol)
            mock_asignar.assert_called_once()
    
    def test_procesar_rol_opcional_invalid(self, usuario_service):
        """Test: Process invalid optional role (línea 229)."""
        mock_usuario = MagicMock()
        mock_rol_por_defecto = MagicMock()
        mock_usuario.set_rol_activo = MagicMock()
        
        usuario_service._procesar_rol_opcional(mock_usuario, 'invalid', None, mock_rol_por_defecto)
        
        mock_usuario.set_rol_activo.assert_called_once_with(mock_rol_por_defecto)
    
    def test_crear_persona_y_usuario_with_rol_opcional(self, usuario_service, datos_persona_validos, datos_usuario_validos, app_context):
        """Test: Create person and user with optional role (líneas 208-235)."""
        with patch.object(usuario_service, '_crear_persona') as mock_crear_persona, \
             patch.object(usuario_service, '_crear_usuario') as mock_crear_usuario, \
             patch.object(usuario_service, '_asignar_rol_por_defecto') as mock_rol, \
             patch.object(usuario_service, '_procesar_rol_opcional') as mock_procesar, \
             patch.object(usuario_service, '_serializar_usuario', return_value={'id_usuario': 1}), \
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
            
            datos_rol = {'id_categoria': 1}
            result = usuario_service._crear_persona_y_usuario(
                datos_persona_validos,
                datos_usuario_validos,
                'deportista',
                datos_rol
            )
            
            assert result['id_usuario'] == 1
            mock_procesar.assert_called_once_with(mock_usuario, 'deportista', datos_rol, mock_rol_obj)
    
    def test_crear_persona_y_usuario_generic_error(self, usuario_service, datos_persona_validos, datos_usuario_validos, app_context):
        """Test: Generic error in crear_persona_y_usuario (líneas 276-279)."""
        with patch.object(usuario_service, '_crear_persona', side_effect=Exception('Generic error')), \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_db.session.rollback = MagicMock()
            
            with pytest.raises(UsuarioServiceError, match="Error al crear usuario"):
                usuario_service._crear_persona_y_usuario(
                    datos_persona_validos,
                    datos_usuario_validos
                )
            
            mock_db.session.rollback.assert_called_once()

    def test_procesar_fecha_nacimiento_deportista_fecha_invalida(self, usuario_service):
        """Test: Process invalid date format in _procesar_fecha_nacimiento_deportista (línea 354)."""
        # Test invalid string format that's neither ISO nor an integer
        with pytest.raises(UsuarioServiceError, match="Formato de fecha de nacimiento inválido"):
            usuario_service._procesar_fecha_nacimiento_deportista("invalid-date-format")

    def test_procesar_fecha_nacimiento_deportista_none(self, usuario_service):
        """Test: Process None date in _procesar_fecha_nacimiento_deportista (línea 335)."""
        result = usuario_service._procesar_fecha_nacimiento_deportista(None)
        assert result is None

    def test_procesar_fecha_nacimiento_deportista_date_object(self, usuario_service):
        """Test: Process date object in _procesar_fecha_nacimiento_deportista (línea 340)."""
        fecha = date(2000, 1, 1)
        result = usuario_service._procesar_fecha_nacimiento_deportista(fecha)
        assert result == fecha

    def test_procesar_fecha_nacimiento_deportista_int(self, usuario_service):
        """Test: Process int year in _procesar_fecha_nacimiento_deportista (línea 343)."""
        result = usuario_service._procesar_fecha_nacimiento_deportista(2000)
        assert result == date(2000, 1, 1)

    def test_procesar_fecha_nacimiento_deportista_iso_string(self, usuario_service):
        """Test: Process ISO string in _procesar_fecha_nacimiento_deportista (línea 348)."""
        result = usuario_service._procesar_fecha_nacimiento_deportista("2000-06-15")
        assert result == date(2000, 6, 15)

    def test_procesar_fecha_nacimiento_deportista_year_string(self, usuario_service):
        """Test: Process year string in _procesar_fecha_nacimiento_deportista (línea 351)."""
        result = usuario_service._procesar_fecha_nacimiento_deportista("2000")
        assert result == date(2000, 1, 1)

    def test_crear_deportista_registro_success(self, usuario_service, app_context):
        """Test: Successful deportista registration (líneas 381-382)."""
        datos = {
            'id_categoria': 1,
            'peso': 70.5,
            'altura': 1.75,
            'fecha_nacimiento': date(2000, 1, 1)
        }
        
        with patch('src.services.Auth.usuario_service.Deportista') as mock_deportista_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None  # No existe
            mock_deportista_class.query = mock_query
            
            mock_deportista = MagicMock()
            mock_deportista_class.return_value = mock_deportista
            mock_db.session.add = MagicMock()
            
            usuario_service._crear_deportista_registro(1, datos)
            
            mock_deportista_class.assert_called_once()
            mock_db.session.add.assert_called_once_with(mock_deportista)

    def test_crear_deportista_registro_existente(self, usuario_service, app_context):
        """Test: Deportista registration when already exists (línea 362)."""
        datos = {'id_categoria': 1}
        
        with patch('src.services.Auth.usuario_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_existing = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_existing  # Ya existe
            mock_deportista_class.query = mock_query
            
            with pytest.raises(UsuarioServiceError, match="Ya existe un registro de deportista"):
                usuario_service._crear_deportista_registro(1, datos)

    def test_crear_deportista_registro_sin_categoria(self, usuario_service, app_context):
        """Test: Deportista registration without categoria (línea 365)."""
        datos = {}
        
        with patch('src.services.Auth.usuario_service.Deportista') as mock_deportista_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista_class.query = mock_query
            
            with pytest.raises(UsuarioServiceError, match="id_categoria.*es obligatorio"):
                usuario_service._crear_deportista_registro(1, datos)

    def test_crear_acudiente_registro_success(self, usuario_service, app_context):
        """Test: Successful acudiente registration (líneas 399-400)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_usuario.persona = mock_persona
        
        datos = {'estado': True}
        
        with patch('src.services.Auth.usuario_service.Acudiente') as mock_acudiente_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db, \
             patch('src.services.Auth.usuario_service.puede_registrarse_como_acudiente', return_value=True):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None  # No existe
            mock_acudiente_class.query = mock_query
            
            mock_acudiente = MagicMock()
            mock_acudiente_class.return_value = mock_acudiente
            mock_db.session.add = MagicMock()
            
            usuario_service._crear_acudiente_registro(1, mock_usuario, datos)
            
            mock_acudiente_class.assert_called_once()
            mock_db.session.add.assert_called_once_with(mock_acudiente)

    def test_crear_acudiente_registro_existente(self, usuario_service, app_context):
        """Test: Acudiente registration when already exists (líneas 387-388)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        
        with patch('src.services.Auth.usuario_service.Acudiente') as mock_acudiente_class:
            mock_query = MagicMock()
            mock_existing = MagicMock()
            mock_query.filter_by.return_value.first.return_value = mock_existing  # Ya existe
            mock_acudiente_class.query = mock_query
            
            with pytest.raises(UsuarioServiceError, match="Ya existe un registro de acudiente"):
                usuario_service._crear_acudiente_registro(1, mock_usuario, None)

    def test_crear_acudiente_registro_no_puede_registrarse(self, usuario_service, app_context):
        """Test: Acudiente registration when cannot register (líneas 390-393)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_usuario.persona = mock_persona
        
        with patch('src.services.Auth.usuario_service.Acudiente') as mock_acudiente_class, \
             patch('src.services.Auth.usuario_service.puede_registrarse_como_acudiente', return_value=False):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None  # No existe
            mock_acudiente_class.query = mock_query
            
            with pytest.raises(UsuarioServiceError, match="Para registrarse como acudiente"):
                usuario_service._crear_acudiente_registro(1, mock_usuario, None)

    def test_crear_acudiente_registro_sin_datos(self, usuario_service, app_context):
        """Test: Acudiente registration without datos (línea 397)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        mock_persona = MagicMock()
        mock_persona.id_persona = 1
        mock_usuario.persona = mock_persona
        
        with patch('src.services.Auth.usuario_service.Acudiente') as mock_acudiente_class, \
             patch('src.services.Auth.usuario_service.db') as mock_db, \
             patch('src.services.Auth.usuario_service.puede_registrarse_como_acudiente', return_value=True):
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_acudiente_class.query = mock_query
            
            mock_acudiente = MagicMock()
            mock_acudiente_class.return_value = mock_acudiente
            mock_db.session.add = MagicMock()
            
            # Llamar con datos=None
            usuario_service._crear_acudiente_registro(1, mock_usuario, None)
            
            # Verificar que se creó con estado=True por defecto
            mock_acudiente_class.assert_called_once_with(id_persona=1, estado=True)

    def test_crear_registro_rol_deportista(self, usuario_service, app_context):
        """Test: Create registro rol for deportista (línea 418)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        datos = {'id_categoria': 1}
        
        with patch.object(usuario_service, '_crear_deportista_registro') as mock_crear:
            usuario_service._crear_registro_rol(mock_usuario, 'deportista', datos)
            mock_crear.assert_called_once_with(1, datos)

    def test_crear_registro_rol_acudiente(self, usuario_service, app_context):
        """Test: Create registro rol for acudiente (línea 420)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        datos = {'estado': True}
        
        with patch.object(usuario_service, '_crear_acudiente_registro') as mock_crear:
            usuario_service._crear_registro_rol(mock_usuario, 'acudiente', datos)
            mock_crear.assert_called_once_with(1, mock_usuario, datos)

    def test_crear_registro_rol_invalido(self, usuario_service, app_context):
        """Test: Create registro rol with invalid role (líneas 421-422)."""
        mock_usuario = MagicMock()
        datos = {}
        
        with pytest.raises(UsuarioServiceError, match="Rol inválido: invalid"):
            usuario_service._crear_registro_rol(mock_usuario, 'invalid', datos)

    def test_crear_registro_rol_exception(self, usuario_service, app_context):
        """Test: Create registro rol with exception (líneas 426-428)."""
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        
        with patch.object(usuario_service, '_crear_deportista_registro', side_effect=Exception("DB Error")):
            with pytest.raises(UsuarioServiceError, match="Error al crear registro de deportista"):
                usuario_service._crear_registro_rol(mock_usuario, 'deportista', {})

    def test_asignar_rol_por_defecto_sin_roles_existentes(self, usuario_service, app_context):
        """Test: Assign default role when no existing roles (línea 462)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        mock_rol_usuario = MagicMock()
        mock_rol_usuario.id_rol = 1
        
        with patch('src.services.Auth.usuario_service.UsuarioRol') as mock_usuario_rol_class, \
             patch.object(usuario_service, '_obtener_o_crear_rol_usuario', return_value=mock_rol_usuario) as mock_obtener, \
             patch('src.services.Auth.usuario_service.db') as mock_db:
            
            mock_query = MagicMock()
            mock_query.filter_by.return_value.all.return_value = []  # Sin roles existentes
            mock_usuario_rol_class.query = mock_query
            
            mock_usuario_rol = MagicMock()
            mock_usuario_rol_class.return_value = mock_usuario_rol
            mock_db.session.add = MagicMock()
            
            result = usuario_service._asignar_rol_por_defecto(mock_usuario)
            
            assert result == mock_rol_usuario
            mock_obtener.assert_called_once()
            mock_db.session.add.assert_called_once_with(mock_usuario_rol)

    def test_asignar_rol_por_defecto_con_roles_existentes(self, usuario_service, app_context):
        """Test: Assign default role when roles already exist (líneas 448-451)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        mock_rol_usuario = MagicMock()
        mock_rol_usuario.id_rol = 1
        
        mock_rol_existente = MagicMock()
        mock_rol_existente.id_rol = 2
        
        mock_primer_rol = MagicMock()
        mock_primer_rol.id_rol = 2
        
        with patch('src.services.Auth.usuario_service.UsuarioRol') as mock_usuario_rol_class, \
             patch('src.services.Auth.usuario_service.Rol') as mock_rol_class:
            
            # Mock roles existentes
            mock_usuario_rol_query = MagicMock()
            mock_usuario_rol_query.filter_by.return_value.all.return_value = [mock_rol_existente]
            mock_usuario_rol_class.query = mock_usuario_rol_query
            
            # Mock rol 'usuario'
            mock_rol_query = MagicMock()
            mock_rol_query.filter_by.return_value.first.return_value = mock_rol_usuario
            mock_rol_class.query = mock_rol_query
            
            # Mock get para obtener primer_rol
            mock_rol_query.get.return_value = mock_primer_rol
            
            result = usuario_service._asignar_rol_por_defecto(mock_usuario)
            
            assert result == mock_primer_rol

    def test_asignar_rol_por_defecto_con_rol_usuario_asignado(self, usuario_service, app_context):
        """Test: Assign default role when usuario role already assigned (línea 448)."""
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        
        mock_rol_usuario = MagicMock()
        mock_rol_usuario.id_rol = 1
        
        mock_rol_existente = MagicMock()
        mock_rol_existente.id_rol = 1  # Mismo que rol_usuario
        
        with patch('src.services.Auth.usuario_service.UsuarioRol') as mock_usuario_rol_class, \
             patch('src.services.Auth.usuario_service.Rol') as mock_rol_class:
            
            mock_usuario_rol_query = MagicMock()
            mock_usuario_rol_query.filter_by.return_value.all.return_value = [mock_rol_existente]
            mock_usuario_rol_class.query = mock_usuario_rol_query
            
            mock_rol_query = MagicMock()
            mock_rol_query.filter_by.return_value.first.return_value = mock_rol_usuario
            mock_rol_class.query = mock_rol_query
            
            result = usuario_service._asignar_rol_por_defecto(mock_usuario)
            
            assert result == mock_rol_usuario

    def test_obtener_usuario_para_detalle_con_usuario_obj(self, usuario_service, app_context):
        """Test: Get usuario for detail with provided usuario_obj (línea 872)."""
        mock_usuario = MagicMock()
        mock_usuario.usuario = 'testuser'
        mock_usuario.id_usuario = 1
        mock_usuario.estado = True
        
        result = usuario_service._obtener_usuario_para_detalle(1, mock_usuario)
        
        assert result == mock_usuario

    def test_obtener_usuario_para_detalle_sin_filtro_estado(self, usuario_service, app_context):
        """Test: Get usuario for detail without estado filter (líneas 875-877)."""
        mock_usuario_sin_filtro = MagicMock()
        mock_usuario_sin_filtro.usuario = 'inactive_user'
        mock_usuario_sin_filtro.estado = False
        
        mock_usuario_activo = MagicMock()
        mock_usuario_activo.usuario = 'active_user'
        mock_usuario_activo.estado = True
        mock_usuario_activo.id_usuario = 1
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            # Primera llamada (sin filtro de estado)
            mock_query.filter_by.return_value.first.side_effect = [
                mock_usuario_sin_filtro,  # Sin filtro
                mock_usuario_activo  # Con filtro estado=True
            ]
            mock_usuario_class.query = mock_query
            
            result = usuario_service._obtener_usuario_para_detalle(1, None)
            
            assert result == mock_usuario_activo

    def test_obtener_usuario_para_detalle_inactivo_pero_valido(self, usuario_service, app_context):
        """Test: Get inactive usuario but valid token (líneas 881-883)."""
        mock_usuario_sin_filtro = MagicMock()
        mock_usuario_sin_filtro.usuario = 'inactive_user'
        mock_usuario_sin_filtro.estado = False
        mock_usuario_sin_filtro.id_usuario = 1
        
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            # Primera llamada (sin filtro) devuelve usuario inactivo
            # Segunda llamada (con filtro) devuelve None
            mock_query.filter_by.return_value.first.side_effect = [
                mock_usuario_sin_filtro,  # Sin filtro
                None  # Con filtro estado=True (no encontrado)
            ]
            mock_usuario_class.query = mock_query
            
            result = usuario_service._obtener_usuario_para_detalle(1, None)
            
            # Debe usar el usuario inactivo porque tiene token válido
            assert result == mock_usuario_sin_filtro

    def test_obtener_usuario_para_detalle_no_encontrado(self, usuario_service, app_context):
        """Test: Get usuario for detail when not found (líneas 886-887)."""
        with patch('src.services.Auth.usuario_service.Usuario') as mock_usuario_class:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None  # No encontrado
            mock_usuario_class.query = mock_query
            
            result = usuario_service._obtener_usuario_para_detalle(999, None)
            
            assert result is None

