"""
Archivo principal de arranque de la API Puerta Orion.

Responsabilidad:
- Inicializa la aplicación Flask.
- Carga la configuración adecuada según el entorno.
- Configura CORS para permitir peticiones desde orígenes definidos.
- Inicializa la base de datos y migraciones.
- Expone endpoints básicos de estado y bienvenida.
- (Preparado para registrar blueprints de rutas de la aplicación).

Este archivo sigue el principio SRP: solo se encarga de la inicialización y arranque de la app.
"""

from flask import Flask, request, make_response
from flask_migrate import Migrate
from config import config, get_config, validate_config
from src.models.base import db
from src.utils.logger import gestor_logs
from flask_cors import CORS
import os

# Configurar PyMySQL como reemplazo de MySQLdb, si está disponible
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass

def create_app(config_name=None):
    """
    Crea y configura la aplicación Flask según el entorno especificado.

    Args:
        config_name (str): Nombre del entorno de configuración ('development', 'production', etc.)

    Returns:
        Flask: Instancia de la aplicación Flask configurada.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Validar configuración (solo mostrar advertencias, no fallar)
    is_valid, errors = validate_config()
    if not is_valid:
        app.logger.warning(f"Configuración con problemas: {', '.join(errors)}")
    
    # Configurar CORS usando flask-cors con configuración desde config.py
    origins = app.config.get('CORS_ORIGINS', ['*'])
    CORS(app, 
         origins=origins,
         methods=app.config.get('CORS_METHODS', ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']),
         allow_headers=app.config.get('CORS_HEADERS', ['Content-Type', 'Authorization']),
         supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True))

    # Inicializar sistema de logs
    gestor_logs.inicializar_aplicacion(app)

    # Configurar base de datos
    db.init_app(app)

    # Configurar migraciones
    migrate = Migrate(app, db)

    # Registrar blueprints de rutas
    from src.routes.auth_routes import registrar_auth_routes
    registrar_auth_routes(app)

    from src.routes.pagos_routes import pagos_bp
    from src.routes.catalogos_routes import catalogos_bp
    from src.routes.dynamic_data_routes import dynamic_data_bp
    from src.routes.personas_routes import personas_bp
    from src.routes.eventos_routes import eventos_bp
    from src.routes.usuarios_routes import usuarios_bp
    from src.routes.deportistas_routes import deportistas_bp
    
    app.register_blueprint(pagos_bp, url_prefix='/api')
    app.register_blueprint(catalogos_bp)
    app.register_blueprint(dynamic_data_bp, url_prefix='/api')
    app.register_blueprint(personas_bp, url_prefix='/api')
    app.register_blueprint(eventos_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp)  # Ya tiene url_prefix='/api/usuarios'
    app.register_blueprint(deportistas_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {'message': 'API de Puerta Orion funcionando correctamente'}

    @app.route('/health')
    def health():
        return {
            'status': 'healthy', 
            'environment': config_name,
            'debug': app.config.get('DEBUG', False),
            'database': 'connected' if db.engine else 'disconnected'
        }

    @app.route('/config')
    def config_info():
        """Endpoint para verificar configuración (solo en desarrollo)"""
        if app.config.get('DEBUG'):
            return {
                'environment': config_name,
                'debug': app.config.get('DEBUG'),
                'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', '').split('@')[0] + '@***',  # Ocultar credenciales
                'cors_origins': app.config.get('CORS_ORIGINS'),
                'jwt_expires': str(app.config.get('JWT_ACCESS_TOKEN_EXPIRES')),
                'log_level': app.config.get('LOG_LEVEL')
            }
        return {'message': 'Configuración no disponible en producción'}

    return app

# Instancia global de la aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Obtener configuración para el servidor
    config_obj = get_config()
    
    app.run(
        host=config_obj.HOST,
        port=config_obj.PORT,
        debug=config_obj.DEBUG,
        use_reloader=config_obj.FLASK_RUN_RELOAD
    )
