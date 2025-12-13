"""
Rutas de recuperación y restablecimiento de contraseña.

Responsabilidad:
- Exponer endpoints para solicitar recuperación de contraseña
- Validar tokens y actualizar contraseñas
- Enviar correos con enlaces de restablecimiento vía Gmail

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

import os
import smtplib
import ssl
import uuid
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, Flask, Response, jsonify, request
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

from ..models.base import db
from ..models.personas.persona import Persona
from ..models.usuarios.password_reset_token import PasswordResetToken
from ..models.usuarios.usuario import Usuario
from ..utils.logger import obtener_registrador
from ..utils.request_validators import RequestValidationError, obtener_json_requerido

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

auth_reset_bp = Blueprint('auth_reset', __name__, url_prefix='/api/auth')
logger = obtener_registrador('aplicacion')

JsonResponse = Tuple[Response, int]

# Constantes de configuración
EMAIL_ADDRESS = (
    os.environ.get('EMAIL_HOST_USER') or
    os.environ.get('MAIL_USERNAME') or
    os.environ.get('EMAIL_ADDRESS') or
    ''
)
EMAIL_PASSWORD = (
    os.environ.get('EMAIL_HOST_PASSWORD') or
    os.environ.get('MAIL_PASSWORD') or
    os.environ.get('EMAIL_PASSWORD') or
    ''
)
SMTP_SERVER = os.environ.get('EMAIL_HOST') or os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('EMAIL_PORT') or os.environ.get('MAIL_PORT', 587))
USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_ADDRESS)
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# Constantes de validación
REQUIRED_PASSWORD_LENGTH = 16
MIN_PASSWORD_LENGTH = 6
TOKEN_EXPIRY_HOURS = 1

# Constantes de mensajes
ERROR_CONTENT_TYPE_JSON = 'Content-Type debe ser application/json'
ERROR_DATOS_REQUERIDOS = 'No se proporcionaron datos'
ERROR_EMAIL_REQUERIDO = 'Correo electrónico requerido.'
ERROR_CONFIGURACION_SERVIDOR = 'Error de configuración del servidor de correo.'
ERROR_EMAIL_NO_CONFIGURADO = 'EMAIL_PASSWORD NO CONFIGURADO en .env'
ERROR_PASSWORD_LENGTH = (
    'Error de configuración: La contraseña de aplicación debe tener 16 caracteres, '
    'pero tiene {length}. Verifica que copiaste la contraseña completa desde Google.'
)
ERROR_EMAIL_NO_REGISTRADO = 'El correo electrónico no está registrado en el sistema.'
ERROR_USUARIO_NO_ENCONTRADO = 'Usuario no encontrado.'
ERROR_USUARIO_INACTIVO = 'El usuario está inactivo.'
ERROR_TOKEN_INVALIDO = 'Token inválido o no encontrado.'
ERROR_TOKEN_EXPIRADO = 'El enlace de recuperación ha expirado. Por favor, solicita uno nuevo.'
ERROR_CAMPOS_INCOMPLETOS = 'Campos incompletos. Se requiere: token, new_password, confirm_password.'
ERROR_CONTRASEÑAS_NO_COINCIDEN = 'Las contraseñas no coinciden.'
ERROR_CONTRASEÑA_CORTA = 'La contraseña debe tener al menos 6 caracteres.'
ERROR_AUTENTICACION_SMTP = (
    'Error de autenticación del servidor de correo. '
    'Verifica EMAIL_ADDRESS y EMAIL_PASSWORD en .env'
)
ERROR_DETALLE_CREDENCIALES = (
    'Las credenciales de Gmail no son válidas. '
    'Verifica que hayas configurado una \'Contraseña de aplicación\' en tu cuenta de Gmail.'
)
ERROR_ENVIAR_CORREO = 'Error al enviar el correo: {detail}'
ERROR_INTERNO_SERVIDOR = 'Error interno del servidor.'
ERROR_ENDPOINT_NO_ENCONTRADO = 'Endpoint no encontrado.'

MENSAJE_CORREO_ENVIADO = 'Correo de recuperación enviado correctamente.'
MENSAJE_CONTRASEÑA_ACTUALIZADA = 'Contraseña actualizada correctamente.'

# Constantes de plantillas de correo
ASUNTO_RESET = 'Restablecimiento de contraseña - Puerta de Orión'
PLANTILLA_CORREO = """Hola {nombre_usuario},

