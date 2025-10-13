# UsuarioService - Servicio de Gestión de Usuarios

## Descripción

El `UsuarioService` es un servicio que encapsula toda la lógica de negocio relacionada con el registro y gestión de usuarios en el sistema Puerta Orion. Sigue los principios SOLID, especialmente el **Principio de Responsabilidad Única (SRP)**.

## Características Principales

### ✅ Funcionalidades Implementadas

1. **Registro Completo de Usuario**
   - Registra una persona en la tabla `Persona`
   - Crea un usuario asociado en la tabla `Usuario`
   - **Asigna automáticamente el rol 'usuario' por defecto**
   - **Crea el rol 'usuario' si no existe**
   - Aplica hashing seguro de contraseñas con Werkzeug
   - Maneja transacciones atómicas

2. **Validaciones Robustas**
   - Validación de campos requeridos
   - Validación de formato de email
   - Validación de longitud de campos
   - Validación de unicidad (documento, email, username)

3. **Seguridad**
   - Hashing de contraseñas con `generate_password_hash`
   - Verificación de credenciales con `check_password_hash`
   - No exposición de contraseñas en respuestas

4. **Manejo de Errores**
   - Excepción personalizada `UsuarioServiceError`
   - Logging detallado de operaciones
   - Rollback automático en caso de errores

## Estructura del Servicio

```python
class UsuarioService:
    def registrar_usuario_completo(datos_persona, datos_usuario)
    def verificar_credenciales(usuario, password)
    def obtener_usuario_por_id(id_usuario)
    def obtener_usuario_con_roles(id_usuario)
    
    # Métodos privados
    def _validar_datos_persona(datos)
    def _validar_datos_usuario(datos)
    def _validar_unicidad(datos_persona, datos_usuario)
    def _crear_persona_y_usuario(datos_persona, datos_usuario)
    def _asignar_rol_por_defecto(id_usuario)
    def _obtener_o_crear_rol_usuario()
    def _serializar_usuario(usuario)
```

## Uso Básico

### 1. Registrar un Nuevo Usuario

```python
from src.services.usuario_service import usuario_service

# Datos de la persona
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

# Datos del usuario
datos_usuario = {
    'usuario': 'juan.perez',
    'password': 'mi_contraseña_segura'
}

# Registrar usuario
try:
    usuario_creado = usuario_service.registrar_usuario_completo(
        datos_persona, 
        datos_usuario
    )
    print(f"Usuario creado: {usuario_creado['usuario']}")
except UsuarioServiceError as e:
    print(f"Error: {e}")
```

### 2. Verificar Credenciales

```python
usuario_obj = usuario_service.verificar_credenciales(
    'juan.perez', 
    'mi_contraseña_segura'
)

if usuario_obj:
    print("Credenciales válidas")
else:
    print("Credenciales inválidas")
```

### 3. Obtener Usuario por ID

```python
usuario = usuario_service.obtener_usuario_por_id(1)
if usuario:
    print(f"Usuario encontrado: {usuario.usuario}")
```

### 4. Obtener Usuario con Roles

```python
usuario_con_roles = usuario_service.obtener_usuario_con_roles(1)
if usuario_con_roles:
    print(f"Usuario: {usuario_con_roles['usuario']}")
    print(f"Roles: {[rol['nombre_rol'] for rol in usuario_con_roles['roles']]}")
```

## Validaciones Implementadas

### Campos Requeridos para Persona
- `primer_nombre` (máx. 50 caracteres)
- `primer_apellido` (máx. 50 caracteres)
- `documento` (único)
- `correo_electronico` (único, formato válido)
- `direccion` (máx. 50 caracteres)
- `telefono`
- `id_tipo_documento`
- `id_sexo`

### Campos Requeridos para Usuario
- `usuario` (único, mín. 3, máx. 200 caracteres)
- `password` (mín. 6 caracteres)

