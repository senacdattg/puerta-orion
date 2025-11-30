/**
 * Utilidades generales para el proyecto Puerta Orion
 * Funciones auxiliares reutilizables en toda la aplicación
 */

import { ROLES, PERMISSIONS } from '@/config/constants'

// ===== UTILIDADES DE FECHA =====

/**
 * Formatea una fecha a string legible
 * @param {Date|string} date - Fecha a formatear
 * @param {string} locale - Locale para formateo
 * @returns {string} Fecha formateada
 */
export const formatDate = (date, locale = 'es-ES') => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (Number.isNaN(dateObj.getTime())) return ''

  return dateObj.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

/**
 * Formatea una fecha y hora a string legible
 * @param {Date|string} date - Fecha a formatear
 * @param {string} locale - Locale para formateo
 * @returns {string} Fecha y hora formateada
 */
export const formatDateTime = (date, locale = 'es-ES') => {
  if (!date) return ''

  const dateObj = typeof date === 'string' ? new Date(date) : date

  if (Number.isNaN(dateObj.getTime())) return ''

  return dateObj.toLocaleString(locale, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Calcula la edad basada en la fecha de nacimiento
 * @param {Date|string} birthDate - Fecha de nacimiento
 * @returns {number} Edad en años
 */
export const calculateAge = (birthDate) => {
  if (!birthDate) return 0

  const birth = typeof birthDate === 'string' ? new Date(birthDate) : birthDate
  const today = new Date()

  if (Number.isNaN(birth.getTime())) return 0

  let age = today.getFullYear() - birth.getFullYear()
  const monthDiff = today.getMonth() - birth.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--
  }

  return age
}

/**
 * Verifica si una fecha es válida
 * @param {Date|string} date - Fecha a verificar
 * @returns {boolean} True si es válida
 */
export const isValidDate = (date) => {
  if (!date) return false

  const dateObj = typeof date === 'string' ? new Date(date) : date
  return !Number.isNaN(dateObj.getTime())
}

// ===== UTILIDADES DE STRING =====

/**
 * Capitaliza la primera letra de un string
 * @param {string} str - String a capitalizar
 * @returns {string} String capitalizado
 */
export const capitalize = (str) => {
  if (!str || typeof str !== 'string') return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * Capitaliza cada palabra de un string
 * @param {string} str - String a capitalizar
 * @returns {string} String con palabras capitalizadas
 */
export const capitalizeWords = (str) => {
  if (!str || typeof str !== 'string') return ''
  return str.split(' ').map(word => capitalize(word)).join(' ')
}

/**
 * Trunca un string a una longitud específica
 * @param {string} str - String a truncar
 * @param {number} length - Longitud máxima
 * @param {string} suffix - Sufijo para strings truncados
 * @returns {string} String truncado
 */
export const truncate = (str, length = 50, suffix = '...') => {
  if (!str || typeof str !== 'string') return ''
  if (str.length <= length) return str
  return str.substring(0, length) + suffix
}

/**
 * Genera un slug a partir de un string
 * @param {string} str - String a convertir
 * @returns {string} Slug generado
 */
export const generateSlug = (str) => {
  if (!str || typeof str !== 'string') return ''

  let slug = str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, '') // NOSONAR: S7781 - replaceAll no acepta regex
    .replace(/[\s_-]+/g, '-') // NOSONAR: S7781 - replaceAll no acepta regex

  // Remove leading and trailing hyphens without regex quantifiers to avoid ReDoS
  // Find first non-hyphen character from start
  let start = 0
  for (let i = 0; i < slug.length; i++) {
    if (slug[i] !== '-') {
      start = i
      break
    }
  }

  // Find last non-hyphen character from end
  let end = slug.length
  for (let i = slug.length - 1; i >= 0; i--) {
    if (slug[i] !== '-') {
      end = i + 1
      break
    }
  }

  return slug.substring(start, end)
}

// ===== UTILIDADES DE VALIDACIÓN =====

/**
 * Valida un email
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido
 */
export const isValidEmail = (email) => {
  if (!email || typeof email !== 'string') return false

  // Use a safe regex pattern that avoids ReDoS vulnerability
  // This pattern uses specific character classes instead of negative character classes with quantifiers
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email)
}

/**
 * Valida un teléfono
 * @param {string} phone - Teléfono a validar
 * @returns {boolean} True si es válido
 */
export const isValidPhone = (phone) => {
  if (!phone || typeof phone !== 'string') return false

  const phoneRegex = /^\+?[1-9]\d{0,15}$/
  return phoneRegex.test(phone.replace(/\s/g, '')) // NOSONAR: S7781 - replaceAll no acepta regex
}

/**
 * Valida un documento de identidad
 * @param {string} document - Documento a validar
 * @param {string} type - Tipo de documento
 * @returns {boolean} True si es válido
 */