Has solicitado restablecer tu contraseña en Puerta de Orión. Para continuar, haz clic en el siguiente enlace:

{reset_link}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, puedes ignorar este correo de forma segura. Tu contraseña no será modificada.

Saludos,
Equipo Puerta de Orión"""


def _build_response(success: bool, status_code: int = 200, **payload: Any) -> JsonResponse:
    """Construye una respuesta JSON estándar."""
    body = {'success': success, **payload}
    return jsonify(body), status_code


def _validar_configuracion_email() -> None:
    """Valida que la configuración de email esté correcta."""
    if not EMAIL_PASSWORD:
        logger.error("[FORGOT_PASSWORD] %s", ERROR_EMAIL_NO_CONFIGURADO)
        logger.error("[FORGOT_PASSWORD] Verifica que EMAIL_HOST_PASSWORD esté configurado correctamente")
        raise RequestValidationError(ERROR_CONFIGURACION_SERVIDOR, status_code=500)

    password_clean = EMAIL_PASSWORD.replace(' ', '').strip()
    password_length = len(password_clean)

    logger.info("[FORGOT_PASSWORD] EMAIL_PASSWORD configurado: %s", '*' * min(16, password_length))
    logger.info("[FORGOT_PASSWORD] Longitud de contraseña (sin espacios): %s caracteres", password_length)

    if password_length != REQUIRED_PASSWORD_LENGTH:
        logger.error(
            "[FORGOT_PASSWORD] ERROR: La contraseña de aplicación debe tener exactamente %s caracteres (sin espacios).",
            REQUIRED_PASSWORD_LENGTH
        )
        logger.error("[FORGOT_PASSWORD] Longitud actual: %s caracteres", password_length)
        raise RequestValidationError(
            ERROR_PASSWORD_LENGTH.format(length=password_length),
            status_code=500
        )

    if not EMAIL_ADDRESS:
        logger.error("[FORGOT_PASSWORD] EMAIL_ADDRESS no configurado")
        raise RequestValidationError(ERROR_CONFIGURACION_SERVIDOR, status_code=500)


def _obtener_persona_por_email(email: str) -> Persona:
    """Obtiene una persona por su correo electrónico."""
    persona = Persona.query.filter_by(correo_electronico=email).first()
    if not persona:
        logger.warning("[FORGOT_PASSWORD] Correo no encontrado: %s", email)
        raise RequestValidationError(ERROR_EMAIL_NO_REGISTRADO, status_code=404)
    return persona


def _obtener_usuario_por_persona(persona: Persona) -> Usuario:
    """Obtiene el usuario asociado a una persona."""
    usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
    if not usuario:
        logger.warning("[FORGOT_PASSWORD] Usuario no encontrado para persona ID: %s", persona.id_persona)
        raise RequestValidationError(ERROR_USUARIO_NO_ENCONTRADO, status_code=404)
    return usuario


def _validar_usuario_activo(usuario: Usuario) -> None:
    """Valida que el usuario esté activo."""
    if not usuario.estado:
        logger.warning("[FORGOT_PASSWORD] Usuario inactivo: %s", usuario.id_usuario)
        raise RequestValidationError(ERROR_USUARIO_INACTIVO, status_code=403)


def _eliminar_tokens_previos(usuario_id: int) -> None:
    """Elimina todos los tokens de reset previos del usuario."""
    tokens_previos = PasswordResetToken.query.filter_by(id_usuario=usuario_id).all()
    for token_previo in tokens_previos:
        db.session.delete(token_previo)


def _generar_y_guardar_token(usuario_id: int) -> str:
    """Genera un nuevo token de reset y lo guarda en la base de datos."""
    token = str(uuid.uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS)

    reset_token = PasswordResetToken(
        id_usuario=usuario_id,
        token=token,
        expires_at=expires_at
    )

    db.session.add(reset_token)
    db.session.commit()

    logger.info("[FORGOT_PASSWORD] Token generado para usuario ID: %s", usuario_id)
    return token


def _extraer_email_remitente() -> str:
    """Extrae el email del remitente desde DEFAULT_FROM_EMAIL."""
    if DEFAULT_FROM_EMAIL and '@' in DEFAULT_FROM_EMAIL:
        if '<' in DEFAULT_FROM_EMAIL:
            return DEFAULT_FROM_EMAIL.split('<')[1].split('>')[0].strip()
        return DEFAULT_FROM_EMAIL
    return EMAIL_ADDRESS


def _construir_mensaje_correo(email: str, nombre_usuario: str, reset_link: str) -> MIMEMultipart:
    """Construye el mensaje de correo para el reset de contraseña."""
    msg = MIMEMultipart()
    from_email = _extraer_email_remitente()

    msg["From"] = from_email
    msg["To"] = email
    msg["Subject"] = ASUNTO_RESET
    msg.attach(MIMEText(PLANTILLA_CORREO.format(nombre_usuario=nombre_usuario, reset_link=reset_link), "plain"))

    return msg


def _enviar_correo_reset(email: str, nombre_usuario: str, reset_link: str) -> None:
    """Envía el correo de recuperación de contraseña."""
    msg = _construir_mensaje_correo(email, nombre_usuario, reset_link)

    # Create secure SSL context with TLS 1.2+ minimum
    context = ssl.create_default_context()
    # Ensure minimum TLS version is 1.2 or higher for security
    if hasattr(ssl, 'TLSVersion'):
        # Python 3.7+ supports TLSVersion enum
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    else:
        # Fallback for older Python versions: disable insecure protocols
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
    
    logger.info("[FORGOT_PASSWORD] Conectando a SMTP: %s:%s, TLS: %s", SMTP_SERVER, SMTP_PORT, USE_TLS)
    logger.info("[FORGOT_PASSWORD] Autenticando con EMAIL_ADDRESS: %s", EMAIL_ADDRESS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        if USE_TLS:
            server.starttls(context=context)
            logger.info("[FORGOT_PASSWORD] TLS iniciado correctamente")

        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        logger.info("[FORGOT_PASSWORD] Autenticación SMTP exitosa")

        server.send_message(msg)

    logger.info("[FORGOT_PASSWORD] Correo enviado exitosamente a: %s", email)


def _validar_datos_reset(data: Dict[str, Any]) -> Tuple[str, str, str]:
    """Valida los datos de reset de contraseña."""
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all([token, new_password, confirm_password]):
        raise RequestValidationError(ERROR_CAMPOS_INCOMPLETOS, status_code=400)

    if new_password != confirm_password:
        raise RequestValidationError(ERROR_CONTRASEÑAS_NO_COINCIDEN, status_code=400)

    if len(new_password) < MIN_PASSWORD_LENGTH:
        raise RequestValidationError(ERROR_CONTRASEÑA_CORTA, status_code=400)

    return token, new_password, confirm_password


def _obtener_y_validar_token(token: str) -> PasswordResetToken:
    """Obtiene y valida un token de reset."""
    reset_token = PasswordResetToken.query.filter_by(token=token).first()

    if not reset_token:
        logger.warning("[RESET_PASSWORD] Token no encontrado: %s...", token[:8])
        raise RequestValidationError(ERROR_TOKEN_INVALIDO, status_code=400)

    if reset_token.is_expired():
        logger.warning("[RESET_PASSWORD] Token expirado: %s...", token[:8])
        db.session.delete(reset_token)
        db.session.commit()
        raise RequestValidationError(ERROR_TOKEN_EXPIRADO, status_code=400)

    return reset_token


def _obtener_y_validar_usuario(reset_token: PasswordResetToken) -> Usuario:
    """Obtiene y valida el usuario asociado al token."""
    usuario = Usuario.query.get(reset_token.id_usuario)

    if not usuario:
        logger.error("[RESET_PASSWORD] Usuario no encontrado para token: %s...", reset_token.token[:8])
        db.session.delete(reset_token)
        db.session.commit()
        raise RequestValidationError(ERROR_USUARIO_NO_ENCONTRADO, status_code=404)

    if not usuario.estado:
        logger.warning("[RESET_PASSWORD] Usuario inactivo: %s", usuario.id_usuario)
        db.session.delete(reset_token)
        db.session.commit()
        raise RequestValidationError(ERROR_USUARIO_INACTIVO, status_code=403)

    return usuario


def _actualizar_password_usuario(usuario: Usuario, new_password: str, reset_token: PasswordResetToken) -> None:
    """Actualiza la contraseña del usuario y elimina el token usado."""
    usuario.password = generate_password_hash(new_password)
    db.session.delete(reset_token)
    db.session.commit()

    logger.info("[RESET_PASSWORD] Contraseña actualizada exitosamente para usuario ID: %s", usuario.id_usuario)


@auth_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password() -> JsonResponse:
    """Genera un token de recuperación y envía correo con el enlace."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        email = data.get("email")
        if not email:
            raise RequestValidationError(ERROR_EMAIL_REQUERIDO, status_code=400)

        logger.info("[FORGOT_PASSWORD] Solicitud de recuperación para: %s", email)
        logger.info("[FORGOT_PASSWORD] EMAIL_ADDRESS configurado: %s", EMAIL_ADDRESS)

        _validar_configuracion_email()

        persona = _obtener_persona_por_email(email)
        usuario = _obtener_usuario_por_persona(persona)
        _validar_usuario_activo(usuario)

        _eliminar_tokens_previos(usuario.id_usuario)
        token = _generar_y_guardar_token(usuario.id_usuario)

        reset_link = f"{FRONTEND_URL}/auth/reset-password/?token={token}"
        nombre_usuario = persona.nombre_completo or persona.primer_nombre or "Usuario"

        _enviar_correo_reset(email, nombre_usuario, reset_link)

        return _build_response(True, message=MENSAJE_CORREO_ENVIADO, status_code=200)

    except RequestValidationError as error:
        return _build_response(False, message=str(error), status_code=error.status_code)
    except smtplib.SMTPAuthenticationError as error:
        logger.error("[FORGOT_PASSWORD] Error de autenticación SMTP: %s", str(error))
        logger.error("[FORGOT_PASSWORD] EMAIL_ADDRESS usado: %s", EMAIL_ADDRESS)
        return _build_response(
            False,
            message=ERROR_AUTENTICACION_SMTP,
            error_detail=ERROR_DETALLE_CREDENCIALES,
            status_code=500,
        )
    except smtplib.SMTPException as error:
        logger.error("[FORGOT_PASSWORD] Error SMTP: %s", str(error))
        return _build_response(
            False,
            message=ERROR_ENVIAR_CORREO.format(detail=str(error)),
            status_code=500,
        )
    except Exception as error:  # pylint: disable=broad-except
        logger.error("[FORGOT_PASSWORD] Error inesperado: %s", str(error))
        db.session.rollback()
        return _build_response(False, message=ERROR_INTERNO_SERVIDOR, status_code=500)


@auth_reset_bp.route('/reset-password', methods=['POST'])
def reset_password() -> JsonResponse:
    """Valida el token y actualiza la contraseña del usuario."""
    try:
        data = obtener_json_requerido(
            request,
            mensaje_tipo=ERROR_CONTENT_TYPE_JSON,
            mensaje_vacio=ERROR_DATOS_REQUERIDOS,
        )

        token, new_password, _ = _validar_datos_reset(data)

        logger.info("[RESET_PASSWORD] Intento de restablecimiento con token: %s...", token[:8])

        reset_token = _obtener_y_validar_token(token)
        usuario = _obtener_y_validar_usuario(reset_token)
        _actualizar_password_usuario(usuario, new_password, reset_token)

        return _build_response(True, message=MENSAJE_CONTRASEÑA_ACTUALIZADA, status_code=200)

    except RequestValidationError as error:
        return _build_response(False, message=str(error), status_code=error.status_code)
    except Exception as error:  # pylint: disable=broad-except
        logger.error("[RESET_PASSWORD] Error inesperado: %s", str(error))
        db.session.rollback()
        return _build_response(False, message=ERROR_INTERNO_SERVIDOR, status_code=500)


@auth_reset_bp.errorhandler(404)
def not_found(error: Exception) -> JsonResponse:
    """Manejo de errores 404."""
    return _build_response(False, message=ERROR_ENDPOINT_NO_ENCONTRADO, status_code=404)


@auth_reset_bp.errorhandler(500)
def internal_error(error: Exception) -> JsonResponse:
    """Manejo de errores 500."""
    logger.error("Error interno en auth_reset: %s", str(error))
    return _build_response(False, message=ERROR_INTERNO_SERVIDOR, status_code=500)


def registrar_auth_reset_routes(app: Flask) -> None:
    """Registra las rutas de recuperación de contraseña en la aplicación Flask.

    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(auth_reset_bp)
    logger.info("Rutas de recuperación de contraseña registradas exitosamente")
