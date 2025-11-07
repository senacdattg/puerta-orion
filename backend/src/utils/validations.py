import re
import unicodedata
from typing import Optional


NAME_PATTERN = re.compile(r"^[A-ZÁÉÍÓÚÜÑ\s'\-]+$")
ADDRESS_PATTERN = re.compile(r"^[A-Z0-9ÁÉÍÓÚÜÑ#\-\.\s]+$")
EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)


class ValidationError(ValueError):
    """Error de validación específico para datos de negocio."""


def normalize_spaces(value: str) -> str:
    return " ".join(value.strip().split()) if value else ""


def normalize_upper(value: str) -> str:
    if not value:
        return ""

    normalized = normalize_spaces(value)
    # Mantener caracteres especiales propios del idioma
    return unicodedata.normalize("NFC", normalized.upper())


def validate_name(field: str, value: Optional[str], *, required: bool = True, max_length: int = 50) -> str:
    if not value:
        if required:
            raise ValidationError(f"El campo '{field}' es obligatorio")
        return ""

    normalized = normalize_upper(value)

    if len(normalized) > max_length:
        raise ValidationError(f"El campo '{field}' excede la longitud máxima ({max_length} caracteres)")

    if not NAME_PATTERN.match(normalized):
        raise ValidationError(
            f"El campo '{field}' solo debe contener letras, espacios, apóstrofes o guiones"
        )

    return normalized


def validate_document(field: str, value: Optional[str], *, min_length: int = 6, max_length: int = 10) -> str:
    if not value:
        raise ValidationError(f"El campo '{field}' es obligatorio")

    digits = re.sub(r"\D", "", str(value))

    if len(digits) < min_length or len(digits) > max_length:
        raise ValidationError(
            f"El campo '{field}' debe contener entre {min_length} y {max_length} dígitos"
        )

    if not digits.isdigit():
        raise ValidationError(f"El campo '{field}' debe contener únicamente dígitos")

    return digits


def validate_phone(field: str, value: Optional[str], *, min_length: int = 10, max_length: int = 10) -> str:
    if not value:
        raise ValidationError(f"El campo '{field}' es obligatorio")

    digits = re.sub(r"\D", "", str(value))

    if len(digits) < min_length or len(digits) > max_length:
        raise ValidationError(
            f"El campo '{field}' debe contener exactamente {min_length} dígitos"
        )

    if not digits.isdigit():
        raise ValidationError(f"El campo '{field}' debe contener únicamente dígitos")

    return digits


def validate_email(field: str, value: Optional[str]) -> str:
    if not value:
        raise ValidationError(f"El campo '{field}' es obligatorio")

    correo = normalize_spaces(value).lower()
    if not EMAIL_PATTERN.match(correo):
        raise ValidationError(f"El campo '{field}' no tiene un formato válido")

    return correo


def sanitize_address(field: str, value: Optional[str], *, required: bool = True, max_length: int = 120) -> str:
    if not value:
        if required:
            raise ValidationError(f"El campo '{field}' es obligatorio")
        return ""

    normalized = normalize_upper(value)

    if len(normalized) > max_length:
        raise ValidationError(f"El campo '{field}' excede la longitud máxima ({max_length} caracteres)")

    if not ADDRESS_PATTERN.match(normalized):
        raise ValidationError(
            f"El campo '{field}' contiene caracteres inválidos. Solo se permiten letras, números, espacios, '#', '-' y '.'"
        )

    return normalized


def sanitize_free_text(field: str, value: Optional[str], *, max_length: int = 500) -> str:
    if not value:
        return ""

    normalized = normalize_upper(value)

    if len(normalized) > max_length:
        raise ValidationError(f"El campo '{field}' excede la longitud máxima ({max_length} caracteres)")

    return normalized

