"""
Configuración temporal de CORS para desarrollo
"""

# Configuración de CORS para desarrollo
CORS_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173', 
    'http://localhost:4173',
    'http://127.0.0.1:5173'
]

# Configuración de la aplicación
SECRET_KEY = 'mi-clave-secreta-desarrollo'
DEBUG = True
FLASK_ENV = 'development'




