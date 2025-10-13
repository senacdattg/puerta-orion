# AuthService - Servicio de Autenticación

## Descripción

El `AuthService` es un servicio que maneja toda la lógica de autenticación del sistema Puerta Orion. Incluye validación de credenciales, generación de tokens JWT, gestión de sesiones y verificación de tokens. Sigue los principios SOLID y las mejores prácticas de seguridad.

## Características Principales

### ✅ Funcionalidades Implementadas

1. **Autenticación de Usuarios**
   - Validación de credenciales con bcrypt/Werkzeug
   - Verificación de usuarios activos
   - Manejo seguro de contraseñas

2. **Generación de Tokens JWT**
   - Tokens con información de usuario y roles
   - Configuración de expiración desde variables de entorno
   - Algoritmo HS256 para seguridad

3. **Gestión de Sesiones**
   - Registro automático en tabla `SesionAuth`
   - Captura de IP y User Agent
   - Control de expiración de sesiones

4. **Verificación de Tokens**
   - Validación de tokens JWT
   - Manejo de tokens expirados
   - Decodificación segura de payloads

5. **Gestión de Sesiones Activas**
   - Cierre de sesiones
   - Consulta de sesiones activas por usuario
   - Invalidación de tokens

## Estructura del Servicio

```python
class AuthService:
    def autenticar_usuario(username, password, ip_origen, user_agent)
    def verificar_token_jwt(token)
    def cerrar_sesion(token)
    def obtener_sesiones_activas(id_usuario)
    
    # Métodos privados
    def _validar_datos_login(username, password)
    def _verificar_credenciales(username, password)
    def _generar_token_jwt(usuario)
    def _registrar_sesion(usuario, token_jwt, ip_origen, user_agent)
    def _preparar_respuesta_login(usuario, token_jwt, sesion)
```

## Uso Básico

### 1. Autenticar Usuario (Login)

```python
from src.services.Auth.auth_service import auth_service

# Datos de login
username = 'juan.perez'
password = 'mi_contraseña_segura'

# Realizar login
try:
    resultado = auth_service.autenticar_usuario(
        username=username,
        password=password,
        ip_origen='192.168.1.100',
        user_agent='Mozilla/5.0...'
    )
    
    print(f"Token: {resultado['token']}")
    print(f"Usuario: {resultado['user']['username']}")
    
except AuthServiceError as e:
    print(f"Error: {e}")
```

### 2. Verificar Token JWT

```python
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

payload = auth_service.verificar_token_jwt(token)
if payload:
    print(f"Usuario ID: {payload['user_id']}")
    print(f"Roles: {payload['roles']}")
else:
    print("Token inválido o expirado")
```

### 3. Cerrar Sesión

```python
token = "token_del_usuario"

if auth_service.cerrar_sesion(token):
    print("Sesión cerrada exitosamente")
else:
    print("Error al cerrar sesión")
```

### 4. Obtener Sesiones Activas

```python
sesiones = auth_service.obtener_sesiones_activas(usuario_id=1)

for sesion in sesiones:
    print(f"Sesión: {sesion['id_sesion']}")
    print(f"IP: {sesion['ip_origen']}")
    print(f"Expira: {sesion['fecha_expiracion']}")
```

## Configuración

### Variables de Entorno Requeridas

```bash
# Configuración de JWT
JWT_SECRET_KEY=tu_jwt_secret_key_muy_segura_aqui
JWT_ACCESS_TOKEN_EXPIRES=3600  # Segundos (1 hora por defecto)

# Configuración de Flask
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
```

### Configuración en config.py

```python
class Config:
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
```

## Respuesta del Login

El servicio retorna una respuesta completa con toda la información necesaria:

```json
{
    "success": true,
    "message": "Login exitoso",
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
}
```

## Payload del Token JWT

El token JWT contiene la siguiente información:

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

## Validaciones Implementadas

### Datos de Login
- **Username**: Requerido, mínimo 3 caracteres
- **Password**: Requerido, no puede estar vacío
- **Usuario activo**: Solo usuarios con estado=True pueden hacer login

### Seguridad
- **Hashing de contraseñas**: Verificación con Werkzeug
- **Tokens únicos**: Generación con secrets.token_urlsafe()
- **Expiración**: Control automático de tokens expirados
- **IP y User Agent**: Captura automática para auditoría

## Manejo de Errores

El servicio utiliza una excepción personalizada `AuthServiceError`:

```python
try:
    resultado = auth_service.autenticar_usuario(username, password)
except AuthServiceError as e:
    # Error de validación o credenciales inválidas
    print(f"Error de autenticación: {e}")
except Exception as e:
    # Error interno del servidor
    print(f"Error interno: {e}")
```

### Tipos de Errores

- **Credenciales inválidas**: Usuario o contraseña incorrectos
- **Usuario inactivo**: Usuario con estado=False
- **Datos inválidos**: Username o password vacíos
- **Token expirado**: Token JWT fuera de fecha
- **Token inválido**: Token malformado o corrupto

## Logging

El servicio registra todas las operaciones importantes:

- ✅ Login exitoso con username
- ✅ Token JWT generado
- ✅ Sesión registrada
- ❌ Credenciales inválidas
- ❌ Tokens expirados
- ❌ Errores de verificación

## Seguridad

### Medidas Implementadas

1. **Hashing Seguro**: Verificación con Werkzeug (bcrypt)
2. **Tokens JWT**: Algoritmo HS256 con clave secreta
3. **Expiración**: Tokens con tiempo de vida limitado
4. **Sesiones**: Registro en base de datos para auditoría
5. **IP Tracking**: Captura de IP de origen
6. **User Agent**: Registro del cliente utilizado

### Mejores Prácticas

- **Claves secretas**: Configuración desde variables de entorno
- **Expiración**: Tiempo de vida configurable
- **Rollback**: Transacciones atómicas en base de datos
- **Logging**: Registro detallado de operaciones
- **Validación**: Verificación exhaustiva de datos de entrada

## Dependencias

- `PyJWT` - Para generación y verificación de tokens JWT
- `Werkzeug` - Para verificación de contraseñas hasheadas
- `SQLAlchemy` - Para operaciones de base de datos
- `Flask` - Para contexto de la aplicación
- `secrets` - Para generación de tokens únicos

## Archivos Relacionados

- `src/services/Auth/auth_service.py` - Servicio principal
- `src/services/Auth/ejemplo_auth_service.py` - Ejemplos de uso
- `src/models/eventos/sesionAuth.py` - Modelo de sesiones
- `src/models/usuarios/usuario.py` - Modelo de usuarios
- `config.py` - Configuración de JWT

## Integración con Frontend

### Headers de Autorización

```javascript
// En el frontend, incluir el token en las peticiones
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
// Procesar respuesta del login
const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});

const data = await response.json();

if (data.success) {
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user_data', JSON.stringify(data.user));
} else {
    console.error('Error de login:', data.message);
}
```

## Próximos Pasos Sugeridos

1. **Middleware de Autenticación**: Crear decorador para proteger rutas
2. **Refresh Tokens**: Implementar renovación automática de tokens
3. **Rate Limiting**: Limitar intentos de login por IP
4. **2FA**: Implementar autenticación de dos factores
5. **Auditoría**: Sistema de logs de seguridad avanzado
