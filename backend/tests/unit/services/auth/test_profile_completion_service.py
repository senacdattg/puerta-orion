"""
Tests unitarios para profile_completion_service.

Cubre validación, creación de perfiles y asignación de roles.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from src.services.Auth.profile_completion_service import (
    ProfileCompletionService,
    ProfileCompletionError,
    DeportistaValidator,
    AcudienteValidator,
    DeportistaCreator,
    AcudienteCreator,
    RoleAssigner,
)


@pytest.mark.unit
class TestProfileValidators:
    """Tests para validadores de perfil"""
    
    def test_deportista_validator_campos_requeridos(self):
        """Test: Validar campos requeridos para deportista."""
        validator = DeportistaValidator()
        
        with pytest.raises(ProfileCompletionError) as exc:
            validator.validate({})
        assert 'requeridos' in str(exc.value).lower()
    
    def test_deportista_validator_peso_invalido(self):
        """Test: Validar peso inválido."""
        validator = DeportistaValidator()
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'peso': -10})
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'peso': 500})
    
    def test_deportista_validator_altura_invalida(self):
        """Test: Validar altura inválida."""
        validator = DeportistaValidator()
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'altura': -1})
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'altura': 5})
    
    def test_deportista_validator_fecha_nacimiento_invalida(self):
        """Test: Validar fecha de nacimiento inválida."""
        validator = DeportistaValidator()
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'fecha_nacimiento': 1800})
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_categoria': 1, 'fecha_nacimiento': 2100})
    
    def test_deportista_validator_success(self):
        """Test: Validación exitosa de deportista."""
        validator = DeportistaValidator()
        data = {
            'id_categoria': 1,
            'peso': 60.5,
            'altura': 1.70,
            'fecha_nacimiento': 2000
        }
        
        # No debe lanzar excepción
        validator.validate(data)
    
    def test_acudiente_validator_campos_requeridos(self):
        """Test: Validar campos requeridos para acudiente."""
        validator = AcudienteValidator()
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({})
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({'id_deportista': 1})
    
    def test_acudiente_validator_success(self):
        """Test: Validación exitosa de acudiente."""
        validator = AcudienteValidator()
        data = {
            'id_deportista': 1,
            'id_parentesco': 1,
            'es_responsable': True
        }
        
        validator.validate(data)
    
    def test_acudiente_validator_parentesco_invalido(self):
        """Test: Validar parentesco inválido."""
        validator = AcudienteValidator()
        
        with pytest.raises(ProfileCompletionError):
            validator.validate({
                'id_deportista': 1,
                'id_parentesco': -1,
                'es_responsable': True
            })


@pytest.mark.unit
class TestProfileCreators:
    """Tests para creadores de perfil"""
    
    def test_deportista_creator_get_profile_type(self):
        """Test: Obtener tipo de perfil deportista."""
        creator = DeportistaCreator()
        assert creator.get_profile_type() == 'deportista'
    
    def test_deportista_creator_create_success(self, app_context):
        """Test: Crear deportista exitosamente."""
        from src.models.usuarios.usuario import Usuario
        from src.models.base import db
        
        creator = DeportistaCreator()
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        
        data = {
            'id_categoria': 1,
            'peso': 60.5,
            'altura': 1.70,
            'fecha_nacimiento': '2000-01-15'
        }
        
        with patch('src.services.Auth.profile_completion_service.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.services.Auth.profile_completion_service.Deportista') as mock_deportista:
                mock_instance = MagicMock()
                mock_deportista.return_value = mock_instance
                with patch('src.services.Auth.profile_completion_service.db') as mock_db:
                    mock_db.session.add = MagicMock()
                    
                    result = creator.create(1, data)
                    assert result == mock_instance
    
    def test_acudiente_creator_get_profile_type(self):
        """Test: Obtener tipo de perfil acudiente."""
        creator = AcudienteCreator()
        assert creator.get_profile_type() == 'acudiente'
    
    def test_acudiente_creator_create_success(self, app_context):
        """Test: Crear acudiente exitosamente."""
        from src.models.usuarios.usuario import Usuario
        from src.models.deportistas.deportista import Deportista
        
        creator = AcudienteCreator()
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 2  # Diferente al usuario
        
        data = {
            'id_deportista': 1,
            'id_parentesco': 1,
            'es_responsable': True
        }
        
        with patch('src.services.Auth.profile_completion_service.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.models.deportistas.deportista.Deportista.query') as mock_deportista_query:
                mock_deportista_query.filter_by.return_value.first.return_value = mock_deportista
                with patch('src.models.acudientes.parentesco.Parentesco.query') as mock_parentesco_query:
                    mock_parentesco = MagicMock()
                    mock_parentesco_query.filter_by.return_value.first.return_value = mock_parentesco
                    with patch('src.models.acudientes.deportista_acudiente.DeportistaAcudiente.query') as mock_rel_query:
                        mock_filter_by = MagicMock()
                        mock_filter_by.count.return_value = 0
                        mock_filter_by.first.return_value = None
                        mock_rel_query.filter_by.return_value = mock_filter_by
                        with patch('src.services.Auth.profile_completion_service.Acudiente') as mock_acudiente:
                            mock_instance = MagicMock()
                            mock_instance.id_acudiente = 1
                            mock_instance.id_persona = 1
                            mock_acudiente.return_value = mock_instance
                            with patch('src.services.Auth.profile_completion_service.db') as mock_db:
                                mock_db.session.add = MagicMock()
                                mock_db.session.flush = MagicMock()
                                
                                result = creator.create(1, data)
                                assert result == mock_instance


@pytest.mark.unit
class TestRoleAssigner:
    """Tests para asignador de roles"""
    
    def test_assign_role_success(self, app_context):
        """Test: Asignar rol exitosamente."""
        assigner = RoleAssigner()
        
        mock_rol = MagicMock()
        mock_rol.id_rol = 1
        
        mock_ur_instance = MagicMock()
        
        # Mockear Rol.query para que encuentre el rol
        with patch('src.services.Auth.profile_completion_service.Rol.query') as mock_rol_query:
            mock_rol_filter = MagicMock()
            mock_rol_filter.first.return_value = mock_rol
            mock_rol_query.filter_by.return_value = mock_rol_filter
            
            # Mockear UsuarioRol.query para que NO encuentre relación existente
            with patch('src.services.Auth.profile_completion_service.UsuarioRol') as mock_ur_class:
                mock_ur_class.return_value = mock_ur_instance
                
                mock_ur_query = MagicMock()
                mock_ur_filter = MagicMock()
                mock_ur_filter.first.return_value = None  # No existe relación
                mock_ur_query.filter_by.return_value = mock_ur_filter
                mock_ur_class.query = mock_ur_query
                
                # Mockear db.session.add - parchear en el módulo donde se usa
                with patch('src.services.Auth.profile_completion_service.db') as mock_db:
                    mock_add = MagicMock()
                    mock_db.session.add = mock_add
                    
                    assigner.assign_role(1, 'Deportista')
                    # Verificar que se llamó al menos una vez
                    assert mock_add.called, "db.session.add debería haberse llamado"
    
    def test_assign_role_already_exists(self, app_context):
        """Test: Rol ya asignado."""
        from src.models.roles_y_permisos.usuario_rol import UsuarioRol
        
        assigner = RoleAssigner()
        
        mock_rol = MagicMock()
        mock_rol.id_rol = 1
        
        mock_ur_existente = MagicMock()
        
        with patch('src.services.Auth.profile_completion_service.Rol.query') as mock_rol_query:
            mock_rol_query.filter_by.return_value.first.return_value = mock_rol
            with patch('src.services.Auth.profile_completion_service.UsuarioRol.query') as mock_ur_query:
                mock_ur_query.filter_by.return_value.first.return_value = mock_ur_existente
                with patch('src.services.Auth.profile_completion_service.db') as mock_db:
                    # No debe agregar nuevo rol
                    assigner.assign_role(1, 'Deportista')
                    mock_db.session.add.assert_not_called()
    
    def test_assign_role_not_found(self, app_context):
        """Test: Rol no encontrado."""
        assigner = RoleAssigner()
        
        with patch('src.services.Auth.profile_completion_service.Rol.query') as mock_rol_query:
            mock_rol_query.filter_by.return_value.first.return_value = None
            
            with pytest.raises(ProfileCompletionError) as exc:
                assigner.assign_role(1, 'RolInexistente')
            assert 'no encontrado' in str(exc.value).lower()


@pytest.mark.unit
class TestProfileCompletionService:
    """Tests para ProfileCompletionService"""
    
    @pytest.fixture
    def service(self):
        """Fixture para servicio."""
        return ProfileCompletionService()
    
    def test_complete_profile_deportista_success(self, service, app_context):
        """Test: Completar perfil deportista exitosamente."""
        from src.models.usuarios.usuario import Usuario
        from src.models.deportistas.deportista import Deportista
        
        mock_usuario = MagicMock()
        mock_usuario.id_persona = 1
        mock_usuario.roles = []
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        mock_deportista.id_persona = 1
        
        data = {
            'id_categoria': 1,
            'peso': 60.5,
            'altura': 1.70
        }
        
        with patch('src.services.Auth.profile_completion_service.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.services.Auth.profile_completion_service.Deportista.query') as mock_dep_query:
                mock_dep_query.filter_by.return_value.first.return_value = None
                with patch.object(service, '_validate_user_can_complete_profile'):
                    with patch.object(service.profile_components['deportista']['creator'], 'create', return_value=mock_deportista):
                        with patch.object(service.role_assigner, 'assign_role'):
                            with patch('src.services.Auth.profile_completion_service.db') as mock_db:
                                mock_db.session.flush = MagicMock()
                                mock_db.session.commit = MagicMock()
                                
                                result = service.complete_profile(1, 'deportista', data)
                                
                                assert result.success is True
                                assert result.profile_type == 'deportista'
                                assert result.profile_id == 1
    
    def test_complete_profile_tipo_invalido(self, service):
        """Test: Tipo de perfil inválido."""
        with pytest.raises(ProfileCompletionError) as exc:
            service.complete_profile(1, 'tipo_invalido', {})
        assert 'no válido' in str(exc.value).lower()
    
    def test_check_profile_status_success(self, service, app_context):
        """Test: Verificar estado de perfil."""
        from src.models.usuarios.usuario import Usuario
        from src.models.deportistas.deportista import Deportista
        
        mock_usuario = MagicMock()
        mock_usuario.id_usuario = 1
        mock_usuario.id_persona = 1
        mock_rol = MagicMock()
        mock_rol.nombre_rol = 'Deportista'
        mock_usuario.roles = [mock_rol]
        
        mock_deportista = MagicMock()
        mock_deportista.id_deportista = 1
        
        with patch('src.services.Auth.profile_completion_service.Usuario.query') as mock_query:
            mock_query.filter_by.return_value.first.return_value = mock_usuario
            with patch('src.services.Auth.profile_completion_service.Deportista.query') as mock_dep_query:
                mock_dep_query.filter_by.return_value.first.return_value = mock_deportista
                with patch('src.services.Auth.profile_completion_service.Acudiente.query') as mock_acud_query:
                    mock_acud_query.filter_by.return_value.first.return_value = None
                    
                    result = service.check_profile_status(1)
                    
                    assert result['es_deportista'] is True
                    assert result['es_acudiente'] is False
                    assert result['perfil_completo'] is True
