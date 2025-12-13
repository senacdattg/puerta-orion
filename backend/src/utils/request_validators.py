"""
Utilidades para validar y extraer información de solicitudes HTTP.

Este módulo centraliza las validaciones repetidas requeridas por varios
endpoints, manteniendo la lógica alineada con los principios DRY y SOLID.
"""

from typing import Any, Dict

from flask import Request


class RequestValidationError(ValueError):
    """Error específico para validar peticiones HTTP."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def obtener_json_requerido(
    req: Request,
    *,
    mensaje_tipo: str,
    mensaje_vacio: str,
) -> Dict[str, Any]:
    """Devuelve el cuerpo JSON validando su presencia.

    Args:
        req: Solicitud HTTP entrante.
        mensaje_tipo: Mensaje de error cuando el contenido no es JSON.
        mensaje_vacio: Mensaje de error cuando el cuerpo está vacío.

    Raises:
        RequestValidationError: Si la solicitud no es JSON o está vacía.

    Returns:
        Diccionario con los datos JSON.
    """
    if not req.is_json:
        raise RequestValidationError(mensaje_tipo, status_code=400)

    data = req.get_json()
    if not data:
        raise RequestValidationError(mensaje_vacio, status_code=400)

    return data


def validar_campo_booleano(
    data: Dict[str, Any],
    campo: str,
    *,
    mensaje_faltante: str,
    mensaje_tipo: str,
) -> bool:
    """Valida que un campo exista en el cuerpo JSON y sea booleano.

    Args:
        data: Datos JSON previamente validados.
        campo: Nombre del campo a validar.
        mensaje_faltante: Mensaje de error si el campo no existe.
        mensaje_tipo: Mensaje de error si el valor no es booleano.

    Raises:
        RequestValidationError: Si el campo no existe o no es booleano.

    Returns:
        Valor booleano del campo.
    """
    if campo not in data:
        raise RequestValidationError(mensaje_faltante, status_code=400)

    valor = data.get(campo)
    if not isinstance(valor, bool):
        raise RequestValidationError(mensaje_tipo, status_code=400)

    return valor

