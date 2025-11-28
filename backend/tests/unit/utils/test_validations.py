"""
Tests for validations utility module.

This module contains tests that verify data validation functions,
including name, document, phone, email, and address validation.
"""

import pytest

from src.utils.validations import (
    ValidationError,
    normalize_spaces,
    normalize_upper,
    validate_name,
    validate_document,
    validate_phone,
    validate_email,
    sanitize_address,
    sanitize_free_text
)


@pytest.mark.unit
class TestNormalizeSpaces:
    """Tests for normalize_spaces function."""
    
    def test_normalize_spaces_multiple_spaces(self):
        """Test: Normalize multiple spaces."""
        result = normalize_spaces("  test    string  ")
        
        assert result == "test string"
    
    def test_normalize_spaces_empty_string(self):
        """Test: Normalize empty string."""
        result = normalize_spaces("")
        
        assert result == ""
    
    def test_normalize_spaces_none(self):
        """Test: Normalize None value."""
        result = normalize_spaces(None)
        
        assert result == ""
    
    def test_normalize_spaces_single_word(self):
        """Test: Normalize single word."""
        result = normalize_spaces("  test  ")
        
        assert result == "test"


@pytest.mark.unit
class TestNormalizeUpper:
    """Tests for normalize_upper function."""
    
    def test_normalize_upper_basic(self):
        """Test: Basic uppercase normalization."""
        result = normalize_upper("test string")
        
        assert result == "TEST STRING"
    
    def test_normalize_upper_with_accents(self):
        """Test: Normalize with accents."""
        result = normalize_upper("José María")
        
        assert result == "JOSÉ MARÍA"
    
    def test_normalize_upper_empty_string(self):
        """Test: Normalize empty string."""
        result = normalize_upper("")
        
        assert result == ""
    
    def test_normalize_upper_none(self):
        """Test: Normalize None value."""
        result = normalize_upper(None)
        
        assert result == ""


