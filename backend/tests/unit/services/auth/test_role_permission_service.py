"""
Tests para role_permission_service.py.

Este módulo contiene tests que verifican las funciones
de gestión de roles, permisos y visibilidad de paneles.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from datetime import date, datetime
from src.services.Auth.role_permission_service import (
    RoleNames,
    ROLE_PRIORITY,
    MODULE_ACCESS,
    HIDE_USUARIO_IF_HAS,
    PanelVisibility,
    normalizar_nombre_rol,
    obtener_roles_usuario,
    calcular_edad,
    es_deportista_menor,
    filtrar_roles_visibles,
    asegurar_rol_activo_valido,
    obtener_paneles_autorizados,
    puede_registrarse_como_acudiente,
    validar_mayoria_de_edad,
    obtener_roles_para_selector,
    cambiar_rol_activo,
)


@pytest.mark.unit
class TestNormalizarNombreRol:
    """Tests para normalizar_nombre_rol."""
    
    def test_normalizar_nombre_rol_basic(self):
        """Test: Normalizar nombre de rol básico."""
        result = normalizar_nombre_rol("  Admin  ")
        assert result == "Admin"
    
    def test_normalizar_nombre_rol_empty(self):
        """Test: Normalizar nombre de rol vacío."""
        result = normalizar_nombre_rol("")
        assert result == ""
    
    def test_normalizar_nombre_rol_none(self):
        """Test: Normalizar nombre de rol None."""
        result = normalizar_nombre_rol(None)
        assert result == ""


@pytest.mark.unit
class TestObtenerRolesUsuario:
    """Tests para obtener_roles_usuario."""
    
    def test_obtener_roles_usuario_with_roles(self):
        """Test: Obtener roles de usuario con roles asignados."""
        usuario = MagicMock()
        rol1 = MagicMock()
        rol1.nombre_rol = "Admin"
        rol2 = MagicMock()
        rol2.nombre_rol = "Usuario"
        usuario.roles = [rol1, rol2]
        
        result = obtener_roles_usuario(usuario)
        
        assert result == {"Admin", "Usuario"}
    
    def test_obtener_roles_usuario_no_roles(self):
        """Test: Obtener roles de usuario sin roles."""
        usuario = MagicMock()
        usuario.roles = []
        
        result = obtener_roles_usuario(usuario)
        
        assert result == set()
    
    def test_obtener_roles_usuario_none(self):
        """Test: Obtener roles de usuario None."""
        result = obtener_roles_usuario(None)
        
        assert result == set()
    
    def test_obtener_roles_usuario_no_roles_attribute(self):
        """Test: Obtener roles de usuario sin atributo roles."""
        usuario = MagicMock()
        del usuario.roles
        
        result = obtener_roles_usuario(usuario)
        
        assert result == set()


@pytest.mark.unit
class TestCalcularEdad:
    """Tests para calcular_edad."""
    
    def test_calcular_edad_from_date(self):
        """Test: Calcular edad desde date."""
        fecha_nacimiento = date(2000, 1, 1)
        edad = calcular_edad(fecha_nacimiento)
        
        assert isinstance(edad, int)
        assert edad > 20  # Debe ser mayor a 20 años
    
    def test_calcular_edad_from_datetime(self):
        """Test: Calcular edad desde datetime."""
        fecha_nacimiento = datetime(2000, 1, 1, 12, 0, 0)
        edad = calcular_edad(fecha_nacimiento)
        
        assert isinstance(edad, int)
        assert edad > 20
    
    def test_calcular_edad_from_int(self):
        """Test: Calcular edad desde int (año)."""
        edad = calcular_edad(2000)
        
        assert isinstance(edad, int)
        assert edad > 20
    
    def test_calcular_edad_none(self):
        """Test: Calcular edad con None."""
        edad = calcular_edad(None)
        
        assert edad is None
    
    def test_calcular_edad_invalid_type(self):
        """Test: Calcular edad con tipo inválido."""
        edad = calcular_edad("2000-01-01")
        
        assert edad is None


@pytest.mark.unit
class TestEsDeportistaMenor:
    """Tests para es_deportista_menor."""
    
    def test_es_deportista_menor_true(self):
        """Test: Verificar si es deportista menor (True)."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        deportista = MagicMock()
        deportista.fecha_nacimiento = date.today().replace(year=date.today().year - 10)
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = deportista
            mock_deportista.query = mock_query
            
            result = es_deportista_menor(usuario)
            
            assert result is True
    
    def test_es_deportista_menor_false(self):
        """Test: Verificar si es deportista menor (False)."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        deportista = MagicMock()
        deportista.fecha_nacimiento = date.today().replace(year=date.today().year - 20)
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = deportista
            mock_deportista.query = mock_query
            
            result = es_deportista_menor(usuario)
            
            assert result is False
    
    def test_es_deportista_menor_no_usuario(self):
        """Test: Verificar si es deportista menor sin usuario."""
        result = es_deportista_menor(None)
        
        assert result is False
    
    def test_es_deportista_menor_no_persona(self):
        """Test: Verificar si es deportista menor sin persona."""
        usuario = MagicMock()
        del usuario.persona
        
        result = es_deportista_menor(usuario)
        
        assert result is False
    
    def test_es_deportista_menor_no_deportista(self):
        """Test: Verificar si es deportista menor sin deportista."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista.query = mock_query
            
            result = es_deportista_menor(usuario)
            
            assert result is False
    
    def test_es_deportista_menor_edad_none(self):
        """Test: Verificar si es deportista menor cuando edad es None (línea 152)."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        deportista = MagicMock()
        deportista.fecha_nacimiento = date.today().replace(year=date.today().year - 10)
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            with patch('src.services.Auth.role_permission_service.calcular_edad', return_value=None):
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = deportista
                mock_deportista.query = mock_query
                
                result = es_deportista_menor(usuario)
                
                assert result is False


@pytest.mark.unit
class TestFiltrarRolesVisibles:
    """Tests para filtrar_roles_visibles."""
    
    def test_filtrar_roles_visibles_basic(self):
        """Test: Filtrar roles visibles básico."""
        usuario = MagicMock()
        rol = MagicMock()
        rol.nombre_rol = RoleNames.ADMINISTRADOR
        usuario.roles = [rol]
        
        with patch('src.services.Auth.role_permission_service.es_deportista_menor', return_value=False):
            result = filtrar_roles_visibles(usuario)
            
            assert RoleNames.ADMINISTRADOR in result
    
    def test_filtrar_roles_visibles_hide_usuario(self):
        """Test: Ocultar rol Usuario cuando hay otros roles."""
        usuario = MagicMock()
        rol1 = MagicMock()
        rol1.nombre_rol = RoleNames.USUARIO
        rol2 = MagicMock()
        rol2.nombre_rol = RoleNames.DEPORTISTA
        usuario.roles = [rol1, rol2]
        
        with patch('src.services.Auth.role_permission_service.es_deportista_menor', return_value=False):
            result = filtrar_roles_visibles(usuario)
            
            assert RoleNames.USUARIO not in result
            assert RoleNames.DEPORTISTA in result
    
    def test_filtrar_roles_visibles_hide_usuario_menor(self):
        """Test: Ocultar rol Usuario cuando es menor."""
        usuario = MagicMock()
        rol = MagicMock()
        rol.nombre_rol = RoleNames.USUARIO
        usuario.roles = [rol]
        
        with patch('src.services.Auth.role_permission_service.es_deportista_menor', return_value=True):
            result = filtrar_roles_visibles(usuario)
            
            assert RoleNames.USUARIO not in result
    
    def test_filtrar_roles_visibles_no_roles(self):
        """Test: Filtrar roles visibles sin roles."""
        usuario = MagicMock()
        usuario.roles = []
        
        result = filtrar_roles_visibles(usuario)
        
        assert result == []


@pytest.mark.unit
class TestValidarMayoriaDeEdad:
    """Tests para validar_mayoria_de_edad."""
    
    def test_validar_mayoria_de_edad_true(self):
        """Test: Validar mayoría de edad (True)."""
        fecha_nacimiento = date.today().replace(year=date.today().year - 20)
        
        result = validar_mayoria_de_edad(fecha_nacimiento)
        
        assert result is True
    
    def test_validar_mayoria_de_edad_false(self):
        """Test: Validar mayoría de edad (False)."""
        fecha_nacimiento = date.today().replace(year=date.today().year - 10)
        
        result = validar_mayoria_de_edad(fecha_nacimiento)
        
        assert result is False
    
    def test_validar_mayoria_de_edad_none(self):
        """Test: Validar mayoría de edad con None."""
        result = validar_mayoria_de_edad(None)
        
        assert result is True
    
    def test_validar_mayoria_de_edad_custom_age(self):
        """Test: Validar mayoría de edad con edad mínima personalizada."""
        fecha_nacimiento = date.today().replace(year=date.today().year - 21)
        
        result = validar_mayoria_de_edad(fecha_nacimiento, edad_minima=25)
        
        assert result is False


@pytest.mark.unit
class TestPuedeRegistrarseComoAcudiente:
    """Tests para puede_registrarse_como_acudiente."""
    
    def test_puede_registrarse_como_acudiente_true_no_deportista(self):
        """Test: Puede registrarse como acudiente si no es deportista."""
        usuario = MagicMock()
        persona = MagicMock()
        usuario.persona = persona
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = None
            mock_deportista.query = mock_query
            
            result = puede_registrarse_como_acudiente(usuario)
            
            assert result is True
    
    def test_puede_registrarse_como_acudiente_true_mayor(self):
        """Test: Puede registrarse como acudiente si es mayor."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        deportista = MagicMock()
        deportista.fecha_nacimiento = date.today().replace(year=date.today().year - 20)
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = deportista
            mock_deportista.query = mock_query
            
            with patch('src.services.Auth.role_permission_service.es_deportista_menor', return_value=False):
                result = puede_registrarse_como_acudiente(usuario)
                
                assert result is True
    
    def test_puede_registrarse_como_acudiente_false_menor(self):
        """Test: No puede registrarse como acudiente si es menor."""
        usuario = MagicMock()
        persona = MagicMock()
        persona.id_persona = 1
        usuario.persona = persona
        
        deportista = MagicMock()
        deportista.fecha_nacimiento = date.today().replace(year=date.today().year - 10)
        
        with patch('src.services.Auth.role_permission_service.Deportista') as mock_deportista:
            mock_query = MagicMock()
            mock_query.filter_by.return_value.first.return_value = deportista
            mock_deportista.query = mock_query
            
            with patch('src.services.Auth.role_permission_service.es_deportista_menor', return_value=True):
                result = puede_registrarse_como_acudiente(usuario)
                
                assert result is False
    
    def test_puede_registrarse_como_acudiente_no_usuario(self):
        """Test: No puede registrarse como acudiente sin usuario."""
        result = puede_registrarse_como_acudiente(None)
        
        assert result is False


