/**
 * Constantes globales del proyecto Puerta Orion
 * Centraliza todas las constantes utilizadas en la aplicación
 */

import { CURRENT_CONFIG } from '@/config/environment'

// ===== CONFIGURACIÓN DE LA APLICACIÓN =====
export const APP_CONFIG = {
  name: 'Puerta Orion',
  fullName: 'Club Deportivo Puerta de Orión',
  description: 'Club deportivo comprometido con el desarrollo integral de nuestros deportistas',
  founded: '2020',
  contact: {
    address: 'Carrera 12 # 34-56, Colombia',
    phone: '+57 300 123 4567',
    email: 'contacto@puertaorion.com'
  }
}

/**
 * Función para validar URLs seguras
 * Solo permite URLs que comiencen con http:// o https:// para prevenir XSS
 */
function validarUrlSegura(url) {
  if (!url || typeof url !== 'string') {
    return '#'
  }

  const urlTrimmed = url.trim()

  // Validación estricta: solo permitir http:// o https://
  if (!urlTrimmed.startsWith('http://') && !urlTrimmed.startsWith('https://')) {
    console.warn('URL no segura detectada:', url)
    return '#'
  }

  // Validación adicional: verificar que no contenga caracteres peligrosos
  // No usar clases de caracteres para caracteres simples
  const urlPattern = /^https?:\/\/[^\s<>"']+$/i
  if (!urlPattern.test(urlTrimmed)) {
    console.warn('URL contiene caracteres no permitidos:', url)
    return '#'
  }

  return urlTrimmed
}

// ===== ENLACES DE REDES SOCIALES =====
// URLs validadas en tiempo de compilación para prevenir XSS
const SOCIAL_LINKS_RAW = [
  {
    name: 'Facebook',
    url: 'https://facebook.com/puertaorion',
    icon: 'fab fa-facebook'
  },
  {
    name: 'Instagram',
    url: 'https://instagram.com/puertaorion',
    icon: 'fab fa-instagram'
  },
  {
    name: 'Twitter',
    url: 'https://twitter.com/puertaorion',
    icon: 'fab fa-twitter'
  },
  {
    name: 'YouTube',
    url: 'https://youtube.com/@puertaorion',
    icon: 'fab fa-youtube'
  }
]

// Exportar URLs ya validadas y sanitizadas
export const SOCIAL_LINKS = SOCIAL_LINKS_RAW.map(social => ({
  name: social.name,
  icon: social.icon,
  url: validarUrlSegura(social.url)
}))

// ===== ROLES DEL SISTEMA =====
export const ROLES = {
  SUPERADMIN: 'SuperAdmin',
  ADMINISTRADOR: 'Administrador',
  ENTRENADOR: 'Entrenador',
  DEPORTISTA: 'Deportista',
  ACUDIENTE: 'Acudiente',
  USUARIO: 'usuario'
}

// ===== PERMISOS POR ROL =====
export const PERMISSIONS = {
  [ROLES.SUPERADMIN]: [
    'manage_users',
    'manage_roles',
    'manage_system',
    'view_reports',
    'manage_payments'
  ],
  [ROLES.ADMINISTRADOR]: [
    'manage_users',
    'view_reports',
    'manage_payments',
    'manage_events'
  ],
  [ROLES.ENTRENADOR]: [
    'manage_athletes',
    'view_reports',
    'manage_events',
    'view_payments'
  ],
  [ROLES.DEPORTISTA]: [
    'view_profile',
    'update_profile',
    'view_events',
    'view_payments',
    'assign_guardian'
  ],
  [ROLES.ACUDIENTE]: [
    'view_profile',
    'update_profile',
    'manage_athletes',
    'view_payments',
    'view_events'
  ],
  [ROLES.USUARIO]: [
    'view_profile',
    'complete_registration'
  ]
}

// ===== RUTAS POR ROL =====
export const ROUTES_BY_ROLE = {
  [ROLES.SUPERADMIN]: ['/admin-manager', '/home'],
  [ROLES.ADMINISTRADOR]: ['/admin-manager', '/home'],
  [ROLES.ENTRENADOR]: ['/home', '/deportistas', '/mensualidades'],
  [ROLES.DEPORTISTA]: ['/home', '/perfil', '/eventos', '/mensualidades'],
  [ROLES.ACUDIENTE]: ['/home', '/perfil', '/acudiente/ver-acudidos', '/eventos'],
  [ROLES.USUARIO]: ['/home', '/completar-perfil']
}

// ===== CONFIGURACIÓN DE API =====
export const API_CONFIG = {
  BASE_URL: CURRENT_CONFIG.apiUrl,
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// ===== ENDPOINTS DE API =====
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    REFRESH: '/api/auth/refresh',
    PROFILE: '/api/auth/profile'
  },
  USERS: {
    BASE: '/api/usuarios',
    DEPORTISTAS: '/api/usuarios/deportistas',
    ACUDIENTES: '/api/usuarios/acudientes',
    ENTRENADORES: '/api/usuarios/entrenadores'
  },
  CATALOGOS: {
    BASE: '/api/catalogos',
    GENEROS: '/api/catalogos/sexos',
    TIPOS_DOCUMENTO: '/api/catalogos/tipos-documento',
    CATEGORIAS: '/api/catalogos/categorias',
    COMPLETOS: '/api/catalogos/catalogos-completos'
  },
  EVENTOS: {
    BASE: '/api/eventos',
    CALENDARIO: '/api/eventos/calendario'
  },
  PAGOS: {
    BASE: '/api/pagos',
    MENSUALIDADES: '/api/pagos/mensualidades'
  }
}

