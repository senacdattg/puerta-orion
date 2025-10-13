# Decorador @token_required - Autenticación JWT

## Descripción

El decorador `@token_required` es un middleware de autenticación para Flask que valida tokens JWT, verifica sesiones activas y proporciona acceso a datos del usuario autenticado. Se integra perfectamente con el `AuthService` existente.

## Características Principales

### ✅ Funcionalidades Implementadas

1. **Validación de Tokens JWT**
   - Verificación de formato y firma del token
   - Validación de expiración automática
   - Decodificación segura del payload

2. **Verificación de Sesiones Activas**
   - Consulta a la tabla `SesionAuth`
   - Verificación de estado activo
   - Validación de fecha de expiración

3. **Inyección de Datos de Usuario**
   - Usuario completo con roles en `g.current_user`
   - Información de sesión en `g.current_session`
   - Payload del token en `g.token_payload`

4. **Control de Roles**
   - Decoradores específicos por rol
   - Validación de múltiples roles
   - Funciones helper para verificar permisos

5. **Manejo de Errores**
   - Respuestas JSON consistentes
   - Códigos de estado HTTP apropiados
   - Logging detallado de errores

## Uso Básico

### 1. Decorador Básico

```python
from src.middleware.auth_decorator import token_required

@app.route('/protected')
@token_required()
def ruta_protegida():
    user = get_current_user()
    return jsonify({'message': 'Acceso autorizado', 'user': user})
```

### 2. Decorador con Roles Específicos

```python
@app.route('/admin-only')
@token_required(['admin'])
def ruta_admin():
    return jsonify({'message': 'Solo para administradores'})
```

### 3. Decoradores Específicos por Rol

```python
from src.middleware.auth_decorator import admin_required, user_required

@app.route('/admin/users')
@admin_required
def gestionar_usuarios():
    return jsonify({'message': 'Gestión de usuarios'})

@app.route('/user/profile')
@user_required
def perfil_usuario():
    return jsonify({'message': 'Perfil de usuario'})
```

### 4. Múltiples Roles

```python
from src.middleware.auth_decorator import any_role_required

@app.route('/multi-access')
@any_role_required('admin', 'usuario', 'deportista')
def ruta_multi_rol():
    return jsonify({'message': 'Acceso para múltiples roles'})
```

## Funciones Helper

### Acceso a Datos del Usuario

```python
from src.middleware.auth_decorator import (
    get_current_user,
    get_current_session,
    get_token_payload
)

@app.route('/profile')
@token_required()
def perfil():
    user = get_current_user()
    session = get_current_session()
    payload = get_token_payload()
    
    return jsonify({
        'user': user,
        'session': session,
        'token_data': payload
    })
```

### Verificación de Roles

```python
from src.middleware.auth_decorator import has_role, has_any_role

@app.route('/check-permissions')
@token_required()
def verificar_permisos():
    permissions = {
        'is_admin': has_role('admin'),
        'is_user': has_role('usuario'),
        'can_access_admin': has_any_role('admin'),
        'can_access_sports': has_any_role('deportista', 'admin')
    }
    
    return jsonify({'permissions': permissions})
```

## Estructura de Datos Inyectados

### g.current_user

```json
{
    "id_usuario": 1,
    "username": "juan.perez",
    "estado": true,
    "roles": [
        {
            "id_rol": 1,
            "nombre_rol": "usuario",
            "descripcion": "Rol por defecto para usuarios del sistema"
        }
    ],
    "persona": {
        "id_persona": 1,
        "nombre_completo": "Juan Pérez",
        "correo_electronico": "juan@email.com",
        "documento": 12345678
    }
}
```

### g.current_session

```json
{
    "id_sesion": 1,
    "fecha_inicio": "2024-01-15T10:30:00",
    "fecha_expiracion": "2024-01-15T11:30:00",
    "ip_origen": "192.168.1.100"
}
```

### g.token_payload

```json
{
    "user_id": 1,
    "username": "juan.perez",
    "persona_id": 1,
    "roles": ["usuario"],
    "exp": 1705400000,
    "iat": 1705396400,
    "iss": "puerta_orion_api"
}
```

## Decoradores Disponibles

### Decoradores Principales

| Decorador | Descripción | Uso |
|-----------|-------------|-----|
| `@token_required()` | Cualquier usuario autenticado | `@token_required()` |
| `@token_required(['admin'])` | Roles específicos | `@token_required(['admin', 'usuario'])` |
| `@admin_required` | Solo administradores | `@admin_required` |
| `@user_required` | Solo usuarios | `@user_required` |
| `@any_role_required('rol1', 'rol2')` | Cualquiera de los roles | `@any_role_required('admin', 'usuario')` |

### Funciones Helper

| Función | Descripción | Retorno |
|---------|-------------|---------|
| `get_current_user()` | Usuario autenticado | `Dict` o `None` |
| `get_current_session()` | Sesión actual | `Dict` o `None` |
| `get_token_payload()` | Payload del token | `Dict` o `None` |
| `has_role('rol')` | Verifica rol específico | `bool` |
| `has_any_role('rol1', 'rol2')` | Verifica múltiples roles | `bool` |

## Flujo de Validación

### 1. Extracción del Token
```python
# Header: Authorization: Bearer <token>
auth_header = request.headers.get('Authorization')
token = auth_header.split()[1]  # Extrae el token
```

