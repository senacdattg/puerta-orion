"""
Utilidades para construir respuestas HTTP estandarizadas.

Este módulo proporciona funciones y clases para construir respuestas HTTP
consistentes en toda la aplicación, siguiendo principios de Clean Code,
SRP (Single Responsibility Principle) y DRY (Don't Repeat Yourself).
"""

from typing import Any, Dict, Optional, Tuple
from flask import Response, jsonify

from .error_messages import (
    ERROR_INTERNO_SERVIDOR,
    ERROR_CONTENT_TYPE_JSON,
    ERROR_USUARIO_NO_AUTENTICADO,
    ERROR_RECURSO_NO_ENCONTRADO,
)


# ============================================================================
# TIPOS
# ============================================================================

JsonResponse = Tuple[Response, int]


# ============================================================================
# CLASE BASE PARA RESPUESTAS HTTP
# ============================================================================

class HttpResponseBuilder:
    """
    Clase para construir respuestas HTTP estandarizadas.
    
    Sigue el principio SRP: una sola responsabilidad (construir respuestas).
    Implementa el patrón Builder para facilitar la construcción de respuestas.
    """
    
    @staticmethod
    def success(
        data: Optional[Any] = None,
        message: Optional[str] = None,
        status_code: int = 200,
        **kwargs: Any
    ) -> JsonResponse:
        """
        Construye una respuesta de éxito.
        
        Args:
            data: Datos a incluir en la respuesta.
            message: Mensaje de éxito opcional.
            status_code: Código de estado HTTP (default: 200).
            **kwargs: Campos adicionales para la respuesta.
            
        Returns:
            Tupla (Response, status_code).
        """
        body: Dict[str, Any] = {
            'success': True,
            'status_code': status_code,
        }
        
        if data is not None:
            body['data'] = data
        if message:
            body['message'] = message
        if kwargs:
            body.update(kwargs)
            
        return jsonify(body), status_code
    
    @staticmethod
    def error(
        error: str,
        message: Optional[str] = None,
        status_code: int = 400,
        data: Optional[Any] = None,
        **kwargs: Any
    ) -> JsonResponse:
        """
        Construye una respuesta de error.
        
        Args:
            error: Mensaje de error principal.
            message: Mensaje descriptivo adicional opcional.
            status_code: Código de estado HTTP (default: 400).
            data: Datos adicionales opcionales.
            **kwargs: Campos adicionales para la respuesta.
            
        Returns:
            Tupla (Response, status_code).
        """
        body: Dict[str, Any] = {
            'success': False,
            'error': error,
            'status_code': status_code,
        }
        
        if message:
            body['message'] = message
        if data is not None:
            body['data'] = data
        if kwargs:
            body.update(kwargs)
            
        return jsonify(body), status_code
    
    @staticmethod
    def created(
        data: Optional[Any] = None,
        message: Optional[str] = None,
        **kwargs: Any
    ) -> JsonResponse:
        """Construye una respuesta 201 (Created)."""
        return HttpResponseBuilder.success(
            data=data,
            message=message or 'Recurso creado exitosamente',
            status_code=201,
            **kwargs
        )
    
    @staticmethod
    def not_found(
        error: Optional[str] = None,
        message: Optional[str] = None
    ) -> JsonResponse:
        """Construye una respuesta 404 (Not Found)."""
        return HttpResponseBuilder.error(
            error=error or ERROR_RECURSO_NO_ENCONTRADO,
            message=message,
            status_code=404
        )
    
    @staticmethod
    def unauthorized(
        error: Optional[str] = None,
        message: Optional[str] = None
    ) -> JsonResponse:
        """Construye una respuesta 401 (Unauthorized)."""
        return HttpResponseBuilder.error(
            error=error or ERROR_USUARIO_NO_AUTENTICADO,
            message=message,
            status_code=401
        )
    
    @staticmethod
    def bad_request(
        error: str,
        message: Optional[str] = None
    ) -> JsonResponse:
        """Construye una respuesta 400 (Bad Request)."""
        return HttpResponseBuilder.error(
            error=error,
            message=message,
            status_code=400
        )
    
    @staticmethod
    def internal_server_error(
        error: Optional[str] = None,
        message: Optional[str] = None
    ) -> JsonResponse:
        """Construye una respuesta 500 (Internal Server Error)."""
        return HttpResponseBuilder.error(
            error=error or ERROR_INTERNO_SERVIDOR,
            message=message or 'Contacte al administrador',
            status_code=500
        )
    
    @staticmethod
    def json_required() -> JsonResponse:
        """Construye una respuesta 400 para contenido JSON requerido."""
        return HttpResponseBuilder.bad_request(
            error=ERROR_CONTENT_TYPE_JSON,
            message='La solicitud debe tener Content-Type: application/json'
        )


# ============================================================================
# FUNCIONES DE CONVENIENCIA (Mantienen compatibilidad con código existente)
# ============================================================================

def build_response(
    success: bool,
    status_code: int = 200,
    **payload: Any
) -> JsonResponse:
    """
    Construye una respuesta JSON estándar.
    
    Función de conveniencia que mantiene compatibilidad con código existente.
    Se recomienda usar HttpResponseBuilder para nuevo código.
    
    Args:
        success: Indica si la operación fue exitosa.
        status_code: Código de estado HTTP.
        **payload: Campos adicionales para la respuesta.
        
    Returns:
        Tupla (Response, status_code).
    """
    body: Dict[str, Any] = {'success': success, **payload}
    body.setdefault('status_code', status_code)
    return jsonify(body), status_code


def handle_exception(
    exception: Exception,
    logger: Any,
    context: str = "operación",
    custom_message: Optional[str] = None
) -> JsonResponse:
    """
    Maneja excepciones de forma estandarizada.
    
    Args:
        exception: Excepción capturada.
        logger: Logger para registrar el error.
        context: Contexto donde ocurrió el error.
        custom_message: Mensaje personalizado opcional.
        
    Returns:
        Respuesta HTTP de error 500.
    """
    error_msg = str(exception)
    logger.error(f"Error inesperado en {context}: {error_msg}")
    
    return HttpResponseBuilder.internal_server_error(
        message=custom_message
    )