// ===== CONFIGURACIÓN DE FORMULARIOS =====
export const FORM_CONFIG = {
  VALIDATION: {
    PASSWORD_MIN_LENGTH: 6,
    USERNAME_MIN_LENGTH: 3,
    PHONE_PATTERN: /^\+?[1-9]\d{0,15}$/,
    // NOSONAR: S5852 - Using a safe and efficient email regex pattern
    EMAIL_PATTERN: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  },
  DEBOUNCE_DELAY: 300,
  AUTO_SAVE_INTERVAL: 30000
}

// ===== CONFIGURACIÓN DE NOTIFICACIONES =====
export const NOTIFICATION_CONFIG = {
  DURATION: {
    SUCCESS: 3000,
    ERROR: 5000,
    WARNING: 4000,
    INFO: 3000
  },
  POSITION: {
    TOP_RIGHT: 'top-right',
    TOP_LEFT: 'top-left',
    BOTTOM_RIGHT: 'bottom-right',
    BOTTOM_LEFT: 'bottom-left'
  }
}

// ===== CONFIGURACIÓN DE PAGINACIÓN =====
export const PAGINATION_CONFIG = {
  DEFAULT_PAGE_SIZE: 10,
  PAGE_SIZE_OPTIONS: [5, 10, 20, 50],
  MAX_PAGE_SIZE: 100
}

// ===== CONFIGURACIÓN DE ARCHIVOS =====
export const FILE_CONFIG = {
  MAX_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_TYPES: {
    IMAGES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    DOCUMENTS: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  },
  UPLOAD_PATH: '/uploads'
}

// ===== CONFIGURACIÓN DE CACHE =====
export const CACHE_CONFIG = {
  USER_DATA_TTL: 5 * 60 * 1000, // 5 minutos
  CATALOGOS_TTL: 30 * 60 * 1000, // 30 minutos
  EVENTS_TTL: 10 * 60 * 1000 // 10 minutos
}

// ===== CONFIGURACIÓN DE TEMA =====
export const THEME_CONFIG = {
  DEFAULT: 'light',
  OPTIONS: ['light', 'dark'],
  STORAGE_KEY: 'puerta-orion-theme'
}

// ===== CONFIGURACIÓN DE IDIOMA =====
export const LANGUAGE_CONFIG = {
  DEFAULT: 'es',
  OPTIONS: [
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'en', name: 'English', flag: '🇺🇸' }
  ],
  STORAGE_KEY: 'puerta-orion-language'
}

// ===== CONFIGURACIÓN DE BREAKPOINTS =====
export const BREAKPOINTS = {
  XS: 0,
  SM: 576,
  MD: 768,
  LG: 992,
  XL: 1200,
  XXL: 1400
}

// ===== CONFIGURACIÓN DE ANIMACIONES =====
export const ANIMATION_CONFIG = {
  DURATION: {
    FAST: 150,
    NORMAL: 300,
    SLOW: 500
  },
  EASING: {
    EASE: 'ease',
    EASE_IN: 'ease-in',
    EASE_OUT: 'ease-out',
    EASE_IN_OUT: 'ease-in-out'
  }
}

// ===== CONFIGURACIÓN DE LOGGING =====
export const LOG_CONFIG = {
  LEVELS: {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug'
  },
  STORAGE_KEY: 'puerta-orion-logs',
  MAX_LOGS: 100
}

// ===== MENSAJES DEL SISTEMA =====
export const MESSAGES = {
  SUCCESS: {
    LOGIN: 'Inicio de sesión exitoso',
    LOGOUT: 'Sesión cerrada correctamente',
    REGISTER: 'Registro completado exitosamente',
    UPDATE: 'Información actualizada correctamente',
    DELETE: 'Elemento eliminado correctamente',
    SAVE: 'Información guardada correctamente'
  },
  ERROR: {
    LOGIN: 'Error al iniciar sesión',
    LOGOUT: 'Error al cerrar sesión',
    REGISTER: 'Error en el registro',
    UPDATE: 'Error al actualizar información',
    DELETE: 'Error al eliminar elemento',
    SAVE: 'Error al guardar información',
    NETWORK: 'Error de conexión',
    VALIDATION: 'Error de validación',
    PERMISSION: 'No tienes permisos para realizar esta acción'
  },
  VALIDATION: {
    REQUIRED: 'Este campo es requerido',
    EMAIL: 'Email inválido',
    PASSWORD: 'Contraseña inválida', // NOSONAR: S2068 - This is an error message, not a hard-coded password
    PHONE: 'Teléfono inválido',
    MIN_LENGTH: 'Mínimo {min} caracteres',
    MAX_LENGTH: 'Máximo {max} caracteres',
    PASSWORD_MISMATCH: 'Las contraseñas no coinciden' // NOSONAR: S2068 - This is an error message, not a hard-coded password
  }
}

// ===== CONFIGURACIÓN DE DESARROLLO =====
export const DEV_CONFIG = {
  DEBUG: import.meta.env.DEV,
  MOCK_API: import.meta.env.VITE_MOCK_API === 'true',
  LOG_LEVEL: import.meta.env.VITE_LOG_LEVEL || 'info'
}