@pytest.mark.unit
class TestObtenerRolesParaSelector:
    """Tests para obtener_roles_para_selector."""
    
    def test_obtener_roles_para_selector_basic(self):
        """Test: Obtener roles para selector básico."""
        usuario = MagicMock()
        rol1 = MagicMock()
        rol1.nombre_rol = RoleNames.ADMINISTRADOR
        rol2 = MagicMock()
        rol2.nombre_rol = RoleNames.DEPORTISTA
        usuario.roles = [rol1, rol2]
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.ADMINISTRADOR, RoleNames.DEPORTISTA]):
            result = obtener_roles_para_selector(usuario)
            
            assert RoleNames.ADMINISTRADOR in result
            assert RoleNames.DEPORTISTA in result
    
    def test_obtener_roles_para_selector_usuario_always_visible(self):
        """Test: Rol Usuario siempre visible en selector."""
        usuario = MagicMock()
        rol = MagicMock()
        rol.nombre_rol = RoleNames.USUARIO
        usuario.roles = [rol]
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[]):
            result = obtener_roles_para_selector(usuario)
            
            assert RoleNames.USUARIO in result
            assert result[RoleNames.USUARIO] is True


@pytest.mark.unit
class TestCambiarRolActivo:
    """Tests para cambiar_rol_activo."""
    
    def test_cambiar_rol_activo_success(self):
        """Test: Cambiar rol activo exitosamente."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        
        rol_objetivo_obj = MagicMock()
        rol_objetivo_obj.nombre_rol = RoleNames.ADMINISTRADOR
        
        rol_usuario = MagicMock()
        rol_usuario.nombre_rol = RoleNames.USUARIO
        usuario.roles = [rol_usuario, rol_objetivo_obj]
        
        with patch('src.services.Auth.role_permission_service.obtener_roles_para_selector', return_value={RoleNames.ADMINISTRADOR: True}):
            usuario.set_rol_activo = MagicMock()
            
            result = cambiar_rol_activo(usuario, RoleNames.ADMINISTRADOR, commit=False)
            
            assert result == rol_objetivo_obj
            usuario.set_rol_activo.assert_called_once_with(rol_objetivo_obj)
    
    def test_cambiar_rol_activo_not_in_selector(self):
        """Test: Error cuando rol no está en selector."""
        usuario = MagicMock()
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.obtener_roles_para_selector', return_value={}):
            with pytest.raises(ValueError) as exc_info:
                cambiar_rol_activo(usuario, RoleNames.ADMINISTRADOR)
            
            assert "no tiene asignado el rol" in str(exc_info.value)
    
    def test_cambiar_rol_activo_not_visible(self):
        """Test: Error cuando rol no está visible."""
        usuario = MagicMock()
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.obtener_roles_para_selector', return_value={RoleNames.ADMINISTRADOR: False}):
            with pytest.raises(PermissionError) as exc_info:
                cambiar_rol_activo(usuario, RoleNames.ADMINISTRADOR)
            
            assert "no está disponible como rol activo" in str(exc_info.value)
    
    def test_cambiar_rol_activo_rol_not_found(self):
        """Test: Error cuando rol no se encuentra."""
        usuario = MagicMock()
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.obtener_roles_para_selector', return_value={RoleNames.ADMINISTRADOR: True}):
            with pytest.raises(ValueError) as exc_info:
                cambiar_rol_activo(usuario, RoleNames.ADMINISTRADOR)
            
            assert "No se encontró la definición del rol" in str(exc_info.value)


@pytest.mark.unit
class TestAsegurarRolActivoValido:
    """Tests para asegurar_rol_activo_valido."""
    
    def test_asegurar_rol_activo_valido_mantener_rol(self):
        """Test: Mantener rol activo si está en roles asignados."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        
        rol_activo = MagicMock()
        rol_activo.nombre_rol = RoleNames.ADMINISTRADOR
        usuario.rol_activo = rol_activo
        
        rol_obj = MagicMock()
        rol_obj.nombre_rol = RoleNames.ADMINISTRADOR
        usuario.roles = [rol_obj]
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.ADMINISTRADOR]):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                result = asegurar_rol_activo_valido(usuario, commit=False)
                
                assert result == rol_activo
    
    def test_asegurar_rol_activo_valido_ajustar_rol(self):
        """Test: Ajustar rol activo cuando no está en roles asignados."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.rol_activo = None
        
        rol_obj = MagicMock()
        rol_obj.nombre_rol = RoleNames.ADMINISTRADOR
        usuario.roles = [rol_obj]
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.ADMINISTRADOR]):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                usuario.set_rol_activo = MagicMock()
                result = asegurar_rol_activo_valido(usuario, commit=False)
                
                assert result == rol_obj
                usuario.set_rol_activo.assert_called_once()
    
    def test_asegurar_rol_activo_valido_sin_roles_visibles(self):
        """Test: Limpiar rol activo cuando no hay roles visibles."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.rol_activo = None
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[]):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                usuario.set_rol_activo = MagicMock()
                result = asegurar_rol_activo_valido(usuario, commit=False)
                
                assert result is None
                usuario.set_rol_activo.assert_called_once_with(None)
    
    def test_asegurar_rol_activo_valido_with_commit_no_roles(self):
        """Test: Limpiar rol activo con commit cuando no hay roles visibles (líneas 228-229)."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.rol_activo = None
        usuario.roles = []
        
        mock_db_session = MagicMock()
        mock_db = MagicMock()
        mock_db.session = mock_db_session
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[]):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                with patch('src.models.base.db', mock_db):
                    usuario.set_rol_activo = MagicMock()
                    result = asegurar_rol_activo_valido(usuario, commit=True)
                    
                    assert result is None
                    usuario.set_rol_activo.assert_called_once_with(None)
                    mock_db_session.commit.assert_called_once()
    
    def test_asegurar_rol_activo_valido_with_commit_ajustar(self):
        """Test: Ajustar rol activo con commit (líneas 244-245)."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        usuario.rol_activo = None
        
        rol_obj = MagicMock()
        rol_obj.nombre_rol = RoleNames.ADMINISTRADOR
        usuario.roles = [rol_obj]
        
        mock_db_session = MagicMock()
        mock_db = MagicMock()
        mock_db.session = mock_db_session
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.ADMINISTRADOR]):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                with patch('src.models.base.db', mock_db):
                    usuario.set_rol_activo = MagicMock()
                    result = asegurar_rol_activo_valido(usuario, commit=True)
                    
                    assert result == rol_obj
                    usuario.set_rol_activo.assert_called_once()
                    mock_db_session.commit.assert_called_once()


