"""
Tests para utilidades de validación.

Este módulo contiene tests que verifican las funciones
de validación de datos de entrada.
"""

import pytest
from unittest.mock import patch
from src.utils.validations import (
    normalize_spaces,
    normalize_upper,
    validate_name,
    validate_document,
    validate_phone,
    validate_email,
    sanitize_address,
    sanitize_free_text,
    ValidationError
)


@pytest.mark.unit
class TestNormalizeSpaces:
    """Tests para normalize_spaces."""
    
    def test_normalize_spaces_basic(self):
        """Test: Normalizar espacios básico."""
        result = normalize_spaces("  test  ")
        assert result == "test"
    
    def test_normalize_spaces_multiple(self):
        """Test: Normalizar múltiples espacios."""
        result = normalize_spaces("test    with    spaces")
        assert result == "test with spaces"
    
    def test_normalize_spaces_empty(self):
        """Test: Normalizar string vacío."""
        result = normalize_spaces("")
        assert result == ""
    
    def test_normalize_spaces_none(self):
        """Test: Normalizar None."""
        result = normalize_spaces(None)
        assert result == ""


@pytest.mark.unit
class TestNormalizeUpper:
    """Tests para normalize_upper."""
    
    def test_normalize_upper_basic(self):
        """Test: Normalizar a mayúsculas básico."""
        result = normalize_upper("test")
        assert result == "TEST"
    
    def test_normalize_upper_with_spaces(self):
        """Test: Normalizar con espacios."""
        result = normalize_upper("  test  with  spaces  ")
        assert result == "TEST WITH SPACES"
    
    def test_normalize_upper_empty(self):
        """Test: Normalizar string vacío."""
        result = normalize_upper("")
        assert result == ""
    
    def test_normalize_upper_none(self):
        """Test: Normalizar None."""
        result = normalize_upper(None)
        assert result == ""


@pytest.mark.unit
class TestValidateName:
    """Tests para validate_name."""
    
    def test_validate_name_success(self):
        """Test: Validar nombre exitosamente."""
        result = validate_name("nombre", "Juan Pérez")
        assert result == "JUAN PÉREZ"
    
    def test_validate_name_required_missing(self):
        """Test: Error cuando nombre requerido está ausente."""
        with pytest.raises(ValidationError) as exc_info:
            validate_name("nombre", None, required=True)
        assert "obligatorio" in str(exc_info.value).lower()
    
    def test_validate_name_optional_missing(self):
        """Test: Retornar vacío cuando nombre opcional está ausente."""
        result = validate_name("nombre", None, required=False)
        assert result == ""
    
    def test_validate_name_max_length(self):
        """Test: Error cuando excede longitud máxima."""
        long_name = "A" * 51
        with pytest.raises(ValidationError) as exc_info:
            validate_name("nombre", long_name, max_length=50)
        assert "excede" in str(exc_info.value).lower()
    
    def test_validate_name_invalid_characters(self):
        """Test: Error con caracteres inválidos."""
        with pytest.raises(ValidationError) as exc_info:
            validate_name("nombre", "Juan123")
        assert "letras" in str(exc_info.value).lower()
    
    def test_validate_name_with_special_chars(self):
        """Test: Validar nombre con caracteres especiales permitidos."""
        result = validate_name("nombre", "María José O'Connor")
        assert "MARÍA" in result