export const isValidDocument = (document, type = 'cedula') => {
  if (!document || typeof document !== 'string') return false

  // NOSONAR: S7781 - replaceAll() no acepta regex como primer argumento, usar replace() con regex para eliminar no-dígitos
  const cleanDoc = document.replace(/\D/g, '') // NOSONAR: S7781

  switch (type.toLowerCase()) {
    case 'cedula':
      return cleanDoc.length >= 7 && cleanDoc.length <= 10
    case 'pasaporte':
      return cleanDoc.length >= 6 && cleanDoc.length <= 12
    case 'nit':
      return cleanDoc.length >= 9 && cleanDoc.length <= 10
    default:
      return cleanDoc.length >= 5 && cleanDoc.length <= 15
  }
}

// ===== UTILIDADES DE ROLES Y PERMISOS =====

/**
 * Verifica si un usuario tiene un rol específico
 * @param {Array} userRoles - Roles del usuario
 * @param {string} role - Rol a verificar
 * @returns {boolean} True si tiene el rol
 */
export const hasRole = (userRoles, role) => {
  if (!userRoles || !Array.isArray(userRoles)) return false

  return userRoles.some(userRole => {
    const roleName = typeof userRole === 'string' ? userRole : userRole.nombre_rol
    return roleName === role
  })
}

/**
 * Verifica si un usuario tiene alguno de los roles especificados
 * @param {Array} userRoles - Roles del usuario
 * @param {Array} roles - Roles a verificar
 * @returns {boolean} True si tiene alguno de los roles
 */
export const hasAnyRole = (userRoles, roles) => {
  if (!userRoles || !Array.isArray(userRoles) || !roles || !Array.isArray(roles)) {
    return false
  }

  return roles.some(role => hasRole(userRoles, role))
}

/**
 * Verifica si un usuario tiene un permiso específico
 * @param {Array} userRoles - Roles del usuario
 * @param {string} permission - Permiso a verificar
 * @returns {boolean} True si tiene el permiso
 */
export const hasPermission = (userRoles, permission) => {
  if (!userRoles || !Array.isArray(userRoles)) return false

  return userRoles.some(userRole => {
    const roleName = typeof userRole === 'string' ? userRole : userRole.nombre_rol
    const rolePermissions = PERMISSIONS[roleName] || []
    return rolePermissions.includes(permission)
  })
}

/**
 * Obtiene el rol principal de un usuario
 * @param {Array} userRoles - Roles del usuario
 * @returns {string} Rol principal
 */
export const getPrimaryRole = (userRoles) => {
  if (!userRoles || !Array.isArray(userRoles) || userRoles.length === 0) {
    return ROLES.USUARIO
  }

  // Orden de prioridad de roles
  const rolePriority = [
    ROLES.SUPERADMIN,
    ROLES.ADMINISTRADOR,
    ROLES.ENTRENADOR,
    ROLES.DEPORTISTA,
    ROLES.ACUDIENTE,
    ROLES.USUARIO
  ]

  for (const role of rolePriority) {
    if (hasRole(userRoles, role)) {
      return role
    }
  }

  return ROLES.USUARIO
}

// ===== UTILIDADES DE FORMATEO =====

/**
 * Formatea un número como moneda
 * @param {number} amount - Cantidad a formatear
 * @param {string} currency - Moneda
 * @param {string} locale - Locale para formateo
 * @returns {string} Cantidad formateada
 */
export const formatCurrency = (amount, currency = 'COP', locale = 'es-CO') => {
  if (typeof amount !== 'number' || Number.isNaN(amount)) return '$0'

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency
  }).format(amount)
}

/**
 * Formatea un número con separadores de miles
 * @param {number} number - Número a formatear
 * @param {string} locale - Locale para formateo
 * @returns {string} Número formateado
 */
export const formatNumber = (number, locale = 'es-CO') => {
  if (typeof number !== 'number' || Number.isNaN(number)) return '0'

  return new Intl.NumberFormat(locale).format(number)
}

/**
 * Formatea un porcentaje
 * @param {number} value - Valor a formatear
 * @param {number} decimals - Número de decimales
 * @returns {string} Porcentaje formateado
 */
export const formatPercentage = (value, decimals = 1) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '0%'

  return `${value.toFixed(decimals)}%`
}

// ===== UTILIDADES DE ARRAY =====

/**
 * Elimina duplicados de un array
 * @param {Array} array - Array a procesar
 * @param {string} key - Clave para objetos
 * @returns {Array} Array sin duplicados
 */
export const removeDuplicates = (array, key = null) => {
  if (!Array.isArray(array)) return []

  if (key) {
    const seen = new Set()
    return array.filter(item => {
      const value = item[key]
      if (seen.has(value)) return false
      seen.add(value)
      return true
    })
  }

  return [...new Set(array)]
}