@pytest.mark.unit
class TestObtenerPanelesAutorizados:
    """Tests para obtener_paneles_autorizados."""
    
    def test_obtener_paneles_autorizados_basic(self):
        """Test: Obtener paneles autorizados básico."""
        usuario = MagicMock()
        rol_activo = MagicMock()
        rol_activo.nombre_rol = RoleNames.SUPERADMIN
        usuario.rol_activo = rol_activo
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.SUPERADMIN]):
            result = obtener_paneles_autorizados(usuario)
            
            assert isinstance(result, list)
            assert all(isinstance(p, PanelVisibility) for p in result)
            assert any(p.module == 'panel_admin' and p.allowed for p in result)
    
    def test_obtener_paneles_autorizados_sin_rol_activo(self):
        """Test: Obtener paneles autorizados sin rol activo (líneas 256-257)."""
        usuario = MagicMock()
        usuario.rol_activo = None
        usuario.roles = []
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.DEPORTISTA]):
            result = obtener_paneles_autorizados(usuario)
            
            assert isinstance(result, list)
            assert all(isinstance(p, PanelVisibility) for p in result)
    
    def test_obtener_paneles_autorizados_with_usuario_role(self):
        """Test: Obtener paneles autorizados con rol Usuario (línea 260)."""
        usuario = MagicMock()
        usuario.rol_activo = None
        rol_usuario = MagicMock()
        rol_usuario.nombre_rol = RoleNames.USUARIO
        usuario.roles = [rol_usuario]
        
        with patch('src.services.Auth.role_permission_service.filtrar_roles_visibles', return_value=[RoleNames.DEPORTISTA]):
            result = obtener_paneles_autorizados(usuario)
            
            assert isinstance(result, list)
            assert all(isinstance(p, PanelVisibility) for p in result)
    
    def test_cambiar_rol_activo_with_commit(self):
        """Test: Cambiar rol activo con commit=True (líneas 331-338)."""
        usuario = MagicMock()
        usuario.id_usuario = 1
        
        rol_objetivo_obj = MagicMock()
        rol_objetivo_obj.nombre_rol = RoleNames.ADMINISTRADOR
        
        usuario.roles = [rol_objetivo_obj]
        
        mock_db_session = MagicMock()
        mock_db = MagicMock()
        mock_db.session = mock_db_session
        
        with patch('src.services.Auth.role_permission_service.obtener_roles_para_selector', return_value={RoleNames.ADMINISTRADOR: True}):
            with patch('src.services.Auth.role_permission_service._get_logger'):
                with patch('src.models.base.db', mock_db):
                    usuario.set_rol_activo = MagicMock()
                    
                    result = cambiar_rol_activo(usuario, RoleNames.ADMINISTRADOR, commit=True)
                    
                    assert result == rol_objetivo_obj
                    usuario.set_rol_activo.assert_called_once_with(rol_objetivo_obj)
                    mock_db_session.commit.assert_called_once()


@pytest.mark.unit
class TestConstants:
    """Tests para constantes del módulo."""
    
    def test_role_names_constants(self):
        """Test: Constantes de nombres de roles."""
        assert RoleNames.SUPERADMIN == 'SuperAdmin'
        assert RoleNames.ADMINISTRADOR == 'Administrador'
        assert RoleNames.ENTRENADOR == 'Entrenador'
        assert RoleNames.DEPORTISTA == 'Deportista'
        assert RoleNames.ACUDIENTE == 'Acudiente'
        assert RoleNames.USUARIO == 'usuario'
    
    def test_role_priority_order(self):
        """Test: Orden de prioridad de roles."""
        assert ROLE_PRIORITY[0] == RoleNames.SUPERADMIN
        assert RoleNames.USUARIO in ROLE_PRIORITY
    
    def test_module_access_structure(self):
        """Test: Estructura de acceso a módulos."""
        assert 'panel_admin' in MODULE_ACCESS
        assert RoleNames.SUPERADMIN in MODULE_ACCESS['panel_admin']
    
    def test_hide_usuario_if_has(self):
        """Test: Reglas para ocultar rol Usuario."""
        assert RoleNames.DEPORTISTA in HIDE_USUARIO_IF_HAS
        assert RoleNames.ACUDIENTE in HIDE_USUARIO_IF_HAS