@pytest.mark.unit
class TestValidateName:
    """Tests for validate_name function."""
    
    def test_validate_name_success(self):
        """Test: Valid name."""
        result = validate_name('first_name', 'Juan Pérez')
        
        assert result == "JUAN PÉREZ"
    
    def test_validate_name_with_apostrophe(self):
        """Test: Valid name with apostrophe."""
        result = validate_name('first_name', "O'Brien")
        
        assert result == "O'BRIEN"
    
    def test_validate_name_with_hyphen(self):
        """Test: Valid name with hyphen."""
        result = validate_name('first_name', 'María-José')
        
        assert result == "MARÍA-JOSÉ"
    
    def test_validate_name_required_missing(self):
        """Test: Required name missing."""
        with pytest.raises(ValidationError) as exc_info:
            validate_name('first_name', None)
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_validate_name_required_empty(self):
        """Test: Required name empty."""
        with pytest.raises(ValidationError) as exc_info:
            validate_name('first_name', '')
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_validate_name_optional_missing(self):
        """Test: Optional name missing."""
        result = validate_name('middle_name', None, required=False)
        
        assert result == ""
    
    def test_validate_name_exceeds_max_length(self):
        """Test: Name exceeds max length."""
        long_name = 'A' * 51
        
        with pytest.raises(ValidationError) as exc_info:
            validate_name('first_name', long_name)
        
        assert "excede la longitud máxima" in str(exc_info.value)
    
    def test_validate_name_invalid_characters(self):
        """Test: Name with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_name('first_name', 'Juan123')
        
        assert "solo debe contener letras" in str(exc_info.value)


@pytest.mark.unit
class TestValidateDocument:
    """Tests for validate_document function."""
    
    def test_validate_document_success(self):
        """Test: Valid document number."""
        result = validate_document('documento', '12345678')
        
        assert result == "12345678"
    
    def test_validate_document_with_spaces(self):
        """Test: Document with spaces."""
        result = validate_document('documento', '12 345 678')
        
        assert result == "12345678"
    
    def test_validate_document_with_dashes(self):
        """Test: Document with dashes."""
        result = validate_document('documento', '12-345-678')
        
        assert result == "12345678"
    
    def test_validate_document_missing(self):
        """Test: Document missing."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document('documento', None)
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_validate_document_too_short(self):
        """Test: Document too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document('documento', '12345')
        
        assert "entre 6 y 10 dígitos" in str(exc_info.value)
    
    def test_validate_document_too_long(self):
        """Test: Document too long."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document('documento', '12345678901')
        
        assert "entre 6 y 10 dígitos" in str(exc_info.value)
    
    def test_validate_document_invalid_characters(self):
        """Test: Document with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_document('documento', 'ABC123')
        
        assert "únicamente dígitos" in str(exc_info.value)


@pytest.mark.unit
class TestValidatePhone:
    """Tests for validate_phone function."""
    
    def test_validate_phone_success(self):
        """Test: Valid phone number."""
        result = validate_phone('telefono', '3001234567')
        
        assert result == "3001234567"
    
    def test_validate_phone_with_spaces(self):
        """Test: Phone with spaces."""
        result = validate_phone('telefono', '300 123 4567')
        
        assert result == "3001234567"
    
    def test_validate_phone_with_dashes(self):
        """Test: Phone with dashes."""
        result = validate_phone('telefono', '300-123-4567')
        
        assert result == "3001234567"
    
    def test_validate_phone_required_missing(self):
        """Test: Required phone missing."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone('telefono', None)
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_validate_phone_optional_missing(self):
        """Test: Optional phone missing."""
        result = validate_phone('telefono', None, required=False)
        
        assert result == ""
    
    def test_validate_phone_too_short(self):
        """Test: Phone too short."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone('telefono', '123456789')
        
        assert "exactamente 10 dígitos" in str(exc_info.value)
    
    def test_validate_phone_too_long(self):
        """Test: Phone too long."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone('telefono', '12345678901')
        
        assert "exactamente 10 dígitos" in str(exc_info.value)
    
    def test_validate_phone_invalid_characters(self):
        """Test: Phone with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            validate_phone('telefono', '300ABC4567')
        
        assert "únicamente dígitos" in str(exc_info.value)


@pytest.mark.unit
class TestValidateEmail:
    """Tests for validate_email function."""
    
    def test_validate_email_success(self):
        """Test: Valid email."""
        result = validate_email('correo', 'test@example.com')
        
        assert result == "test@example.com"
    
    def test_validate_email_with_spaces(self):
        """Test: Email with spaces (normalized)."""
        result = validate_email('correo', '  test@example.com  ')
        
        assert result == "test@example.com"
    
    def test_validate_email_lowercase(self):
        """Test: Email converted to lowercase."""
        result = validate_email('correo', 'TEST@EXAMPLE.COM')
        
        assert result == "test@example.com"
    
    def test_validate_email_missing(self):
        """Test: Email missing."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email('correo', None)
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_validate_email_invalid_format_no_at(self):
        """Test: Invalid email format - no @."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email('correo', 'invalidemail.com')
        
        assert "formato válido" in str(exc_info.value)
    
    def test_validate_email_invalid_format_no_domain(self):
        """Test: Invalid email format - no domain."""
        with pytest.raises(ValidationError) as exc_info:
            validate_email('correo', 'test@')
        
        assert "formato válido" in str(exc_info.value)


@pytest.mark.unit
class TestSanitizeAddress:
    """Tests for sanitize_address function."""
    
    def test_sanitize_address_success(self):
        """Test: Valid address."""
        result = sanitize_address('direccion', 'Calle 123 #45-67')
        
        assert result == "CALLE 123 #45-67"
    
    def test_sanitize_address_with_numbers(self):
        """Test: Address with numbers."""
        result = sanitize_address('direccion', 'Carrera 7 #12-34')
        
        assert result == "CARRERA 7 #12-34"
    
    def test_sanitize_address_with_dot(self):
        """Test: Address with dot."""
        result = sanitize_address('direccion', 'Av. 68 #45-30')
        
        assert result == "AV. 68 #45-30"
    
    def test_sanitize_address_required_missing(self):
        """Test: Required address missing."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address('direccion', None)
        
        assert "obligatorio" in str(exc_info.value)
    
    def test_sanitize_address_optional_missing(self):
        """Test: Optional address missing."""
        result = sanitize_address('direccion', None, required=False)
        
        assert result == ""
    
    def test_sanitize_address_exceeds_max_length(self):
        """Test: Address exceeds max length."""
        long_address = 'A' * 121
        
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address('direccion', long_address)
        
        assert "excede la longitud máxima" in str(exc_info.value)
    
    def test_sanitize_address_invalid_characters(self):
        """Test: Address with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            sanitize_address('direccion', 'Calle 123 @#$')
        
        assert "caracteres inválidos" in str(exc_info.value)


@pytest.mark.unit
class TestSanitizeFreeText:
    """Tests for sanitize_free_text function."""
    
    def test_sanitize_free_text_success(self):
        """Test: Valid free text."""
        result = sanitize_free_text('observaciones', 'Some text here')
        
        assert result == "SOME TEXT HERE"
    
    def test_sanitize_free_text_empty(self):
        """Test: Empty free text."""
        result = sanitize_free_text('observaciones', '')
        
        assert result == ""
    
    def test_sanitize_free_text_none(self):
        """Test: None free text."""
        result = sanitize_free_text('observaciones', None)
        
        assert result == ""
    
    def test_sanitize_free_text_exceeds_max_length(self):
        """Test: Free text exceeds max length."""
        long_text = 'A' * 501
        
        with pytest.raises(ValidationError) as exc_info:
            sanitize_free_text('observaciones', long_text)
        
        assert "excede la longitud máxima" in str(exc_info.value)