/**
 * Agrupa elementos de un array por una clave
 * @param {Array} array - Array a agrupar
 * @param {string} key - Clave para agrupar
 * @returns {Object} Objeto con grupos
 */
export const groupBy = (array, key) => {
  if (!Array.isArray(array)) return {}

  return array.reduce((groups, item) => {
    const group = item[key]
    if (!groups[group]) {
      groups[group] = []
    }
    groups[group].push(item)
    return groups
  }, {})
}

/**
 * Ordena un array por una clave específica
 * @param {Array} array - Array a ordenar
 * @param {string} key - Clave para ordenar
 * @param {string} direction - Dirección del ordenamiento
 * @returns {Array} Array ordenado
 */
export const sortBy = (array, key, direction = 'asc') => {
  if (!Array.isArray(array)) return []

  return [...array].sort((a, b) => {
    const aVal = a[key]
    const bVal = b[key]

    if (aVal < bVal) return direction === 'asc' ? -1 : 1
    if (aVal > bVal) return direction === 'asc' ? 1 : -1
    return 0
  })
}

// ===== UTILIDADES DE OBJETO =====

/**
 * Hace una copia profunda de un objeto
 * @param {any} obj - Objeto a copiar
 * @returns {any} Copia profunda del objeto
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj
  // NOSONAR: S7732 - instanceof Date es necesario para detectar objetos Date correctamente
  if (obj instanceof Date) return new Date(obj.valueOf())
  if (Array.isArray(obj)) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (Object.hasOwn(obj, key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * Fusiona objetos de forma profunda
 * @param {Object} target - Objeto objetivo
 * @param {...Object} sources - Objetos fuente
 * @returns {Object} Objeto fusionado
 */
export const deepMerge = (target, ...sources) => {
  if (!sources.length) return target
  const source = sources.shift()

  if (isObject(target) && isObject(source)) {
    for (const key in source) {
      if (isObject(source[key])) {
        if (!target[key]) Object.assign(target, { [key]: {} })
        deepMerge(target[key], source[key])
      } else {
        Object.assign(target, { [key]: source[key] })
      }
    }
  }

  return deepMerge(target, ...sources)
}

/**
 * Verifica si un valor es un objeto
 * @param {any} item - Valor a verificar
 * @returns {boolean} True si es un objeto
 */
const isObject = (item) => {
  return item && typeof item === 'object' && !Array.isArray(item)
}

// ===== UTILIDADES DE STORAGE =====

/**
 * Guarda datos en localStorage con manejo de errores
 * @param {string} key - Clave
 * @param {any} value - Valor
 * @returns {boolean} True si se guardó correctamente
 */
export const setStorage = (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value))
    return true
  } catch (error) {
    console.error('Error guardando en localStorage:', error)
    return false
  }
}

/**
 * Obtiene datos de localStorage con manejo de errores
 * @param {string} key - Clave
 * @param {any} defaultValue - Valor por defecto
 * @returns {any} Valor obtenido
 */
export const getStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key)
    return item ? JSON.parse(item) : defaultValue
  } catch (error) {
    console.error('Error obteniendo de localStorage:', error)
    return defaultValue
  }
}

/**
 * Elimina datos de localStorage
 * @param {string} key - Clave
 * @returns {boolean} True si se eliminó correctamente
 */
export const removeStorage = (key) => {
  try {
    localStorage.removeItem(key)
    return true
  } catch (error) {
    console.error('Error eliminando de localStorage:', error)
    return false
  }
}

// ===== UTILIDADES DE DEBOUNCE =====

/**
 * Crea una función con debounce
 * @param {Function} func - Función a ejecutar
 * @param {number} delay - Retraso en ms
 * @returns {Function} Función con debounce
 */
export const debounce = (func, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}

/**
 * Crea una función con throttle
 * @param {Function} func - Función a ejecutar
 * @param {number} delay - Retraso en ms
 * @returns {Function} Función con throttle
 */
export const throttle = (func, delay) => {
  let lastCall = 0
  return (...args) => {
    const now = Date.now()
    if (now - lastCall >= delay) {
      lastCall = now
      return func(...args)
    }
  }
}

// ===== UTILIDADES DE URL =====

/**
 * Construye una URL con parámetros
 * @param {string} base - URL base
 * @param {Object} params - Parámetros
 * @returns {string} URL construida
 */
export const buildURL = (base, params = {}) => {
  const url = new URL(base)
  Object.keys(params).forEach(key => {
    if (params[key] !== null && params[key] !== undefined) {
      url.searchParams.append(key, params[key])
    }
  })
  return url.toString()
}

/**
 * Obtiene parámetros de una URL
 * @param {string} url - URL a analizar
 * @returns {Object} Parámetros obtenidos
 */
export const getURLParams = (url) => {
  const urlObj = new URL(url)
  const params = {}
  urlObj.searchParams.forEach((value, key) => {
    params[key] = value
  })
  return params
}
