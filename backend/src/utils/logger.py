"""
Módulo de logging centralizado para la aplicación Puerta Orion.

Responsabilidad:
- Configurar y manejar diferentes tipos de logs (aplicación, error, acceso, base_datos)
- Implementar rotación de logs para evitar archivos muy grandes
- Proporcionar métodos simples para logging en diferentes partes de la app

Este módulo sigue el principio SRP: solo se encarga del manejo de logs.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from urllib.parse import unquote

class GestorLogs:
    """Gestor centralizado de logs para la aplicación"""
    
    def __init__(self, aplicacion=None):
        self.aplicacion = aplicacion
        self.registradores = {}
        if aplicacion is not None:
            self.inicializar_aplicacion(aplicacion)
    
    def inicializar_aplicacion(self, aplicacion):
        """Inicializa el sistema de logging con la aplicación Flask"""
        self.aplicacion = aplicacion
        self._configurar_registradores()
    
    def _configurar_registradores(self):
        """Configura todos los registradores necesarios"""
        # Crear directorios si no existen
        self._asegurar_directorios_logs()
        
        # Logger principal de la aplicación
        self._configurar_logger_aplicacion()
        
        # Logger de errores
        self._configurar_logger_error()
        
        # Logger de acceso
        self._configurar_logger_acceso()
        
        # Logger de base de datos
        self._configurar_logger_base_datos()
    
    def _asegurar_directorios_logs(self):
        """Asegura que existan los directorios de logs"""
        directorios = [
            self.aplicacion.config['LOG_DIR'],
            os.path.dirname(self.aplicacion.config['LOG_FILE']),
            os.path.dirname(self.aplicacion.config['LOG_ERROR_FILE']),
            os.path.dirname(self.aplicacion.config['LOG_ACCESS_FILE']),
            os.path.dirname(self.aplicacion.config['LOG_DB_FILE']),
            self.aplicacion.config['LOG_ARCHIVE_DIR']
        ]
        
        for directorio in directorios:
            if not os.path.exists(directorio):
                os.makedirs(directorio)
    
    def _configurar_logger_aplicacion(self):
        """Configura el logger principal de la aplicación"""
        registrador = logging.getLogger('aplicacion')
        registrador.setLevel(getattr(logging, self.aplicacion.config['LOG_LEVEL']))
        
        manejador_archivo = RotatingFileHandler(
            self.aplicacion.config['LOG_FILE'],
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        
        # Handler para consola en desarrollo
        if self.aplicacion.config['DEBUG']:
            manejador_consola = logging.StreamHandler()
            manejador_consola.setLevel(logging.DEBUG)
            manejador_consola.setFormatter(self._obtener_formateador())
            registrador.addHandler(manejador_consola)
        
        manejador_archivo.setFormatter(self._obtener_formateador())
        registrador.addHandler(manejador_archivo)
        
        self.registradores['aplicacion'] = registrador
    
    def _configurar_logger_error(self):
        """Configura el logger de errores"""
        registrador = logging.getLogger('error')
        registrador.setLevel(logging.ERROR)
        
        manejador_archivo = RotatingFileHandler(
            self.aplicacion.config['LOG_ERROR_FILE'],
            maxBytes=10*1024*1024,
            backupCount=5
        )
        manejador_archivo.setFormatter(self._obtener_formateador())
        registrador.addHandler(manejador_archivo)
        
        self.registradores['error'] = registrador
    
    def _configurar_logger_acceso(self):
        """Configura el logger de acceso"""
        registrador = logging.getLogger('acceso')
        registrador.setLevel(logging.INFO)
        
        manejador_archivo = RotatingFileHandler(
            self.aplicacion.config['LOG_ACCESS_FILE'],
            maxBytes=10*1024*1024,
            backupCount=5
        )
        manejador_archivo.setFormatter(self._obtener_formateador())
        registrador.addHandler(manejador_archivo)
        
        self.registradores['acceso'] = registrador
    
    def _configurar_logger_base_datos(self):
        """Configura el logger de base de datos"""
        registrador = logging.getLogger('base_datos')
        registrador.setLevel(logging.INFO)
        
        manejador_archivo = RotatingFileHandler(
            self.aplicacion.config['LOG_DB_FILE'],
            maxBytes=10*1024*1024,
            backupCount=5
        )
        manejador_archivo.setFormatter(self._obtener_formateador())
        registrador.addHandler(manejador_archivo)
        
        self.registradores['base_datos'] = registrador
    
    def _obtener_formateador(self):
        """Retorna el formateador estándar para los logs"""
        return logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def obtener_registrador(self, nombre='aplicacion'):
        """Obtiene un logger específico"""
        return self.registradores.get(nombre, self.registradores['aplicacion'])
    
    def _obtener_url_amigable(self, ruta):
        """
        Devuelve una versión amigable de la URL para los logs.
        Por ejemplo: '/api/usuarios/123' -> '/api/usuarios/:id'
        """    
        import re
        # Reemplaza números por :id
        ruta = re.sub(r'/\d+([/?]|$)', r'/:id\1', ruta)
        # Reemplaza UUIDs por :uuid
        ruta = re.sub(r'/[0-9a-fA-F-]{36}([/?]|$)', r'/:uuid\1', ruta)
        # Decodifica caracteres especiales
        ruta = unquote(ruta)
        return ruta

    def registrar_peticion(self, peticion, respuesta=None, duracion=None):
        """Registra información de una petición HTTP con URL amigable"""
        registrador = self.obtener_registrador('acceso')
        
        ruta_amigable = self._obtener_url_amigable(peticion.path)
        datos_log = {
            'metodo': peticion.method,
            'ruta': ruta_amigable,
            'ip': peticion.remote_addr,
            'agente_usuario': peticion.headers.get('User-Agent', ''),
            'codigo_estado': respuesta.status_code if respuesta else None,
            'duracion': duracion
        }
        
        registrador.info(f"Petición: {datos_log}")
    
    def registrar_error(self, error, contexto=None):
        """Registra un error con contexto y URL amigable si está disponible"""
        registrador = self.obtener_registrador('error')
        contexto_amigable = contexto.copy() if contexto else {}
        if contexto and 'path' in contexto:
            contexto_amigable['path'] = self._obtener_url_amigable(contexto['path'])
        
        datos_error = {
            'tipo_error': type(error).__name__,
            'mensaje_error': str(error),
            'contexto': contexto_amigable
        }
        
        registrador.error(f"Error: {datos_error}")
    
    def registrar_base_datos(self, operacion, tabla=None, consulta=None, duracion=None):
        """Registra operaciones de base de datos"""
        registrador = self.obtener_registrador('base_datos')
        
        datos_bd = {
            'operacion': operacion,
            'tabla': tabla,
            'consulta': consulta,
            'duracion': duracion
        }
        
        registrador.info(f"BaseDatos: {datos_bd}")

# Instancia global del gestor de logs
gestor_logs = GestorLogs()

def obtener_registrador(nombre='aplicacion'):
    """Función helper para obtener un logger"""
    return gestor_logs.obtener_registrador(nombre)

def registrar_peticion(peticion, respuesta=None, duracion=None):
    """Función helper para loggear peticiones"""
    gestor_logs.registrar_peticion(peticion, respuesta, duracion)

def registrar_error(error, contexto=None):
    """Función helper para loggear errores"""
    gestor_logs.registrar_error(error, contexto)

def registrar_base_datos(operacion, tabla=None, consulta=None, duracion=None):
    """Función helper para loggear operaciones de BD"""
    gestor_logs.registrar_base_datos(operacion, tabla, consulta, duracion)