@pytest.mark.unit
class TestValidateDocument:
    """Tests para validate_document."""
    
    def test_validate_document_success(self):
        """Test: Validar documento exitosamente."""
        result = validate_document("documento", "12345678")
        assert result == "12345678"
    
    def test_validate_document_with_spaces(self):
        """Test: Validar documento con espacios."""
        result = validate_document("documento", "12 345 678")
        assert result == "12345678"
    
    def test_validate_document_missing(self):
        """Test: Error cuando documento está ausente."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document("documento", None)
        assert "obligatorio" in str(exc_info.value).lower()
    
    def test_validate_document_too_short(self):
        """Test: Error cuando documento es muy corto."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document("documento", "12345", min_length=6)
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_document_too_long(self):
        """Test: Error cuando documento es muy largo."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document("documento", "12345678901", max_length=10)
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_document_non_digits(self):
        """Test: Error cuando documento contiene no-dígitos."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document("documento", "12345ABC")
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_document_only_letters(self):
        """Test: Error cuando documento solo contiene letras."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document("documento", "ABC")
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_document_isdigit_check(self):
        """Test: Error cuando digits no pasa isdigit() (línea 59)."""
        # Mock re.sub para retornar una cadena con longitud válida pero que no sea isdigit()
        with patch('src.utils.validations.re.sub', return_value='abc123'):
            with pytest.raises(ValidationError) as exc_info:
                validate_document("documento", "test")
            assert "dígitos" in str(exc_info.value).lower()


@pytest.mark.unit
class TestValidatePhone:
    """Tests para validate_phone."""
    
    def test_validate_phone_success(self):
        """Test: Validar teléfono exitosamente."""
        result = validate_phone("telefono", "3001234567")
        assert result == "3001234567"
    
    def test_validate_phone_with_formatting(self):
        """Test: Validar teléfono con formato."""
        result = validate_phone("telefono", "(300) 123-4567")
        assert result == "3001234567"
    
    def test_validate_phone_required_missing(self):
        """Test: Error cuando teléfono requerido está ausente."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("telefono", None, required=True)
        assert "obligatorio" in str(exc_info.value).lower()
    
    def test_validate_phone_optional_missing(self):
        """Test: Retornar vacío cuando teléfono opcional está ausente."""
        result = validate_phone("telefono", None, required=False)
        assert result == ""
    
    def test_validate_phone_wrong_length(self):
        """Test: Error cuando teléfono tiene longitud incorrecta."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("telefono", "12345", min_length=10, max_length=10)
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_phone_only_letters(self):
        """Test: Error cuando teléfono solo contiene letras."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone("telefono", "ABC", required=True)
        assert "dígitos" in str(exc_info.value).lower()
    
    def test_validate_phone_isdigit_check(self):
        """Test: Error cuando digits no pasa isdigit() (línea 78)."""
        # Mock re.sub para retornar una cadena con longitud válida pero que no sea isdigit()
        with patch('src.utils.validations.re.sub', return_value='abc1234567'):
            with pytest.raises(ValidationError) as exc_info:
                validate_phone("telefono", "test", required=True)
            assert "dígitos" in str(exc_info.value).lower()


@pytest.mark.unit
class TestValidateEmail:
    """Tests para validate_email."""
    
    def test_validate_email_success(self):
        """Test: Validar email exitosamente."""
        result = validate_email("email", "test@example.com")
        assert result == "test@example.com"
    
    def test_validate_email_lowercase(self):
        """Test: Email se convierte a minúsculas."""
        result = validate_email("email", "TEST@EXAMPLE.COM")
        assert result == "test@example.com"
    
    def test_validate_email_missing(self):
        """Test: Error cuando email está ausente."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("email", None)
        assert "obligatorio" in str(exc_info.value).lower()
    
    def test_validate_email_invalid_format(self):
        """Test: Error con formato de email inválido."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email("email", "invalid-email")
        assert "formato" in str(exc_info.value).lower()
    
    def test_validate_email_no_at(self):
        """Test: Error cuando email no tiene @."""
        with pytest.raises(ValidationError):
            validate_email("email", "invalidemail.com")


@pytest.mark.unit
class TestSanitizeAddress:
    """Tests para sanitize_address."""
    
    def test_sanitize_address_success(self):
        """Test: Sanitizar dirección exitosamente."""
        result = sanitize_address("direccion", "Calle 123 #45-67")
        assert result == "CALLE 123 #45-67"
    
    def test_sanitize_address_required_missing(self):
        """Test: Error cuando dirección requerida está ausente."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address("direccion", None, required=True)
        assert "obligatorio" in str(exc_info.value).lower()
    
    def test_sanitize_address_optional_missing(self):
        """Test: Retornar vacío cuando dirección opcional está ausente."""
        result = sanitize_address("direccion", None, required=False)
        assert result == ""
    
    def test_sanitize_address_max_length(self):
        """Test: Error cuando excede longitud máxima."""
        long_address = "A" * 121
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address("direccion", long_address, max_length=120)
        assert "excede" in str(exc_info.value).lower()
    
    def test_sanitize_address_invalid_characters(self):
        """Test: Error con caracteres inválidos."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address("direccion", "Calle 123 @#$")
        assert "inválidos" in str(exc_info.value).lower()


@pytest.mark.unit
class TestSanitizeFreeText:
    """Tests para sanitize_free_text."""
    
    def test_sanitize_free_text_success(self):
        """Test: Sanitizar texto libre exitosamente."""
        result = sanitize_free_text("texto", "Este es un texto de prueba")
        assert result == "ESTE ES UN TEXTO DE PRUEBA"
    
    def test_sanitize_free_text_empty(self):
        """Test: Retornar vacío cuando texto está ausente."""
        result = sanitize_free_text("texto", None)
        assert result == ""
    
    def test_sanitize_free_text_max_length(self):
        """Test: Error cuando excede longitud máxima."""
        long_text = "A" * 501
        with pytest.raises(ValidationError) as exc_info:
            sanitize_free_text("texto", long_text, max_length=500)
        assert "excede" in str(exc_info.value).lower()
