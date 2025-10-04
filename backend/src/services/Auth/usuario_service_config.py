"""
Configuración para el UsuarioService.

Define constantes y configuraciones que pueden ser personalizadas
para el servicio de usuarios.
"""

# Configuración de validaciones
class UsuarioServiceConfig:
    """Configuración del servicio de usuario."""
    
    # Longitudes mínimas y máximas
    MIN_LENGTH_PASSWORD = 6
    MIN_LENGTH_USERNAME = 3
    MAX_LENGTH_USERNAME = 200
    MAX_LENGTH_PRIMER_NOMBRE = 50
    MAX_LENGTH_PRIMER_APELLIDO = 50
    MAX_LENGTH_DIRECCION = 50
    MAX_LENGTH_EMAIL = 50
    
    # Configuración de seguridad
    PASSWORD_HASH_METHOD = 'pbkdf2:sha256'
    PASSWORD_SALT_LENGTH = 16
    
    # Configuración de logging
    LOG_SUCCESSFUL_REGISTRATIONS = True
    LOG_FAILED_ATTEMPTS = True
    LOG_VALIDATION_ERRORS = True
    
    # Configuración de base de datos
    USE_TRANSACTIONS = True
    AUTO_COMMIT = False
    
    # Configuración de respuesta
    INCLUDE_PERSONA_DATA = True
    INCLUDE_CREATION_DATE = True
    EXCLUDE_PASSWORD = True
    
    # Mensajes de error personalizables
    ERROR_MESSAGES = {
        'campos_faltantes': "Campos requeridos faltantes: {campos}",
        'email_invalido': "Formato de email inválido",
        'password_corta': "La contraseña debe tener al menos {min_length} caracteres",
        'username_corto': "El nombre de usuario debe tener al menos {min_length} caracteres",
        'username_largo': "El nombre de usuario excede la longitud máxima ({max_length} caracteres)",
        'nombre_largo': "El primer nombre excede la longitud máxima ({max_length} caracteres)",
        'apellido_largo': "El primer apellido excede la longitud máxima ({max_length} caracteres)",
        'documento_duplicado': "Ya existe una persona con el documento {documento}",
        'email_duplicado': "Ya existe una persona con el email {email}",
        'username_duplicado': "Ya existe un usuario con el nombre {username}",
        'error_integridad': "Error de duplicación de datos",
        'error_creacion': "Error al crear usuario: {error}",
        'error_interno': "Error interno del servidor: {error}"
    }
    
    # Configuración de campos requeridos
    CAMPOS_PERSONA_REQUERIDOS = [
        'primer_nombre',
        'primer_apellido', 
        'documento',
        'correo_electronico',
        'direccion',
        'telefono',
        'id_tipo_documento',
        'id_sexo'
    ]
    
    CAMPOS_USUARIO_REQUERIDOS = [
        'usuario',
        'password'
    ]
    
    # Configuración de campos opcionales
    CAMPOS_PERSONA_OPCIONALES = [
        'segundo_nombre',
        'segundo_apellido'
    ]


# Instancia global de configuración
config = UsuarioServiceConfig()