### 2. Validación JWT
```python
# Usa AuthService para validar
payload = auth_service.verificar_token_jwt(token)
if not payload:
    return error_response("Token inválido", 401)
```

### 3. Verificación de Sesión
```python
# Consulta SesionAuth
sesion = SesionAuth.query.filter_by(
    id_usuario=payload['user_id'],
    estado=True
).filter(
    SesionAuth.fecha_expiracion > datetime.utcnow()
).first()
```

### 4. Obtención de Usuario
```python
# Obtiene usuario completo con roles
usuario = Usuario.query.filter_by(
    id_usuario=payload['user_id'],
    estado=True
).first()
```

### 5. Verificación de Roles
```python
# Si se especificaron roles requeridos
if required_roles:
    user_roles = [rol.nombre_rol for rol in usuario.roles]
    if not any(role in user_roles for role in required_roles):
        return error_response("Permisos insuficientes", 403)
```

### 6. Inyección de Datos
```python
# Inyecta en contexto global
g.current_user = usuario_data
g.current_session = sesion_data
g.token_payload = payload
```

## Manejo de Errores

### Respuestas de Error

```json
{
    "success": false,
    "error": "Token de autorización requerido",
    "status_code": 401
}
```

### Códigos de Estado

| Código | Descripción | Causa |
|--------|-------------|-------|
| 401 | No autorizado | Token faltante, inválido o expirado |
| 403 | Prohibido | Permisos insuficientes |
| 500 | Error interno | Error del servidor |

### Tipos de Errores

- **Token faltante**: No se incluye header Authorization
- **Token malformado**: Formato incorrecto del header
- **Token inválido**: Token corrupto o mal firmado
- **Token expirado**: Token fuera de fecha
- **Sesión inactiva**: Sesión no encontrada o expirada
- **Usuario inactivo**: Usuario con estado=False
- **Permisos insuficientes**: Usuario sin roles requeridos

## Integración con Frontend

### Headers Requeridos

```javascript
// Incluir token en todas las peticiones protegidas
const token = localStorage.getItem('auth_token');

fetch('/api/protected-endpoint', {
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
```

### Manejo de Respuestas

```javascript
// Procesar respuesta de error
const response = await fetch('/api/protected-endpoint');
const data = await response.json();

if (!data.success) {
    if (data.status_code === 401) {
        // Token inválido, redirigir a login
        window.location.href = '/login';
    } else if (data.status_code === 403) {
        // Sin permisos, mostrar error
        alert('No tienes permisos para acceder a esta función');
    }
}
```

## Logging y Auditoría

### Eventos Registrados

- ✅ **Autenticación exitosa**: Usuario y roles
- ❌ **Token faltante**: IP y User Agent
- ❌ **Token inválido**: Detalles del error
- ❌ **Sesión inactiva**: ID de usuario
- ❌ **Permisos insuficientes**: Usuario y roles requeridos

### Información de Auditoría

```python
# Datos capturados automáticamente
{
    'ip_origen': request.remote_addr,
    'user_agent': request.headers.get('User-Agent'),
    'endpoint': request.endpoint,
    'method': request.method,
    'timestamp': datetime.utcnow()
}
```

## Mejores Prácticas

### 1. Uso de Decoradores

```python
# ✅ Bueno: Decorador específico
@admin_required
def admin_function():
    pass

# ✅ Bueno: Roles específicos
@token_required(['deportista', 'acudiente'])
def sports_function():
    pass

# ❌ Evitar: Roles muy amplios
@token_required(['admin', 'usuario', 'deportista', 'acudiente'])
def too_broad():
    pass
```

### 2. Verificación de Permisos

```python
# ✅ Bueno: Verificar permisos específicos
@app.route('/admin/users')
@admin_required
def manage_users():
    if not has_role('admin'):
        return jsonify({'error': 'Admin required'}), 403
    # ...

# ✅ Mejor: Usar decorador directamente
@app.route('/admin/users')
@admin_required
def manage_users():
    # Ya validado por el decorador
    # ...
```

### 3. Manejo de Errores

```python
# ✅ Bueno: Manejar errores específicos
@app.errorhandler(401)
def handle_unauthorized(error):
    return jsonify({
        'error': 'Authentication required',
        'redirect': '/login'
    }), 401
```

## Dependencias

- `Flask` - Framework web
- `PyJWT` - Manejo de tokens JWT
- `SQLAlchemy` - Consultas a base de datos
- `AuthService` - Servicio de autenticación
- `Logger` - Sistema de logging

## Archivos Relacionados

- `src/middleware/auth_decorator.py` - Decorador principal
- `src/middleware/ejemplo_auth_decorator.py` - Ejemplos de uso
- `src/services/Auth/auth_service.py` - Servicio de autenticación
- `src/models/eventos/sesionAuth.py` - Modelo de sesiones
- `src/models/usuarios/usuario.py` - Modelo de usuarios

## Próximos Pasos Sugeridos

1. **Middleware de Rate Limiting**: Limitar peticiones por usuario
2. **Refresh Tokens**: Renovación automática de tokens
3. **Auditoría Avanzada**: Logs detallados de acceso
4. **Caché de Sesiones**: Optimizar consultas a base de datos
5. **Tests Unitarios**: Cobertura completa del decorador
