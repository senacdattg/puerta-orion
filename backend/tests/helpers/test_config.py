"""
Configuración para tests.

Este módulo centraliza las constantes utilizadas en los tests,
incluyendo passwords de prueba.

⚠️ NOTA: Estas passwords son SOLO para testing y NO deben usarse en producción.
Son valores conocidos y simples para facilitar las pruebas automatizadas.
"""

# Passwords de prueba (SOLO PARA TESTS)
TEST_PASSWORD = 'Test123456!'  # NOSONAR: S2068, S6418 - Test password only, never used in production
TEST_PASSWORD_INCORRECTA = 'password_incorrecta'  # NOSONAR: S2068, S6418 - Test password only, never used in production

# Usuarios de prueba
TEST_USERNAME = 'testuser'
TEST_EMAIL = 'test@example.com'

# Tokens de prueba
TEST_TOKEN = 'test_token_12345'  # NOSONAR: S2068, S6418 - Test token only, never used in production

