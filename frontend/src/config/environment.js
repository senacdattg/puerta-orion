// Configuración del entorno de la aplicación
// Siguiendo el principio SRP - este archivo solo maneja configuración del entorno

  const ENV_CONFIG = {
  development: {
    apiUrl: 'http://localhost:5000',
    debug: true,
    logLevel: 'debug'
  },
  production: {
    apiUrl: 'https://api.puertadeorion.com',
    debug: false,
    logLevel: 'error'
  },
  test: {
    apiUrl: 'http://localhost:5000',
    debug: true,
    logLevel: 'debug'
  }
}

const CURRENT_ENV = import.meta.env.MODE || 'development'
const FALLBACK_CONFIG = ENV_CONFIG[CURRENT_ENV] || ENV_CONFIG.development

const runtimeConfig = typeof window !== 'undefined' && window.RUNTIME_CONFIG ? window.RUNTIME_CONFIG : {}

const runtimeApiUrl = runtimeConfig.VITE_API_URL || import.meta.env.VITE_API_URL || FALLBACK_CONFIG.apiUrl

export const CURRENT_CONFIG = {
  ...FALLBACK_CONFIG,
  apiUrl: runtimeApiUrl
}

export const API_CONFIG = {
  baseURL: CURRENT_CONFIG.apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
}

export const LOG_CONFIG = {
  level: CURRENT_CONFIG.logLevel,
  enabled: CURRENT_CONFIG.debug
}

export const APP_ENV_CONFIG = {
  isDevelopment: CURRENT_ENV === 'development',
  isProduction: CURRENT_ENV === 'production',
  isTest: CURRENT_ENV === 'test',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  buildTime: import.meta.env.VITE_APP_BUILD_TIME || new Date().toISOString()
}

const stripTrailingSlash = (value = '') => value.replace(/\/$/, '')

export const getApiUrl = (path = '') => `${stripTrailingSlash(CURRENT_CONFIG.apiUrl)}${path}`

export const getApiBaseUrl = () => getApiUrl('/api')

export const getRuntimeValue = (key, fallback = undefined) => {
  if (key in runtimeConfig) {
    return runtimeConfig[key]
  }

  if (key in import.meta.env) {
    return import.meta.env[key]
  }

  return fallback
}
