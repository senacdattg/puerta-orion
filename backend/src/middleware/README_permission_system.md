# Documentación: Sistema de Permisos con check_permission

## Descripción General

El sistema de permisos implementado proporciona una forma robusta y flexible de controlar el acceso a recursos y funcionalidades en la aplicación Flask. Utiliza una arquitectura basada en roles y permisos (RBAC - Role-Based Access Control) donde los usuarios tienen roles, y los roles tienen permisos específicos.

## Arquitectura del Sistema

### Modelos Involucrados

1. **Usuario**: Representa a los usuarios del sistema
2. **Rol**: Define roles como 'admin', 'usuario', 'auditor', etc.
3. **Permiso**: Define permisos específicos como 'crear_usuario', 'ver_reportes', etc.
4. **UsuarioRol**: Relación many-to-many entre usuarios y roles
5. **RolPermiso**: Relación many-to-many entre roles y permisos

### Flujo de Verificación

```
Usuario → Roles → Permisos → Verificación
```

## Funciones Principales

### 1. `check_permission(usuario, permiso)`

**Propósito**: Verifica si un usuario específico tiene un permiso determinado.

**Parámetros**:
- `usuario` (Usuario): Instancia del modelo Usuario
- `permiso` (str): Nombre del permiso a verificar

**Retorna**: `bool` - True si tiene el permiso, False en caso contrario

**Ejemplo de uso**:
```python
from src.middleware.auth_decorator import check_permission
from src.models.usuarios.usuario import Usuario

usuario = Usuario.query.get(1)
tiene_permiso = check_permission(usuario, 'crear_usuario')
```

### 2. `get_user_permissions(usuario)`

**Propósito**: Obtiene todos los permisos de un usuario a través de sus roles.

**Parámetros**:
- `usuario` (Usuario): Instancia del modelo Usuario

**Retorna**: `list` - Lista de nombres de permisos

**Ejemplo de uso**:
```python
from src.middleware.auth_decorator import get_user_permissions

usuario = Usuario.query.get(1)
permisos = get_user_permissions(usuario)
# Retorna: ['crear_usuario', 'editar_usuario', 'ver_reportes']
```

## Decoradores de Autenticación y Autorización

### 1. `@token_required`

**Versión básica**: Solo requiere autenticación
```python
@token_required()
def mi_endpoint():
    pass
```

**Con roles específicos**:
```python
@token_required(required_roles=['admin'])
def endpoint_admin():
    pass
```

**Con permisos específicos**:
```python
@token_required(required_permissions=['crear_usuario'])
def endpoint_crear_usuario():
    pass
```

**Combinado (roles Y permisos)**:
```python
@token_required(
    required_roles=['admin'], 
    required_permissions=['configurar_sistema']
)
def endpoint_configuracion():
    pass
```

### 2. `@permission_required`

**Propósito**: Requiere que el usuario tenga TODOS los permisos especificados.

```python
@permission_required('crear_usuario', 'editar_usuario')
def gestionar_usuarios():
    # El usuario debe tener AMBOS permisos
    pass
```

### 3. `@any_permission_required`

**Propósito**: Requiere que el usuario tenga AL MENOS UNO de los permisos especificados.

```python
@any_permission_required('ver_reportes', 'administrar_sistema')
def ver_dashboard():
    # El usuario puede tener cualquiera de los permisos
    pass
```

## Funciones Helper

### 1. `has_permission(permiso)`

Verifica si el usuario actual tiene un permiso específico.

```python
from src.middleware.auth_decorator import has_permission

@token_required()
def mi_endpoint():
    if has_permission('crear_usuario'):
        # Lógica para crear usuario
        pass
    else:
        return jsonify({'error': 'Sin permisos'}), 403
```

### 2. `has_role(rol)`

Verifica si el usuario actual tiene un rol específico.

```python
from src.middleware.auth_decorator import has_role

@token_required()
def mi_endpoint():
    if has_role('admin'):
        # Lógica solo para administradores
        pass
```

### 3. `get_user_permissions_list()`

Obtiene la lista de permisos del usuario actual.

```python
from src.middleware.auth_decorator import get_user_permissions_list

@token_required()
def mi_endpoint():
    permisos = get_user_permissions_list()
    return jsonify({'permisos': permisos})
```

### 4. `get_current_user()`

Obtiene los datos del usuario autenticado actual.

```python
from src.middleware.auth_decorator import get_current_user

@token_required()
def mi_endpoint():
    usuario = get_current_user()
    return jsonify({
        'username': usuario['username'],
        'roles': usuario['roles'],
        'permisos': usuario['permisos']
    })
```

## Datos Inyectados en el Contexto

Cuando se usa `@token_required`, se inyectan los siguientes datos en `g.current_user`:

```python
{
    'id_usuario': 1,
    'username': 'juan.perez',
    'estado': 'activo',
    'roles': [
        {
            'id_rol': 1,
            'nombre_rol': 'usuario',
            'descripcion': 'Rol por defecto'
        }
    ],
    'permisos': ['crear_usuario', 'ver_reportes'],
    'persona': {
        'id_persona': 1,
        'nombre_completo': 'Juan Pérez',
        'correo_electronico': 'juan@email.com',
        'documento': 12345678
    }
}
```

