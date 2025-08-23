// Archivo de utilidades y funciones helper
// Siguiendo el principio SRP - este archivo solo maneja funciones de utilidad

/**
 * Formatea un número de teléfono para mostrar
 * @param {string} phone - Número de teléfono sin formato
 * @returns {string} Número de teléfono formateado
 */
export function formatPhoneNumber(phone) {
  if (!phone) return ''

  // Remover todos los caracteres no numéricos
  const cleaned = phone.replace(/\D/g, '')

  // Formatear según el patrón colombiano
  if (cleaned.length === 10) {
    return `+57 ${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`
  }

  if (cleaned.length === 11 && cleaned.startsWith('57')) {
    return `+${cleaned.slice(0, 2)} ${cleaned.slice(2, 5)} ${cleaned.slice(5, 8)} ${cleaned.slice(8)}`
  }

  return phone
}

/**
 * Capitaliza la primera letra de cada palabra
 * @param {string} text - Texto a capitalizar
 * @returns {string} Texto capitalizado
 */
export function capitalizeWords(text) {
  if (!text) return ''

  return text
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}

/**
 * Formatea una fecha para mostrar
 * @param {Date|string} date - Fecha a formatear
 * @param {string} locale - Locale para el formato (default: 'es-CO')
 * @returns {string} Fecha formateada
 */
export function formatDate(date, locale = 'es-CO') {
  if (!date) return ''

  const dateObj = new Date(date)

  if (isNaN(dateObj.getTime())) return ''

  return dateObj.toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

/**
 * Valida si un email tiene formato válido
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido, false si no
 */
export function isValidEmail(email) {
  if (!email) return false

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Trunca un texto a una longitud específica
 * @param {string} text - Texto a truncar
 * @param {number} maxLength - Longitud máxima
 * @param {string} suffix - Sufijo a agregar (default: '...')
 * @returns {string} Texto truncado
 */
export function truncateText(text, maxLength, suffix = '...') {
  if (!text || text.length <= maxLength) return text

  return text.slice(0, maxLength) + suffix
}

/**
 * Genera un ID único simple
 * @returns {string} ID único
 */
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

/**
 * Debounce function para optimizar llamadas
 * @param {Function} func - Función a ejecutar
 * @param {number} wait - Tiempo de espera en ms
 * @returns {Function} Función debounced
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
