/**
 * Utility functions for input sanitization
 * Provides reusable sanitization functions following DRY principles
 */

const LOCALE_COL = 'es-CO'

/**
 * Transforms text to uppercase using locale
 * @param {string} valor - Value to transform
 * @returns {string} Uppercase value
 */
function transformarMayusculas(valor = '') {
  if (!valor || typeof valor !== 'string') {
    return ''
  }
  return valor.toLocaleUpperCase(LOCALE_COL)
}

/**
 * Sanitizes name input by removing invalid characters
 * @param {string} valor - Name value to sanitize
 * @param {boolean} obligatorio - Whether field is required
 * @returns {string} Sanitized name
 */
export function sanitizarNombre(valor = '', obligatorio = true) {
  const mayus = transformarMayusculas(valor)
  // NOSONAR: S7781 - replaceAll() no acepta regex
  const limpio = mayus.replace(/[^A-ZÁÉÍÓÚÜÑ\s]/g, '').replace(/\s{2,}/g, ' ')
  if (!obligatorio && !limpio.trim()) {
    return ''
  }
  return limpio.trimStart()
}

/**
 * Sanitizes address input by removing invalid characters
 * @param {string} valor - Address value to sanitize
 * @returns {string} Sanitized address
 */
export function sanitizarDireccion(valor = '') {
  const mayus = transformarMayusculas(valor)
  // NOSONAR: S7781 - replaceAll() no acepta regex
  return mayus.replace(/[^A-Z0-9ÁÉÍÓÚÜÑ#\-.\s]/g, '').replace(/\s{2,}/g, ' ').trimStart()
}

/**
 * Sanitizes string by normalizing spaces
 * @param {string} valor - String value to sanitize
 * @returns {string} Sanitized string
 */
export function sanitizarString(valor) {
  if (!valor || typeof valor !== 'string') {
    return ''
  }
  // NOSONAR: S7781 - replaceAll() no acepta regex
  return valor.replace(/\s+/g, ' ').trim()
}