## Ejemplos de Uso Completos

### 1. Endpoint con Verificación de Permisos

```python
from flask import Blueprint, jsonify
from src.middleware.auth_decorator import permission_required, get_current_user

bp = Blueprint('usuarios', __name__)

@bp.route('/api/usuarios', methods=['POST'])
@permission_required('crear_usuario')
def crear_usuario():
    """Crear nuevo usuario - requiere permiso 'crear_usuario'"""
    usuario_actual = get_current_user()
    
    return jsonify({
        'success': True,
        'message': 'Usuario creado exitosamente',
        'creado_por': usuario_actual['username']
    })
```

### 2. Endpoint con Lógica Condicional

```python
@bp.route('/api/usuarios/<int:user_id>')
@token_required()
def obtener_usuario(user_id):
    """Obtener usuario con datos según permisos"""
    usuario_actual = get_current_user()
    
    # Datos básicos siempre visibles
    datos_usuario = {
        'id': user_id,
        'username': 'usuario.ejemplo'
    }
    
    # Datos adicionales según permisos
    if has_permission('ver_datos_extendidos'):
        datos_usuario.update({
            'email': 'usuario@email.com',
            'telefono': '3001234567'
        })
    
    # Datos sensibles solo para admins
    if has_permission('ver_informacion_sensible'):
        datos_usuario.update({
            'ultimo_acceso': '2024-01-15T10:30:00',
            'ip_ultimo_acceso': '192.168.1.100'
        })
    
    return jsonify({
        'success': True,
        'data': datos_usuario
    })
```

### 3. Endpoint con Múltiples Niveles de Autorización

```python
@bp.route('/api/reportes')
@any_role_required('admin', 'auditor')
@any_permission_required('ver_reportes', 'administrar_sistema')
def obtener_reportes():
    """Acceso a reportes con múltiples niveles de autorización"""
    usuario_actual = get_current_user()
    
    # Reportes básicos para todos los autorizados
    reportes = ['reporte_usuarios', 'reporte_actividad']
    
    # Reportes adicionales para administradores
    if has_role('admin'):
        reportes.extend(['reporte_seguridad', 'reporte_errores'])
    
    # Reportes sensibles solo con permiso específico
    if has_permission('ver_reporte_sensible'):
        reportes.append('reporte_datos_sensibles')
    
    return jsonify({
        'success': True,
        'data': {
            'reportes_disponibles': reportes,
            'usuario': usuario_actual['username']
        }
    })
```

## Configuración de Permisos

### 1. Crear Permisos en la Base de Datos

```python
from src.models.roles_y_permisos.permiso import Permiso
from src.models.base import db

# Crear permisos
permisos = [
    Permiso(nombre='crear_usuario', descripcion='Crear nuevos usuarios'),
    Permiso(nombre='editar_usuario', descripcion='Editar usuarios existentes'),
    Permiso(nombre='eliminar_usuario', descripcion='Eliminar usuarios'),
    Permiso(nombre='ver_reportes', descripcion='Ver reportes del sistema'),
    Permiso(nombre='administrar_sistema', descripcion='Administrar configuración del sistema'),
    Permiso(nombre='ver_informacion_sensible', descripcion='Ver información sensible')
]

for permiso in permisos:
    db.session.add(permiso)

db.session.commit()
```

### 2. Asignar Permisos a Roles

```python
from src.models.roles_y_permisos.rol import Rol
from src.models.roles_y_permisos.rol_permiso import RolPermiso

# Obtener rol admin
rol_admin = Rol.query.filter_by(nombre_rol='admin').first()

# Obtener permisos
permisos_admin = Permiso.query.filter(
    Permiso.nombre.in_([
        'crear_usuario', 'editar_usuario', 'eliminar_usuario',
        'ver_reportes', 'administrar_sistema', 'ver_informacion_sensible'
    ])
).all()

# Asignar permisos al rol
for permiso in permisos_admin:
    rol_permiso = RolPermiso(
        id_rol=rol_admin.id_rol,
        id_permiso=permiso.id_permiso
    )
    db.session.add(rol_permiso)

db.session.commit()
```

## Manejo de Errores

### 1. Permiso No Existe

Si se verifica un permiso que no existe en la base de datos:

```python
# check_permission retorna False
tiene_permiso = check_permission(usuario, 'permiso_inexistente')
# Retorna: False
```

### 2. Usuario Sin Roles

Si un usuario no tiene roles asignados:

```python
# check_permission retorna False
tiene_permiso = check_permission(usuario_sin_roles, 'cualquier_permiso')
# Retorna: False
```

### 3. Error en Decorador

Si un decorador falla, retorna respuesta JSON con error:

```python
# Respuesta automática del decorador
{
    "success": false,
    "message": "Permisos insuficientes",
    "status_code": 403
}
```

## Mejores Prácticas

### 1. Nomenclatura de Permisos

- Usar nombres descriptivos: `crear_usuario`, `editar_perfil`, `ver_reportes`
- Usar snake_case para consistencia
- Agrupar por funcionalidad: `usuario_crear`, `usuario_editar`, `usuario_eliminar`

