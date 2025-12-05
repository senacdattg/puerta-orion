"""
Constantes para mensajes de error estandarizados.

Este módulo centraliza todos los mensajes de error utilizados en la aplicación,
siguiendo el principio DRY (Don't Repeat Yourself) y facilitando la
mantenibilidad y localización futura.
"""

from typing import Final

# ============================================================================
# ERRORES GENERALES
# ============================================================================

ERROR_INTERNO_SERVIDOR: Final[str] = 'Error interno del servidor'
ERROR_CONTENT_TYPE_JSON: Final[str] = 'El contenido debe ser JSON'
ERROR_CONTENT_TYPE_JSON_ALT: Final[str] = 'Content-Type debe ser application/json'

# ============================================================================
# ERRORES DE AUTENTICACIÓN
# ============================================================================

ERROR_USUARIO_NO_ENCONTRADO: Final[str] = 'Usuario no encontrado'
ERROR_USUARIO_NO_ENCONTRADO_CONTEXTO: Final[str] = 'Usuario no encontrado en el contexto'
ERROR_USUARIO_NO_AUTENTICADO: Final[str] = 'Usuario no autenticado'
ERROR_TOKEN_REQUERIDO: Final[str] = 'Token de autorización requerido'
ERROR_TOKEN_INVALIDO: Final[str] = 'Token inválido o expirado'

# ============================================================================
# ERRORES DE VALIDACIÓN
# ============================================================================

ERROR_DATOS_REQUERIDOS: Final[str] = 'Datos requeridos'
ERROR_DATOS_VACIOS: Final[str] = 'El cuerpo de la solicitud está vacío'
ERROR_NO_SE_ENVIARON_DATOS: Final[str] = 'No se enviaron datos'
ERROR_NO_SE_PROPORCIONARON_DATOS: Final[str] = 'No se proporcionaron datos'
ERROR_CAMPO_REQUERIDO: Final[str] = 'Campo requerido'
ERROR_NOMBRE_MINIMO_CARACTERES: Final[str] = 'El nombre debe tener al menos 3 caracteres'
ERROR_LUGAR_MINIMO_CARACTERES: Final[str] = 'El lugar debe tener al menos 3 caracteres'
ERROR_ID_INVALIDO: Final[str] = 'ID inválido'
ERROR_ID_ENTERO_POSITIVO: Final[str] = 'El ID debe ser un número entero positivo'

# ============================================================================
# ERRORES DE RECURSOS
# ============================================================================

ERROR_RECURSO_NO_ENCONTRADO: Final[str] = 'Recurso no encontrado'
ERROR_DEPORTISTA_NO_ENCONTRADO: Final[str] = 'Deportista no encontrado'
ERROR_ACUDIENTE_NO_ENCONTRADO: Final[str] = 'Acudiente no encontrado'
ERROR_PERSONA_NO_ENCONTRADA: Final[str] = 'Persona no encontrada'
ERROR_LIMITE_EXCEDIDO: Final[str] = 'Límite excedido'

# ============================================================================
# MENSAJES DE ÉXITO
# ============================================================================

MENSAJE_EXITO: Final[str] = 'Operación realizada exitosamente'
MENSAJE_CREADO: Final[str] = 'Recurso creado exitosamente'
MENSAJE_ACTUALIZADO: Final[str] = 'Recurso actualizado exitosamente'
MENSAJE_ELIMINADO: Final[str] = 'Recurso eliminado exitosamente'

