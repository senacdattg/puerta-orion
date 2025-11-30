/**
 * Utility functions for form field normalization
 * Provides reusable normalization functions following DRY principles
 */

const MAX_DOCUMENTO = 10
const MIN_DOCUMENTO = 6

/**
 * Normalizes document number by removing non-digits and limiting length
 * @param {string} valor - Document value to normalize
 * @param {number} maxLength - Maximum length (default: MAX_DOCUMENTO)
 * @returns {string} Normalized document
 */
export function normalizarDocumento(valor = '', maxLength = MAX_DOCUMENTO) {
  return (valor || '')
    .toString()
    .replace(/\D/g, '') // NOSONAR: S7781 - replaceAll() no acepta regex
    .slice(0, maxLength)
}

/**
 * Normalizes amount value by removing non-numeric characters and handling decimals
 * @param {string} valor - Amount value to normalize
 * @returns {string} Normalized amount
 */
export function normalizarMonto(valor = '') {
  if (!valor) {
    return ''
  }
  const saneado = valor
    .toString()
    .replace(/[^0-9.,]/g, '') // NOSONAR: S7781 - replaceAll() no acepta regex
    .replaceAll(',', '.')

  const partes = saneado.split('.')
  if (partes.length === 1) {
    return partes[0]
  }

  const enteros = partes.shift() || ''
  const decimales = partes.join('')
  return decimales ? `${enteros}.${decimales}` : enteros
}

/**
 * Parses amount value to number
 * @param {string|number} valor - Amount value to parse
 * @returns {number} Parsed number or NaN if invalid
 */
export function parseMonto(valor = '') {
  if (valor === '' || valor === null || valor === undefined) {
    return Number.NaN
  }
  const numero = Number(valor)
  return Number.isFinite(numero) ? numero : Number.NaN
}

/**
 * Normalizes payment method ID
 * @param {any} valor - Payment method ID value
 * @returns {number|undefined} Normalized ID or undefined
 */
export function normalizarIdMetodoPago(valor) {
  if (valor === undefined || valor === null || valor === '') {
    return undefined
  }
  const numero = Number(valor)
  return Number.isFinite(numero) ? numero : undefined
}

export { MIN_DOCUMENTO, MAX_DOCUMENTO }

