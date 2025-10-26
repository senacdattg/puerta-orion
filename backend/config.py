import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env si existe
if os.path.exists('.env'):
    load_dotenv()

class Config:
    """Configuración base de la aplicación Flask"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Configuración del servidor
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    FLASK_RUN_RELOAD = os.environ.get('FLASK_RUN_RELOAD', 'True').lower() == 'true'
    
    # Configuración de la base de datos
    # Intentar DATABASE_URL primero, luego construir desde variables individuales
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Construir URL desde variables individuales
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '3306')
        db_username = os.environ.get('DB_USERNAME', 'root')
        db_password = os.environ.get('DB_PASSWORD', '')
        db_name = os.environ.get('DB_NAME', 'puerta_orion')
        
        if db_password:
            database_url = f'mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}'
        else:
            database_url = f'mysql+pymysql://{db_username}@{db_host}:{db_port}/{db_name}'
    
    # Si no hay configuración de MySQL, usar SQLite como fallback
    if not database_url:
        database_url = f'sqlite:///{os.path.join(os.path.dirname(__file__), "instance", "puerta_orion.db")}'
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173,http://localhost:5174,http://localhost:4173,http://localhost:8080,http://127.0.0.1:5173,http://127.0.0.1:3000').split(',')
    CORS_METHODS = ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    CORS_SUPPORTS_CREDENTIALS = True
    
    # Configuración de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))  # 1 hora
    
    # Configuración de email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de APIs externas
    API_KEY = os.environ.get('API_KEY')
    API_URL = os.environ.get('API_URL')
    
    # Configuración de logs
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_DIR = os.environ.get('LOG_DIR', 'logs')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app/app.log')
    LOG_ERROR_FILE = os.environ.get('LOG_ERROR_FILE', 'logs/app/error.log')
    LOG_ACCESS_FILE = os.environ.get('LOG_ACCESS_FILE', 'logs/app/access.log')
    LOG_DB_FILE = os.environ.get('LOG_DB_FILE', 'logs/database/db.log')
    LOG_ARCHIVE_DIR = os.environ.get('LOG_ARCHIVE_DIR', 'logs/archive')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'


# Diccionario de configuraciones disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env_name=None):
    """
    Obtiene la configuración según el entorno especificado.
    
    Args:
        env_name (str, optional): Nombre del entorno ('development', 'production', 'testing').
                                  Si no se especifica, usa el valor de FLASK_ENV.
    
    Returns:
        class: Clase de configuración correspondiente al entorno
    """
    if not env_name:
        env_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env_name, DevelopmentConfig)


def validate_config():
    """
    Valida la configuración de la aplicación.
    
    Returns:
        tuple: (is_valid, errors) donde is_valid es True si la configuración es válida
               y errors es una lista de mensajes de error
    """
    errors = []
    
    # Validar variables de entorno críticas
    if not os.environ.get('SECRET_KEY') and os.environ.get('FLASK_ENV') == 'production':
        errors.append('SECRET_KEY no está configurada en producción')
    
    # Validar configuración de base de datos
    database_url = os.environ.get('DATABASE_URL')
    if not database_url and os.environ.get('FLASK_ENV') == 'production':
        errors.append('DATABASE_URL no está configurada en producción')
    
    # Validar configuración de JWT
    jwt_secret = os.environ.get('JWT_SECRET_KEY')
    if not jwt_secret and os.environ.get('FLASK_ENV') == 'production':
        errors.append('JWT_SECRET_KEY no está configurada en producción')
    
    return (len(errors) == 0, errors)