### Validaciones de Unicidad
- **Documento**: No puede existir otra persona con el mismo documento
- **Email**: No puede existir otra persona con el mismo email
- **Username**: No puede existir otro usuario con el mismo nombre

## Manejo de Errores

El servicio utiliza una excepción personalizada `UsuarioServiceError` para errores de validación:

```python
try:
    usuario_service.registrar_usuario_completo(datos_persona, datos_usuario)
except UsuarioServiceError as e:
    # Error de validación o duplicación
    print(f"Error de validación: {e}")
except Exception as e:
    # Error interno del servidor
    print(f"Error interno: {e}")
```

## Respuesta del Servicio

El servicio retorna un diccionario con la información del usuario creado (sin exponer la contraseña):

```python
{
    'id_usuario': 1,
    'id_persona': 1,
    'usuario': 'juan.perez',
    'estado': True,
    'roles': [
        {
            'id_rol': 1,
            'nombre_rol': 'usuario',
            'descripcion': 'Rol por defecto para usuarios del sistema'
        }
    ],
    'persona': {
        'nombre_completo': 'Juan Pérez',
        'correo_electronico': 'juan@email.com',
        'documento': 12345678,
        'telefono': 3001234567
    },
    'fecha_creacion': '2024-01-15T10:30:00'
}
```

## Logging

El servicio registra todas las operaciones importantes:

- ✅ Registro exitoso de usuarios
- ✅ Asignación automática de roles
- ✅ Creación automática de rol 'usuario'
- ❌ Errores de validación
- ❌ Errores de duplicación
- ❌ Errores internos

## Principios Aplicados

### SRP (Single Responsibility Principle)
- El servicio tiene una única responsabilidad: gestionar usuarios
- Cada método tiene una función específica y bien definida

### KISS (Keep It Simple, Stupid)
- Código simple y fácil de entender
- Métodos pequeños y enfocados
- Validaciones claras y directas

### DRY (Don't Repeat Yourself)
- Validaciones reutilizables
- Métodos privados para lógica común
- Serialización centralizada

### SOLID
- **S**: Responsabilidad única
- **O**: Extensible para nuevas funcionalidades
- **L**: Comportamiento predecible
- **I**: Interfaz específica para usuarios
- **D**: Depende de abstracciones (SQLAlchemy)

## Gestión Automática de Roles

### ✅ Funcionalidades de Roles

1. **Asignación Automática**
   - Cada usuario nuevo recibe automáticamente el rol 'usuario'
   - La asignación se realiza dentro de la misma transacción

2. **Creación Automática del Rol**
   - Si el rol 'usuario' no existe, se crea automáticamente
   - Descripción: "Rol por defecto para usuarios del sistema"

3. **Transaccionalidad**
   - Si falla la asignación del rol, se hace rollback completo
   - Garantiza consistencia de datos

### Flujo de Asignación de Roles

```python
# 1. Crear persona
persona = self._crear_persona(datos_persona)

# 2. Crear usuario
usuario = self._crear_usuario(persona.id_persona, datos_usuario)

# 3. Asignar rol por defecto
self._asignar_rol_por_defecto(usuario.id_usuario)

# 4. Commit de toda la transacción
db.session.commit()
```

### Estructura de Roles en Respuesta

```python
'roles': [
    {
        'id_rol': 1,
        'nombre_rol': 'usuario',
        'descripcion': 'Rol por defecto para usuarios del sistema'
    }
]
```

## Dependencias

- `Werkzeug` - Para hashing de contraseñas
- `SQLAlchemy` - Para operaciones de base de datos
- `Flask` - Para el contexto de la aplicación
- `Rol` - Modelo de roles del sistema
- `UsuarioRol` - Modelo de asociación usuario-rol

## Archivos Relacionados

- `src/services/usuario_service.py` - Servicio principal
- `src/services/ejemplo_usuario_service.py` - Ejemplos de uso
- `src/models/personas/persona.py` - Modelo Persona
- `src/models/usuarios/usuario.py` - Modelo Usuario
- `src/utils/logger.py` - Sistema de logging
