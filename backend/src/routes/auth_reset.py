"""
Rutas de recuperación y restablecimiento de contraseña.

Responsabilidad:
- Exponer endpoints para solicitar recuperación de contraseña
- Validar tokens y actualizar contraseñas
- Enviar correos con enlaces de restablecimiento vía Gmail

Este módulo sigue los principios SRP, KISS, DRY y SOLID.
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import smtplib
import ssl
import uuid
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from ..models.base import db
from ..models.usuarios.usuario import Usuario
from ..models.usuarios.password_reset_token import PasswordResetToken
from ..models.personas.persona import Persona
from ..utils.logger import obtener_registrador

auth_reset_bp = Blueprint('auth_reset', __name__, url_prefix='/api/auth')
logger = obtener_registrador('aplicacion')

# Configuración de Gmail desde variables de entorno
# Soporta múltiples nombres de variables para compatibilidad
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

# URL del frontend para el enlace de restablecimiento
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')


@auth_reset_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Genera un token de recuperación y envía correo con el enlace.
    
    Request Body:
        {
            "email": "usuario@example.com"
        }
    
    Returns:
        JSON: Respuesta con éxito o error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Datos no proporcionados."
            }), 400
        
        email = data.get("email")
        
        if not email:
            return jsonify({
                "success": False,
                "message": "Correo electrónico requerido."
            }), 400
        
        logger.info(f"[FORGOT_PASSWORD] Solicitud de recuperación para: {email}")
        logger.info(f"[FORGOT_PASSWORD] EMAIL_ADDRESS configurado: {EMAIL_ADDRESS}")
        
        # Validar que EMAIL_PASSWORD esté configurado
        if not EMAIL_PASSWORD:
            logger.error("[FORGOT_PASSWORD] EMAIL_PASSWORD NO CONFIGURADO en .env")
            logger.error("[FORGOT_PASSWORD] Verifica que EMAIL_HOST_PASSWORD esté configurado correctamente")
            return jsonify({
                "success": False,
                "message": "Error de configuración del servidor de correo."
            }), 500
        
        # Las contraseñas de aplicación de Gmail tienen 16 caracteres (pueden tener espacios)
        # Eliminar espacios para contar caracteres
        password_clean = EMAIL_PASSWORD.replace(' ', '').strip()
        password_length = len(password_clean)
        
        logger.info(f"[FORGOT_PASSWORD] EMAIL_PASSWORD configurado: {'*' * min(16, password_length)}")
        logger.info(f"[FORGOT_PASSWORD] Longitud de contraseña (sin espacios): {password_length} caracteres")
        
        if password_length != 16:
            logger.error(f"[FORGOT_PASSWORD] ERROR: La contraseña de aplicación debe tener exactamente 16 caracteres (sin espacios).")
            logger.error(f"[FORGOT_PASSWORD] Longitud actual: {password_length} caracteres")
            logger.error(f"[FORGOT_PASSWORD] Formato correcto: xxxx xxxx xxxx xxxx (4 grupos de 4 caracteres = 16 total)")
            logger.error(f"[FORGOT_PASSWORD] Tu contraseña actual parece tener {password_length} caracteres. Verifica que copiaste la contraseña completa de Gmail.")
            logger.error(f"[FORGOT_PASSWORD] Ejemplo: 'abcd efgh ijkl mnop' (16 caracteres) o 'abcdefghijklmnop' (sin espacios)")
            return jsonify({
                "success": False,
                "message": f"Error de configuración: La contraseña de aplicación debe tener 16 caracteres, pero tiene {password_length}. Verifica que copiaste la contraseña completa desde Google."
            }), 500
        
        # Buscar usuario por correo electrónico a través de la relación con Persona
        persona = Persona.query.filter_by(correo_electronico=email).first()
        
        if not persona:
            logger.warning(f"[FORGOT_PASSWORD] Correo no encontrado: {email}")
            return jsonify({
                "success": False,
                "message": "El correo electrónico no está registrado en el sistema."
            }), 404
        
        # Buscar usuario asociado a esta persona
        usuario = Usuario.query.filter_by(id_persona=persona.id_persona).first()
        
        if not usuario:
            logger.warning(f"[FORGOT_PASSWORD] Usuario no encontrado para persona ID: {persona.id_persona}")
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado."
            }), 404
        
        if not usuario.estado:
            logger.warning(f"[FORGOT_PASSWORD] Usuario inactivo: {usuario.id_usuario}")
            return jsonify({
                "success": False,
                "message": "El usuario está inactivo."
            }), 403
        
        # Eliminar tokens previos del usuario (si existen)
        tokens_previos = PasswordResetToken.query.filter_by(id_usuario=usuario.id_usuario).all()
        for token_previo in tokens_previos:
            db.session.delete(token_previo)
        
        # Generar nuevo token único
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset_token = PasswordResetToken(
            id_usuario=usuario.id_usuario,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        logger.info(f"[FORGOT_PASSWORD] Token generado para usuario ID: {usuario.id_usuario}")
        
        # Construir enlace de restablecimiento
        reset_link = f"{FRONTEND_URL}/auth/reset-password/?token={token}"
        
        # Preparar correo
        nombre_usuario = persona.nombre_completo or persona.primer_nombre or "Usuario"
        subject = "Restablecimiento de contraseña - Puerta de Orión"
        body = f"""
