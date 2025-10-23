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

from flask import Flask, request, g, make_response
from flask_migrate import Migrate
from config import config
from src.models.base import db
from src.utils.logger import gestor_logs
from src.models import *
import os

# Configurar PyMySQL como reemplazo de MySQLdb
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # Si no está instalado, intentará usar MySQLdb

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
    app.config.from_object(config[config_name])
    
    # Configuración simple de CORS
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        return response
    
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            return response

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
    app.register_blueprint(pagos_bp, url_prefix='/api')
    app.register_blueprint(catalogos_bp)  # Ya tiene url_prefix='/api/catalogos'
    app.register_blueprint(dynamic_data_bp, url_prefix='/api')
    app.register_blueprint(personas_bp, url_prefix='/api')
    app.register_blueprint(eventos_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp)  # Ya tiene url_prefix='/api/usuarios'

    @app.route('/')
    def index():
        return {'message': 'API de Puerta Orion funcionando correctamente'}
    
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'environment': config_name}
    
    return app

# Instancia global de la aplicación Flask
app = create_app()

if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )