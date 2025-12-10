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

from typing import Iterable, Sequence

from flask import Blueprint, Flask, Response, make_response, request
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

migrate = Migrate()


def create_app(config_name: str | None = None) -> Flask:
    """
    Crea y configura la aplicación Flask según el entorno especificado.

    Args:
        config_name (str): Nombre del entorno de configuración ('development', 'production', etc.)

    Returns:
        Flask: Instancia de la aplicación Flask configurada.
    """
    selected_config = _resolve_config_name(config_name)
    app = _build_flask_app()

    _load_configuration(app, selected_config)
    _configure_cors(app)
    _register_preflight_handler(app)
    _initialize_extensions(app)
    _register_blueprints(app)
    _register_status_routes(app, selected_config)

    return app

def _resolve_config_name(config_name: str | None) -> str:
    """Obtiene el nombre de configuración a utilizar."""
    return config_name or os.environ.get('FLASK_ENV', 'development')


def _build_flask_app() -> Flask:
    """Crea la instancia base de Flask con configuración de estáticos controlada."""
    return Flask(
        __name__,
        static_folder='static',
        static_url_path='/static'
    )


def _load_configuration(app: Flask, config_name: str) -> None:
    """Carga y valida la configuración de la aplicación."""
    app.config.from_object(config[config_name])
    is_valid, errors = validate_config()
    if not is_valid:
        app.logger.warning("Configuración con problemas: %s", ", ".join(errors))


def _configure_cors(app: Flask) -> Sequence[str]:
    """Configura CORS reforzando reglas seguras."""
    configured_origins = _normalize_origins(app.config.get('CORS_ORIGINS', []))
    supports_credentials = bool(app.config.get('CORS_SUPPORTS_CREDENTIALS', False))

    if supports_credentials and (not configured_origins or '*' in configured_origins):
        supports_credentials = False
        configured_origins = [origin for origin in configured_origins if origin != '*']
        app.logger.warning(
            "CORS soportaba credenciales, pero se deshabilitó por orígenes no seguros."
        )

    if not configured_origins:
        app.logger.warning(
            "No se definieron orígenes específicos para CORS; se usará '*' sin credenciales."
        )

    CORS(
        app,
        origins=configured_origins or "*",
        methods=app.config.get('CORS_METHODS', ['GET', 'PUT', 'POST', 'DELETE', 'OPTIONS']),
        allow_headers=app.config.get('CORS_HEADERS', ['Content-Type', 'Authorization']),
        supports_credentials=supports_credentials,
    )

    effective_origins = tuple(configured_origins or ['*'])
    app.config['EFFECTIVE_CORS_ORIGINS'] = effective_origins
    app.config['EFFECTIVE_CORS_SUPPORTS_CREDENTIALS'] = supports_credentials
    return effective_origins


def _register_preflight_handler(app: Flask) -> None:
    """Registra un handler seguro para solicitudes OPTIONS."""

    @app.before_request
    def handle_preflight() -> Response | None:
        if request.method != 'OPTIONS':
            return None

        response = make_response()
        origin = request.headers.get('Origin')
        allowed_origin = _select_origin_for_response(app, origin)

        if allowed_origin:
            response.headers['Access-Control-Allow-Origin'] = allowed_origin

        allowed_methods = ', '.join(app.config.get(
            'CORS_METHODS', ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        ))
        response.headers['Access-Control-Allow-Methods'] = allowed_methods

        allowed_headers = ', '.join(app.config.get(
            'CORS_HEADERS', ['Content-Type', 'Authorization', 'X-Requested-With']
        ))
        response.headers['Access-Control-Allow-Headers'] = allowed_headers

        if app.config.get('EFFECTIVE_CORS_SUPPORTS_CREDENTIALS', False) and allowed_origin:
            response.headers['Access-Control-Allow-Credentials'] = 'true'

        response.headers['Access-Control-Max-Age'] = '3600'
        response.status_code = 200

        app.logger.info("OPTIONS preflight handled for: %s", request.path)
        return response


def _select_origin_for_response(app: Flask, request_origin: str | None) -> str | None:
    """Determina qué origin devolver en el preflight."""
    if request_origin:
        return request_origin

    effective_origins: Sequence[str] = app.config.get('EFFECTIVE_CORS_ORIGINS', ())
    if effective_origins:
        first_origin = effective_origins[0]
        if first_origin == '*':
            return '*'
        return first_origin

    return None


def _initialize_extensions(app: Flask) -> None:
    """Configura logs, base de datos y migraciones."""
    gestor_logs.inicializar_aplicacion(app)
    db.init_app(app)
    migrate.init_app(app, db)
    _initialize_scheduler(app)


def _initialize_scheduler(app: Flask) -> None:
    """Inicializa el scheduler de tareas programadas."""
    # No inicializar scheduler en modo testing
    if app.config.get('TESTING', False):
        return
    
    try:
        from src.utils.scheduler import init_scheduler
        init_scheduler(app)
        app.logger.info("Scheduler de tareas programadas inicializado")
    except ImportError as exc:
        app.logger.warning("No se pudo inicializar el scheduler: %s", str(exc))
    except Exception as exc:
        app.logger.error("Error inicializando scheduler: %s", str(exc))


def _register_blueprints(app: Flask) -> None:
    """Registra todos los blueprints de la aplicación."""
    _register_auth_blueprints(app)
    _register_domain_blueprints(app)


def _register_auth_blueprints(app: Flask) -> None:
    """Registra los blueprints relacionados con autenticación."""
    from src.routes.auth_routes import registrar_auth_routes
    from src.routes.auth_reset import registrar_auth_reset_routes

    registrar_auth_routes(app)
    registrar_auth_reset_routes(app)


def _register_domain_blueprints(app: Flask) -> None:
    """Registra los blueprints del dominio de negocio."""
    from src.routes.pagos_routes import pagos_bp
    from src.routes.catalogos_routes import catalogos_bp
    from src.routes.dynamic_data_routes import dynamic_data_bp
    from src.routes.personas_routes import personas_bp
    from src.routes.eventos_routes import eventos_bp
    from src.routes.usuarios_routes import usuarios_bp
    from src.routes.deportistas_routes import deportistas_bp
    from src.routes.galeria_routes import galeria_bp
    from src.routes.archivos_routes import archivos_bp
    from src.routes.mensualidades_routes import mensualidades_bp

    blueprint_configs: tuple[tuple[Blueprint, str | None], ...] = (
        (pagos_bp, '/api'),
        (catalogos_bp, None),
        (dynamic_data_bp, '/api'),
        (personas_bp, '/api'),
        (eventos_bp, None),  # El blueprint ya tiene url_prefix='/api/eventos'
        (usuarios_bp, None),
        (deportistas_bp, '/api/deportistas'),
        (galeria_bp, None),
        (archivos_bp, None),
        (mensualidades_bp, None),
    )

    for blueprint, prefix in blueprint_configs:
        if prefix:
            app.register_blueprint(blueprint, url_prefix=prefix)
        else:
            app.register_blueprint(blueprint)


def _register_status_routes(app: Flask, config_name: str) -> None:
    """Registra endpoints básicos de estado y configuración."""

    @app.route('/')
    def index() -> dict[str, str]:
        return {'message': 'API de Puerta Orion funcionando correctamente'}

    @app.route('/health')
    def health() -> dict[str, object]:
        database_status = 'connected' if db.engine else 'disconnected'
        return {
            'status': 'healthy',
            'environment': config_name,
            'debug': app.config.get('DEBUG', False),
            'database': database_status
        }

    @app.route('/config')
    def config_info() -> dict[str, object]:
        """Endpoint para verificar configuración (solo en desarrollo)"""
        if app.config.get('DEBUG'):
            database_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            masked_uri = database_uri.split('@')[0] + '@***' if '@' in database_uri else database_uri
            return {
                'environment': config_name,
                'debug': app.config.get('DEBUG'),
                'database_uri': masked_uri,
                'cors_origins': list(app.config.get('EFFECTIVE_CORS_ORIGINS', ())),
                'jwt_expires': str(app.config.get('JWT_ACCESS_TOKEN_EXPIRES')),
                'log_level': app.config.get('LOG_LEVEL')
            }
        return {'message': 'Configuración no disponible en producción'}


def _normalize_origins(origins: Iterable[str]) -> list[str]:
    """Normaliza la lista de orígenes eliminando vacíos y espacios."""
    return [origin.strip() for origin in origins if origin and origin.strip()]


# Instancia global de la aplicación Flask
app = create_app()


def shutdown_handler() -> None:
    """Maneja el cierre de la aplicación, deteniendo el scheduler."""
    try:
        from src.utils.scheduler import shutdown_scheduler
        shutdown_scheduler()
    except Exception:
        pass


if __name__ == '__main__':
    # Obtener configuración para el servidor
    config_obj = get_config()
    
    try:
        app.run(
            host=config_obj.HOST, port=config_obj.PORT, debug=config_obj.DEBUG
        )
    finally:
        shutdown_handler()