Hola {nombre_usuario},

Has solicitado restablecer tu contraseña en Puerta de Orión. Para continuar, haz clic en el siguiente enlace:

{reset_link}

Este enlace expirará en 1 hora.

Si no solicitaste este cambio, puedes ignorar este correo de forma segura. Tu contraseña no será modificada.

Saludos,
Equipo Puerta de Orión
"""
        
        # Enviar correo con Gmail SMTP
        try:
            if not EMAIL_ADDRESS:
                logger.error("[FORGOT_PASSWORD] EMAIL_ADDRESS no configurado")
                return jsonify({
                    "success": False,
                    "message": "Error de configuración del servidor de correo."
                }), 500
            
            msg = MIMEMultipart()
            # Usar EMAIL_ADDRESS como remitente principal si DEFAULT_FROM_EMAIL no está configurado
            # O parsear DEFAULT_FROM_EMAIL para extraer solo el correo si está en formato "Nombre <correo>"
            if DEFAULT_FROM_EMAIL and '@' in DEFAULT_FROM_EMAIL:
                # Si DEFAULT_FROM_EMAIL tiene formato "Nombre <correo>", extraer solo el correo
                if '<' in DEFAULT_FROM_EMAIL:
                    from_email = DEFAULT_FROM_EMAIL.split('<')[1].split('>')[0].strip()
                else:
                    from_email = DEFAULT_FROM_EMAIL
            else:
                from_email = EMAIL_ADDRESS
            
            msg["From"] = from_email
            msg["To"] = email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            context = ssl.create_default_context()
            logger.info(f"[FORGOT_PASSWORD] Conectando a SMTP: {SMTP_SERVER}:{SMTP_PORT}, TLS: {USE_TLS}")
            logger.info(f"[FORGOT_PASSWORD] Autenticando con EMAIL_ADDRESS: {EMAIL_ADDRESS}")
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if USE_TLS:
                    server.starttls(context=context)
                    logger.info(f"[FORGOT_PASSWORD] TLS iniciado correctamente")
                
                # Usar EMAIL_ADDRESS (no from_email) para la autenticación SMTP
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                logger.info(f"[FORGOT_PASSWORD] Autenticación SMTP exitosa")
                
                server.send_message(msg)
            
            logger.info(f"[FORGOT_PASSWORD] Correo enviado exitosamente a: {email}")
            
            return jsonify({
                "success": True,
                "message": "Correo de recuperación enviado correctamente."
            }), 200
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[FORGOT_PASSWORD] Error de autenticación SMTP: {str(e)}")
            logger.error(f"[FORGOT_PASSWORD] EMAIL_ADDRESS usado: {EMAIL_ADDRESS}")
            return jsonify({
                "success": False,
                "message": "Error de autenticación del servidor de correo. Verifica EMAIL_ADDRESS y EMAIL_PASSWORD en .env",
                "error_detail": "Las credenciales de Gmail no son válidas. Verifica que hayas configurado una 'Contraseña de aplicación' en tu cuenta de Gmail."
            }), 500
        except smtplib.SMTPException as e:
            logger.error(f"[FORGOT_PASSWORD] Error SMTP: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error al enviar el correo: {str(e)}"
            }), 500
        except Exception as e:
            logger.error(f"[FORGOT_PASSWORD] Error inesperado al enviar correo: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error al enviar el correo: {str(e)}"
            }), 500
            
    except Exception as e:
        logger.error(f"[FORGOT_PASSWORD] Error inesperado: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error interno del servidor."
        }), 500


@auth_reset_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Valida el token y actualiza la contraseña del usuario.
    
    Request Body:
        {
            "token": "uuid-del-token",
            "new_password": "nueva_contraseña",
            "confirm_password": "nueva_contraseña"
        }
    
    Returns:
        JSON: Respuesta con éxito o error
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "message": "Datos no proporcionados."
            }), 400
        
        token = data.get("token")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        
        if not all([token, new_password, confirm_password]):
            return jsonify({
                "success": False,
                "message": "Campos incompletos. Se requiere: token, new_password, confirm_password."
            }), 400
        
        if new_password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Las contraseñas no coinciden."
            }), 400
        
        if len(new_password) < 6:
            return jsonify({
                "success": False,
                "message": "La contraseña debe tener al menos 6 caracteres."
            }), 400
        
        logger.info(f"[RESET_PASSWORD] Intento de restablecimiento con token: {token[:8]}...")
        
        # Buscar token
        reset_token = PasswordResetToken.query.filter_by(token=token).first()
        
        if not reset_token:
            logger.warning(f"[RESET_PASSWORD] Token no encontrado: {token[:8]}...")
            return jsonify({
                "success": False,
                "message": "Token inválido o no encontrado."
            }), 400
        
        # Verificar expiración
        if reset_token.is_expired():
            logger.warning(f"[RESET_PASSWORD] Token expirado: {token[:8]}...")
            db.session.delete(reset_token)
            db.session.commit()
            return jsonify({
                "success": False,
                "message": "El enlace de recuperación ha expirado. Por favor, solicita uno nuevo."
            }), 400
        
        # Buscar usuario
        usuario = Usuario.query.get(reset_token.id_usuario)
        
        if not usuario:
            logger.error(f"[RESET_PASSWORD] Usuario no encontrado para token: {token[:8]}...")
            db.session.delete(reset_token)
            db.session.commit()
            return jsonify({
                "success": False,
                "message": "Usuario no encontrado."
            }), 404
        
        if not usuario.estado:
            logger.warning(f"[RESET_PASSWORD] Usuario inactivo: {usuario.id_usuario}")
            db.session.delete(reset_token)
            db.session.commit()
            return jsonify({
                "success": False,
                "message": "El usuario está inactivo."
            }), 403
        
        # Actualizar contraseña
        usuario.password = generate_password_hash(new_password)
        
        # Eliminar token usado
        db.session.delete(reset_token)
        db.session.commit()
        
        logger.info(f"[RESET_PASSWORD] Contraseña actualizada exitosamente para usuario ID: {usuario.id_usuario}")
        
        return jsonify({
            "success": True,
            "message": "Contraseña actualizada correctamente."
        }), 200
        
    except Exception as e:
        logger.error(f"[RESET_PASSWORD] Error inesperado: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Error interno del servidor."
        }), 500


@auth_reset_bp.errorhandler(404)
def not_found(error):
    """Manejo de errores 404."""
    return jsonify({
        "success": False,
        "message": "Endpoint no encontrado.",
        "status_code": 404
    }), 404


@auth_reset_bp.errorhandler(500)
def internal_error(error):
    """Manejo de errores 500."""
    logger.error(f"Error interno en auth_reset: {str(error)}")
    return jsonify({
        "success": False,
        "message": "Error interno del servidor.",
        "status_code": 500
    }), 500


def registrar_auth_reset_routes(app):
    """
    Registra las rutas de recuperación de contraseña en la aplicación Flask.
    
    Args:
        app: Instancia de la aplicación Flask
    """
    app.register_blueprint(auth_reset_bp)
    logger.info("Rutas de recuperación de contraseña registradas exitosamente")

