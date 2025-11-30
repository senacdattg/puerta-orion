/**
 * Utility functions for normalizing text inputs
 * Provides reusable normalization functions following DRY principles
 */

const LOCALE_COL = 'es-CO'

/**
 * Normalizes a name value by converting to uppercase and removing invalid characters
 * @param {string} valor - Value to normalize
 * @param {RegExp} allowedPattern - Regex pattern for allowed characters
 * @returns {string} Normalized value
 */
function normalizeNameWithPattern(valor = '', allowedPattern = /[^A-ZÁÉÍÓÚÜÑ\s'-]/g) {
  if (!valor || typeof valor !== 'string') {
    return ''
  }

  const mayus = valor.toLocaleUpperCase(LOCALE_COL)
  // NOSONAR: S7781 - replaceAll() no acepta regex
  return mayus.replace(allowedPattern, '').replace(/\s{2,}/g, ' ').trimStart()
}

/**
 * Normalizes a name for standard text fields (tipo-documento, sexo)
 * @param {string} valor - Value to normalize
 * @returns {string} Normalized value
 */
export function normalizarNombre(valor = '') {
  return normalizeNameWithPattern(valor, /[^A-ZÁÉÍÓÚÜÑ\s'-]/g)
}

/**
 * Normalizes a name for city fields (allows numbers and dots)
 * @param {string} valor - Value to normalize
 * @returns {string} Normalized value
 */
export function normalizarNombreCiudad(valor = '') {
  return normalizeNameWithPattern(valor, /[^A-ZÁÉÍÓÚÜÑ0-9\s'.-]/g)
}

/**
 * Normalizes a code value (alphanumeric with hyphens)
 * @param {string} valor - Value to normalize
 * @param {number} maxLength - Maximum length
 * @returns {string} Normalized value
 */
export function normalizarCodigo(valor = '', maxLength = 20) {
  if (!valor) {
    return ''
  }

  const valorStr = String(valor)
  const mayus = valorStr.toLocaleUpperCase(LOCALE_COL)
  // NOSONAR: S7781 - replaceAll() no acepta regex
  return mayus.replace(/[^A-Z0-9-]/g, '').slice(0, maxLength)
}

/**
 * Normalizes a description value
 * @param {string} valor - Value to normalize
 * @param {number} maxLength - Maximum length
 * @returns {string} Normalized value
 */
export function normalizarDescripcion(valor = '', maxLength = 500) {
  if (!valor) {
    return ''
  }

  const mayus = valor.toLocaleUpperCase(LOCALE_COL)
  // NOSONAR: S7781 - replaceAll() no acepta regex
  return mayus.replace(/\s{2,}/g, ' ').trim().slice(0, maxLength)
}

