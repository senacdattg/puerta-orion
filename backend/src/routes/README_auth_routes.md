# Rutas de Autenticación - API REST

## Descripción

Las rutas de autenticación exponen endpoints REST para el registro, login y gestión de usuarios en el sistema Puerta Orion. Utilizan Flask Blueprint para organización modular y se integran perfectamente con los servicios de autenticación existentes.

## Características Principales

### ✅ Endpoints Implementados

1. **POST /api/auth/register** - Registro de nuevos usuarios
2. **POST /api/auth/login** - Autenticación de usuarios
3. **GET /api/auth/perfil** - Perfil del usuario autenticado
4. **POST /api/auth/logout** - Cierre de sesión
5. **POST /api/auth/verify-token** - Verificación de tokens

### ✅ Funcionalidades

- **Registro completo** con asignación automática de rol por defecto
- **Autenticación segura** con tokens JWT
- **Protección de rutas** con decorador @token_required
- **Respuestas JSON** consistentes con códigos de estado apropiados
- **Manejo de errores** robusto y logging detallado

## Endpoints Disponibles

### 1. POST /api/auth/register

Registra un nuevo usuario en el sistema con asignación automática del rol por defecto.

#### Request Body
```json
{
    "persona": {
        "primer_nombre": "Juan",
        "primer_apellido": "Pérez",
        "documento": 12345678,
        "correo_electronico": "juan@email.com",
        "direccion": "Calle 123",
        "telefono": 3001234567,
        "id_tipo_documento": 1,
        "id_sexo": 1
    },
    "usuario": {
        "usuario": "juan.perez",
        "password": "mi_contraseña_segura"
    }
}
```

#### Response Success (201)
```json
{
    "success": true,
    "message": "Usuario registrado exitosamente",
    "data": {
        "id_usuario": 1,
        "id_persona": 1,
        "usuario": "juan.perez",
        "estado": true,
        "roles": [
            {
                "id_rol": 1,
                "nombre_rol": "usuario",
                "descripcion": "Rol por defecto para usuarios del sistema"
            }
        ],
        "persona": {
            "nombre_completo": "Juan Pérez",
            "correo_electronico": "juan@email.com",
            "documento": 12345678,
            "telefono": 3001234567
        },
        "fecha_creacion": "2024-01-15T10:30:00"
    },
    "status_code": 201
}
```

#### Response Error (400)
```json
{
    "success": false,
    "error": "Campos requeridos faltantes: documento, correo_electronico",
    "status_code": 400
}
```

### 2. POST /api/auth/login

Autentica un usuario y retorna un token JWT con datos del usuario.

#### Request Body
```json
{
    "username": "juan.perez",
    "password": "mi_contraseña_segura"
}
```

#### Response Success (200)
```json
{
    "success": true,
    "message": "Login exitoso",
    "data": {
        "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
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
        },
        "session": {
            "id_sesion": 1,
            "fecha_inicio": "2024-01-15T10:30:00",
            "fecha_expiracion": "2024-01-15T11:30:00",
            "ip_origen": "192.168.1.100"
        }
    },
    "status_code": 200
}
```

#### Response Error (401)
```json
{
    "success": false,
    "error": "Credenciales inválidas",
    "status_code": 401
}
```

### 3. GET /api/auth/perfil

Obtiene el perfil del usuario autenticado. Requiere token JWT válido.

#### Headers
```
Authorization: Bearer <token>
```

#### Response Success (200)
```json
{
    "success": true,
    "message": "Perfil obtenido exitosamente",
    "data": {
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
            "primer_nombre": "Juan",
            "primer_apellido": "Pérez",
            "correo_electronico": "juan@email.com",
            "documento": 12345678,
            "telefono": 3001234567,
            "direccion": "Calle 123"
        }
    },
    "status_code": 200
}
```

#### Response Error (401)
```json
{
    "success": false,
    "error": "Token de autorización requerido",
    "status_code": 401
}
```

### 4. POST /api/auth/logout

Cierra la sesión del usuario autenticado. Requiere token JWT válido.

#### Headers
```
Authorization: Bearer <token>
```

#### Response Success (200)
```json
{
    "success": true,
    "message": "Sesión cerrada exitosamente",
    "status_code": 200
}
```

### 5. POST /api/auth/verify-token

Verifica si un token JWT es válido.

#### Request Body
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Response Success (200)
```json
{
    "success": true,
    "message": "Token válido",
    "data": {
        "user_id": 1,
        "username": "juan.perez",
        "roles": ["usuario"],
        "expires_at": 1705400000,
        "issued_at": 1705396400
    },
    "status_code": 200
}
```

#### Response Error (401)
```json
{
    "success": false,
    "error": "Token inválido o expirado",
    "status_code": 401
}
```

## Códigos de Estado HTTP

| Código | Descripción | Uso |
|--------|-------------|-----|
| 200 | OK | Operación exitosa |
| 201 | Created | Usuario registrado exitosamente |
| 400 | Bad Request | Datos de entrada inválidos |
| 401 | Unauthorized | Token requerido o inválido |
| 403 | Forbidden | Permisos insuficientes |
| 500 | Internal Server Error | Error interno del servidor |

