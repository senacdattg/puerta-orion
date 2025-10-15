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

from flask import Flask, request, g
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from src.models.base import db
from src.utils.logger import gestor_logs
from src.models import *
import os

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
    CORS(app, origins=app.config['CORS_ORIGINS'])

    gestor_logs.inicializar_aplicacion(app)
    
    # Configurar base de datos
    db.init_app(app)
    
    # Configurar migraciones
    migrate = Migrate(app, db)

    # Registrar blueprints de rutas
    from src.routes.auth_routes import registrar_auth_routes
    registrar_auth_routes(app)
    
    from src.routes.pagos_routes import pagos_bp
    app.register_blueprint(pagos_bp, url_prefix='/api')

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