"""
Tests de integración para cambiar rol de usuario.

Endpoint: PUT /api/usuarios/<id>/rol
Funcionalidad: Cambiar el rol de un usuario

NOTA IMPORTANTE:
---------------
Estos tests presentan un comportamiento conocido:
- ✅ Pasan cuando se ejecutan individualmente
- ❌ Fallan con 404 cuando se ejecutan con toda la suite de tests

Causa: El decorador @token_required se instancia al importar el módulo,
y cuando se ejecutan todos los tests, el mock no se aplica correctamente
a todas las instancias del decorador.

Solución: Ejecutar estos tests de forma aislada:
    pytest tests/integration/routes/usuarios/test_cambiar_rol_usuario_completo.py -v

Ver README.md en este directorio para más detalles.
"""

import pytest  # pyright: ignore[reportMissingImports]

from tests.helpers import (
    assert_success_response,
    assert_error_response,
    make_json_request,
    create_auth_headers
)


@pytest.mark.routes
@pytest.mark.integration
@pytest.mark.usuarios
class TestCambiarRolUsuarioCompleto:
    """Tests para el endpoint PUT /api/usuarios/<id>/rol"""
    
    def test_cambiar_rol_usuario_exitoso(
        self, client, db_session, usuario, mock_token_required
    ):
        """
        Test: Cambiar rol de usuario exitosamente.
        
        Valida:
        - Actualización de rol en BD
        - Validación de rol existente
        - Respuesta con datos actualizados
        """
        # Arrange
        from src.models.roles_y_permisos.rol import Rol
        from src.models.roles_y_permisos.usuario_rol import UsuarioRol
        
        # Debug: Verificar que la ruta esté registrada
        app = client.application
        rules = [r for r in app.url_map.iter_rules() if 'rol' in r.rule and 'usuario' in r.rule]
        if not rules:
            pytest.fail(f"Ruta no encontrada. Rutas disponibles: {[r.rule for r in app.url_map.iter_rules() if 'usuario' in r.rule]}")
        
        # Crear rol nuevo
        rol_nuevo = Rol(nombre_rol='Entrenador', descripcion='Rol de entrenador')
        db_session.add(rol_nuevo)
        db_session.commit()
        
        datos_rol = {
            'id_rol': rol_nuevo.id_rol
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'PUT', f'/api/usuarios/{usuario.id_usuario}/rol',
            data=datos_rol,
            headers=headers
        )
        
        # Assert
        data = assert_success_response(response)
        assert 'data' in data
        
        # Verificar actualización en BD
        db_session.refresh(usuario)
        usuario_rol = UsuarioRol.query.filter_by(
            id_usuario=usuario.id_usuario,
            id_rol=rol_nuevo.id_rol
        ).first()
        assert usuario_rol is not None
    
    def test_cambiar_rol_usuario_rol_no_existe(
        self, client, db_session, usuario, mock_token_required
    ):
        """
        Test: Comportamiento cuando el rol no existe.
        
        Valida que el sistema ignora roles inexistentes (no lanza error).
        El endpoint filtra roles inválidos y solo asigna los válidos.
        """
        # Arrange
        datos_rol = {
            'id_rol': 99999  # Rol inexistente
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'PUT', f'/api/usuarios/{usuario.id_usuario}/rol',
            data=datos_rol,
            headers=headers
        )
        
        # Assert
        # El endpoint filtra roles inexistentes y devuelve 200 con éxito
        # pero sin asignar el rol (el rol no está en ROLES_PERMITIDOS)
        # Si el rol no está en ROLES_PERMITIDOS, el endpoint lo filtra silenciosamente
        assert response.status_code == 200
        data = response.get_json()
        assert data.get('success') is True
        # El rol inexistente no se asigna, pero la respuesta es exitosa
    
    def test_cambiar_rol_usuario_no_existe(
        self, client, db_session, rol, mock_token_required
    ):
        """
        Test: Error cuando el usuario no existe.
        
        Valida que el sistema maneja usuarios inexistentes.
        """
        # Arrange
        datos_rol = {
            'id_rol': rol.id_rol
        }
        
        headers = create_auth_headers('test_token')
        
        # Act
        response = make_json_request(
            client, 'PUT', '/api/usuarios/99999/rol',
            data=datos_rol,
            headers=headers
        )
        
        # Assert
        assert_error_response(response, expected_status=404)