## Integración con la Aplicación

### 1. Registrar el Blueprint

```python
# En app.py o main.py
from src.routes.auth_routes import registrar_auth_routes

app = Flask(__name__)

# Registrar rutas de autenticación
registrar_auth_routes(app)
```

### 2. Usar en Frontend

#### Registro de Usuario
```javascript
const registrarUsuario = async (datosPersona, datosUsuario) => {
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                persona: datosPersona,
                usuario: datosUsuario
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            console.log('Usuario registrado:', data.data);
            return data.data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error en registro:', error);
        throw error;
    }
};
```

#### Login de Usuario
```javascript
const loginUsuario = async (username, password) => {
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Guardar token en localStorage
            localStorage.setItem('auth_token', data.data.token);
            localStorage.setItem('user_data', JSON.stringify(data.data.user));
            
            return data.data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error en login:', error);
        throw error;
    }
};
```

#### Obtener Perfil
```javascript
const obtenerPerfil = async () => {
    try {
        const token = localStorage.getItem('auth_token');
        
        const response = await fetch('/api/auth/perfil', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error al obtener perfil:', error);
        throw error;
    }
};
```

#### Logout
```javascript
const logoutUsuario = async () => {
    try {
        const token = localStorage.getItem('auth_token');
        
        const response = await fetch('/api/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Limpiar datos locales
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user_data');
            
            return true;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error en logout:', error);
        throw error;
    }
};
```

## Cliente Python

### Usar el Cliente AuthClient

```python
from src.routes.ejemplo_auth_routes import AuthClient

# Crear cliente
client = AuthClient()

# Registrar usuario
datos_persona = {
    'primer_nombre': 'Juan',
    'primer_apellido': 'Pérez',
    'documento': 12345678,
    'correo_electronico': 'juan@email.com',
    'direccion': 'Calle 123',
    'telefono': 3001234567,
    'id_tipo_documento': 1,
    'id_sexo': 1
}

datos_usuario = {
    'usuario': 'juan.perez',
    'password': 'mi_contraseña_segura'
}

resultado = client.registrar_usuario(datos_persona, datos_usuario)

# Hacer login
resultado = client.login('juan.perez', 'mi_contraseña_segura')

# Obtener perfil
resultado = client.obtener_perfil()

# Hacer logout
resultado = client.logout()
```

## Validaciones Implementadas

### Registro de Usuario
- **Campos requeridos**: primer_nombre, primer_apellido, documento, correo_electronico, direccion, telefono, id_tipo_documento, id_sexo, usuario, password
- **Unicidad**: documento, correo_electronico, usuario
- **Formato**: email válido, longitudes de campos
- **Contraseña**: mínimo 6 caracteres

### Login de Usuario
- **Campos requeridos**: username, password
- **Usuario activo**: solo usuarios con estado=True
- **Credenciales**: verificación con bcrypt

### Perfil de Usuario
- **Token válido**: verificación JWT
- **Sesión activa**: verificación en base de datos
- **Usuario existente**: validación de existencia

## Manejo de Errores

### Tipos de Errores
- **400 Bad Request**: Datos de entrada inválidos o faltantes
- **401 Unauthorized**: Token faltante, inválido o expirado
- **403 Forbidden**: Permisos insuficientes
- **500 Internal Server Error**: Errores internos del servidor

### Respuestas de Error Consistentes
```json
{
    "success": false,
    "error": "Descripción del error",
    "status_code": 400
}
```

## Logging y Auditoría

### Eventos Registrados
- ✅ **Registro exitoso**: Usuario y datos básicos
- ✅ **Login exitoso**: Usuario, IP y User Agent
- ✅ **Acceso a perfil**: Usuario y timestamp
- ✅ **Logout exitoso**: Usuario y timestamp
- ❌ **Errores de validación**: Detalles del error
- ❌ **Errores de autenticación**: Usuario y motivo
- ❌ **Errores de autorización**: Usuario y endpoint

### Información de Auditoría
```python
{
    'endpoint': '/api/auth/login',
    'method': 'POST',
    'ip_origen': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
    'timestamp': '2024-01-15T10:30:00',
    'user_id': 1,
    'status_code': 200
}
```

## Dependencias

- `Flask` - Framework web
- `UsuarioService` - Servicio de registro de usuarios
- `AuthService` - Servicio de autenticación
- `@token_required` - Decorador de autenticación
- `Logger` - Sistema de logging

## Archivos Relacionados

- `src/routes/auth_routes.py` - Rutas principales
- `src/routes/ejemplo_auth_routes.py` - Cliente y ejemplos
- `src/services/Auth/usuario_service.py` - Servicio de usuarios
- `src/services/Auth/auth_service.py` - Servicio de autenticación
- `src/middleware/auth_decorator.py` - Decorador de autenticación

## Próximos Pasos Sugeridos

1. **Validación de formularios**: Integrar Flask-WTF
2. **Rate limiting**: Limitar intentos de login
3. **Refresh tokens**: Renovación automática de tokens
4. **Tests unitarios**: Cobertura completa de endpoints
5. **Documentación OpenAPI**: Swagger/ReDoc
6. **Versionado de API**: Soporte para múltiples versiones
