// Configuración del entorno de la aplicación
// Siguiendo el principio SRP - este archivo solo maneja configuración del entorno

export const ENV_CONFIG = {
  // Entorno de desarrollo
  development: {
    apiUrl: 'http://localhost:5000',
    debug: true,
    logLevel: 'debug'
  },

  // Entorno de producción
  production: {
    apiUrl: 'https://api.puertadeorion.com',
    debug: false,
    logLevel: 'error'
  },

  // Entorno de testing
  test: {
    apiUrl: 'http://localhost:5000',
    debug: true,
    logLevel: 'debug'
  }
}

// Obtener el entorno actual
export const CURRENT_ENV = import.meta.env.MODE || 'development'

// Configuración actual basada en el entorno
export const CURRENT_CONFIG = ENV_CONFIG[CURRENT_ENV] || ENV_CONFIG.development

// Configuración de la API
export const API_CONFIG = {
  baseURL: CURRENT_CONFIG.apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}

// Configuración de logging
export const LOG_CONFIG = {
  level: CURRENT_CONFIG.logLevel,
  enabled: CURRENT_CONFIG.debug
}

// Configuración de la aplicación
export const APP_ENV_CONFIG = {
  isDevelopment: CURRENT_ENV === 'development',
  isProduction: CURRENT_ENV === 'production',
  isTest: CURRENT_ENV === 'test',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  buildTime: import.meta.env.VITE_APP_BUILD_TIME || new Date().toISOString()
}
