// Configuración del entorno de la aplicación
// Siguiendo el principio SRP - este archivo solo maneja configuración del entorno

const LOCAL_API_FALLBACK = 'http://localhost:5000';

const ENV_CONFIG = {
  development: {
    apiUrl: LOCAL_API_FALLBACK,
    debug: true,
    logLevel: 'debug'
  },
  production: {
    apiUrl: 'https://api.puertadeorion.com',
    debug: false,
    logLevel: 'error'
  },
  test: {
    apiUrl: LOCAL_API_FALLBACK,
    debug: true,
    logLevel: 'debug'
  }
};

const CURRENT_ENV = import.meta.env.MODE || 'development';
const FALLBACK_CONFIG = ENV_CONFIG[CURRENT_ENV] || ENV_CONFIG.development;

const sanitizeValue = (value) => {
  if (!value) return '';
  const trimmed = String(value).trim();
  if (trimmed === '' || trimmed === 'auto' || trimmed === 'undefined' || trimmed === 'null') {
    return '';
  }
  return trimmed;
};

// Using globalThis instead of window for better cross-platform compatibility
const readRuntimeConfig = () => (typeof globalThis !== 'undefined' && globalThis.RUNTIME_CONFIG ? globalThis.RUNTIME_CONFIG : {});

const computeDefaultApiUrl = () => {
  // Using globalThis instead of window for better cross-platform compatibility
  if (typeof globalThis === 'undefined' || !globalThis.location) {
    return LOCAL_API_FALLBACK;
  }

  const hostname = globalThis.location.hostname || '';
  const protocol = globalThis.location.protocol || 'http:';
  const isLocalhost =
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname === '[::1]' ||
    hostname === '::1';

  if (isLocalhost) {
    return LOCAL_API_FALLBACK;
  }

  if (hostname) {
    return `${protocol}//${hostname}`;
  }

  return LOCAL_API_FALLBACK;
};

const resolveApiUrl = () => {
  const runtimeUrl = sanitizeValue(readRuntimeConfig().VITE_API_URL);
  if (runtimeUrl) return runtimeUrl;

  const envUrl = sanitizeValue(import.meta.env.VITE_API_URL);
  if (envUrl) return envUrl;

  const fallbackUrl = sanitizeValue(FALLBACK_CONFIG.apiUrl);
  if (fallbackUrl) return fallbackUrl;

  return computeDefaultApiUrl();
};

export const CURRENT_CONFIG = {
  ...FALLBACK_CONFIG
};

Object.defineProperty(CURRENT_CONFIG, 'apiUrl', {
  enumerable: true,
  configurable: true,
  get: resolveApiUrl
});

export const API_CONFIG = {
  get baseURL() {
    return resolveApiUrl();
  },
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

export const LOG_CONFIG = {
  level: CURRENT_CONFIG.logLevel,
  enabled: CURRENT_CONFIG.debug
};

export const APP_ENV_CONFIG = {
  isDevelopment: CURRENT_ENV === 'development',
  isProduction: CURRENT_ENV === 'production',
  isTest: CURRENT_ENV === 'test',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  buildTime: import.meta.env.VITE_APP_BUILD_TIME || new Date().toISOString()
};

const stripTrailingSlash = (value = '') => value.replace(/\/$/, '');

export const getApiUrl = (path = '') => `${stripTrailingSlash(resolveApiUrl())}${path}`;

export const getApiBaseUrl = () => getApiUrl('/api');

export const getRuntimeValue = (key, fallback = undefined) => {
  const runtimeConfig = readRuntimeConfig();

  if (key in runtimeConfig) {
    return runtimeConfig[key];
  }

  if (key in import.meta.env) {
    return import.meta.env[key];
  }

  return fallback;
};
