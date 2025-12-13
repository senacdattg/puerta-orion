/**
 * Utility functions for date parsing and validation
 * Provides reusable date functions following DRY principles
 */

/**
 * Parses an ISO date string to a local Date object
 * Handles both full ISO strings and date-only strings (YYYY-MM-DD)
 * @param {string} iso - ISO date string
 * @returns {Date|null} Parsed date or null if invalid
 */
export function parseISODateLocal(iso) {
  if (!iso) {
    return null
  }
  if (typeof iso === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const [y, m, d] = iso.split('-').map(n => Number.parseInt(n, 10))
    return new Date(y, m - 1, d)
  }
  const d = new Date(iso)
  return Number.isNaN(d.getTime()) ? null : d
}

/**
 * Validates if a date string is valid
 * @param {string} fecha - Date string to validate
 * @returns {boolean} True if date is valid
 */
export function esFechaValida(fecha) {
  return !!fecha && !Number.isNaN(Date.parse(fecha))
}