### 2. Granularidad de Permisos

- **Muy granular**: Un permiso por acción (`crear_usuario`, `editar_usuario`, `eliminar_usuario`)
- **Moderadamente granular**: Un permiso por módulo (`gestionar_usuarios`, `gestionar_reportes`)
- **Poco granular**: Un permiso por área (`administracion`, `operaciones`)

### 3. Uso de Decoradores

```python
# ✅ Bueno: Específico y claro
@permission_required('crear_usuario')
def crear_usuario():
    pass

# ❌ Malo: Muy genérico
@token_required()
def crear_usuario():
    if not has_permission('crear_usuario'):
        return jsonify({'error': 'Sin permisos'}), 403
    # lógica...
```

### 4. Verificación en Servicios

```python
class UsuarioService:
    def crear_usuario(self, datos_usuario):
        # Verificar permisos en el servicio
        if not check_permission(self.usuario_actual, 'crear_usuario'):
            raise PermissionError("Sin permisos para crear usuarios")
        
        # Lógica del servicio
        pass
```

## Testing

### 1. Test de Función check_permission

```python
import unittest
from src.middleware.auth_decorator import check_permission
from src.models.usuarios.usuario import Usuario

class TestCheckPermission(unittest.TestCase):
    def setUp(self):
        self.usuario = Usuario.query.get(1)
    
    def test_usuario_con_permiso(self):
        resultado = check_permission(self.usuario, 'crear_usuario')
        self.assertTrue(resultado)
    
    def test_usuario_sin_permiso(self):
        resultado = check_permission(self.usuario, 'permiso_inexistente')
        self.assertFalse(resultado)
    
    def test_usuario_nulo(self):
        resultado = check_permission(None, 'crear_usuario')
        self.assertFalse(resultado)
```

### 2. Test de Decoradores

```python
from flask import Flask
from src.middleware.auth_decorator import permission_required

app = Flask(__name__)

@app.route('/test')
@permission_required('crear_usuario')
def test_endpoint():
    return {'success': True}

def test_permission_required():
    with app.test_client() as client:
        # Test sin token (debería fallar)
        response = client.get('/test')
        assert response.status_code == 401
        
        # Test con token válido pero sin permisos (debería fallar)
        headers = {'Authorization': 'Bearer token_sin_permisos'}
        response = client.get('/test', headers=headers)
        assert response.status_code == 403
```

## Integración con Frontend

### 1. Verificación de Permisos en JavaScript

```javascript
// Función helper para verificar permisos
function hasPermission(permission) {
    const user = getCurrentUser();
    return user && user.permisos && user.permisos.includes(permission);
}

// Uso en componentes
if (hasPermission('crear_usuario')) {
    // Mostrar botón de crear usuario
    showCreateUserButton();
} else {
    // Ocultar botón
    hideCreateUserButton();
}
```

### 2. Respuesta de Login con Permisos

```json
{
    "success": true,
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "user": {
            "id_usuario": 1,
            "username": "juan.perez",
            "roles": [{"nombre_rol": "usuario"}],
            "permisos": ["crear_usuario", "ver_reportes"]
        }
    }
}
```

## Troubleshooting

### 1. Problema: Permiso siempre retorna False

**Causas posibles**:
- El permiso no existe en la base de datos
- El usuario no tiene roles asignados
- Los roles no tienen el permiso asignado
- Error en la relación many-to-many

**Solución**:
```python
# Verificar que el permiso existe
permiso = Permiso.query.filter_by(nombre='crear_usuario').first()
print(f"Permiso existe: {permiso is not None}")

# Verificar roles del usuario
usuario = Usuario.query.get(1)
print(f"Roles del usuario: {[r.nombre_rol for r in usuario.roles]}")

# Verificar permisos del rol
for rol in usuario.roles:
    print(f"Permisos del rol {rol.nombre_rol}: {[p.nombre for p in rol.permisos]}")
```

### 2. Problema: Decorador no funciona

**Causas posibles**:
- Token JWT inválido o expirado
- Sesión inactiva en la base de datos
- Error en la configuración del decorador

**Solución**:
```python
# Verificar token manualmente
from src.services.Auth.auth_service import auth_service

payload = auth_service.verificar_token_jwt(token)
print(f"Token válido: {payload is not None}")

# Verificar sesión
sesion = SesionAuth.query.filter_by(token_sesion=token).first()
print(f"Sesión activa: {sesion and sesion.estado == 'activa'}")
```

## Conclusión

El sistema de permisos implementado proporciona:

1. **Flexibilidad**: Múltiples formas de verificar permisos
2. **Seguridad**: Verificación robusta con manejo de errores
3. **Facilidad de uso**: Decoradores simples y funciones helper
4. **Escalabilidad**: Fácil agregar nuevos permisos y roles
5. **Integración**: Funciona perfectamente con el sistema de autenticación existente

La función `check_permission()` es el núcleo del sistema y puede ser utilizada en cualquier parte de la aplicación para verificar permisos de manera consistente y confiable.
